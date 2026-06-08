# BizPadi build: 2026-06-07 smart-memory
import logging
from pathlib import Path
from typing import Optional

from app.models.schemas import SMEProfile, UserState
from app.services.database import (
    get_profile, upsert_profile, update_profile_fields,
    save_message, format_history_for_llm,
    track_application, get_applications,
    save_doc_session, load_doc_session, clear_doc_session,
)
from app.services.llm import (
    chat_with_sme,
    extract_profile_data,
    extract_profile_update,
    message_has_business_info,
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
from app.services.document_flow import (
    get_next_unchecked_document, build_document_question,
    build_how_to_get, build_readiness_summary,
    set_document_status, calculate_readiness_score,
    OPPORTUNITY_DOCUMENTS,
)
from app.core.prompts import (
    LANGUAGE_MENU, LANGUAGE_CONFIRMATIONS, LANGUAGE_SWITCH_MESSAGES,
)
from data.opportunities import get_opportunities_text, FUNDING_OPPORTUNITIES

logger = logging.getLogger(__name__)

MENU_LANGUAGE_MAP = {"1": "en", "2": "yo", "3": "ha", "4": "pcm", "5": "fr"}

CONFIRMATION_PROMPTS = {
    "yes", "correct", "yeah", "yep", "yh", "y", "sure", "right",
    "true", "ok", "okay", "confirmed",
}

APPLICATION_CONFIRMATIONS = {
    "applied", "i applied", "done", "submitted",
    "i have applied", "i submitted", "i've applied",
}

YES_WORDS = {"yes", "yep", "yeah", "yh", "y", "sure", "i have", "i do",
             "got it", "i got", "have it", "beeni", "eh", "oui", "si"}
NO_WORDS = {"no", "nope", "nah", "don't", "dont", "i don't", "i dont",
            "rara", "a'a", "non"}

_doc_flow_sessions: dict[str, dict] = {}


async def _get_doc_session(phone: str) -> dict:
    if phone in _doc_flow_sessions:
        return _doc_flow_sessions[phone]
    session = await load_doc_session(phone)
    if session:
        _doc_flow_sessions[phone] = session
    return session


async def _set_doc_session(phone: str, session: dict):
    _doc_flow_sessions[phone] = session
    await save_doc_session(phone, session)


async def _del_doc_session(phone: str):
    _doc_flow_sessions.pop(phone, None)
    await clear_doc_session(phone)


async def handle_incoming_message(
    phone_number: str,
    body: Optional[str] = None,
    media_url: Optional[str] = None,
    num_media: int = 0,
    media_content_type: str = "audio/ogg",
) -> dict:
    user_text = body or ""
    is_voice = num_media > 0 and media_url

    if is_voice:
        audio_bytes = await download_twilio_media(media_url)
        if not audio_bytes:
            return {"text_response": "Had trouble receiving your voice note. Try again or type it.", "audio_path": None}
        hint_lang = await detect_language_llm(body) if body else "en"
        transcript = await aethex.transcribe_audio(audio_bytes, media_content_type, hint_lang)
        if not transcript:
            return {"text_response": "Got your voice note but couldn't make it out. Try again or type it!", "audio_path": None}
        user_text = transcript
        logger.info(f"Transcribed: {transcript[:80]}")

    if not user_text.strip():
        return {"text_response": "Didn't catch that. Send me a message!", "audio_path": None}

    profile = await get_profile(phone_number)
    is_new_user = profile is None

    if is_new_user:
        profile = SMEProfile(phone_number=phone_number, state=UserState.LANGUAGE_SELECT, language="en")
        await upsert_profile(profile)
        await save_message(phone_number, "assistant", LANGUAGE_MENU)
        return {"text_response": LANGUAGE_MENU, "audio_path": None}

    # Language switch detection
    new_lang = detect_language_switch(user_text)
    if new_lang and new_lang != profile.language:
        profile.language = new_lang
        await upsert_profile(profile)
        msg = LANGUAGE_SWITCH_MESSAGES.get(new_lang, f"Switched to {LANGUAGE_NAMES.get(new_lang)}.")
        await save_message(phone_number, "user", user_text)
        await save_message(phone_number, "assistant", msg)
        return {"text_response": msg, "audio_path": None}

    # Activation phrase
    if user_text.lower().strip() in ("join industry-plain", "join industry plain"):
        msg = LANGUAGE_MENU if profile.state == UserState.LANGUAGE_SELECT else (
            "You are connected to BizPadi!\\n\\nType *menu* to see what I can do, or just tell me about your business."
        )
        await save_message(phone_number, "assistant", msg)
        return {"text_response": msg, "audio_path": None}

    await save_message(phone_number, "user", user_text)

    # Smart profile update: only during onboarding, only on substantive messages.
    # If this runs, we flag it so _handle_onboarding skips the redundant
    # extract_profile_data call (avoids 3 Groq calls -> 2 Groq calls per message).
    _smart_updated = False
    if (profile.state == UserState.ONBOARDING
            and len(user_text) > 30
            and message_has_business_info(user_text)):
        extracted = await extract_profile_update(user_text, profile.to_summary())
        if extracted:
            updated = await update_profile_fields(phone_number, extracted)
            if updated:
                profile = updated
                _smart_updated = True
                logger.info(f"Smart profile update: {extracted}")

    response = await _process(profile, user_text, smart_updated=_smart_updated)
    await save_message(phone_number, "assistant", response)
    return {"text_response": response, "audio_path": None}


async def _process(profile: SMEProfile, user_text: str, smart_updated: bool = False) -> str:
    lower = user_text.lower().strip()
    lang = profile.language

    if profile.state == UserState.LANGUAGE_SELECT:
        return await _handle_language_selection(profile, user_text)

    # Document flow
    session = await _get_doc_session(profile.phone_number)
    if session:
        if any(w in lower for w in YES_WORDS):
            return await _handle_doc_yes(profile, session)
        elif any(w in lower for w in NO_WORDS):
            return await _handle_doc_no(profile, session)
        elif lower in ("stop", "quit", "exit", "done", "finish"):
            await _del_doc_session(profile.phone_number)
            return build_readiness_summary(profile.phone_number, session["opp_id"], session["opp_name"], lang)
        else:
            history = await format_history_for_llm(profile.phone_number)
            response = await chat_with_sme(history, user_text, lang)
            resume = f"\n\nWhen ready, let's continue. {build_document_question(session['current_doc'], lang)}"
            return (response or "No wahala.") + resume

    # Global commands
    if lower in ("reset", "start over", "restart"):
        return await _handle_reset(profile)
    if lower in ("help", "menu"):
        return _help_menu(lang)
    if lower in ("my applications", "applications", "track", "my apps"):
        return await _handle_applications(profile)
    if lower.startswith("documents") or lower.startswith("docs "):
        return await _handle_document_request(profile, user_text)
    if lower in ("readiness plan", "fund readiness", "readiness"):
        return await _handle_readiness_plan(profile)
    if lower in ("find new", "search", "latest opportunities", "new opportunities"):
        return await _handle_live_search(profile, user_text)

    if user_text.strip().isdigit() and profile.state in (UserState.PROFILED, UserState.SUPPORT, UserState.CONFIRMING):
        num = int(user_text.strip())
        if 1 <= num <= 10:
            return await _handle_opportunity_selection(profile, num)

    if any(lower == p for p in APPLICATION_CONFIRMATIONS):
        return await _handle_application_confirmation(profile)

    if should_get_readiness_plan(user_text):
        return await _handle_readiness_plan(profile)
    if should_search_web(user_text):
        return await _handle_live_search(profile, user_text)

    if profile.state == UserState.ONBOARDING:
        return await _handle_onboarding(profile, user_text, smart_updated=smart_updated)
    elif profile.state == UserState.CONFIRMING:
        return await _handle_confirmation(profile, user_text)
    elif profile.state in (UserState.PROFILED, UserState.SUPPORT):
        return await _handle_profiled(profile, user_text)
    else:
        return await _handle_onboarding(profile, user_text, smart_updated=smart_updated)


async def _handle_language_selection(profile: SMEProfile, user_text: str) -> str:
    lower = user_text.strip().lower()
    selected = MENU_LANGUAGE_MAP.get(lower.strip())
    if not selected:
        text_map = {"english": "en", "yoruba": "yo", "hausa": "ha",
                    "pidgin": "pcm", "french": "fr", "français": "fr"}
        for kw, code in text_map.items():
            if kw in lower:
                selected = code
                break
    if selected:
        profile.language = selected
        profile.state = UserState.ONBOARDING
        await upsert_profile(profile)
        return LANGUAGE_CONFIRMATIONS.get(selected, LANGUAGE_CONFIRMATIONS["en"])
    return f"Please reply with a number:\n\n{LANGUAGE_MENU}"


async def _handle_reset(profile: SMEProfile) -> str:
    profile.state = UserState.LANGUAGE_SELECT
    for f in ["business_name", "business_type", "location_city", "location_state",
              "business_stage", "monthly_revenue", "employee_count",
              "cac_registered", "biggest_challenge", "owner_name"]:
        setattr(profile, f, None)
    await upsert_profile(profile)
    await _del_doc_session(profile.phone_number)
    return f"Fresh start.\n\n{LANGUAGE_MENU}"


def _help_menu(lang: str) -> str:
    menus = {
        "en": (
            "*BizPadi can help you with:*\n\n"
            "Find funding that matches your business\n\n"
            "Walk you through applying step by step\n\n"
            "Check which documents you have and help you get the missing ones\n\n"
            "Search for the latest grants and loans in real time\n\n"
            "Give you a personalised fund readiness plan\n\n"
            "Track your applications with deadlines\n\n"
            "Explain CAC, BVN, TIN, bank statements and anything Nigerian business\n\n"
            "*Commands:*\n"
            "*opportunities* - see your matches\n"
            "*find new* - search latest opportunities live\n"
            "*readiness plan* - get your fund readiness assessment\n"
            "*my applications* - track what you've applied for\n"
            "*documents 1* - document checklist for opportunity 1\n"
            "*reset* - start over\n"
            "*switch to Yoruba* - change language anytime"
        ),
        "pcm": (
            "*Wetin BizPadi fit do for you:*\n\n"
            "Find funding wey match your business\n\n"
            "Walk you through how to apply step by step\n\n"
            "Check your documents and help you get wetin you no get\n\n"
            "Search for latest grants and loans\n\n"
            "Give you plan on how to qualify for more\n\n"
            "Track your applications\n\n"
            "Explain CAC, BVN, TIN, bank statement - anything about Nigeria business\n\n"
            "*Commands:*\n"
            "*opportunities* - see your matches\n"
            "*find new* - search latest\n"
            "*my applications* - check wetin you apply\n"
            "*reset* - start again\n"
            "*switch to English* - change language"
        ),
    }
    return menus.get(lang, menus["en"])


async def _handle_onboarding(profile: SMEProfile, user_text: str, smart_updated: bool = False) -> str:
    history = await format_history_for_llm(profile.phone_number)
    response = await chat_with_sme(history, user_text, profile.language)
    if not response:
        return "Having a small issue. Try again in a moment."

    # If smart_updated already ran extract_profile_update this turn, skip the
    # redundant extract_profile_data call to avoid burning Groq rate limit budget.
    if not smart_updated:
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
    else:
        # smart_update already ran - just check if profile is now complete
        fresh = await upsert_profile(profile)  # re-read via upsert to get latest
        if fresh and fresh.is_profile_complete():
            fresh.state = UserState.CONFIRMING
            await upsert_profile(fresh)
            return fresh.to_confirmation_message()

    return response


async def _handle_confirmation(profile: SMEProfile, user_text: str) -> str:
    lower = user_text.lower().strip()
    lang = profile.language

    if any(lower == p or lower.startswith(p) for p in CONFIRMATION_PROMPTS):
        profile.state = UserState.PROFILED
        await upsert_profile(profile)
        result = await match_with_explanation(profile.to_summary(), get_opportunities_text(), lang)
        if result:
            return result
        matches = get_matched_opportunities(profile)
        return format_opportunities_for_whatsapp(matches)

    history = await format_history_for_llm(profile.phone_number)
    response = await chat_with_sme(history, user_text, lang)
    extracted = await extract_profile_data(history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response or ""},
    ])
    if extracted:
        updated = await update_profile_fields(profile.phone_number, extracted)
        if updated:
            return updated.to_confirmation_message()
    return response or "What would you like to change?"


