"""
Voice service   Groq Whisper transcription.
Used as the fallback when Aethex transcription is unavailable,
and as primary for Yoruba, Hausa, Arabic, Pidgin.
"""
import io
import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
WHISPER_FAST = "whisper-large-v3-turbo"     # English, Pidgin
WHISPER_ACCURATE = "whisper-large-v3"       # Yoruba, Hausa, French, Arabic

MIN_AUDIO_BYTES = 1000

LANGUAGE_PROMPTS = {
    "en": (
        "Nigerian business owner speaking English. "
        "Common words: naira, kobo, wahala, CAC, SME, grant, loan, funding, "
        "Abuja, Lagos, Kano, SMEDAN, BOI, CBN, NIRSAL, TEF. May use Pidgin."
    ),
    "yo": (
        "Yoruba speaker discussing business and money. "
        "Common words: owo, ise, oja, ile, oba, ebi, omo, bawo, ese, pelu, oga. "
        "May mix Yoruba and English."
    ),
    "ha": (
        "Hausa speaker discussing business and finance. "
        "Common words: kudi, aiki, gida, kasuwa, abinci, sannu, barka, malam. "
        "May mix Hausa and English."
    ),
    "fr": (
        "Francophone African business owner. "
        "Discussing grants, loans, business development in French. "
        "May reference: CEMAC, UEMOA, CFA, microfinance, subvention."
    ),
    "ar": (
        "Arabic speaker discussing business and finance. "
        "Northern Nigerian context. May mix Arabic and Hausa."
    ),
    "pcm": (
        "Nigerian Pidgin English speaker. "
        "Common words: abeg, wahala, e don happen, wetin, na so, dem, naira, kobo."
    ),
}

WHATSAPP_AUDIO_TYPES = {
    "audio/ogg": ("voice.ogg", "audio/ogg"),
    "audio/ogg; codecs=opus": ("voice.ogg", "audio/ogg"),
    "audio/mp4": ("voice.mp4", "audio/mp4"),
    "audio/mpeg": ("voice.mp3", "audio/mpeg"),
    "audio/amr": ("voice.amr", "audio/amr"),
    "audio/webm": ("voice.webm", "audio/webm"),
    "audio/wav": ("voice.wav", "audio/wav"),
}


async def download_twilio_media(media_url: str) -> Optional[bytes]:
    """Download voice note from Twilio with proper auth + redirect handling."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio credentials missing")
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(
                media_url,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                headers={"Accept": "*/*"},
            )
            if response.status_code == 401:
                logger.error("Twilio media 401   check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN")
                return None
            if response.status_code == 404:
                logger.error("Twilio media 404   message may have expired")
                return None
            response.raise_for_status()
            content = response.content
            if len(content) < MIN_AUDIO_BYTES:
                logger.warning(f"Audio too small: {len(content)} bytes")
                return None
            logger.info(f"Downloaded media: {len(content)} bytes, type={response.headers.get('content-type', '?')}")
            return content

    except httpx.HTTPStatusError as e:
        logger.error(f"Twilio media HTTP {e.response.status_code}: {e.response.text[:200]}")
        return None
    except Exception as e:
        logger.error(f"Twilio media download error: {e}")
        return None


async def transcribe_audio(
    audio_bytes: bytes,
    content_type: str = "audio/ogg",
    detected_language: str = "en",
) -> Optional[str]:
    """
    Transcribe audio using Groq Whisper.
    Called directly for non-EN/FR languages, and as fallback from aethex.py.
    """
    if not settings.groq_enabled:
        return None
    if len(audio_bytes) < MIN_AUDIO_BYTES:
        return None

    file_info = WHATSAPP_AUDIO_TYPES.get(content_type, ("voice.ogg", "audio/ogg"))
    filename, mime_type = file_info
    prompt = LANGUAGE_PROMPTS.get(detected_language, LANGUAGE_PROMPTS["en"])
    model = WHISPER_ACCURATE if detected_language not in ("en", "pcm") else WHISPER_FAST

    whisper_lang_map = {"en": "en", "yo": "yo", "ha": "ha", "fr": "fr", "ar": "ar", "pcm": None}
    language_hint = whisper_lang_map.get(detected_language)

    logger.info(f"Groq Whisper: model={model}, lang={detected_language}, size={len(audio_bytes)}b")
    result = await _call_whisper(audio_bytes, filename, mime_type, model, prompt, language_hint)

    # Fallback to fast model if accurate failed
    if result is None and model == WHISPER_ACCURATE:
        logger.info("Whisper accurate failed, trying fast model")
        result = await _call_whisper(audio_bytes, filename, mime_type, WHISPER_FAST, prompt, None)

    return result


async def _call_whisper(
    audio_bytes: bytes,
    filename: str,
    mime_type: str,
    model: str,
    prompt: str,
    language: Optional[str],
) -> Optional[str]:
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
    form_data = {"model": model, "response_format": "text", "prompt": prompt}
    if language:
        form_data["language"] = language

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                GROQ_TRANSCRIPTION_URL,
                headers=headers,
                files={"file": (filename, io.BytesIO(audio_bytes), mime_type)},
                data=form_data,
            )
            response.raise_for_status()
            transcript = response.text.strip()
            if not transcript:
                return None
            logger.info(f"Whisper ({model}): {transcript[:120]}")
            return transcript
    except httpx.HTTPStatusError as e:
        logger.error(f"Whisper HTTP {e.response.status_code}: {e.response.text[:300]}")
        return None
    except Exception as e:
        logger.error(f"Whisper error: {e}")
        return None
