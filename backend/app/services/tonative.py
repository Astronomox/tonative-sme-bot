import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def detect_language(text: str) -> str:
    """
    Detect the language of incoming text.
    When Tonative API is available, this calls their language detection endpoint.
    Falls back to a simple heuristic for the hackathon MVP.
    """
    if settings.tonative_enabled:
        return await _tonative_detect(text)
    return _fallback_detect(text)


async def translate_to_english(text: str, source_lang: str) -> str:
    """
    Translate incoming text to English for LLM processing.
    If already English, returns as-is.
    """
    if source_lang == "en":
        return text

    if settings.tonative_enabled:
        result = await _tonative_translate(text, source_lang, "en")
        if result:
            return result

    # Fallback: pass through (Groq's Llama handles many languages natively)
    logger.info(f"Tonative not available, passing {source_lang} text directly to LLM")
    return text


async def translate_from_english(text: str, target_lang: str) -> str:
    """
    Translate the AI response from English back to the user's language.
    If target is English, returns as-is.
    """
    if target_lang == "en":
        return text

    if settings.tonative_enabled:
        result = await _tonative_translate(text, "en", target_lang)
        if result:
            return result

    # Fallback: the LLM is instructed to respond in the user's language,
    # so in many cases the response is already multilingual
    logger.info(f"Tonative not available, relying on LLM's native {target_lang} capability")
    return text


# ---------------------------------------------------------------------------
# Tonative API calls (plug in when docs arrive)
# ---------------------------------------------------------------------------

async def _tonative_detect(text: str) -> str:
    """Call Tonative's language detection endpoint."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.TONATIVE_API_URL}/detect",
                json={"text": text},
                headers={
                    "Authorization": f"Bearer {settings.TONATIVE_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()
            # Adjust these keys based on actual Tonative API response format
            return data.get("language", data.get("lang", data.get("detected_language", "en")))
    except Exception as e:
        logger.warning(f"Tonative detect failed, using fallback: {e}")
        return _fallback_detect(text)


async def _tonative_translate(text: str, source: str, target: str) -> Optional[str]:
    """Call Tonative's translation endpoint."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{settings.TONATIVE_API_URL}/translate",
                json={
                    "text": text,
                    "source_language": source,
                    "target_language": target,
                },
                headers={
                    "Authorization": f"Bearer {settings.TONATIVE_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("translated_text", data.get("translation", data.get("text", None)))
    except Exception as e:
        logger.warning(f"Tonative translate failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Fallback language detection (simple keyword heuristic)
# ---------------------------------------------------------------------------

_YORUBA_MARKERS = ["bawo", "oga", "ekaaro", "ese", "omo", "owo", "pelu", "nkan", "igba", "aje"]
_HAUSA_MARKERS = ["sannu", "barka", "ina", "yaya", "malam", "kudin", "aiki", "gida", "ruwa", "abinci"]
_FRENCH_MARKERS = ["bonjour", "merci", "comment", "oui", "entreprise", "argent", "aide", "travail"]
_ARABIC_MARKERS = ["مرحبا", "شكرا", "كيف", "مساعدة", "عمل", "مال"]


def _fallback_detect(text: str) -> str:
    """Keyword-based language detection with minimum threshold to avoid false positives."""
    lower = text.lower()

    # Arabic uses a different script, so even one marker is reliable
    for marker in _ARABIC_MARKERS:
        if marker in text:
            return "ar"

    # For Latin-script languages, require 2+ marker hits to avoid
    # false positives from Nigerian English slang (e.g. "omo", "oga")
    yo_hits = sum(1 for m in _YORUBA_MARKERS if m in lower)
    ha_hits = sum(1 for m in _HAUSA_MARKERS if m in lower)
    fr_hits = sum(1 for m in _FRENCH_MARKERS if m in lower)

    if yo_hits >= 2:
        return "yo"
    if ha_hits >= 2:
        return "ha"
    if fr_hits >= 2:
        return "fr"

    return "en"
