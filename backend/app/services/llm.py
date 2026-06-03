import asyncio
import json
import logging
import random
import time
from typing import Optional

import httpx

from app.core.config import settings
from app.core.prompts import SYSTEM_PROMPT, ONBOARDING_EXTRACTION_PROMPT, MATCHING_PROMPT

logger = logging.getLogger(__name__)

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_COMPOUND_MODEL = "compound-beta"  # Groq compound for web search

_last_groq_status = {"ok": False, "last_check": None, "error": None, "latency_ms": 0}

# Language names for system prompt injection
LANGUAGE_NAMES = {
    "en": "English",
    "fr": "French",
    "yo": "Yoruba",
    "ha": "Hausa",
    "pcm": "Nigerian Pidgin",
    "ar": "Arabic",
}


def get_groq_status() -> dict:
    return _last_groq_status.copy()


def _build_language_system_prompt(base_prompt: str, language: str) -> str:
    """Inject language instruction into system prompt."""
    lang_name = LANGUAGE_NAMES.get(language, "English")
    if language == "en":
        return base_prompt
    injection = (
        f"\n\nIMPORTANT: The user is communicating in {lang_name}. "
        f"You MUST respond in {lang_name} throughout this entire conversation. "
        f"Do not switch to English unless the user switches first."
    )
    return base_prompt + injection


async def _call_groq(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 1024,
    max_retries: int = 3,
) -> Optional[str]:
    if not settings.groq_enabled:
        return "[BizPadi offline   GROQ_API_KEY not set]"

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    for attempt in range(max_retries):
        try:
            start = time.monotonic()
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(GROQ_CHAT_URL, json=payload, headers=headers)
                response.raise_for_status()
                elapsed_ms = int((time.monotonic() - start) * 1000)
                data = response.json()
                _last_groq_status.update(ok=True, last_check=time.time(), error=None, latency_ms=elapsed_ms)
                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            _last_groq_status.update(ok=False, last_check=time.time(), error=f"HTTP {e.response.status_code}")
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("retry-after", "2"))
                wait = retry_after + random.uniform(0.5, 1.5)
                logger.warning(f"Groq rate limited (attempt {attempt + 1}), waiting {wait:.1f}s")
                await asyncio.sleep(wait)
                continue
            logger.error(f"Groq HTTP error: {e.response.status_code} - {e.response.text[:200]}")
            return None

        except Exception as e:
            _last_groq_status.update(ok=False, last_check=time.time(), error=str(e))
            logger.error(f"Groq error: {e}")
            return None

    return None


async def chat_with_sme(
    conversation_history: list[dict],
    user_message: str,
    language: str = "en",
) -> Optional[str]:
    """Main conversation. Responds in user's detected language."""
    system = _build_language_system_prompt(SYSTEM_PROMPT, language)
    messages = [{"role": "system", "content": system}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})
    return await _call_groq(messages, temperature=0.7, max_tokens=800)


async def extract_profile_data(conversation_history: list[dict]) -> dict:
    """Extract structured profile including detected language."""
    conversation_text = ""
    for msg in conversation_history:
        role_label = "SME" if msg["role"] == "user" else "Assistant"
        conversation_text += f"{role_label}: {msg['content']}\n"

    prompt = ONBOARDING_EXTRACTION_PROMPT.format(conversation=conversation_text)
    result = await _call_groq([{"role": "user", "content": prompt}], temperature=0.0, max_tokens=500)

    if not result:
        return {}
    try:
        cleaned = result.strip().strip("```json").strip("```").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning(f"Profile extraction parse failed: {result[:200]}")
        return {}


