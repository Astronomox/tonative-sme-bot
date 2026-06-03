"""
Language detection and multilingual support.
Uses Groq LLM for detection (supports all Nigerian languages).
AethexAI supports English + French only — used for TTS in those languages.
"""
import logging

logger = logging.getLogger(__name__)


async def detect_language(text: str) -> str:
    """
    Detect language of text. Returns ISO 639-1 code.
    Supported: en, fr, yo (Yoruba), ha (Hausa), pcm (Pidgin), ar (Arabic).
    """
    if not text or len(text.strip()) < 3:
        return "en"

    from app.services.llm import detect_language_llm
    try:
        lang = await detect_language_llm(text)
        logger.debug(f"Language detected: {lang} for text: {text[:50]}")
        return lang
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
        return "en"


async def translate_to_english(text: str, source_language: str) -> str:
    """
    For non-English input, we no longer translate to English before processing.
    Instead, the LLM handles multilingual input natively.
    This function is kept for backward compatibility but passes text through.
    """
    return text


async def translate_from_english(text: str, target_language: str) -> str:
    """
    For non-English responses, we no longer translate after processing.
    The LLM responds in the user's language natively via the system prompt.
    This function is kept for backward compatibility but passes text through.
    """
    return text
