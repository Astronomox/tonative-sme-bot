# BizPadi build: 2026-06-07 smart-memory
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
    "ar": ["speak arabic", "arabic please", "switch to arabic", "use arabic",
           "arabic", "عربي"],
}


def get_groq_status() -> dict:
    return _groq_status.copy()


def detect_language_switch(text: str) -> Optional[str]:
    lower = text.lower().strip()
    for lang_code, patterns in LANGUAGE_SWITCH_PATTERNS.items():
        if any(pattern in lower for pattern in patterns):
            return lang_code
    return None


def _inject_language(system: str, language: str) -> str:
    if language == "en":
        return system
    if language in ("fr", "pcm"):
        lang_name = LANGUAGE_NAMES.get(language)
        return system + f"\n\nIMPORTANT: Respond in {lang_name}. Be natural and fluent."
    lang_name = LANGUAGE_NAMES.get(language, "English")
    return system + (
        f"\n\nIMPORTANT: The user speaks {lang_name}. "
        f"Compose your response in clear simple English first, "
        f"then translate it accurately into {lang_name}. "
        f"Keep the translation SHORT and NATURAL. "
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
                resp = await asyncio.wait_for(
                    client.post(GROQ_CHAT_URL, json=payload, headers=headers),
                    timeout=timeout + 5.0
                )
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


def _build_smart_messages(
    system: str,
    history: list[dict],
    user_message: str,
    language: str = "en",
) -> list[dict]:
    """
    Build LLM messages with smart memory weighting.

    Strategy:
    - Always include system prompt
    - Include a SUMMARY of older context (compressed)
    - Always include the last 8 messages in full (recency matters most)
    - Always include the current user message

    This prevents old context from overriding new information.
    """
    injected_system = _inject_language(system, language)
    messages = [{"role": "system", "content": injected_system}]

    if len(history) <= 8:
        messages.extend(history)
    else:
        # Older messages: summarise into a single system context note
        older = history[:-8]
        recent = history[-8:]

        # Build a compact summary of older context
        older_summary_parts = []
        for msg in older:
            role = "User" if msg["role"] == "user" else "BizPadi"
            content = msg["content"][:200]  # truncate long messages
            older_summary_parts.append(f"{role}: {content}")
        older_summary = "\n".join(older_summary_parts)

        messages.append({
            "role": "system",
            "content": (
                f"EARLIER CONVERSATION SUMMARY (for context only, "
                f"recent messages below are more accurate):\n{older_summary}"
            )
        })
        messages.extend(recent)

    messages.append({"role": "user", "content": user_message})
    return messages


async def chat_with_sme(
    conversation_history: list[dict],
    user_message: str,
    language: str = "en",
) -> Optional[str]:
    """Main conversation with smart memory weighting."""
    messages = _build_smart_messages(SYSTEM_PROMPT, conversation_history, user_message, language)
    return await _call_groq(messages, temperature=0.75, max_tokens=800)


async def extract_profile_data(conversation_history: list[dict]) -> dict:
    """
    Extract profile from conversation.
    CRITICAL: Always prioritise the MOST RECENT information.
    If user says bakery in message 2 but building materials in message 8,
    building materials is the truth.
    """
    # Only use the last 12 messages for extraction to avoid stale data
    recent_history = conversation_history[-12:]

    conversation_text = "\n".join(
        f"{'SME' if m['role'] == 'user' else 'BizPadi'}: {m['content']}"
        for m in recent_history
    )

    # Enhanced prompt that explicitly handles contradictions
    prompt = f"""{ONBOARDING_EXTRACTION_PROMPT.format(conversation=conversation_text)}

CRITICAL RULE: If the user mentions different businesses or corrects themselves,
always use the MOST RECENT information. The last thing they said about any field
is the truth. Ignore earlier contradicted information."""

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


async def extract_profile_update(user_message: str, current_profile_summary: str) -> dict:
    """
    Specifically extract profile changes from a single message.
    Used when user sends new business information mid-conversation.
    Returns only the fields that changed.
    """
    prompt = f"""A user is chatting with a business funding bot. They just sent this message:

"{user_message}"

Their current profile:
{current_profile_summary}

Extract ONLY the fields this message is changing or adding. If this message contains
new business information that contradicts the current profile, extract the new values.

Return ONLY valid JSON with changed fields. If nothing changed, return {{}}.

Fields: business_name, business_type, location_city, location_state,
business_stage (idea/early/growing/established),
monthly_revenue (under_100k/100k_500k/500k_2m/2m_10m/above_10m),
employee_count (integer), cac_registered (boolean), biggest_challenge, owner_name

No explanation. No markdown. Just JSON."""

    result = await _call_groq(
        [{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=300,
    )
    if not result:
        return {}
    try:
        cleaned = result.strip().strip("```json").strip("```").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {}


def message_has_business_info(text: str) -> bool:
    """
    Detect if a message contains business profile information
    that should trigger profile re-extraction.
    """
    lower = text.lower()

    # Revenue mentions
    revenue_patterns = [
        "naira", "million", "thousand", "k monthly", "k per month",
        "per month", "monthly", "revenue", "income", "i make", "we make",
        "i earn", "we earn", "turnover", "i need", "we need",
        "stock", "capital", "expand", "open another",
    ]

    # Business description patterns
    business_patterns = [
        "i sell", "i run", "i own", "we sell", "we run", "my business",
        "my shop", "my store", "i have been", "years now", "years of",
        "located at", "located in", "based in", "my office",
        "i am a", "i work as", "i do", "we do", "building materials",
        "fashion", "food", "agriculture", "technology", "bakery",
        "clothing", "trading", "contractor", "supplier",
    ]

    # Location patterns
    location_patterns = [
        "lagos", "abuja", "kano", "ibadan", "port harcourt", "aba",
        "enugu", "kaduna", "ogun", "oyo", "delta", "trade fair",
        "island", "mainland", "market", "abuleoshun", "ikeja",
        "surulere", "yaba", "lekki", "victoria island",
    ]

    has_revenue = any(p in lower for p in revenue_patterns)
    has_business = any(p in lower for p in business_patterns)
    has_location = any(p in lower for p in location_patterns)

    # Single strong signal is enough if message is substantial
    if has_business and len(text) > 20:
        return True
    if has_revenue and len(text) > 20:
        return True
    signals = sum([has_revenue, has_business, has_location])
    return signals >= 2 and len(text) > 15


async def detect_language_llm(text: str) -> str:
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
    if not result:
        result = await _call_groq(messages, temperature=0.3, max_tokens=1200, use_compound=False)
    return result


async def get_fund_readiness_plan(profile_summary: str, language: str = "en") -> Optional[str]:
    lang_name = LANGUAGE_NAMES.get(language, "English")
    prompt = CONSULTANT_PROMPT.format(language_name=lang_name, profile=profile_summary)
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
