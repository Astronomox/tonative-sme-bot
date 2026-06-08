# BizPadi build: 2026-06-08 async-webhook-fix
"""
Webhook router.

KEY ARCHITECTURE: Async background processing.

Twilio WhatsApp has a 15-second response window.
Voice notes + LLM calls take 10-30 seconds.
Solution: ACK immediately with empty 200 OK, process in background,
send reply via Twilio REST API (send_whatsapp_message).

This eliminates ALL timeout-related silent failures.
"""
import asyncio
import hashlib
import logging
import time

from fastapi import APIRouter, Request, Response

from app.services.conversation import handle_incoming_message
from app.services.whatsapp import send_whatsapp_message, split_message
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Dedup: prevents double processing when Twilio retries (same MessageSid)
_seen: dict[str, float] = {}
_DEDUP_TTL = 120.0  # 2 minutes - covers Twilio's full retry window


def _is_duplicate(message_sid: str, phone: str, body: str, media_url: str) -> bool:
    if message_sid:
        key = f"sid:{message_sid}"
    else:
        key = hashlib.md5(f"{phone}:{body}:{media_url}".encode()).hexdigest()

    now = time.time()
    # Clean expired entries
    for k in [k for k, t in list(_seen.items()) if now - t > _DEDUP_TTL]:
        del _seen[k]

    if key in _seen:
        logger.info(f"Duplicate {key[:40]}, skipping")
        return True
    _seen[key] = now
    return False


def _ack() -> Response:
    """Empty 200 OK TwiML - tells Twilio we got the message."""
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="text/xml",
    )


async def _process_and_reply(phone: str, body: str, media_url, num_media: int, media_type: str):
    """
    Background task: process message and send reply via REST API.
    Runs AFTER webhook already returned 200 OK to Twilio.
    No timeout pressure - Twilio is already satisfied.
    """
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

        # Split long messages and send each chunk
        chunks = split_message(text)
        for i, chunk in enumerate(chunks):
            if i > 0:
                await asyncio.sleep(0.5)  # Small delay between chunks
            await send_whatsapp_message(phone, chunk)

    except Exception as e:
        logger.error(f"Background processing error for {phone}: {e}", exc_info=True)
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

    phone = form.get("From", "")
    body = form.get("Body", "")
    num_media = int(form.get("NumMedia", "0") or "0")
    media_url = form.get("MediaUrl0")
    media_type = form.get("MediaContentType0", "audio/ogg")
    message_sid = form.get("MessageSid", "")

    logger.info(f"IN | {phone} | body='{(body or '')[:60]}' | media={num_media} | sid={message_sid[:16]}")

    # Dedup check - block retries from being re-processed
    if _is_duplicate(message_sid, phone, body or "", media_url or ""):
        return _ack()

    # ACK Twilio immediately - no timeout risk
    # Fire background task to do the actual work
    asyncio.create_task(
        _process_and_reply(phone, body, media_url, num_media, media_type)
    )

    return _ack()