async def detect_language_llm(text: str) -> str:
    """
    Use LLM to detect language. Returns ISO 639-1 code.
    Handles: en, fr, yo (Yoruba), ha (Hausa), pcm (Pidgin), ar (Arabic).
    """
    if not text or len(text.strip()) < 3:
        return "en"

    prompt = f"""Detect the language of this text and return ONLY the ISO code.

Codes to use:
- en = English
- fr = French
- yo = Yoruba
- ha = Hausa
- pcm = Nigerian Pidgin / Pidgin English
- ar = Arabic
- other = anything else

Text: "{text[:200]}"

Return ONLY one of: en, fr, yo, ha, pcm, ar, other
No explanation. No punctuation."""

    result = await _call_groq(
        [{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=5,
    )
    if not result:
        return "en"
    detected = result.strip().lower().replace(".", "").replace('"', '')
    valid = {"en", "fr", "yo", "ha", "pcm", "ar"}
    return detected if detected in valid else "en"


async def match_opportunities(profile_summary: str, opportunities_text: str, language: str = "en") -> Optional[str]:
    """Match SME profile against opportunities. Responds in user's language."""
    prompt = MATCHING_PROMPT.format(
        profile=profile_summary,
        opportunities=opportunities_text,
    )
    # Prepend language instruction
    if language != "en":
        lang_name = LANGUAGE_NAMES.get(language, "English")
        prompt = f"Respond entirely in {lang_name}.\n\n{prompt}"

    return await _call_groq([{"role": "user", "content": prompt}], temperature=0.5, max_tokens=1200)


# ─────────────────────────────────────────────────────────────────────────────
# WEB SEARCH
# ─────────────────────────────────────────────────────────────────────────────

SEARCH_SYSTEM_PROMPT = """You are BizPadi, a smart WhatsApp AI companion for Nigerian SMEs.

The user has asked a question that needs real, current information. Search the web and give a pinpoint accurate answer. Be specific to Nigeria and Africa where relevant.

Format for WhatsApp:
- Under 400 words
- Bold key information with *asterisks*
- Always mention your source briefly
- End with one actionable next step

Speak like a trusted Nigerian business friend. Warm, direct, no jargon."""


async def search_and_respond(query: str, sme_profile_summary: str = "", language: str = "en") -> Optional[str]:
    """Live web search via Groq compound model. Responds in user's language."""
    if not settings.groq_enabled:
        return None

    system = _build_language_system_prompt(SEARCH_SYSTEM_PROMPT, language)
    context = f"\nSME Profile: {sme_profile_summary}" if sme_profile_summary else ""

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"{query}{context}"},
    ]

    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": GROQ_COMPOUND_MODEL, "messages": messages, "max_tokens": 1024}

    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(GROQ_CHAT_URL, json=payload, headers=headers)
            response.raise_for_status()
            elapsed = int((time.monotonic() - start) * 1000)
            data = response.json()
            _last_groq_status.update(ok=True, last_check=time.time(), latency_ms=elapsed)
            return data["choices"][0]["message"]["content"]

    except httpx.HTTPStatusError as e:
        logger.warning(f"Groq compound failed ({e.response.status_code}), using regular model")
        return await _call_groq(messages, temperature=0.3, max_tokens=1024)
    except Exception as e:
        logger.error(f"Groq compound error: {e}")
        return None


def should_search_web(text: str) -> bool:
    lower = text.lower()
    triggers = [
        "grant", "grants", "funding", "loan", "loans", "finance", "capital",
        "cbn", "bank of industry", "boi", "smedan", "youwin", "tef",
        "tony elumelu", "lsetf", "nirsal", "agsmeis", "vc4a", "cartier",
        "how to register", "cac registration", "how do i", "where can i",
        "what is the deadline", "apply for", "application",
        "price of", "cost of", "market for", "naira", "exchange rate",
        "latest", "current", "new", "2025", "2026", "this year",
        "recently", "just announced", "new programme",
        "should i", "is it worth", "advice on", "tips for", "how to grow",
        "fidelity", "vc4a", "federalgrants", "federal grant",
    ]
    return any(t in lower for t in triggers)


async def ping_groq() -> dict:
    if not settings.groq_enabled:
        return {"ok": False, "error": "API key not configured", "latency_ms": 0}
    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                GROQ_CHAT_URL,
                json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"},
            )
            elapsed = int((time.monotonic() - start) * 1000)
            response.raise_for_status()
            _last_groq_status.update(ok=True, last_check=time.time(), error=None, latency_ms=elapsed)
            return {"ok": True, "latency_ms": elapsed}
    except Exception as e:
        _last_groq_status.update(ok=False, last_check=time.time(), error=str(e))
        return {"ok": False, "latency_ms": 0, "error": str(e)}
