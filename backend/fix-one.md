# Fix One

A full audit of the Tonative SME Bot codebase. Every weakness found, every upgrade proposed, every line that needs attention before demo day. Read top to bottom. Fix top to bottom. Each section is one problem, one solution, one code block you can copy-paste.

---

## 1. The Webhook Has No Security

**Where:** `app/routers/webhook.py`

**Problem:** Right now, anyone on the internet can POST to `/webhook/whatsapp` and pretend to be Twilio. No signature validation. A bad actor could spam fake messages, corrupt user profiles, or burn through your Groq API quota.

**Fix:** Validate the `X-Twilio-Signature` header on every incoming request. Twilio signs every webhook with your Auth Token using HMAC-SHA1. If the signature does not match, reject the request with a 403.

**Code:** Add this to the top of `app/routers/webhook.py`:

```python
import hashlib
import hmac
import base64
from urllib.parse import urlencode
from fastapi import HTTPException

def validate_twilio_signature(url: str, params: dict, signature: str, auth_token: str) -> bool:
    """Validate that a request came from Twilio using HMAC-SHA1."""
    if not auth_token:
        return True  # skip validation in dev mode (no token set)

    data = url
    for key in sorted(params.keys()):
        data += key + params[key]

    expected = base64.b64encode(
        hmac.new(auth_token.encode(), data.encode(), hashlib.sha1).digest()
    ).decode()

    return hmac.compare_digest(expected, signature)
```

Then in the `whatsapp_webhook` function, before processing:

```python
signature = request.headers.get("X-Twilio-Signature", "")
url = str(request.url)
params = dict(form_data)

if settings.TWILIO_AUTH_TOKEN and not validate_twilio_signature(url, params, signature, settings.TWILIO_AUTH_TOKEN):
    raise HTTPException(status_code=403, detail="Invalid Twilio signature")
```

**Priority:** HIGH. Without this, your webhook is an open door.

---

## 2. No Rate Limit Handling on Groq

**Where:** `app/services/llm.py`

**Problem:** Groq's free tier allows only 30 requests per minute and 1,000 requests per day. If multiple users message the bot at the same time, or if one conversation triggers both `chat_with_sme` and `extract_profile_data` (which it does on every onboarding message), you will hit 429 errors. The current code logs the error and returns `None`, which the user sees as "I am having a moment."

**Fix:** Add retry with exponential backoff. Parse the `retry-after` header from Groq's 429 response.

**Code:** Replace the `_call_groq` function:

```python
import asyncio
import random

async def _call_groq(messages: list[dict], temperature: float = 0.7, max_tokens: int = 1024, max_retries: int = 3) -> Optional[str]:
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

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(GROQ_CHAT_URL, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("retry-after", "2"))
                wait_time = retry_after + random.uniform(0.5, 1.5)
                logger.warning(f"Groq rate limited (attempt {attempt + 1}/{max_retries}), waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                continue
            logger.error(f"Groq API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return None

    logger.error("Groq API: max retries exhausted")
    return None
```

**Priority:** HIGH. Without this, the hackathon demo will break if the judges are testing quickly.

---

## 3. Twilio Message Length Limit Will Silently Truncate Responses

**Where:** `app/services/whatsapp.py` and `app/services/conversation.py`

**Problem:** Twilio enforces a 1,600 character limit on WhatsApp messages. Any response longer than that fails with Error 21617 or gets truncated. The matching response (which includes 5 opportunities with details) can easily exceed this. The LLM response is uncapped. There is no splitting logic.

**Fix:** Add a message splitter that chunks long responses at sentence boundaries, then send each chunk as a separate TwiML message or via the REST API.

**Code:** Add to `app/services/whatsapp.py`:

