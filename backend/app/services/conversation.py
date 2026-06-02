import logging
from typing import Optional

from app.models.schemas import SMEProfile, UserState
from app.services.database import (
    get_profile, upsert_profile, update_profile_fields,
    save_message, format_history_for_llm,
    track_application, get_applications,
)
from app.services.llm import chat_with_sme, extract_profile_data, search_and_respond, should_search_web
from app.services.matching import get_matched_opportunities, format_opportunities_for_whatsapp
from app.services.tonative import detect_language, translate_to_english, translate_from_english
from app.services.voice import download_twilio_media, transcribe_audio

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = """Hey, good to meet you.

I'm BizPadi. I help Nigerian businesses find funding that actually fits them   grants, loans, government support programmes, all of that.

What kind of business do you run?"""

CONFIRMATION_PROMPTS = {
    "yes", "correct", "yeah", "yep", "yh", "y", "sure", "right",
    "true", "ok", "okay", "confirmed", "correct", "that's right",
    "yes that's right", "yes correct"
}

APPLICATION_CONFIRMATIONS = {
    "applied", "i applied", "done", "submitted",
    "i have applied", "i submitted", "i've applied"
}


async def handle_incoming_message(
    phone_number: str,
    body: Optional[str] = None,
    media_url: Optional[str] = None,
    num_media: int = 0,
    media_content_type: str = "audio/ogg",
) -> dict:

    user_text = body or ""
    detected_lang = "en"

    if body:
        detected_lang = await detect_language(body)

    # Voice note
    if num_media > 0 and media_url:
        audio_bytes = await download_twilio_media(media_url)
        if audio_bytes:
            transcript = await transcribe_audio(
                audio_bytes,
                content_type=media_content_type,
                detected_language=detected_lang,
            )
            if transcript:
                user_text = transcript
                logger.info(f"Voice transcribed ({detected_lang}): {transcript[:80]}")
            else:
                return {
                    "text_response": "Got your voice note but couldn't make it out clearly.\n\nTry sending it again or just type it out, whichever is easier for you.",
                    "audio_bytes": None,
                }
        else:
            return {
                "text_response": "Had trouble receiving that voice note.\n\nCould you try again or type your message instead?",
                "audio_bytes": None,
            }

    if not user_text.strip():
        return {
            "text_response": "Didn't catch that. Send me a message and I'll sort you out.",
            "audio_bytes": None,
        }

    english_text = await translate_to_english(user_text, detected_lang)

    profile = await get_profile(phone_number)
    is_new_user = profile is None

    if not profile:
        profile = SMEProfile(
            phone_number=phone_number,
            state=UserState.ONBOARDING,
            language=detected_lang,
        )
        await upsert_profile(profile)

    if detected_lang != profile.language:
        profile.language = detected_lang
        await upsert_profile(profile)

    if is_new_user:
        await save_message(phone_number, "assistant", WELCOME_MESSAGE)
        return {"text_response": WELCOME_MESSAGE, "audio_bytes": None}

    await save_message(phone_number, "user", english_text)

    response_text = await _process_by_state(profile, english_text)

    final_response = await translate_from_english(response_text, detected_lang)
    await save_message(phone_number, "assistant", response_text)

    return {"text_response": final_response, "audio_bytes": None}


async def _process_by_state(profile: SMEProfile, user_text: str) -> str:
    lower = user_text.lower().strip()

    # Global commands
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
        return "No problem, let's start fresh.\n\n" + WELCOME_MESSAGE

    if lower in ("help", "menu"):
        return (
            "Here's what BizPadi can do for you:\n\n"
            "Find funding opportunities that match your specific business\n\n"
            "Walk you through applications step by step\n\n"
            "Track applications you've submitted\n\n"
            "Search for the latest grants, loans, and programmes in Nigeria\n\n"
            "Answer any business question you throw at me\n\n"
            "Commands you can use:\n"
            "Type *opportunities* to see your matched funding\n"
            "Type *my applications* to track what you've applied for\n"
            "Type a *number* (1 to 5) to get application steps for a listed opportunity\n"
            "Type *reset* to start your profile over"
        )

    if lower in ("my applications", "applications", "track", "my apps"):
        return await _handle_application_status(profile)

    if _is_opportunity_selection(user_text, profile):
        return await _handle_opportunity_selection(profile, user_text)

    if any(lower == p for p in APPLICATION_CONFIRMATIONS):
        return await _handle_application_confirmation(profile, lower)

    if profile.state in (UserState.NEW, UserState.ONBOARDING):
        return await _handle_onboarding(profile, user_text)
    elif profile.state == UserState.CONFIRMING:
        return await _handle_confirmation(profile, user_text)
    elif profile.state == UserState.PROFILED:
        return await _handle_profiled(profile, user_text)
    else:
        return await _handle_support(profile, user_text)


async def _handle_onboarding(profile: SMEProfile, user_text: str) -> str:
    history = await format_history_for_llm(profile.phone_number)
    response = await chat_with_sme(history, user_text)

    if not response:
        return "I'm having a small issue right now. Try again in a moment."

    full_history = history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response},
    ]
    extracted = await extract_profile_data(full_history)

    if extracted:
        updated = await update_profile_fields(profile.phone_number, extracted)

        if updated and updated.is_profile_complete():
            updated.state = UserState.CONFIRMING
            await upsert_profile(updated)
            return updated.to_confirmation_message()

    return response


