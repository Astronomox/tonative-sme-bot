import asyncio
import json
import logging
import random
from typing import Optional

import httpx

from app.core.config import settings
from app.core.prompts import SYSTEM_PROMPT, ONBOARDING_EXTRACTION_PROMPT, MATCHING_PROMPT

logger = logging.getLogger(__name__)

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_COMPOUND_MODEL = "groq/compound"  # web search + visit website built in

# Track API health for the status dashboard
_last_groq_status = {"ok": False, "last_check": None, "error": None, "latency_ms": 0}


def get_groq_status() -> dict:
    return _last_groq_status.copy()


async def _call_groq(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 1024,
    max_retries: int = 3,
) -> Optional[str]:
    if not settings.groq_enabled:
        logger.warning("Groq API key not set, returning mock response")
        return "[Mock] I am Tonative, your AI business companion. Please set your GROQ_API_KEY to enable real responses."

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

    import time

    for attempt in range(max_retries):
        try:
            start = time.monotonic()
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(GROQ_CHAT_URL, json=payload, headers=headers)
                response.raise_for_status()
                elapsed_ms = int((time.monotonic() - start) * 1000)

                data = response.json()

                # Update health tracker
                _last_groq_status["ok"] = True
                _last_groq_status["last_check"] = time.time()
                _last_groq_status["error"] = None
                _last_groq_status["latency_ms"] = elapsed_ms

                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            _last_groq_status["ok"] = False
            _last_groq_status["last_check"] = time.time()
            _last_groq_status["error"] = f"HTTP {e.response.status_code}"

            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("retry-after", "2"))
                wait_time = retry_after + random.uniform(0.5, 1.5)
                logger.warning(
                    f"Groq rate limited (attempt {attempt + 1}/{max_retries}), "
                    f"waiting {wait_time:.1f}s"
                )
                await asyncio.sleep(wait_time)
                continue

            logger.error(f"Groq API HTTP error: {e.response.status_code} - {e.response.text}")
            return None

        except Exception as e:
            _last_groq_status["ok"] = False
            _last_groq_status["last_check"] = time.time()
            _last_groq_status["error"] = str(e)
            logger.error(f"Groq API error: {e}")
            return None

    logger.error("Groq API: max retries exhausted after rate limiting")
    return None


async def chat_with_sme(conversation_history: list[dict], user_message: str) -> Optional[str]:
    """Main conversation handler. Takes history + new message, returns AI response."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    return await _call_groq(messages, temperature=0.7, max_tokens=800)


async def extract_profile_data(conversation_history: list[dict]) -> dict:
    """Extract structured profile data from conversation history."""
    conversation_text = ""
    for msg in conversation_history:
        role_label = "SME" if msg["role"] == "user" else "Assistant"
        conversation_text += f"{role_label}: {msg['content']}\n"

    prompt = ONBOARDING_EXTRACTION_PROMPT.format(conversation=conversation_text)

    messages = [{"role": "user", "content": prompt}]
    result = await _call_groq(messages, temperature=0.0, max_tokens=500)

    if not result:
        return {}

    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse profile extraction: {result}")
        return {}


async def match_opportunities(profile_summary: str, opportunities_text: str) -> Optional[str]:
    """Match an SME profile against available funding opportunities."""
    prompt = MATCHING_PROMPT.format(profile=profile_summary, opportunities=opportunities_text)

    messages = [{"role": "user", "content": prompt}]
    return await _call_groq(messages, temperature=0.5, max_tokens=1000)


async def ping_groq() -> dict:
    """Lightweight health check - sends a tiny request to verify the API key works."""
    import time

    if not settings.groq_enabled:
        return {"ok": False, "error": "API key not configured", "latency_ms": 0}

    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                GROQ_CHAT_URL,
                json={
                    "model": GROQ_MODEL,
                    "messages": [{"role": "user", "content": "hi"}],
                    "max_tokens": 1,
                },
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            elapsed = int((time.monotonic() - start) * 1000)
            response.raise_for_status()
            _last_groq_status.update(ok=True, last_check=time.time(), error=None, latency_ms=elapsed)
            return {"ok": True, "latency_ms": elapsed, "error": None}
    except httpx.HTTPStatusError as e:
        _last_groq_status.update(ok=False, last_check=time.time(), error=f"HTTP {e.response.status_code}")
        return {"ok": False, "latency_ms": 0, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        _last_groq_status.update(ok=False, last_check=time.time(), error=str(e))
        return {"ok": False, "latency_ms": 0, "error": str(e)}


# ===================================================================
# WEB SEARCH — uses groq/compound which searches the web automatically
# ===================================================================

SEARCH_SYSTEM_PROMPT = """You are BizPadi, a smart WhatsApp AI companion for Nigerian SMEs.