```python
WHATSAPP_CHAR_LIMIT = 1500  # leave some margin below 1600

def split_message(text: str, limit: int = WHATSAPP_CHAR_LIMIT) -> list[str]:
    """Split a long message into chunks that fit within WhatsApp's character limit."""
    if len(text) <= limit:
        return [text]

    chunks = []
    current_chunk = ""

    paragraphs = text.split("\n\n")

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= limit:
            if current_chunk:
                current_chunk += "\n\n"
            current_chunk += paragraph
        else:
            if current_chunk:
                chunks.append(current_chunk)
            if len(paragraph) <= limit:
                current_chunk = paragraph
            else:
                # Split long paragraphs by sentence
                sentences = paragraph.replace(". ", ".\n").split("\n")
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 <= limit:
                        current_chunk += (" " if current_chunk else "") + sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
```

Then update the webhook to handle multiple chunks:

```python
chunks = split_message(text_response)
if len(chunks) == 1:
    twiml = build_twiml_text(chunks[0])
    return Response(content=twiml, media_type="application/xml")
else:
    # Send first chunk via TwiML, rest via REST API
    twiml = build_twiml_text(chunks[0])
    for chunk in chunks[1:]:
        await send_whatsapp_message(phone_number, chunk)
    return Response(content=twiml, media_type="application/xml")
```

**Priority:** HIGH. Long matching results will fail without this.

---

## 4. No Global Exception Handler

**Where:** `main.py`

**Problem:** If any unhandled exception occurs in the webhook handler, FastAPI returns a raw 500 error to Twilio. Twilio retries failed webhooks, which can create a loop of errors. The user sees nothing or gets a Twilio error message.

**Fix:** Add a global exception handler that always returns valid TwiML, even when things break.

**Code:** Add to `main.py`:

```python
from fastapi import Request
from fastapi.responses import Response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)

    # If this is the webhook, return valid TwiML so Twilio does not retry
    if "/webhook/" in request.url.path:
        from app.services.whatsapp import build_twiml_text
        error_twiml = build_twiml_text(
            "I am having a technical issue right now. Please try again in a few minutes."
        )
        return Response(content=error_twiml, media_type="application/xml")

    # For other endpoints, return JSON
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )
```

**Priority:** HIGH. Without this, one bug crashes the whole demo.

---

## 5. Opportunity Selection Uses Wrong Index After Matching

**Where:** `app/services/conversation.py`, function `_handle_opportunity_selection`

**Problem:** When we show matched opportunities, we show them ranked by match score (top 5 from `get_matched_opportunities`). But when the user replies with a number like "2", the code looks up `FUNDING_OPPORTUNITIES[1]` (the raw list, not the sorted matches). So user picks "2" thinking it is the TEF programme, but gets the BOI loan instead.

**Fix:** Store the last matched results for each user, or rebuild the match list and index into it.

**Code:** The simplest fix is to rebuild the matches in the selection handler:

```python
async def _handle_opportunity_selection(profile: SMEProfile, user_text: str) -> str:
    """Handle when a user selects an opportunity by number."""
    index = int(user_text.strip())

    # Rebuild the same match list the user saw
    matches = get_matched_opportunities(profile)

    if index < 1 or index > len(matches) or index > 5:
        return "That number does not match any opportunity. Please reply with a number from the list I showed you."

    opp = matches[index - 1]["opportunity"]

    steps = "\n".join(f"{i}. {step}" for i, step in enumerate(opp["application_steps"], 1))

    return (
        f"*{opp['name']}*\n\n"
        f"{opp['description']}\n\n"
        f"Amount: {opp['amount']}\n"
        f"Deadline: {opp['deadline']}\n"
        f"CAC Required: {'Yes' if opp['requires_cac'] else 'No'}\n\n"
        f"*How to apply:*\n{steps}\n\n"
        f"Link: {opp['application_link']}\n\n"
        "Do you need help with any of these steps? Just ask."
    )
```

And update `_is_opportunity_selection` to accept up to 5 (not hardcoded 7):

```python
def _is_opportunity_selection(text: str) -> bool:
    stripped = text.strip()
    return stripped.isdigit() and 1 <= int(stripped) <= 5
```

**Priority:** HIGH. This is a logic bug that will confuse every user during the demo.

---

## 6. Conversation History Grows Without Limit

