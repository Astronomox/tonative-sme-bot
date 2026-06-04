import asyncio
import json
import logging
import random
import time
from typing import Optional

import httpx

from app.core.config import settings
from app.core.prompts import (
    SYSTEM_PROMPT,
    ONBOARDING_EXTRACTION_PROMPT,
    MATCHING_PROMPT,
    LIVE_SEARCH_SYSTEM_PROMPT,
    CONSULTANT_PROMPT,
)

logger = logging.getLogger(__name__)

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_COMPOUND_MODEL = "compound-beta"

_groq_status = {"ok": False, "last_check": None, "error": None, "latency_ms": 0}

LANGUAGE_NAMES = {
    "en": "English",
    "fr": "French",
    "yo": "Yoruba",
    "ha": "Hausa",
    "pcm": "Nigerian Pidgin",
    "ar": "Arabic",
}

# Language switch phrases — detect these mid-conversation
LANGUAGE_SWITCH_PATTERNS = {
    "en": ["speak english", "english please", "switch to english", "use english",
           "let's speak english", "change to english", "english"],
    "yo": ["speak yoruba", "yoruba please", "switch to yoruba", "yoruba",
           "lo yoruba", "e lo yoruba"],
    "ha": ["speak hausa", "hausa please", "switch to hausa", "hausa",
           "yi hausa", "ku yi hausa"],
    "pcm": ["speak pidgin", "pidgin please", "switch to pidgin", "pidgin",
            "use pidgin", "make we do pidgin"],
    "fr": ["speak french", "french please", "switch to french", "français",
           "parle français", "en français", "french"],
}


def get_groq_status() -> dict:
    return _groq_status.copy()


def detect_language_switch(text: str) -> Optional[str]:
    """Check if user is requesting a language switch. Returns new lang code or None."""
    lower = text.lower().strip()
    for lang_code, patterns in LANGUAGE_SWITCH_PATTERNS.items():
        if any(pattern in lower for pattern in patterns):
            return lang_code
    return None


def _inject_language(system: str, language: str) -> str:
    """Inject language instruction into system prompt."""
    if language == "en":
        return system

    # For French and Pidgin: LLM handles these well natively
    if language in ("fr", "pcm"):
        lang_name = LANGUAGE_NAMES.get(language)
        return system + (
            f"\n\nIMPORTANT: Respond in {lang_name}. Be natural and fluent."
        )

    # For Yoruba, Hausa, Arabic: LLM is NOT fluent enough to generate well.
    # Instead: think in English internally, then translate your response.
    # This prevents repetitive hallucination garbage.
    lang_name = LANGUAGE_NAMES.get(language, "English")
    return system + (
        f"\n\nIMPORTANT: The user speaks {lang_name}. "
        f"Compose your response in clear simple English first, "
        f"then translate it accurately into {lang_name}. "
        f"Keep the translation SHORT and NATURAL. "
        f"If you are not certain of a {lang_name} phrase, use simple English words "
        f"that a {lang_name} speaker would understand rather than guessing. "
        f"DO NOT repeat phrases. DO NOT fill space with similar-sounding words. "
        f"If a sentence is done, stop."
    )


async def _call_groq(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 1024,
    max_retries: int = 3,
    use_compound: bool = False,
) -> Optional[str]:
    if not settings.groq_enabled:
        return None

    model = GROQ_COMPOUND_MODEL if use_compound else GROQ_MODEL
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    timeout = 45.0 if use_compound else 30.0

    for attempt in range(max_retries):
        try:
            start = time.monotonic()
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(GROQ_CHAT_URL, json=payload, headers=headers)
                resp.raise_for_status()
                elapsed = int((time.monotonic() - start) * 1000)
                data = resp.json()
                _groq_status.update(ok=True, last_check=time.time(), error=None, latency_ms=elapsed)
                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            _groq_status.update(ok=False, last_check=time.time(), error=f"HTTP {e.response.status_code}")
            if e.response.status_code == 429:
                wait = int(e.response.headers.get("retry-after", "2")) + random.uniform(0.5, 1.5)
                logger.warning(f"Groq rate limited, waiting {wait:.1f}s (attempt {attempt+1})")
                await asyncio.sleep(wait)
                continue
            if use_compound and e.response.status_code in (400, 404):
                logger.info("Compound model unavailable, falling back to standard model")
                payload["model"] = GROQ_MODEL
                use_compound = False
                continue
            logger.error(f"Groq HTTP {e.response.status_code}: {e.response.text[:200]}")
            return None

        except Exception as e:
            _groq_status.update(ok=False, last_check=time.time(), error=str(e))
            logger.error(f"Groq error: {e}")
            return None

    return None


async def chat_with_sme(
    conversation_history: list[dict],
    user_message: str,
    language: str = "en",
) -> Optional[str]:
    """Main conversation — responds in user's chosen language."""
    system = _inject_language(SYSTEM_PROMPT, language)
    messages = [{"role": "system", "content": system}]
    messages.extend(conversation_history[-16:])  # last 16 messages for context
    messages.append({"role": "user", "content": user_message})
    return await _call_groq(messages, temperature=0.75, max_tokens=800)


