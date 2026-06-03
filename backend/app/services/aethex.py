"""
AethexAI service — Transcription + TTS.

Transcription:  POST /transcribe   (WAV, FLAC, Ogg/Opus, max 8 MiB)
TTS:            POST /tts          (English and French; returns WAV)

Both use X-API-Key header auth.
Falls back gracefully when the API is unavailable.
"""
import io
import logging
import time
import uuid
from pathlib import Path
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = settings.AETHEX_BASE_URL
HEADERS = {"X-API-Key": settings.AETHEX_API_KEY}

# Aethex currently supports English and French only.
# Yoruba, Hausa, Pidgin, Arabic fall back to Groq Whisper.
AETHEX_SUPPORTED_LANGUAGES = {"en", "fr"}
AETHEX_LANG_MAP = {
    "en": "english",
    "fr": "french",
}

# Temp directory for serving TTS audio files to WhatsApp
import tempfile
TTS_CACHE_DIR = Path(tempfile.gettempdir()) / "bizpadi_tts"
TTS_CACHE_DIR.mkdir(exist_ok=True)

_status = {"transcription": {"ok": False, "latency_ms": 0, "error": None},
           "tts": {"ok": False, "latency_ms": 0, "error": None}}


def get_aethex_status() -> dict:
    return _status.copy()


# ─────────────────────────────────────────────────────────────────────────────
# TRANSCRIPTION
# ─────────────────────────────────────────────────────────────────────────────

async def transcribe_audio(
    audio_bytes: bytes,
    content_type: str = "audio/ogg",
    detected_language: str = "en",
) -> Optional[str]:
    """
    Transcribe audio using AethexAI (primary) or Groq Whisper (fallback).

    Aethex accepts WAV, FLAC, Ogg/Opus.
    WhatsApp sends audio/ogg (Opus codec) — perfect match.
    """
    if not audio_bytes or len(audio_bytes) < 500:
        logger.warning(f"Audio too small to transcribe: {len(audio_bytes) if audio_bytes else 0} bytes")
        return None

    # Try Aethex first
    if settings.aethex_enabled:
        result = await _aethex_transcribe(audio_bytes, content_type, detected_language)
        if result:
            return result
        logger.info("Aethex transcription failed, falling back to Groq Whisper")

    # Fallback to Groq Whisper
    return await _groq_transcribe(audio_bytes, content_type, detected_language)


async def _aethex_transcribe(
    audio_bytes: bytes,
    content_type: str,
    detected_language: str,
) -> Optional[str]:
    """Call Aethex /transcribe endpoint."""
    # Map content type to filename
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

    # Aethex only natively supports english/french hints
    lang_hint = AETHEX_LANG_MAP.get(detected_language)  # None = auto-detect

    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"file": (filename, io.BytesIO(audio_bytes), mime)}
            data = {}
            if lang_hint:
                data["language"] = lang_hint

            response = await client.post(
                f"{BASE_URL}/transcribe",
                headers=HEADERS,
                files=files,
                data=data,
            )

            elapsed = int((time.monotonic() - start) * 1000)

            if response.status_code == 422:
                logger.warning(f"Aethex transcription 422 (unsupported format?): {response.text[:200]}")
                return None

            response.raise_for_status()
            result = response.json()
            text = result.get("text", "").strip()

            _status["transcription"].update(ok=True, latency_ms=elapsed, error=None)
            logger.info(f"Aethex transcription OK ({elapsed}ms): {text[:80]}")
            return text if text else None

    except httpx.HTTPStatusError as e:
        _status["transcription"].update(ok=False, error=f"HTTP {e.response.status_code}")
        logger.warning(f"Aethex transcription HTTP {e.response.status_code}: {e.response.text[:200]}")
        return None
    except Exception as e:
        _status["transcription"].update(ok=False, error=str(e))
        logger.warning(f"Aethex transcription error: {e}")
        return None


async def _groq_transcribe(
    audio_bytes: bytes,
    content_type: str,
    detected_language: str,
) -> Optional[str]:
    """Groq Whisper fallback — handles Yoruba, Hausa, Pidgin, Arabic."""
    from app.services.voice import transcribe_audio as groq_transcribe
    return await groq_transcribe(audio_bytes, content_type, detected_language)


# ─────────────────────────────────────────────────────────────────────────────
# TEXT-TO-SPEECH
# ─────────────────────────────────────────────────────────────────────────────