**Where:** `app/services/database.py` and `app/services/llm.py`

**Problem:** Every message is saved. The LLM receives the last 20 messages as history. But there is no token counting. A 20-message conversation with long responses can easily exceed Groq's 6,000 tokens-per-minute free tier limit, or blow past the model's context window. Llama 3.3 70B has a 128K context, but Groq may enforce lower limits on the free tier.

**Fix:** Trim conversation history to the most recent N messages, and add a rough token estimate to stay safe.

**Code:** Update `format_history_for_llm` in `database.py`:

```python
async def format_history_for_llm(phone_number: str, max_messages: int = 10, max_chars: int = 4000) -> list[dict]:
    history = await get_conversation_history(phone_number, limit=max_messages)
    formatted = []
    total_chars = 0

    # Take most recent messages that fit within the character budget
    for msg in reversed(history):
        msg_len = len(msg["content"])
        if total_chars + msg_len > max_chars:
            break
        formatted.insert(0, {
            "role": msg["role"],
            "content": msg["content"],
        })
        total_chars += msg_len

    return formatted
```

**Priority:** MEDIUM. Will not crash the demo with 1-2 test users, but will hit limits with sustained testing.

---

## 7. Extraction Runs on Every Onboarding Message (Double API Calls)

**Where:** `app/services/conversation.py`, function `_handle_onboarding`

**Problem:** Every onboarding message makes TWO Groq API calls: one for the chat response, one for profile extraction. That is 2 out of your 30 requests-per-minute budget gone per message. With the free tier at 1,000 requests/day, a single user completing onboarding (around 8 messages) uses 16 requests. Multiply by a few testers and you are burning through quota fast.

**Fix:** Only run extraction every 3 messages, or after the LLM response indicates the profile might be complete.

**Code:**

```python
async def _handle_onboarding(profile: SMEProfile, user_text: str) -> str:
    history = await format_history_for_llm(profile.phone_number)
    response = await chat_with_sme(history, user_text)

    if not response:
        return "I am having a moment. Please try again shortly."

    # Only extract every 3 messages to save API calls
    message_count = len(history) + 2  # +2 for new user msg and assistant response
    should_extract = (message_count % 3 == 0) or message_count >= 6

    if should_extract:
        full_history = history + [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": response},
        ]
        extracted = await extract_profile_data(full_history)

        if extracted:
            await update_profile_fields(profile.phone_number, extracted)
            updated_profile = await get_profile(profile.phone_number)

            if updated_profile and updated_profile.is_profile_complete():
                updated_profile.state = UserState.PROFILED
                await upsert_profile(updated_profile)

                matches = get_matched_opportunities(updated_profile)
                match_text = format_opportunities_for_whatsapp(matches)
                response += f"\n\nGreat news! I have found some opportunities for your business:\n\n{match_text}"

    return response
```

**Priority:** MEDIUM. Saves API quota during the hackathon.

---

## 8. The `on_event` Startup Hook Is Deprecated

**Where:** `main.py`

**Problem:** `@app.on_event("startup")` is deprecated in FastAPI 0.109+. The current code will print a deprecation warning in logs. The replacement is the `lifespan` context manager.

**Fix:**

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("TONATIVE SME BOT starting up")
    logger.info("=" * 60)
    logger.info(f"Groq LLM:      {'READY' if settings.groq_enabled else 'NOT CONFIGURED'}")
    logger.info(f"Supabase DB:   {'READY' if settings.supabase_enabled else 'USING IN-MEMORY STORE'}")
    logger.info(f"Tonative AI:   {'READY' if settings.tonative_enabled else 'USING FALLBACK'}")
    logger.info(f"ElevenLabs:    {'READY' if settings.elevenlabs_enabled else 'DISABLED'}")
    logger.info(f"Twilio:        {'READY' if settings.TWILIO_ACCOUNT_SID else 'NOT CONFIGURED'}")
    logger.info("=" * 60)
    yield
    logger.info("TONATIVE SME BOT shutting down")