async def _handle_confirmation(profile: SMEProfile, user_text: str) -> str:
    lower = user_text.lower().strip()

    if any(lower == p or lower.startswith(p) for p in CONFIRMATION_PROMPTS):
        profile.state = UserState.PROFILED
        await upsert_profile(profile)

        matches = get_matched_opportunities(profile)
        match_text = format_opportunities_for_whatsapp(matches)

        return f"Perfect. Let me pull up your best matches.\n\n{match_text}"

    # User wants to correct something
    history = await format_history_for_llm(profile.phone_number)
    response = await chat_with_sme(history, user_text)

    full_history = history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response or ""},
    ]
    extracted = await extract_profile_data(full_history)
    if extracted:
        updated = await update_profile_fields(profile.phone_number, extracted)
        if updated:
            return updated.to_confirmation_message()

    return response or "What would you like to change? Just tell me and I'll fix it."


async def _handle_profiled(profile: SMEProfile, user_text: str) -> str:
    lower = user_text.lower().strip()

    if any(kw in lower for kw in ["opportunities", "funding", "grants", "loans", "show me", "find"]) and len(user_text) < 30:
        matches = get_matched_opportunities(profile)
        return format_opportunities_for_whatsapp(matches)

    if should_search_web(user_text):
        logger.info(f"Web search triggered: {user_text[:50]}")
        result = await search_and_respond(user_text, profile.to_summary())
        if result:
            return result

    history = await format_history_for_llm(profile.phone_number)
    response = await chat_with_sme(history, user_text)
    return response or "Having a small issue right now. Try again in a moment."


async def _handle_support(profile: SMEProfile, user_text: str) -> str:
    if should_search_web(user_text):
        result = await search_and_respond(
            user_text,
            profile.to_summary() if profile.business_name else ""
        )
        if result:
            return result

    history = await format_history_for_llm(profile.phone_number)
    response = await chat_with_sme(history, user_text)
    return response or "Having a small issue right now. Try again in a moment."


def _is_opportunity_selection(text: str, profile: SMEProfile) -> bool:
    stripped = text.strip()
    if not stripped.isdigit():
        return False
    return 1 <= int(stripped) <= 5 and profile.state in (
        UserState.PROFILED, UserState.SUPPORT, UserState.CONFIRMING
    )


async def _handle_opportunity_selection(profile: SMEProfile, user_text: str) -> str:
    index = int(user_text.strip())
    matches = get_matched_opportunities(profile)

    if index < 1 or index > len(matches):
        return "That number doesn't match anything on the list. Try a number between 1 and 5."

    match = matches[index - 1]
    opp = match["opportunity"]
    already_applied = match.get("already_applied", False)

    steps = "\n\n".join(
        f"{i}. {step}" for i, step in enumerate(opp["application_steps"], 1)
    )

    response = (
        f"*{opp['name']}*\n\n"
        f"{opp['description']}\n\n"
        f"Amount: {opp['amount']}\n\n"
        f"Deadline: {opp['deadline']}\n\n"
        f"CAC required: {'Yes' if opp['requires_cac'] else 'No'}\n\n"
        f"How to apply:\n\n{steps}\n\n"
        f"Link: {opp['application_link']}\n\n"
    )

    if already_applied:
        response += "You already applied for this one. Want me to check on the status?"
    else:
        response += "Once you apply, just reply *applied* and I'll track it for you. Need help with any of the steps?"

    profile.state = UserState.SUPPORT
    await upsert_profile(profile)

    await save_message(
        profile.phone_number,
        "system",
        f"[VIEWED_OPPORTUNITY:{opp['id']}:{opp['name']}]"
    )

    return response


async def _handle_application_confirmation(profile: SMEProfile, user_text: str) -> str:
    from app.services.database import get_conversation_history
    full_history = await get_conversation_history(profile.phone_number, limit=30)

    last_opp_id = None
    last_opp_name = None
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
            f"That's great news.\n\n"
            f"I've logged your application for *{last_opp_name}*. "
            f"I'll remind you as the deadline gets closer.\n\n"
            f"Type *my applications* anytime to see your tracking. Fingers crossed for you."
        )
    else:
        return (
            "That's great. Which opportunity did you apply for? "
            "Just tell me the name and I'll track it for you."
        )


async def _handle_application_status(profile: SMEProfile) -> str:
    applications = await get_applications(profile.phone_number)

    if not applications:
        return (
            "You haven't tracked any applications yet.\n\n"
            "After you apply for an opportunity, just reply *applied* and I'll log it for you.\n\n"
            "Type *opportunities* to see your matched funding."
        )

    status_emoji = {
        "applied": "📤",
        "pending": "⏳",
        "approved": "✅",
        "rejected": "❌",
    }

    lines = ["Here's your application tracker:\n"]
    for app in applications[:10]:
        emoji = status_emoji.get(app.get("status", "applied"), "📤")
        name = app.get("opportunity_name", "Unknown")
        status = app.get("status", "applied").capitalize()
        lines.append(f"{emoji} *{name}*")
        lines.append(f"Status: {status}\n")

    lines.append("To update a status just tell me, for example: *approved Tony Elumelu* or *rejected BOI loan*.")
    return "\n".join(lines)
