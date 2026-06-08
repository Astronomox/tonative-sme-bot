import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

WHATSAPP_CHAR_LIMIT = 1500  # safe margin below Twilio's 1600 hard limit


def split_message(text: str, limit: int = WHATSAPP_CHAR_LIMIT) -> list[str]:
    """Split a long message into chunks that fit WhatsApp's character limit."""
    if len(text) <= limit:
        return [text]

    chunks = []
    current_chunk = ""

    paragraphs = text.split("\n\n")

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= limit:
            if current_chunk:
                current_chunk += "\n\n"
            current_chunk += paragraph
        else:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            if len(paragraph) <= limit:
                current_chunk = paragraph
            else:
                # Break long paragraphs into lines, then sentences, then hard-cut
                pieces = paragraph.split("\n")
                for piece in pieces:
                    if len(piece) <= limit:
                        if len(current_chunk) + len(piece) + 1 <= limit:
                            current_chunk += ("\n" if current_chunk else "") + piece
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = piece
                    else:
                        # Split on sentence boundaries (". ")
                        sentences = piece.replace(". ", ".\n").split("\n")
                        for sentence in sentences:
                            if len(current_chunk) + len(sentence) + 1 <= limit:
                                current_chunk += (" " if current_chunk else "") + sentence
                            else:
                                if current_chunk:
                                    chunks.append(current_chunk)
                                # Hard-cut if a single sentence exceeds the limit
                                while len(sentence) > limit:
                                    chunks.append(sentence[:limit])
                                    sentence = sentence[limit:]
                                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks if chunks else [text[:limit]]


def build_twiml_text(message: str) -> str:
    """Build a TwiML response with a text message."""
    escaped = (
        message
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{escaped}</Message>
</Response>"""


def build_twiml_media(message: str, media_url: str) -> str:
    """Build a TwiML response with text + media (voice note)."""
    escaped = (
        message
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>
        <Body>{escaped}</Body>
        <Media>{media_url}</Media>
    </Message>
</Response>"""


async def send_whatsapp_message(to: str, body: str, media_url: Optional[str] = None):
    """Send a WhatsApp message via Twilio REST API with retry for sandbox rate limits."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio credentials not set, skipping send")
        return None

    import asyncio
    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
    data = {"From": settings.TWILIO_WHATSAPP_NUMBER, "To": to, "Body": body}
    if media_url:
        data["MediaUrl"] = media_url

    for attempt in range(4):  # up to 3 retries
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                )
                if response.status_code == 429:
                    # Twilio sandbox rate limit - wait and retry
                    wait = (attempt + 1) * 2.0  # 2s, 4s, 6s
                    logger.warning(f"Twilio 429 for {to}, retrying in {wait}s (attempt {attempt+1})")
                    await asyncio.sleep(wait)
                    continue
                response.raise_for_status()
                logger.info(f"Message sent to {to}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Twilio HTTP {e.response.status_code} for {to}: {e.response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message to {to}: {e}")
            return None

    logger.error(f"Twilio send failed after retries for {to}")
    return None
