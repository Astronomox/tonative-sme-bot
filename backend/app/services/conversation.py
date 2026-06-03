import logging
from pathlib import Path
from typing import Optional

from app.models.schemas import SMEProfile, UserState
from app.services.database import (
    get_profile, upsert_profile, update_profile_fields,
    save_message, format_history_for_llm,
    track_application, get_applications,
)
from app.services.llm import (
    chat_with_sme,
    extract_profile_data,
    detect_language_switch,
    detect_language_llm,
    get_live_opportunities,
    get_fund_readiness_plan,
    match_with_explanation,
    should_search_web,
    should_get_readiness_plan,
    LANGUAGE_NAMES,
)
from app.services.matching import get_matched_opportunities, format_opportunities_for_whatsapp
from app.services.voice import download_twilio_media
from app.services import aethex
from app.core.prompts import (
    LANGUAGE_MENU,
    LANGUAGE_CONFIRMATIONS,
    LANGUAGE_SWITCH_MESSAGES,
)
from data.opportunities import get_opportunities_text

logger = logging.getLogger(__name__)

# Number to language code mapping for menu selection
MENU_LANGUAGE_MAP = {
    "1": "en",
    "2": "yo",
    "3": "ha",
    "4": "pcm",
    "5": "fr",
}

CONFIRMATION_PROMPTS = {
    "yes", "correct", "yeah", "yep", "yh", "y", "sure", "right",
    "true", "ok", "okay", "confirmed", "yes correct", "yes that's right",
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
        "audio_path": Optional[Path],
    }
    """
    user_text = body or ""
    is_voice = num_media > 0 and media_url

    # ── Voice transcription ──────────────────────────────────────────────────
    if is_voice:
        audio_bytes = await download_twilio_media(media_url)
        if not audio_bytes:
            return {
                "text_response": "Had trouble receiving your voice note. Try again or type it.",
                "audio_path": None,
            }
        # Detect language from text body first as hint
        hint_lang = "en"
        if body:
            hint_lang = await detect_language_llm(body)

        transcript = await aethex.transcribe_audio(audio_bytes, media_content_type, hint_lang)
        if not transcript:
            return {
                "text_response": "Got your voice note but couldn't make it out clearly. Try again or type it!",
                "audio_path": None,
            }
        user_text = transcript
        logger.info(f"Transcribed: {transcript[:80]}")

    if not user_text.strip():
        return {"text_response": "Didn't catch that. Send me a message!", "audio_path": None}

    # ── Load or create profile ────────────────────────────────────────────────
    profile = await get_profile(phone_number)
    is_new_user = profile is None

    if is_new_user:
        profile = SMEProfile(
            phone_number=phone_number,
            state=UserState.LANGUAGE_SELECT,
            language="en",
        )
        await upsert_profile(profile)
        # Brand new user — show language menu
        await save_message(phone_number, "assistant", LANGUAGE_MENU)
        audio_path = await _maybe_tts(LANGUAGE_MENU, "en", is_voice)
        return {"text_response": LANGUAGE_MENU, "audio_path": audio_path}

    # ── Check for mid-conversation language switch ────────────────────────────
    new_lang = detect_language_switch(user_text)
    if new_lang and new_lang != profile.language:
        profile.language = new_lang
        await upsert_profile(profile)
        switch_msg = LANGUAGE_SWITCH_MESSAGES.get(new_lang, f"Switched to {LANGUAGE_NAMES.get(new_lang, 'the new language')}.")
        await save_message(phone_number, "user", user_text)
        await save_message(phone_number, "assistant", switch_msg)
        audio_path = await _maybe_tts(switch_msg, new_lang, is_voice)
        return {"text_response": switch_msg, "audio_path": audio_path}

    await save_message(phone_number, "user", user_text)

    # ── Route by state ────────────────────────────────────────────────────────
    response_text = await _process_by_state(profile, user_text, is_voice)
    await save_message(phone_number, "assistant", response_text)

    audio_path = await _maybe_tts(response_text, profile.language, is_voice)
    return {"text_response": response_text, "audio_path": audio_path}


async def _maybe_tts(text: str, language: str, user_sent_voice: bool) -> Optional[Path]:
    if not user_sent_voice:
        return None
    if language not in ("en", "fr"):
        return None
    clean = text.replace("*", "").replace("_", "").replace("\n\n", " ").replace("\n", " ")
    if len(clean) > 500:
        clean = clean[:497] + "..."
    return await aethex.text_to_speech(clean, language)


async def _process_by_state(profile: SMEProfile, user_text: str, is_voice: bool) -> str:
    lower = user_text.lower().strip()
    lang = profile.language

    # ── Language selection state ──────────────────────────────────────────────
    if profile.state == UserState.LANGUAGE_SELECT:
        return await _handle_language_selection(profile, user_text)

    # ── Global commands (work in any state) ───────────────────────────────────
    if lower in ("reset", "start over", "restart"):
        return await _handle_reset(profile)

    if lower in ("help", "menu"):
        return _build_help_menu(lang)

    if lower in ("my applications", "applications", "track", "my apps"):
        return await _handle_application_status(profile)

    if _is_opportunity_selection(user_text, profile):
        return await _handle_opportunity_selection(profile, user_text)

    if any(lower == p for p in APPLICATION_CONFIRMATIONS):
        return await _handle_application_confirmation(profile)

    if lower.startswith("documents") or lower.startswith("docs "):
        return await _handle_document_request(profile, user_text)

    # Fund readiness / consultant mode
    if should_get_readiness_plan(user_text):
        return await _handle_readiness_plan(profile)

    # Live opportunity search
    if "find new" in lower or "search" in lower or "latest" in lower:
        return await _handle_live_search(profile)

    # ── Route by profile state ────────────────────────────────────────────────
    if profile.state == UserState.ONBOARDING:
        return await _handle_onboarding(profile, user_text)
    elif profile.state == UserState.CONFIRMING:
        return await _handle_confirmation(profile, user_text)
    elif profile.state in (UserState.PROFILED, UserState.SUPPORT):
        return await _handle_profiled_or_support(profile, user_text)
    else:
        return await _handle_onboarding(profile, user_text)


# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE SELECTION
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_language_selection(profile: SMEProfile, user_text: str) -> str:
    lower = user_text.strip().lower()

    # Check numbered selection
    selected_lang = MENU_LANGUAGE_MAP.get(lower.strip())

    # Also handle text-based selection
    if not selected_lang:
        text_map = {
            "english": "en", "yoruba": "yo", "hausa": "ha",
            "pidgin": "pcm", "french": "fr", "français": "fr",
        }
        for keyword, code in text_map.items():
            if keyword in lower:
                selected_lang = code
                break

    if selected_lang:
        profile.language = selected_lang
        profile.state = UserState.ONBOARDING
        await upsert_profile(profile)
        return LANGUAGE_CONFIRMATIONS.get(selected_lang, LANGUAGE_CONFIRMATIONS["en"])

    # Didn't understand — show menu again
    return f"Please reply with a number:\n\n{LANGUAGE_MENU}"


# ─────────────────────────────────────────────────────────────────────────────
# RESET
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_reset(profile: SMEProfile) -> str:
    profile.state = UserState.LANGUAGE_SELECT
    for f in ["business_name", "business_type", "location_city", "location_state",
              "business_stage", "monthly_revenue", "employee_count", "cac_registered",
              "biggest_challenge", "owner_name"]:
        setattr(profile, f, None)
    await upsert_profile(profile)
    return f"No problem, fresh start.\n\n{LANGUAGE_MENU}"


# ─────────────────────────────────────────────────────────────────────────────
# HELP MENU (in user's language via LLM)
# ─────────────────────────────────────────────────────────────────────────────

def _build_help_menu(lang: str) -> str:
    menus = {
        "en": (
            "Here's what BizPadi can do:\n\n"
            "Find funding opportunities matching your business\n\n"
            "Search for the latest grants and loans in real time\n\n"
            "Give you a fund readiness plan (what to do to qualify for more)\n\n"
            "Walk you through applications step by step\n\n"
            "Show you exactly which documents to gather\n\n"
            "Track your applications\n\n"
            "Commands:\n"
            "*opportunities* - see your matches\n"
            "*find new* - search for latest opportunities\n"
            "*readiness plan* - get your fund readiness assessment\n"
            "*my applications* - track what you've applied for\n"
            "*documents 1* - document checklist for opportunity 1\n"
            "*reset* - start over\n"
            "*switch to Yoruba* - change language anytime"
        ),
        "pcm": (
            "Na wetin BizPadi fit do for you:\n\n"
            "Find funding wey match your business\n\n"
            "Search for latest grants and loans for real\n\n"
            "Give you plan on how to qualify for more funding\n\n"
            "Show you document wey you need\n\n"
            "Track your applications\n\n"
            "Commands:\n"
            "*opportunities* - see your matches\n"
            "*find new* - search latest opportunities\n"
            "*my applications* - check wetin you apply for\n"
            "*reset* - start again\n"
            "*switch to English* - change language"
        ),
    }
    return menus.get(lang, menus["en"])


# ─────────────────────────────────────────────────────────────────────────────
# ONBOARDING
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_onboarding(profile: SMEProfile, user_text: str) -> str:
    history = await format_history_for_llm(profile.phone_number)
    response = await chat_with_sme(history, user_text, profile.language)
    if not response:
        return "Having a small issue. Try again in a moment."

    # Extract profile silently from conversation
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


# ─────────────────────────────────────────────────────────────────────────────
# CONFIRMATION
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_confirmation(profile: SMEProfile, user_text: str) -> str:
    lower = user_text.lower().strip()

    if any(lower == p or lower.startswith(p) for p in CONFIRMATION_PROMPTS):
        profile.state = UserState.PROFILED
        await upsert_profile(profile)

        # Use AI matching with bracket scores
        profile_summary = profile.to_summary()
        opportunities_text = get_opportunities_text()
        ai_match = await match_with_explanation(profile_summary, opportunities_text, profile.language)

        if ai_match:
            return ai_match

        # Fallback to keyword matching
        matches = get_matched_opportunities(profile)
        return format_opportunities_for_whatsapp(matches)

    # User wants to correct something
    history = await format_history_for_llm(profile.phone_number)
    response = await chat_with_sme(history, user_text, profile.language)
    full_history = history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response or ""},
    ]
    extracted = await extract_profile_data(full_history)
    if extracted:
        updated = await update_profile_fields(profile.phone_number, extracted)
        if updated:
            return updated.to_confirmation_message()

    return response or "What would you like to change?"


# ─────────────────────────────────────────────────────────────────────────────
# PROFILED / SUPPORT
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_profiled_or_support(profile: SMEProfile, user_text: str) -> str:
    lower = user_text.lower().strip()
    lang = profile.language

    # Show current matches
    if any(kw in lower for kw in ["opportunities", "funding", "grants", "loans", "show me"]) and len(user_text) < 40:
        profile_summary = profile.to_summary()
        opportunities_text = get_opportunities_text()
        ai_match = await match_with_explanation(profile_summary, opportunities_text, lang)
        if ai_match:
            return ai_match
        matches = get_matched_opportunities(profile)
        return format_opportunities_for_whatsapp(matches)

    # Web search
    if should_search_web(user_text):
        return await _handle_live_search(profile, user_text)

    history = await format_history_for_llm(profile.phone_number)
    return await chat_with_sme(history, user_text, lang) or "Having a small issue. Try again in a moment."


# ─────────────────────────────────────────────────────────────────────────────
# LIVE SEARCH
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_live_search(profile: SMEProfile, user_text: str = "") -> str:
    lang = profile.language
    lang_name = LANGUAGE_NAMES.get(lang, "English")

    # Build preamble in user's language
    preambles = {
        "en": "Searching for the latest funding opportunities for you right now...\n\n",
        "yo": "Mo n wa awon anfaani igbeowosile titun fun yin ni bayi...\n\n",
        "ha": "Ina neman damammaki na kudin tallafi a yanzu...\n\n",
        "pcm": "I dey find latest funding opportunities for you now now...\n\n",
        "fr": "Je recherche les dernières opportunités de financement pour vous maintenant...\n\n",
    }

    profile_summary = profile.to_summary() if profile.business_name else (
        f"Nigerian SME looking for funding. Query: {user_text}"
    )

    result = await get_live_opportunities(profile_summary, lang)

    if result:
        return preambles.get(lang, "") + result

    return (
        "I had trouble connecting to search right now. "
        "Here are your saved matches instead:\n\n"
        + format_opportunities_for_whatsapp(get_matched_opportunities(profile))
    )


# ─────────────────────────────────────────────────────────────────────────────
# FUND READINESS CONSULTANT
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_readiness_plan(profile: SMEProfile) -> str:
    lang = profile.language

    if not profile.business_name:
        prompts = {
            "en": "Tell me about your business first, then I can give you a personalised fund readiness plan.",
            "pcm": "First tell me about your business, then I go give you the plan wey you need.",
            "yo": "Je ki n gbo nipa ise re ni kete, ki n le fun yin ni eto igbeowosile to dara.",
            "ha": "Fara mini game da kasuwancinka, sai in ba ka tsarin kudin tallafi.",
            "fr": "Parlez-moi d'abord de votre entreprise, puis je vous donnerai un plan personnalisé.",
        }
        return prompts.get(lang, prompts["en"])

    profile_summary = profile.to_summary()
    plan = await get_fund_readiness_plan(profile_summary, lang)

    if plan:
        return plan

    return "Having trouble right now. Try asking: what do I need to qualify for more funding?"


# ─────────────────────────────────────────────────────────────────────────────
# OPPORTUNITY SELECTION + DOCUMENTS
# ─────────────────────────────────────────────────────────────────────────────

def _is_opportunity_selection(text: str, profile: SMEProfile) -> bool:
    return (
        text.strip().isdigit()
        and 1 <= int(text.strip()) <= 10
        and profile.state in (UserState.PROFILED, UserState.SUPPORT, UserState.CONFIRMING)
    )


async def _handle_opportunity_selection(profile: SMEProfile, user_text: str) -> str:
    index = int(user_text.strip())
    matches = get_matched_opportunities(profile)

    if index < 1 or index > len(matches):
        return "That number doesn't match anything. Reply with a number from the list."

    match = matches[index - 1]
    opp = match["opportunity"]
    score = match["score"]
    already_applied = match.get("already_applied", False)

    docs = opp.get("required_documents", [])
    doc_list = "\n".join(f"{i}. {d}" for i, d in enumerate(docs, 1))
    steps = "\n\n".join(f"{i}. {s}" for i, s in enumerate(opp["application_steps"], 1))

    response = (
        f"*{opp['name']}* ({score}% match)\n\n"
        f"{opp['description'][:350]}\n\n"
        f"Amount: {opp['amount']}\n\n"
        f"Deadline: {opp['deadline']}\n\n"
        f"CAC required: {'Yes' if opp['requires_cac'] else 'No'}\n\n"
        f"*Documents to gather:*\n{doc_list}\n\n"
        f"*How to apply:*\n\n{steps}\n\n"
        f"Link: {opp['application_link']}\n\n"
    )

    if already_applied:
        response += "You already applied for this one. Want me to check the status?"
    else:
        response += (
            "Once you have all your documents ready, reply *applied* and I'll track it.\n\n"
            "Need help getting any of these documents? Just ask."
        )

    profile.state = UserState.SUPPORT
    await upsert_profile(profile)
    await save_message(profile.phone_number, "system", f"[VIEWED_OPPORTUNITY:{opp['id']}:{opp['name']}]")
    return response


async def _handle_document_request(profile: SMEProfile, user_text: str) -> str:
    parts = user_text.split()
    num = next((int(p) for p in parts if p.isdigit()), None)

    if num:
        matches = get_matched_opportunities(profile)
        if 1 <= num <= len(matches):
            opp = matches[num - 1]["opportunity"]
            docs = opp.get("required_documents", [])
            doc_list = "\n".join(f"{i}. {d}" for i, d in enumerate(docs, 1))
            return (
                f"*Documents for {opp['name']}:*\n\n{doc_list}\n\n"
                f"Which ones do you already have? I'll help you get the rest."
            )

    return "Which opportunity? Type the number from the list, like: *documents 1*"


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION TRACKING
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_application_confirmation(profile: SMEProfile) -> str:
    from app.services.database import get_conversation_history
    history = await get_conversation_history(profile.phone_number, limit=30)

    last_opp_id = last_opp_name = None
    for msg in reversed(history):
        content = msg.get("content", "")
        if content.startswith("[VIEWED_OPPORTUNITY:"):
            parts = content.replace("[VIEWED_OPPORTUNITY:", "").replace("]", "").split(":", 1)
            if len(parts) == 2:
                last_opp_id, last_opp_name = parts
                break

    if last_opp_id and last_opp_name:
        await track_application(profile.phone_number, last_opp_id, last_opp_name)
        msgs = {
            "en": f"Logged your application for *{last_opp_name}*. I'll remind you as the deadline approaches.\n\nType *my applications* to see your tracker.",
            "pcm": f"I don log your application for *{last_opp_name}*. I go remind you before deadline.\n\nType *my applications* to check.",
            "yo": f"Mo ti forukosile ohun elo re fun *{last_opp_name}*. Emi yoo ran yin leto saju ipari akoko.",
            "ha": f"Na yi rajistar aikacenku na *{last_opp_name}*. Zan tunatar maka kafin lokaci ya kare.",
            "fr": f"Votre candidature pour *{last_opp_name}* est enregistrée. Je vous rappellerai avant la date limite.",
        }
        return msgs.get(profile.language, msgs["en"])

    return "Which opportunity did you apply for? Tell me the name and I'll track it."


async def _handle_application_status(profile: SMEProfile) -> str:
    apps = await get_applications(profile.phone_number)
    if not apps:
        msgs = {
            "en": "No tracked applications yet. After you apply for something, reply *applied* and I'll log it.\n\nType *opportunities* to see your matches.",
            "pcm": "You never track any application yet. When you apply, say *applied* make I log am.\n\nType *opportunities* to see your matches.",
        }
        return msgs.get(profile.language, msgs["en"])

    emojis = {"applied": "📤", "pending": "⏳", "approved": "✅", "rejected": "❌"}
    lines = ["*Your Applications:*\n"]
    for app in apps[:10]:
        emoji = emojis.get(app.get("status", "applied"), "📤")
        lines.append(f"{emoji} *{app.get('opportunity_name', 'Unknown')}*")
        lines.append(f"Status: {app.get('status', 'applied').capitalize()}\n")
    lines.append("To update: *approved [name]* or *rejected [name]*")
    return "\n".join(lines)
