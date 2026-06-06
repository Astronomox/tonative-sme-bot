# BizPadi build: 2026-06-06 22:59:25
import asyncio
import hashlib
import logging
import time
from typing import Optional

from fastapi import APIRouter, Request, Response

from app.services.conversation import handle_incoming_message
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Deduplication   prevents double replies when Twilio retries on slow responses
_seen: dict[str, float] = {}
_DEDUP_TTL = 30.0


def _is_duplicate(phone: str, body: str, media_url: str) -> bool:
    key = hashlib.md5(f"{phone}:{body}:{media_url}".encode()).hexdigest()
    now = time.time()
    _seen.update({k: v for k, v in _seen.items() if now - v < _DEDUP_TTL})
    if key in _seen:
        return True
    _seen[key] = now
    return False


def _twiml(text: str) -> str:
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped}</Message></Response>'


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    try:
        form = await request.form()
    except Exception as e:
        logger.error(f"Form parse error: {e}")
        return Response(content=_twiml("Something went wrong. Try again."), media_type="text/xml")

    phone = form.get("From", "")
    body = form.get("Body", "")
    num_media = int(form.get("NumMedia", "0"))
    media_url = form.get("MediaUrl0")
    media_type = form.get("MediaContentType0", "audio/ogg")

    logger.info(f"IN | {phone} | body='{body[:60]}' | media={num_media}")

    if _is_duplicate(phone, body or "", media_url or ""):
        logger.info(f"Duplicate from {phone}, skipping")
        return Response(content=_twiml(""), media_type="text/xml")

    try:
        result = await asyncio.wait_for(
            handle_incoming_message(
                phone_number=phone,
                body=body,
                media_url=media_url,
                num_media=num_media,
                media_content_type=media_type,
            ),
            timeout=45.0,
        )
    except asyncio.TimeoutError:
        logger.error(f"Timeout for {phone}")
        return Response(
            content=_twiml("Processing your message   I will reply in a moment."),
            media_type="text/xml",
        )
    except Exception as e:
        logger.error(f"Error for {phone}: {e}", exc_info=True)
        return Response(content=_twiml("Something went wrong. Try again."), media_type="text/xml")

    return Response(content=_twiml(result.get("text_response", "")), media_type="text/xml")
