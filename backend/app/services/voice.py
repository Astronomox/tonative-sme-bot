import io
import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

# whisper-large-v3-turbo: fastest, multilingual, great for Nigerian accents
# whisper-large-v3: slower but more accurate — use for Yoruba/Hausa/Arabic
WHISPER_FAST = "whisper-large-v3-turbo"
WHISPER_ACCURATE = "whisper-large-v3"

# Nigerian language prompts — massively improves transcription accuracy
# by priming Whisper with the vocabulary and context it will hear
LANGUAGE_PROMPTS = {
    "en": (
        "Nigerian business owner speaking English. "
        "Common words: naira, kobo, wahala, oga, abeg, CAC, SME, grant, loan, funding, "
        "Abuja, Lagos, Kano, Ibadan, Port Harcourt, SMEDAN, BOI, CBN, NIRSAL, YouWiN, TEF. "
        "May use Nigerian Pidgin words mixed in."
    ),
    "yo": (
        "Yoruba speaker discussing business and money. "
        "Common Yoruba words: owo, ise, oja, ile, oba, ebi, omo, bawo, ese, pelu, oga. "
        "May mix Yoruba and English (code-switching)."
    ),
    "ha": (
        "Hausa speaker discussing business and finance. "
        "Common Hausa words: kudi, aiki, gida, kasuwa, abinci, ruwa, sannu, barka, malam. "
        "May mix Hausa and English."
    ),
    "fr": (
        "Francophone African business owner. "
        "Discussing grants, loans, and business development in French. "
        "May reference: CEMAC, UEMOA, CFA, microfinance, subvention."
    ),
    "ar": (
        "Arabic speaker discussing business and finance. "
        "Northern Nigerian context. May mix Arabic and Hausa."
    ),
    "pcm": (  # Nigerian Pidgin
        "Nigerian Pidgin English speaker. "
        "Common words: abeg, oga, wahala, e don happen, make I, wetin, na so, "
        "how e dey, e no easy, dem, we, naira, kobo."
    ),
}

DEFAULT_PROMPT = LANGUAGE_PROMPTS["en"]

# WhatsApp sends voice notes in these formats
WHATSAPP_AUDIO_TYPES = {
    "audio/ogg": ("voice.ogg", "audio/ogg"),
    "audio/ogg; codecs=opus": ("voice.ogg", "audio/ogg"),
    "audio/mp4": ("voice.mp4", "audio/mp4"),
    "audio/mpeg": ("voice.mp3", "audio/mpeg"),
    "audio/amr": ("voice.amr", "audio/amr"),
    "audio/webm": ("voice.webm", "audio/webm"),
}

MIN_AUDIO_BYTES = 1000  # Groq rejects files under ~10 seconds but we catch tiny files early


async def download_twilio_media(media_url: str) -> Optional[bytes]:
    """
    Download a voice note from Twilio's media URL.
    Follows redirects, uses correct auth, logs detailed errors.
    """
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio credentials missing — cannot download media")
        return None

    try:
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,  # Twilio sometimes redirects
        ) as client:
            response = await client.get(
                media_url,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                headers={"Accept": "*/*"},
            )

            if response.status_code == 401:
                logger.error(
                    "Twilio media download 401 Unauthorized. "
                    "Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in env vars."
                )
                return None

            if response.status_code == 404:
                logger.error("Twilio media URL not found (404). Message may have expired.")
                return None

            response.raise_for_status()
            content = response.content

            if len(content) < MIN_AUDIO_BYTES:
                logger.warning(f"Audio file too small ({len(content)} bytes), likely empty")
                return None

            content_type = response.headers.get("content-type", "")
            logger.info(
                f"Downloaded media: {len(content)} bytes, "
                f"type={content_type}, url={media_url[:60]}"
            )
            return content

    except httpx.HTTPStatusError as e:
        logger.error(
            f"Twilio media download failed: HTTP {e.response.status_code} "
            f"— {e.response.text[:200]}"
        )
        return None
    except httpx.TimeoutException:
        logger.error("Twilio media download timed out after 30s")
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

    Improvements for Nigerian languages:
    1. Language-specific prompts prime Whisper with local vocabulary
    2. Language hint passed to Whisper when confident
    3. Uses accurate model for non-English languages
    4. Falls back to fast model if accurate fails
    """
    if not settings.groq_enabled:
        logger.warning("Groq API key not set, cannot transcribe")
        return None

    if len(audio_bytes) < MIN_AUDIO_BYTES:
        logger.warning(f"Audio too small to transcribe: {len(audio_bytes)} bytes")
        return None

    # Pick filename and content type based on what WhatsApp sent
    file_info = WHATSAPP_AUDIO_TYPES.get(content_type, ("voice.ogg", "audio/ogg"))
    filename, mime_type = file_info

    # Get the language-specific prompt
    prompt = LANGUAGE_PROMPTS.get(detected_language, DEFAULT_PROMPT)

    # Use accurate model for non-English, fast model for English
    model = WHISPER_ACCURATE if detected_language not in ("en", "pcm") else WHISPER_FAST

    # Groq language hint — ISO 639-1 codes Whisper understands
    whisper_lang_map = {
        "en": "en", "yo": "yo", "ha": "ha",
        "fr": "fr", "ar": "ar", "pcm": None,  # Pidgin not supported directly
    }
    language_hint = whisper_lang_map.get(detected_language)

    logger.info(f"Transcribing with model={model}, lang={detected_language}, size={len(audio_bytes)}b")

    result = await _call_whisper(audio_bytes, filename, mime_type, model, prompt, language_hint)

    # If accurate model failed, try fast model as fallback
    if result is None and model == WHISPER_ACCURATE:
        logger.info("Accurate model failed, trying fast model")
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
    """Make one Whisper API call."""
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

    form_data = {
        "model": model,
        "response_format": "text",
        "prompt": prompt,
    }

    if language:
        form_data["language"] = language

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {"file": (filename, io.BytesIO(audio_bytes), mime_type)}
            response = await client.post(
                GROQ_TRANSCRIPTION_URL,
                headers=headers,
                files=files,
                data=form_data,
            )
            response.raise_for_status()
            transcript = response.text.strip()

            if not transcript:
                logger.warning("Whisper returned empty transcript")
                return None

            logger.info(f"Transcript ({model}): {transcript[:120]}")
            return transcript

    except httpx.HTTPStatusError as e:
        logger.error(
            f"Whisper API error: HTTP {e.response.status_code} — {e.response.text[:300]}"
        )
        return None
    except Exception as e:
        logger.error(f"Whisper API error: {e}")
        return None
