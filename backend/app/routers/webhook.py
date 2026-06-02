import asyncio
import hashlib
import hmac
import base64
import logging

from fastapi import APIRouter, Request, Response, HTTPException

from app.core.config import settings
from app.services.conversation import handle_incoming_message
from app.services.whatsapp import build_twiml_text, split_message, send_whatsapp_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


def _validate_twilio_signature(url: str, params: dict, signature: str, auth_token: str) -> bool:
    """Validate that a request actually came from Twilio using HMAC-SHA1."""
    if not auth_token:
        return True  # skip in dev mode

    data = url
    for key in sorted(params.keys()):
        data += key + str(params[key])

    expected = base64.b64encode(
        hmac.new(auth_token.encode(), data.encode(), hashlib.sha1).digest()
    ).decode()

    return hmac.compare_digest(expected, signature)


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Twilio sends a POST here every time someone messages the WhatsApp sandbox.
    We process it and return TwiML.
    """
    form_data = await request.form()

    # --- Signature validation (Fix #1) ---
    if settings.TWILIO_AUTH_TOKEN:
        signature = request.headers.get("X-Twilio-Signature", "")
        url = str(request.url)
        params = {k: str(v) for k, v in form_data.items()}
        if not _validate_twilio_signature(url, params, signature, settings.TWILIO_AUTH_TOKEN):
            logger.warning(f"Invalid Twilio signature from {request.client.host}")
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    phone_number = form_data.get("From", "")
    body = form_data.get("Body", "")
    num_media = int(form_data.get("NumMedia", "0"))
    media_url = form_data.get("MediaUrl0", None)
    media_content_type = form_data.get("MediaContentType0", "audio/ogg")

    logger.info(
        f"Incoming from {phone_number}: "
        f"body='{body[:50]}' media={num_media} type={media_content_type}"
    )

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
        logger.warning(f"Processing timed out for {phone_number}")
        result = {
            "text_response": "I am taking a bit longer than usual. Please send your message again in a moment.",
            "audio_bytes": None,
        }

    text_response = result["text_response"]

    # --- Message splitting (Fix #3) ---
    chunks = split_message(text_response)

    if len(chunks) == 1:
        twiml = build_twiml_text(chunks[0])
    else:
        # First chunk goes via TwiML (immediate response)
        twiml = build_twiml_text(chunks[0])
        # Remaining chunks sent via REST API as follow-up messages
        for chunk in chunks[1:]:
            await send_whatsapp_message(phone_number, chunk)

    return Response(content=twiml, media_type="application/xml")


@router.get("/whatsapp")
async def whatsapp_webhook_verify(request: Request):
    """Health check endpoint for Twilio webhook verification."""
    return {"status": "ok", "message": "Tonative SME Bot webhook is active"}