async def _handle_profiled(profile: SMEProfile, user_text: str) -> str:
    lower = user_text.lower().strip()
    lang = profile.language

    if any(kw in lower for kw in ["opportunities", "funding", "grants", "loans", "show me", "matches"]) and len(user_text) < 40:
        result = await match_with_explanation(profile.to_summary(), get_opportunities_text(), lang)
        if result:
            return result
        return format_opportunities_for_whatsapp(get_matched_opportunities(profile))

    history = await format_history_for_llm(profile.phone_number)
    return await chat_with_sme(history, user_text, lang) or "Having a small issue. Try again in a moment."


async def _handle_live_search(profile: SMEProfile, user_text: str = "") -> str:
    lang = profile.language
    preambles = {
        "en": "Searching for the latest funding opportunities for you right now...\n\n",
        "pcm": "I dey find latest funding opportunities for you now now...\n\n",
        "fr": "Je recherche les dernières opportunités pour vous maintenant...\n\n",
    }
    profile_summary = profile.to_summary() if profile.business_name else f"Nigerian SME. Query: {user_text}"
    result = await get_live_opportunities(profile_summary, lang)
    if result:
        return preambles.get(lang, "") + result
    return (
        "Had trouble searching right now. Here are your saved matches instead:\n\n"
        + format_opportunities_for_whatsapp(get_matched_opportunities(profile))
    )


