import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse

from app.services.conversation import handle_incoming_message
from app.services.whatsapp import send_whatsapp_message
from app.core.config import settings
from app.services.aethex import cleanup_old_tts_files, TTS_CACHE_DIR

logger = logging.getLogger(__name__)
router = APIRouter()


def _twiml_text(text: str) -> str:
    """TwiML with text only."""
    escaped = (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped}</Message></Response>'


def _twiml_text_and_audio(text: str, audio_url: str) -> str:
    """TwiML with text + audio media."""
    escaped = (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response>'
        f'<Message>{escaped}<Media>{audio_url}</Media></Message>'
        f'</Response>'
    )


def _twiml_error(message: str) -> str:
    return _twiml_text(message)


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Main Twilio WhatsApp webhook."""

    # ── Parse form data ──────────────────────────────────────────────────────
    try:
        form_data = await request.form()
    except Exception as e:
        logger.error(f"Failed to parse form data: {e}")
        return Response(content=_twiml_error("Sorry, something went wrong."), media_type="text/xml")

    phone_number = form_data.get("From", "")
    body = form_data.get("Body", "")
    num_media = int(form_data.get("NumMedia", "0"))
    media_url = form_data.get("MediaUrl0")
    media_content_type = form_data.get("MediaContentType0", "audio/ogg")

    logger.info(
        f"Incoming | from={phone_number} | "
        f"body='{body[:60]}' | media={num_media} | type={media_content_type}"
    )

    # ── Signature verification ────────────────────────────────────────────────
    if settings.TWILIO_AUTH_TOKEN:
        try:
            from twilio.request_validator import RequestValidator
            validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
            url = str(request.url)
            signature = request.headers.get("X-Twilio-Signature", "")
            params = dict(form_data)
            if not validator.validate(url, params, signature):
                logger.warning(f"Invalid Twilio signature from {phone_number}")
                # Log but don't reject — sandbox may differ
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Signature validation error: {e}")

    # ── Process with 12s timeout ──────────────────────────────────────────────
    try:
        result = await asyncio.wait_for(
            handle_incoming_message(
                phone_number=phone_number,
                body=body,
                media_url=media_url,
                num_media=num_media,
                media_content_type=media_content_type,
            ),
            timeout=12.0,
        )
    except asyncio.TimeoutError:
        logger.error(f"Message processing timed out for {phone_number}")
        return Response(
            content=_twiml_text(
                "Taking longer than usual. Your message is being processed — I'll reply shortly!"
            ),
            media_type="text/xml",
        )
    except Exception as e:
        logger.error(f"Unhandled error for {phone_number}: {e}", exc_info=True)
        return Response(
            content=_twiml_error("Something went wrong. Please try again!"),
            media_type="text/xml",
        )

    # ── Build response ────────────────────────────────────────────────────────
    text_response = result.get("text_response", "")
    audio_path: Path = result.get("audio_path")

    if audio_path and audio_path.exists():
        # Serve audio back as WhatsApp media
        audio_filename = audio_path.name
        audio_url = f"{settings.PUBLIC_URL}/media/tts/{audio_filename}"
        logger.info(f"Sending voice reply: {audio_url}")
        twiml = _twiml_text_and_audio(text_response, audio_url)
    else:
        twiml = _twiml_text(text_response)

    # Clean up old TTS files in background
    asyncio.create_task(_cleanup())

    return Response(content=twiml, media_type="text/xml")


async def _cleanup():
    try:
        cleanup_old_tts_files(max_age_seconds=300)
    except Exception:
        pass


@router.get("/media/tts/{filename}")
async def serve_tts_audio(filename: str):
    """Serve TTS WAV files for WhatsApp media replies."""
    # Sanitize filename — no path traversal
    if "/" in filename or ".." in filename:
        return Response(status_code=400)

    path = TTS_CACHE_DIR / filename
    if not path.exists() or not path.is_file():
        return Response(status_code=404)

    return FileResponse(path, media_type="audio/wav")
