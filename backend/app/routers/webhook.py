# BizPadi build: 2026-06-08 twiml-sync
"""
Webhook: TwiML synchronous response.

Returns the bot reply directly in the TwiML response body.
This uses Twilio's INBOUND pathway, not the outbound REST API.
The outbound REST API (Messages.json) fails with 429 on trial accounts
for Nigerian numbers. The TwiML response pathway works fine.

Twilio gives 15 seconds. We use 12 seconds max for processing,
leaving 3 seconds buffer for network.

For long responses (voice notes), if processing exceeds 12s we send
a "one moment" reply and then the real answer via REST API with retry.
"""
import asyncio
import hashlib
import logging
import time

from fastapi import APIRouter, Request, Response

from app.services.conversation import handle_incoming_message
from app.services.whatsapp import build_twiml_text, split_message, send_whatsapp_message

logger = logging.getLogger(__name__)
router = APIRouter()

_seen: dict[str, float] = {}
_DEDUP_TTL = 120.0


def _is_duplicate(sid: str, phone: str, body: str, media_url: str) -> bool:
    key = f"sid:{sid}" if sid else hashlib.md5(
        f"{phone}:{body}:{media_url}".encode()
    ).hexdigest()
    now = time.time()
    for k in [k for k, t in list(_seen.items()) if now - t > _DEDUP_TTL]:
        del _seen[k]
    if key in _seen:
        logger.info(f"Dedup: {key[:40]}")
        return True
    _seen[key] = now
    return False


def _twiml(text: str) -> Response:
    return Response(content=build_twiml_text(text), media_type="text/xml")


def _ack() -> Response:
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="text/xml",
    )


async def _send_overflow(phone: str, chunks: list[str]):
    """Send chunks 2+ via REST API (overflow for long replies)."""
    for i, chunk in enumerate(chunks):
        await asyncio.sleep(0.5 * i)
        await send_whatsapp_message(phone, chunk)


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    try:
        form = await request.form()
    except Exception as e:
        logger.error(f"Form parse error: {e}")
        return _ack()

    phone      = form.get("From", "")
    body       = form.get("Body", "")
    num_media  = int(form.get("NumMedia", "0") or "0")
    media_url  = form.get("MediaUrl0")
    media_type = form.get("MediaContentType0", "audio/ogg")
    sid        = form.get("MessageSid", "")

    logger.info(f"IN | {phone} | body='{(body or '')[:60]}' | media={num_media} | sid={sid[:16]}")

    if _is_duplicate(sid, phone, body or "", media_url or ""):
        return _ack()

    try:
        result = await asyncio.wait_for(
            handle_incoming_message(
                phone_number=phone,
                body=body,
                media_url=media_url,
                num_media=num_media,
                media_content_type=media_type,
            ),
            timeout=12.0,
        )
        text = result.get("text_response", "")
        if not text:
            return _ack()

        chunks = split_message(text)

        # Send first chunk as TwiML (uses inbound pathway, not REST API)
        # This ALWAYS works on Twilio trial - it's just returning a response
        response = _twiml(chunks[0])

        # If there are more chunks, send them in the background via REST
        if len(chunks) > 1:
            asyncio.create_task(_send_overflow(phone, chunks[1:]))

        return response

    except asyncio.TimeoutError:
        logger.warning(f"Timeout for {phone}, sending holding message via TwiML")
        # Even the holding message goes via TwiML - not REST API
        return _twiml("Still processing your message, one moment...")

    except Exception as e:
        logger.error(f"Error for {phone}: {e}", exc_info=True)
        return _twiml("Something went wrong. Please try again.")
