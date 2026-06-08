# BizPadi build: 2026-06-08 final
"""
Webhook: WhatsApp inbound from Twilio.

Architecture: Fire-and-forget async processing.
Twilio WhatsApp requires HTTP response within 15 seconds.
Processing (voice + LLM) takes 5-25 seconds.
Solution: ACK Twilio immediately (<100ms), process in background,
reply via Twilio REST API when done.
"""
import asyncio
import hashlib
import logging
import time

from fastapi import APIRouter, Request, Response

from app.services.conversation import handle_incoming_message
from app.services.whatsapp import send_whatsapp_message, split_message

logger = logging.getLogger(__name__)
router = APIRouter()

_seen: dict[str, float] = {}
_DEDUP_TTL = 120.0


def _is_duplicate(sid: str, phone: str, body: str, media_url: str) -> bool:
    key = f"sid:{sid}" if sid else hashlib.md5(f"{phone}:{body}:{media_url}".encode()).hexdigest()
    now = time.time()
    for k in [k for k, t in list(_seen.items()) if now - t > _DEDUP_TTL]:
        del _seen[k]
    if key in _seen:
        logger.info(f"Dedup: {key[:40]}")
        return True
    _seen[key] = now
    return False


def _ack() -> Response:
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="text/xml",
    )


async def _process_and_reply(phone: str, body: str, media_url, num_media: int, media_type: str):
    try:
        result = await handle_incoming_message(
            phone_number=phone,
            body=body,
            media_url=media_url,
            num_media=num_media,
            media_content_type=media_type,
        )
        text = result.get("text_response", "")
        if not text:
            return
        chunks = split_message(text)
        for i, chunk in enumerate(chunks):
            if i > 0:
                await asyncio.sleep(0.5)
            await send_whatsapp_message(phone, chunk)
    except Exception as e:
        logger.error(f"Background error for {phone}: {e}", exc_info=True)
        try:
            await send_whatsapp_message(phone, "Something went wrong. Please try again.")
        except Exception:
            pass


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

    asyncio.create_task(_process_and_reply(phone, body, media_url, num_media, media_type))
    return _ack()