The user has asked a question that needs real, current information — funding opportunities, grants, loans, business registration, market data, or anything else.

Search the web and give a pinpoint, accurate answer. Be specific to Nigeria and Africa where relevant.

Format your response for WhatsApp:
- Keep it under 400 words
- Use bullet points for lists
- Bold key information with *asterisks*
- Always mention your source briefly
- End with one actionable next step for the SME

Speak like a trusted Nigerian business friend — warm, direct, no jargon.
"""


async def search_and_respond(query: str, sme_profile_summary: str = "") -> Optional[str]:
    """
    Uses Groq's compound model to search the web and give a real-time answer.
    No extra API key needed — same Groq key, different model.
    """
    if not settings.groq_enabled:
        return None

    context = f"\nSME Profile context: {sme_profile_summary}" if sme_profile_summary else ""

    messages = [
        {"role": "system", "content": SEARCH_SYSTEM_PROMPT},
        {"role": "user", "content": f"{query}{context}"},
    ]

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_COMPOUND_MODEL,
        "messages": messages,
        "max_tokens": 1024,
    }

    import time

    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=45.0) as client:  # compound needs more time
            response = await client.post(GROQ_CHAT_URL, json=payload, headers=headers)
            response.raise_for_status()
            elapsed_ms = int((time.monotonic() - start) * 1000)
            data = response.json()

            _last_groq_status["ok"] = True
            _last_groq_status["last_check"] = time.time()
            _last_groq_status["latency_ms"] = elapsed_ms

            return data["choices"][0]["message"]["content"]

    except httpx.HTTPStatusError as e:
        logger.error(f"Groq compound error: {e.response.status_code} - {e.response.text}")
        # Fall back to regular model if compound fails
        logger.info("Falling back to regular model for web search query")
        return await _call_groq(messages, temperature=0.3, max_tokens=1024)
    except Exception as e:
        logger.error(f"Groq compound search error: {e}")
        return None


def should_search_web(user_text: str) -> bool:
    """
    Detect if a message needs a live web search.
    Triggers on: funding questions, grant deadlines, business advice,
    registration queries, market info, news, and anything time-sensitive.
    """
    lower = user_text.lower()

    search_triggers = [
        # Funding and grants
        "grant", "grants", "funding", "loan", "loans", "finance", "capital",
        "cbn", "bank of industry", "boi", "smedan", "youwin", "tef",
        "tony elumelu", "lsetf", "nirsal", "agsmeis",
        # Business operations
        "how to register", "cac registration", "how do i", "where can i",
        "what is the deadline", "apply for", "application",
        # Market and business intelligence
        "price of", "cost of", "market for", "demand for",
        "how much is", "naira", "exchange rate",
        # News and current events
        "latest", "current", "new", "2025", "2026", "this year",
        "recently", "just announced", "new programme",
        # General advice
        "should i", "is it worth", "what do you think about",
        "advice on", "tips for", "how to grow",
    ]

    return any(trigger in lower for trigger in search_triggers)
