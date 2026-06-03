import logging
from pathlib import Path
from typing import Optional

from app.models.schemas import SMEProfile, UserState
from app.services.database import (
    get_profile, upsert_profile, update_profile_fields,
    save_message, format_history_for_llm,
    track_application, get_applications,
)
from app.services.llm import chat_with_sme, extract_profile_data, search_and_respond, should_search_web
from app.services.matching import get_matched_opportunities, format_opportunities_for_whatsapp
from app.services.tonative import detect_language
from app.services.voice import download_twilio_media
from app.services import aethex

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = """Hey, good to meet you.

I'm BizPadi. I help Nigerian businesses find funding that actually fits them   grants, loans, government support programmes, all of that.

What kind of business do you run?"""

CONFIRMATION_PROMPTS = {
    "yes", "correct", "yeah", "yep", "yh", "y", "sure", "right",
    "true", "ok", "okay", "confirmed", "yes that's right", "yes correct",
}

APPLICATION_CONFIRMATIONS = {
    "applied", "i applied", "done", "submitted",
    "i have applied", "i submitted", "i've applied",
}


async def handle_incoming_message(
    phone_number: str,
    body: Optional[str] = None,
    media_url: Optional[str] = None,
    num_media: int = 0,
    media_content_type: str = "audio/ogg",
) -> dict:
    """
    Main entry point. Returns:
    {
        "text_response": str,
        "audio_path": Optional[Path],  # WAV file path for TTS reply
    }
    """
    user_text = body or ""
    detected_lang = "en"
    is_voice_message = num_media > 0 and media_url

    # ── Voice transcription ──────────────────────────────────────────────────
    if is_voice_message:
        # Detect language from any text body first (optional hint)
        if body:
            detected_lang = await detect_language(body)

        audio_bytes = await download_twilio_media(media_url)
        if not audio_bytes:
            return {
                "text_response": (
                    "Had trouble receiving your voice note. Could you try again or type it out?"
                ),
                "audio_path": None,
            }

        # Use Aethex (EN/FR) or Groq Whisper (all languages)
        transcript = await aethex.transcribe_audio(audio_bytes, media_content_type, detected_lang)
        if not transcript:
            return {
                "text_response": (
                    "Got your voice note but couldn't make it out clearly.\n\n"
                    "Try again or just type your message   either works!"
                ),
                "audio_path": None,
            }

        user_text = transcript
        logger.info(f"Transcribed ({detected_lang}): {transcript[:80]}")

    if not user_text.strip():
        return {"text_response": "Didn't catch that. Send me a message!", "audio_path": None}

    # ── Language detection ───────────────────────────────────────────────────
    detected_lang = await detect_language(user_text)

    # ── Load / create profile ────────────────────────────────────────────────
    profile = await get_profile(phone_number)
    is_new_user = profile is None

    if not profile:
        profile = SMEProfile(
            phone_number=phone_number,
            state=UserState.ONBOARDING,
            language=detected_lang,
        )
        await upsert_profile(profile)

    # Update language if changed
    if detected_lang != profile.language:
        profile.language = detected_lang
        await upsert_profile(profile)

    # ── New user welcome ─────────────────────────────────────────────────────
    if is_new_user:
        await save_message(phone_number, "assistant", WELCOME_MESSAGE)
        audio_path = await _maybe_tts(WELCOME_MESSAGE, detected_lang, is_voice_message)
        return {"text_response": WELCOME_MESSAGE, "audio_path": audio_path}

    await save_message(phone_number, "user", user_text)

    # ── Process ──────────────────────────────────────────────────────────────
    response_text = await _process_by_state(profile, user_text, detected_lang)
    await save_message(phone_number, "assistant", response_text)

    # Generate TTS reply if user sent voice
    audio_path = await _maybe_tts(response_text, detected_lang, is_voice_message)

    return {"text_response": response_text, "audio_path": audio_path}


async def _maybe_tts(text: str, language: str, user_sent_voice: bool) -> Optional[Path]:
    """Generate TTS audio if user sent a voice note and language is supported."""
    if not user_sent_voice:
        return None
    # Only EN and FR supported by Aethex TTS
    if language not in ("en", "fr"):
        return None
    # Strip WhatsApp formatting before TTS
    clean = text.replace("*", "").replace("_", "").replace("\n\n", " ").replace("\n", " ")
    # Keep under 500 chars for quick TTS
    if len(clean) > 500:
        clean = clean[:497] + "..."
    return await aethex.text_to_speech(clean, language)