async def text_to_speech(
    text: str,
    language: str = "en",
) -> Optional[Path]:
    """
    Convert text to speech using AethexAI TTS.
    Returns path to a WAV file in /tmp, or None on failure.

    Aethex supports English and French only.
    Returns None for other languages (no voice reply for Hausa/Yoruba yet).
    """
    if not settings.aethex_enabled:
        return None

    if language not in AETHEX_SUPPORTED_LANGUAGES:
        logger.info(f"TTS not available for language '{language}', skipping voice reply")
        return None

    # Chunk text if over 3000 chars (Aethex limit)
    chunks = _chunk_text(text, max_len=2800)
    audio_parts = []

    for chunk in chunks:
        wav = await _aethex_tts(chunk, language)
        if wav:
            audio_parts.append(wav)
        else:
            return None  # Fail fast — partial audio is worse than none

    if not audio_parts:
        return None

    # Combine WAV chunks (strip headers from all but first)
    if len(audio_parts) == 1:
        combined = audio_parts[0]
    else:
        combined = _combine_wav_chunks(audio_parts)

    # Save to temp file
    filename = f"bizpadi_{uuid.uuid4().hex[:12]}.wav"
    path = TTS_CACHE_DIR / filename
    path.write_bytes(combined)
    logger.info(f"TTS audio saved: {path} ({len(combined)} bytes)")
    return path


async def _aethex_tts(text: str, language: str) -> Optional[bytes]:
    """Call Aethex /tts endpoint, return WAV bytes."""
    lang_str = AETHEX_LANG_MAP.get(language, "english")

    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/tts",
                headers={**HEADERS, "Content-Type": "application/json"},
                json={"text": text, "language": lang_str, "voice_id": "default", "streaming": False},
            )
            elapsed = int((time.monotonic() - start) * 1000)

            if response.status_code in (503, 404):
                logger.warning(f"Aethex TTS not available: {response.status_code}")
                _status["tts"].update(ok=False, error=f"HTTP {response.status_code}")
                return None

            response.raise_for_status()
            _status["tts"].update(ok=True, latency_ms=elapsed, error=None)
            logger.info(f"Aethex TTS OK ({elapsed}ms, {len(response.content)} bytes)")
            return response.content

    except httpx.HTTPStatusError as e:
        _status["tts"].update(ok=False, error=f"HTTP {e.response.status_code}")
        logger.warning(f"Aethex TTS HTTP {e.response.status_code}: {e.response.text[:200]}")
        return None
    except Exception as e:
        _status["tts"].update(ok=False, error=str(e))
        logger.warning(f"Aethex TTS error: {e}")
        return None


def _chunk_text(text: str, max_len: int = 2800) -> list[str]:
    """Split text at sentence boundaries to stay under TTS char limit."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    current = ""
    # Split on sentence boundaries
    for sentence in text.replace("\n", " ").split(". "):
        sentence = sentence.strip()
        if not sentence:
            continue
        candidate = f"{current}. {sentence}" if current else sentence
        if len(candidate) <= max_len:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # If single sentence is too long, hard-split it
            if len(sentence) > max_len:
                for i in range(0, len(sentence), max_len):
                    chunks.append(sentence[i:i + max_len])
                current = ""
            else:
                current = sentence

    if current:
        chunks.append(current)

    if not chunks:
        # Hard split as last resort
        return [text[i:i + max_len] for i in range(0, len(text), max_len)]

    return chunks


def _combine_wav_chunks(chunks: list[bytes]) -> bytes:
    """
    Combine multiple WAV files by stripping the 44-byte RIFF header
    from all chunks except the first, then concatenating the PCM data.
    Updates the first header's data size field.
    """
    import struct
    if not chunks:
        return b""
    if len(chunks) == 1:
        return chunks[0]

    # First chunk keeps its header (44 bytes standard WAV)
    header = bytearray(chunks[0][:44])
    pcm_parts = [chunks[0][44:]]
    for chunk in chunks[1:]:
        pcm_parts.append(chunk[44:])  # strip header

    all_pcm = b"".join(pcm_parts)
    total_data_size = len(all_pcm)
    # Fix RIFF chunk size (bytes 4-8): total file size - 8
    struct.pack_into("<I", header, 4, 36 + total_data_size)
    # Fix data sub-chunk size (bytes 40-44)
    struct.pack_into("<I", header, 40, total_data_size)
    return bytes(header) + all_pcm


async def ping_aethex() -> dict:
    """Health check — tiny TTS request."""
    if not settings.aethex_enabled:
        return {"ok": False, "error": "API key not configured", "latency_ms": 0}
    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BASE_URL}/tts",
                headers={**HEADERS, "Content-Type": "application/json"},
                json={"text": "Hello.", "language": "english"},
            )
            elapsed = int((time.monotonic() - start) * 1000)
            if response.status_code in (200, 503):
                ok = response.status_code == 200
                return {"ok": ok, "latency_ms": elapsed, "error": None if ok else "503 not ready"}
            return {"ok": False, "latency_ms": elapsed, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"ok": False, "latency_ms": 0, "error": str(e)}


def cleanup_old_tts_files(max_age_seconds: int = 300):
    """Remove TTS files older than max_age_seconds. Call periodically."""
    now = time.time()
    for f in TTS_CACHE_DIR.glob("*.wav"):
        try:
            if now - f.stat().st_mtime > max_age_seconds:
                f.unlink()
        except Exception:
            pass
