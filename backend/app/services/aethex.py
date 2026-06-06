# BizPadi build: 2026-06-06 22:17:17
"""
AethexAI service.
Active: transcribe_audio()   voice note transcription (EN/FR primary, Groq fallback)
Inactive: TTS disabled (causes timeout issues with WhatsApp 15s limit)
"""
import io
import logging
import time
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = settings.AETHEX_BASE_URL
HEADERS = {"X-API-Key": settings.AETHEX_API_KEY}

AETHEX_SUPPORTED_LANGUAGES = {"en", "fr"}
AETHEX_LANG_MAP = {"en": "english", "fr": "french"}

_status = {
    "transcription": {"ok": False, "latency_ms": 0, "error": None},
}


def get_aethex_status() -> dict:
    return _status.copy()


async def transcribe_audio(
    audio_bytes: bytes,
    content_type: str = "audio/ogg",
    detected_language: str = "en",
) -> Optional[str]:
    """Transcribe audio. Aethex primary (EN/FR), Groq Whisper fallback (all languages)."""
    if not audio_bytes or len(audio_bytes) < 500:
        return None

    if settings.aethex_enabled:
        result = await _aethex_transcribe(audio_bytes, content_type, detected_language)
        if result:
            return result
        logger.info("Aethex transcription failed, falling back to Groq Whisper")

    from app.services.voice import transcribe_audio as groq_transcribe
    return await groq_transcribe(audio_bytes, content_type, detected_language)


async def _aethex_transcribe(audio_bytes: bytes, content_type: str, detected_language: str) -> Optional[str]:
    ext_map = {
        "audio/ogg": ("voice.ogg", "audio/ogg"),
        "audio/ogg; codecs=opus": ("voice.ogg", "audio/ogg"),
        "audio/wav": ("voice.wav", "audio/wav"),
        "audio/flac": ("voice.flac", "audio/flac"),
        "audio/mp4": ("voice.mp4", "audio/mp4"),
        "audio/mpeg": ("voice.mp3", "audio/mpeg"),
        "audio/amr": ("voice.amr", "audio/amr"),
        "audio/webm": ("voice.webm", "audio/webm"),
    }
    filename, mime = ext_map.get(content_type, ("voice.ogg", "audio/ogg"))
    lang_hint = AETHEX_LANG_MAP.get(detected_language)

    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=20.0) as client:
            files = {"file": (filename, io.BytesIO(audio_bytes), mime)}
            data = {"language": lang_hint} if lang_hint else {}
            response = await client.post(f"{BASE_URL}/transcribe", headers=HEADERS, files=files, data=data)
            elapsed = int((time.monotonic() - start) * 1000)

            if response.status_code in (422, 415):
                return None

            response.raise_for_status()
            text = response.json().get("text", "").strip()
            _status["transcription"].update(ok=True, latency_ms=elapsed, error=None)
            logger.info(f"Aethex transcription OK ({elapsed}ms): {text[:80]}")
            return text or None

    except Exception as e:
        _status["transcription"].update(ok=False, error=str(e))
        logger.warning(f"Aethex transcription error: {e}")
        return None


async def ping_aethex() -> dict:
    if not settings.aethex_enabled:
        return {"ok": False, "error": "API key not configured", "latency_ms": 0}
    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(f"{BASE_URL}/models", headers=HEADERS)
            elapsed = int((time.monotonic() - start) * 1000)
            ok = response.status_code < 500
            return {"ok": ok, "latency_ms": elapsed, "error": None if ok else f"HTTP {response.status_code}"}
    except Exception as e:
        return {"ok": False, "latency_ms": 0, "error": str(e)}