async def _process_by_state(profile: SMEProfile, user_text: str, lang: str) -> str:
    lower = user_text.lower().strip()

    # ── Global commands ──────────────────────────────────────────────────────
    if lower in ("reset", "start over", "restart"):
        profile.state = UserState.ONBOARDING
        for field in ["business_name", "business_type", "location_city", "location_state",
                      "business_stage", "monthly_revenue", "employee_count", "cac_registered",
                      "biggest_challenge"]:
            setattr(profile, field, None)
        await upsert_profile(profile)
        return "No problem, let's start fresh.\n\n" + WELCOME_MESSAGE

    if lower in ("help", "menu"):
        return (
            "Here's what BizPadi can do for you:\n\n"
            "Find funding opportunities that match your specific business\n\n"
            "Walk you through applications step by step\n\n"
            "Tell you exactly which documents to gather (fund readiness)\n\n"
            "Track applications you've submitted\n\n"
            "Search for the latest grants and loans in Nigeria\n\n"
            "Answer any business question\n\n"
            "Commands:\n"
            "Type *opportunities* to see your matched funding\n"
            "Type *my applications* to track what you've applied for\n"
            "Type *documents [number]* to get the document checklist for an opportunity\n"
            "Type a *number* (1 to 5) to get application steps\n"
            "Type *reset* to start your profile over"
        )

    if lower in ("my applications", "applications", "track", "my apps"):
        return await _handle_application_status(profile)

    if _is_opportunity_selection(user_text, profile):
        return await _handle_opportunity_selection(profile, user_text, lang)

    if any(lower == p for p in APPLICATION_CONFIRMATIONS):
        return await _handle_application_confirmation(profile)

    # Document checklist request
    if lower.startswith("documents") or lower.startswith("docs "):
        return await _handle_document_request(profile, user_text, lang)

    # ── Route by state ────────────────────────────────────────────────────────
    if profile.state in (UserState.NEW, UserState.ONBOARDING):
        return await _handle_onboarding(profile, user_text, lang)
    elif profile.state == UserState.CONFIRMING:
        return await _handle_confirmation(profile, user_text, lang)
    elif profile.state == UserState.PROFILED:
        return await _handle_profiled(profile, user_text, lang)
    else:
        return await _handle_support(profile, user_text, lang)


# ─────────────────────────────────────────────────────────────────────────────
# ONBOARDING
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_onboarding(profile: SMEProfile, user_text: str, lang: str) -> str:
    history = await format_history_for_llm(profile.phone_number)
    response = await chat_with_sme(history, user_text, lang)

    if not response:
        return "Having a small issue right now. Try again in a moment."

    full_history = history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response},
    ]
    extracted = await extract_profile_data(full_history)

    if extracted:
        # Update language from extraction if detected
        if "language" in extracted and extracted["language"] in ("en", "fr", "yo", "ha", "pcm", "ar"):
            profile.language = extracted["language"]

        updated = await update_profile_fields(profile.phone_number, extracted)
        if updated and updated.is_profile_complete():
            updated.state = UserState.CONFIRMING
            await upsert_profile(updated)
            return updated.to_confirmation_message()

    return response


# ─────────────────────────────────────────────────────────────────────────────
# PROFILE CONFIRMATION
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_confirmation(profile: SMEProfile, user_text: str, lang: str) -> str:
    lower = user_text.lower().strip()

    if any(lower == p or lower.startswith(p) for p in CONFIRMATION_PROMPTS):
        profile.state = UserState.PROFILED
        await upsert_profile(profile)
        matches = get_matched_opportunities(profile)
        match_text = format_opportunities_for_whatsapp(matches)
        return f"Let me pull up your best matches.\n\n{match_text}"

    # Correction request
    history = await format_history_for_llm(profile.phone_number)
    response = await chat_with_sme(history, user_text, lang)
    full_history = history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response or ""},
    ]
    extracted = await extract_profile_data(full_history)
    if extracted:
        updated = await update_profile_fields(profile.phone_number, extracted)
        if updated:
            return updated.to_confirmation_message()

    return response or "What would you like to change? Just tell me."


# ─────────────────────────────────────────────────────────────────────────────
# PROFILED
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_profiled(profile: SMEProfile, user_text: str, lang: str) -> str:
    lower = user_text.lower().strip()

    if any(kw in lower for kw in ["opportunities", "funding", "grants", "loans", "show me", "find"]) and len(user_text) < 30:
        matches = get_matched_opportunities(profile)
        return format_opportunities_for_whatsapp(matches)

    if should_search_web(user_text):
        result = await search_and_respond(user_text, profile.to_summary(), lang)
        if result:
            return result

    history = await format_history_for_llm(profile.phone_number)
    return await chat_with_sme(history, user_text, lang) or "Having a small issue. Try again in a moment."


async def _handle_support(profile: SMEProfile, user_text: str, lang: str) -> str:
    if should_search_web(user_text):
        result = await search_and_respond(
            user_text,
            profile.to_summary() if profile.business_name else "",
            lang,
        )
        if result:
            return result

    history = await format_history_for_llm(profile.phone_number)
    return await chat_with_sme(history, user_text, lang) or "Having a small issue. Try again in a moment."