app = FastAPI(
    title="Tonative SME Bot",
    description="WhatsApp AI Companion for African SMEs.",
    version="1.0.0",
    lifespan=lifespan,
)
```

Then remove the `@app.on_event("startup")` block.

**Priority:** LOW. It still works, but judges might see the deprecation warning and think the code is outdated.

---

## 9. Language Detection Is Too Aggressive With Short Messages

**Where:** `app/services/tonative.py`

**Problem:** The word "omo" is a Yoruba marker, but many Nigerian English speakers say "omo" casually. Similarly, "oga" is used in Nigerian Pidgin. The word "ina" is a Hausa marker but could appear in English sentences. A message like "Omo, my business is struggling" gets classified as Yoruba and the response gets passed through the Tonative translation pipeline (or the LLM responds in Yoruba).

**Fix:** Require at least 2 marker hits before switching away from English. Also add Pidgin English detection.

**Code:**

```python
def _fallback_detect(text: str) -> str:
    """Keyword-based language detection with minimum threshold."""
    lower = text.lower()

    # Arabic uses a different script, so even one marker is reliable
    for marker in _ARABIC_MARKERS:
        if marker in text:
            return "ar"

    # For Latin-script languages, require at least 2 marker hits
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
```

**Priority:** MEDIUM. Gets noticeable when Nigerian users casually mix languages.

---

## 10. No "Reset" or "Start Over" Command

**Where:** `app/services/conversation.py`

**Problem:** If a user makes a mistake during onboarding (wrong business name, wrong location), there is no way to reset their profile and start over. They are stuck with wrong data. There is no "menu" or "help" command either.

**Fix:** Add command detection at the top of the message processing pipeline.

**Code:** Add this to `conversation.py`, at the start of `_process_by_state`:

```python
async def _process_by_state(profile: SMEProfile, user_text: str) -> str:
    lower = user_text.lower().strip()

    # Global commands (work in any state)
    if lower in ("reset", "start over", "restart"):
        profile.state = UserState.ONBOARDING
        profile.business_name = None
        profile.business_type = None
        profile.location_city = None
        profile.location_state = None
        profile.business_stage = None
        profile.monthly_revenue = None
        profile.employee_count = None
        profile.cac_registered = None
        profile.biggest_challenge = None
        await upsert_profile(profile)
        return (
            "No problem! I have reset your profile. "
            "Let us start fresh. Tell me about your business -- "
            "what do you do or sell?"
        )

    if lower in ("help", "menu"):
        return (
            "Here is what I can help you with:\n\n"
            "*1.* Find funding opportunities for your business\n"
            "*2.* Guide you through grant/loan applications\n"
            "*3.* Answer business questions\n\n"
            "You can also type:\n"
            "- *reset* to start your profile over\n"
            "- *opportunities* to see funding matches\n"
            "- A *number* (1-5) to get details on a listed opportunity\n\n"
            "Just type or send a voice note in any language!"
        )

    # ... rest of the existing state routing
```

**Priority:** MEDIUM. This is a feature gap that will frustrate real testers.

---

## 11. The Profile Does Not Track Gender

**Where:** `app/models/schemas.py` and `data/opportunities.py`

**Problem:** The WOTCLEF Women Empowerment Grant is specifically for women-owned businesses. But the profile never asks about the business owner's gender. The matching engine scores it as a match for everyone, which is misleading.

**Fix:** Add a `gender` field to the profile and factor it into matching. Also update the onboarding prompt to ask about it naturally.

**Code:** Add to `SMEProfile`:

```python
owner_gender: Optional[str] = None  # "male", "female", "prefer_not_to_say"
```

Add to the extraction prompt's possible fields:

```
- owner_gender (string - one of: male, female, prefer_not_to_say)
```

Update the matching engine to filter gender-specific opportunities:

```python
# In _score_opportunity, add:
if opp.get("gender_requirement") == "female" and profile.owner_gender == "male":
    return 0  # hard disqualify