async def _handle_readiness_plan(profile: SMEProfile) -> str:
    lang = profile.language
    if not profile.business_name:
        msgs = {
            "en": "Tell me about your business first, then I can give you a personalised fund readiness plan.",
            "pcm": "First tell me about your business, then I go give you the plan.",
            "fr": "Parlez-moi d'abord de votre entreprise.",
        }
        return msgs.get(lang, msgs["en"])
    plan = await get_fund_readiness_plan(profile.to_summary(), lang)
    return plan or "Having trouble right now. Try asking: what do I need to qualify for more funding?"


async def _start_document_flow(profile: SMEProfile, opp_id: str, opp_name: str) -> str:
    lang = profile.language
    next_doc = get_next_unchecked_document(profile.phone_number, opp_id)
    if not next_doc:
        return build_readiness_summary(profile.phone_number, opp_id, opp_name, lang)

    await _set_doc_session(profile.phone_number, {
        "opp_id": opp_id, "opp_name": opp_name, "current_doc": next_doc,
    })

    intros = {
        "en": f"Let me help you get ready to apply for *{opp_name}*.\n\nI will go through the required documents with you one by one. Just reply yes or no for each one.\n\n",
        "pcm": f"Make I help you prepare to apply for *{opp_name}*.\n\nI go go through the documents with you one by one. Just say yes or no for each.\n\n",
        "fr": f"Laissez-moi vous aider à vous préparer pour *{opp_name}*.\n\nNous allons passer en revue les documents un par un. Répondez oui ou non pour chacun.\n\n",
    }
    return intros.get(lang, intros["en"]) + build_document_question(next_doc, lang)