# ─────────────────────────────────────────────────────────────────────────────
# OPPORTUNITY SELECTION + DOCUMENTS
# ─────────────────────────────────────────────────────────────────────────────

def _is_opportunity_selection(text: str, profile: SMEProfile) -> bool:
    stripped = text.strip()
    return (
        stripped.isdigit()
        and 1 <= int(stripped) <= 10
        and profile.state in (UserState.PROFILED, UserState.SUPPORT, UserState.CONFIRMING)
    )


async def _handle_opportunity_selection(profile: SMEProfile, user_text: str, lang: str) -> str:
    index = int(user_text.strip())
    matches = get_matched_opportunities(profile)

    if index < 1 or index > len(matches):
        return "That number doesn't match anything on the list. Reply with a number from the list above."

    match = matches[index - 1]
    opp = match["opportunity"]
    already_applied = match.get("already_applied", False)

    # Application steps
    steps = "\n\n".join(f"{i}. {step}" for i, step in enumerate(opp["application_steps"], 1))

    # Document checklist
    docs = opp.get("required_documents", [])
    doc_list = "\n".join(f"• {doc}" for doc in docs)

    response = (
        f"*{opp['name']}*\n\n"
        f"{opp['description'][:300]}\n\n"
        f"Amount: {opp['amount']}\n\n"
        f"Deadline: {opp['deadline']}\n\n"
        f"CAC required: {'Yes' if opp['requires_cac'] else 'No'}\n\n"
        f"*Documents you need to gather:*\n{doc_list}\n\n"
        f"*How to apply:*\n\n{steps}\n\n"
        f"Link: {opp['application_link']}\n\n"
    )

    if already_applied:
        response += "You already applied for this one. Want me to check on the status?"
    else:
        response += (
            "Once you have all your documents ready, reply *applied* and I'll track it for you.\n\n"
            "Need help getting any of these documents? Just ask."
        )

    profile.state = UserState.SUPPORT
    await upsert_profile(profile)

    await save_message(
        profile.phone_number,
        "system",
        f"[VIEWED_OPPORTUNITY:{opp['id']}:{opp['name']}]",
    )
    return response


async def _handle_document_request(profile: SMEProfile, user_text: str, lang: str) -> str:
    """User asked specifically for document checklist."""
    # Try to extract a number
    parts = user_text.split()
    num = None
    for p in parts:
        if p.isdigit():
            num = int(p)
            break

    if num:
        matches = get_matched_opportunities(profile)
        if 1 <= num <= len(matches):
            opp = matches[num - 1]["opportunity"]
            docs = opp.get("required_documents", [])
            doc_list = "\n".join(f"{i}. {doc}" for i, doc in enumerate(docs, 1))
            return (
                f"*Documents needed for {opp['name']}:*\n\n"
                f"{doc_list}\n\n"
                f"Which of these do you already have? I can help you get the ones you're missing."
            )

    return (
        "Which opportunity do you want the document checklist for?\n\n"
        "Type the number from the list, like: *documents 1*"
    )


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION TRACKING
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_application_confirmation(profile: SMEProfile) -> str:
    from app.services.database import get_conversation_history
    full_history = await get_conversation_history(profile.phone_number, limit=30)

    last_opp_id = last_opp_name = None
    for msg in reversed(full_history):
        content = msg.get("content", "")
        if content.startswith("[VIEWED_OPPORTUNITY:"):
            parts = content.replace("[VIEWED_OPPORTUNITY:", "").replace("]", "").split(":", 1)
            if len(parts) == 2:
                last_opp_id, last_opp_name = parts[0], parts[1]
                break

    if last_opp_id and last_opp_name:
        await track_application(profile.phone_number, last_opp_id, last_opp_name)
        return (
            f"That's great.\n\n"
            f"I've logged your application for *{last_opp_name}*. "
            f"I'll remind you as the deadline approaches.\n\n"
            f"Type *my applications* anytime to see your full tracker."
        )
    return (
        "That's great! Which opportunity did you apply for? "
        "Just tell me the name and I'll track it for you."
    )


async def _handle_application_status(profile: SMEProfile) -> str:
    applications = await get_applications(profile.phone_number)

    if not applications:
        return (
            "You haven't tracked any applications yet.\n\n"
            "After you apply for an opportunity, reply *applied* and I'll log it.\n\n"
            "Type *opportunities* to see your matched funding."
        )

    status_emoji = {"applied": "📤", "pending": "⏳", "approved": "✅", "rejected": "❌"}
    lines = ["*Your Applications:*\n"]
    for app in applications[:10]:
        emoji = status_emoji.get(app.get("status", "applied"), "📤")
        name = app.get("opportunity_name", "Unknown")
        status = app.get("status", "applied").capitalize()
        lines.append(f"{emoji} *{name}*")
        lines.append(f"Status: {status}\n")

    lines.append("To update: reply *approved [name]* or *rejected [name]*")
    return "\n".join(lines)