async def extract_profile_data(conversation_history: list[dict]) -> dict:
    """Extract structured profile from conversation."""
    conversation_text = "\n".join(
        f"{'SME' if m['role'] == 'user' else 'BizPadi'}: {m['content']}"
        for m in conversation_history[-20:]
    )
    prompt = ONBOARDING_EXTRACTION_PROMPT.format(conversation=conversation_text)
    result = await _call_groq(
        [{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=500,
    )
    if not result:
        return {}
    try:
        cleaned = result.strip().strip("```json").strip("```").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning(f"Profile parse failed: {result[:200]}")
        return {}


async def detect_language_llm(text: str) -> str:
    """Detect language via LLM. Returns ISO code."""
    if not text or len(text.strip()) < 3:
        return "en"

    prompt = (
        f'Detect the language of this text. Return ONLY one code:\n'
        f'en=English, fr=French, yo=Yoruba, ha=Hausa, pcm=Nigerian Pidgin, ar=Arabic\n\n'
        f'Text: "{text[:200]}"\n\n'
        f'Return ONLY the code. Nothing else.'
    )
    result = await _call_groq(
        [{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=5,
    )
    if not result:
        return "en"
    detected = result.strip().lower().replace(".", "").replace('"', "").strip()
    return detected if detected in LANGUAGE_NAMES else "en"


async def get_live_opportunities(profile_summary: str, language: str = "en") -> Optional[str]:
    """
    Live web search for current Nigerian funding opportunities.
    Uses Groq compound model to browse the web in real time.
    """
    lang_name = LANGUAGE_NAMES.get(language, "English")
    system = LIVE_SEARCH_SYSTEM_PROMPT.format(language_name=lang_name)

    query = (
        f"Find current open funding opportunities, grants, and loans for Nigerian SMEs in 2025-2026. "
        f"Focus on opportunities that match this profile:\n{profile_summary}\n\n"
        f"Search vc4a.com/programs, opportunitydesk.org, smedan.gov.ng, boi.ng, tony.elumelu.org, "
        f"youthop.com, disruptafrica.com for ACTIVE opportunities with open applications. "
        f"Include the application link and deadline for each one found."
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": query},
    ]

    result = await _call_groq(messages, temperature=0.3, max_tokens=1200, use_compound=True)

    # Fallback to standard model if compound fails
    if not result:
        logger.info("Compound failed for live search, using standard model")
        result = await _call_groq(messages, temperature=0.3, max_tokens=1200, use_compound=False)

    return result


async def get_fund_readiness_plan(profile_summary: str, language: str = "en") -> Optional[str]:
    """
    Consultant mode: tells user exactly what to do to qualify for more funding.
    Gives specific week-by-week action plan.
    """
    lang_name = LANGUAGE_NAMES.get(language, "English")
    prompt = CONSULTANT_PROMPT.format(
        language_name=lang_name,
        profile=profile_summary,
    )
    return await _call_groq(
        [{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=1200,
    )


async def match_with_explanation(
    profile_summary: str,
    opportunities_text: str,
    language: str = "en",
) -> Optional[str]:
    """Match opportunities with scores in brackets and specific explanations."""
    lang_name = LANGUAGE_NAMES.get(language, "English")
    prompt = MATCHING_PROMPT.format(
        language_name=lang_name,
        profile=profile_summary,
        opportunities=opportunities_text,
    )
    return await _call_groq(
        [{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=1400,
    )


def should_search_web(text: str) -> bool:
    lower = text.lower()
    triggers = [
        "grant", "grants", "funding", "loan", "loans", "finance", "capital",
        "cbn", "bank of industry", "boi", "smedan", "youwin", "tef",
        "tony elumelu", "lsetf", "nirsal", "agsmeis", "vc4a", "cartier",
        "new opportunities", "latest opportunities", "current grants",
        "how to register", "cac registration", "apply for", "application",
        "price of", "cost of", "naira", "exchange rate",
        "latest", "current", "2025", "2026", "this year", "new programme",
        "advice on", "how to grow", "fidelity", "federal grant",
    ]
    return any(t in lower for t in triggers)


def should_get_readiness_plan(text: str) -> bool:
    lower = text.lower()
    triggers = [
        "how can i qualify", "what do i need", "how do i get ready",
        "fund ready", "fund readiness", "what am i missing",
        "how to qualify", "what should i do", "next steps",
        "help me qualify", "what do i do next", "my plan",
        "prepare to apply", "get ready", "what is blocking",
    ]
    return any(t in lower for t in triggers)


async def ping_groq() -> dict:
    if not settings.groq_enabled:
        return {"ok": False, "error": "API key not configured", "latency_ms": 0}
    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                GROQ_CHAT_URL,
                json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"},
            )
            elapsed = int((time.monotonic() - start) * 1000)
            resp.raise_for_status()
            _groq_status.update(ok=True, last_check=time.time(), error=None, latency_ms=elapsed)
            return {"ok": True, "latency_ms": elapsed}
    except Exception as e:
        _groq_status.update(ok=False, last_check=time.time(), error=str(e))
        return {"ok": False, "latency_ms": 0, "error": str(e)}