async def _handle_doc_yes(profile: SMEProfile, session: dict) -> str:
    lang = profile.language
    opp_id = session["opp_id"]
    current = session["current_doc"]
    set_document_status(profile.phone_number, opp_id, current, True)
    affirmations = {"en": "Got it.", "pcm": "Okay na.", "yo": "O dara.", "ha": "To dai.", "fr": "Parfait."}
    affirmation = affirmations.get(lang, "Got it.")
    next_doc = get_next_unchecked_document(profile.phone_number, opp_id)
    if next_doc:
        session["current_doc"] = next_doc
        await _set_doc_session(profile.phone_number, session)
        return f"{affirmation} {build_document_question(next_doc, lang)}"
    else:
        await _del_doc_session(profile.phone_number)
        return build_readiness_summary(profile.phone_number, opp_id, session["opp_name"], lang)


async def _handle_doc_no(profile: SMEProfile, session: dict) -> str:
    lang = profile.language
    opp_id = session["opp_id"]
    current = session["current_doc"]
    set_document_status(profile.phone_number, opp_id, current, False)
    instructions = build_how_to_get(current, lang)
    next_doc = get_next_unchecked_document(profile.phone_number, opp_id)
    if next_doc:
        session["current_doc"] = next_doc
        await _set_doc_session(profile.phone_number, session)
        continues = {
            "en": "\n\nWhen you have it, come back. Or reply *skip* to continue to the next document now.",
            "pcm": "\n\nWhen you get am, come back. Or say *skip* to continue to the next one.",
            "fr": "\n\nQuand vous l'avez, revenez. Ou dites *passer* pour continuer.",
        }
        return instructions + continues.get(lang, continues["en"])
    else:
        await _del_doc_session(profile.phone_number)
        return instructions + "\n\n" + build_readiness_summary(profile.phone_number, opp_id, session["opp_name"], lang)