```

And add `"gender_requirement": "female"` to the WOTCLEF entry in `data/opportunities.py`.

**Priority:** LOW for the hackathon, but shows attention to detail if implemented.

---

## 12. No Timeout Protection on the Webhook

**Where:** `app/routers/webhook.py`

**Problem:** Twilio expects a response within 15 seconds. If the Groq API is slow (network issue, rate limiting, cold start), or if the voice transcription takes too long, Twilio will timeout and retry the request. The retry creates a duplicate conversation entry.

**Fix:** Add an overall timeout to the message processing, and return a graceful fallback if it takes too long.

**Code:**

```python
import asyncio

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    # ... (existing form parsing code) ...

    try:
        result = await asyncio.wait_for(
            handle_incoming_message(
                phone_number=phone_number,
                body=body,
                media_url=media_url,
                num_media=num_media,
            ),
            timeout=12.0,  # leave 3 seconds buffer for Twilio's 15s limit
        )
    except asyncio.TimeoutError:
        logger.warning(f"Message processing timed out for {phone_number}")
        result = {
            "text_response": "I am taking a bit longer than usual. Give me a moment and send your message again.",
            "audio_bytes": None,
        }

    # ... (rest of the existing response code) ...
```

**Priority:** MEDIUM. Prevents cascading failures during the demo.

---

## 13. Unused Imports in Multiple Files

**Where:** `app/routers/webhook.py`, `app/services/whatsapp.py`, `app/services/voice.py`

**Problem:** Several files import modules they never use. This is cosmetic but makes the code look sloppy to judges reviewing the repo.

**Fix:**

In `app/routers/webhook.py`, remove: `import base64`, `import tempfile`, `import os`

In `app/services/whatsapp.py`, remove: `import base64`, `import tempfile`

In `app/services/voice.py`, remove: `import tempfile`

In `app/models/schemas.py`, remove: `from datetime import datetime` (not used directly)

**Priority:** LOW. Clean code impresses reviewers.

---

## 14. The Test Endpoint Does Not Simulate Voice

**Where:** `app/routers/test.py`

**Problem:** The `TestMessage` model has an `is_voice` field but it does nothing. You cannot test the voice pipeline locally.

**Fix:** If `is_voice` is true, simulate it by passing `num_media=1` (the actual transcription will still fail without a real audio file, but it tests the fallback path).

**Code:**

```python
@router.post("/chat")
async def test_chat(msg: TestMessage):
    result = await handle_incoming_message(
        phone_number=msg.phone_number,
        body=msg.message,
        media_url=None,
        num_media=1 if msg.is_voice else 0,
    )
    return {
        "user_message": msg.message,
        "bot_response": result["text_response"],
        "has_audio": result.get("audio_bytes") is not None,
    }
```

**Priority:** LOW.

---

## 15. Supabase Upsert May Fail on Enum Serialization

**Where:** `app/services/database.py`

**Problem:** The `UserState` enum is serialized via `model_dump()`, which produces the string value (like `"onboarding"`). But if Supabase's column has a CHECK constraint or TEXT type that does not match exactly, the upsert will fail silently (the error is caught and logged but the profile is not saved).

**Fix:** Ensure the state field is always serialized as a plain string:

```python
data = profile.model_dump()
data["state"] = profile.state.value  # ensure it is a plain string
```

**Priority:** LOW. Only matters when Supabase is connected.

---

## Summary: What to Fix First

Fix these BEFORE the demo (they will break things):

1. Webhook signature validation (security)
2. Groq rate limit retry (API will 429 during testing)
3. Message length splitting (long responses will fail)
4. Global exception handler (one bug kills the demo)
5. Opportunity selection index bug (wrong results shown)

Fix these DURING testing if time permits:

6. Conversation history trimming
7. Extraction frequency reduction
8. Language detection threshold
9. Timeout protection on webhook
10. Reset/help commands

Fix these ONLY if you have extra time:

11. Deprecated startup event
12. Gender tracking for WOTCLEF
13. Unused imports cleanup
14. Voice test simulation
15. Enum serialization guard

---

Good luck tomorrow. You built the skeleton right. These fixes make it bulletproof.