async def _handle_opportunity_selection(profile: SMEProfile, index: int) -> str:
    matches = get_matched_opportunities(profile)
    if index < 1 or index > len(matches):
        return "That number doesn't match anything. Reply with a number from the list."
    match = matches[index - 1]
    opp = match["opportunity"]
    score = match["score"]
    lang = profile.language
    readiness_score, _ = calculate_readiness_score(profile.phone_number, opp["id"])
    readiness_tag = f" - {readiness_score}% ready to apply" if readiness_score > 0 else ""
    docs = opp.get("required_documents", [])
    doc_list = "\n".join(f"{i}. {d}" for i, d in enumerate(docs, 1))
    steps = "\n\n".join(f"{i}. {s}" for i, s in enumerate(opp["application_steps"], 1))
    response = (
        f"*{opp['name']}* ({score}% match{readiness_tag})\n\n"
        f"{opp['description'][:350]}\n\n"
        f"Amount: {opp['amount']}\n\n"
        f"Deadline: {opp['deadline']}\n\n"
        f"CAC required: {'Yes' if opp['requires_cac'] else 'No'}\n\n"
        f"*Documents needed:*\n{doc_list}\n\n"
        f"*How to apply:*\n\n{steps}\n\n"
        f"Link: {opp['application_link']}\n\n"
    )
    check_offers = {
        "en": "Want me to check which of these documents you already have? Reply *check documents*.",
        "pcm": "You wan make I check which documents you get? Say *check documents*.",
        "fr": "Voulez-vous que je vérifie quels documents vous avez? Dites *vérifier documents*.",
    }
    response += check_offers.get(lang, check_offers["en"])
    profile.state = UserState.SUPPORT
    await upsert_profile(profile)
    await save_message(profile.phone_number, "system", f"[VIEWED_OPPORTUNITY:{opp['id']}:{opp['name']}]")
    return response


async def _handle_document_request(profile: SMEProfile, user_text: str) -> str:
    lower = user_text.lower().strip()
    if "check document" in lower or "verify document" in lower or "vérifier document" in lower:
        from app.services.database import get_conversation_history
        history = await get_conversation_history(profile.phone_number, limit=30)
        for msg in reversed(history):
            content = msg.get("content", "")
            if content.startswith("[VIEWED_OPPORTUNITY:"):
                parts = content.replace("[VIEWED_OPPORTUNITY:", "").replace("]", "").split(":", 1)
                if len(parts) == 2:
                    return await _start_document_flow(profile, parts[0], parts[1])
        return "Which opportunity? First select a number from your matches list, then say *check documents*."
    parts = user_text.split()
    num = next((int(p) for p in parts if p.isdigit()), None)
    if num:
        matches = get_matched_opportunities(profile)
        if 1 <= num <= len(matches):
            opp = matches[num - 1]["opportunity"]
            return await _start_document_flow(profile, opp["id"], opp["name"])
    return "Which opportunity? Type the number, like: *documents 1*"


async def _handle_application_confirmation(profile: SMEProfile) -> str:
    from app.services.database import get_conversation_history
    history = await get_conversation_history(profile.phone_number, limit=30)
    for msg in reversed(history):
        content = msg.get("content", "")
        if content.startswith("[VIEWED_OPPORTUNITY:"):
            parts = content.replace("[VIEWED_OPPORTUNITY:", "").replace("]", "").split(":", 1)
            if len(parts) == 2:
                opp_id, opp_name = parts
                await track_application(profile.phone_number, opp_id, opp_name)
                msgs = {
                    "en": f"Logged your application for *{opp_name}*. I will remind you as the deadline approaches.\n\nType *my applications* to see your tracker.",
                    "pcm": f"I don log your application for *{opp_name}*. I go remind you before deadline.\n\nType *my applications* to check.",
                    "fr": f"Candidature pour *{opp_name}* enregistrée. Je vous rappellerai avant la date limite.",
                }
                return msgs.get(profile.language, msgs["en"])
    return "Which opportunity did you apply for? Tell me the name and I will track it."


async def _handle_applications(profile: SMEProfile) -> str:
    apps = await get_applications(profile.phone_number)
    lang = profile.language
    if not apps:
        msgs = {
            "en": "No tracked applications yet.\n\nAfter you apply, reply *applied* and I'll log it.\n\nType *opportunities* to see your matches.",
            "pcm": "You never track any application yet.\n\nWhen you apply, say *applied* and I go log am.\n\nType *opportunities* to see your matches.",
        }
        return msgs.get(lang, msgs["en"])
    emojis = {"applied": "📤", "pending": "⏳", "approved": "✅", "rejected": "❌"}
    lines = ["*Your Applications:*\n"]
    for app in apps[:10]:
        emoji = emojis.get(app.get("status", "applied"), "📤")
        name = app.get("opportunity_name", "Unknown")
        status = app.get("status", "applied").capitalize()
        opp = next((o for o in FUNDING_OPPORTUNITIES if o["id"] == app.get("opportunity_id", "")), None)
        deadline_info = f"\n   Deadline: {opp['deadline']}" if opp else ""
        lines.append(f"{emoji} *{name}*")
        lines.append(f"   Status: {status}{deadline_info}\n")
    lines.append("To update: *approved [name]* or *rejected [name]*")
    return "\n".join(lines)
