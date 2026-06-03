import time
import logging

from fastapi import APIRouter

from app.core.config import settings
from app.services.database import get_profile, get_conversation_history, get_db_status, get_pool
from app.services.matching import get_matched_opportunities
from app.services.llm import get_groq_status, ping_groq
from app.models.schemas import SMEProfile
from data.opportunities import FUNDING_OPPORTUNITIES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "tonative-sme-bot",
        "version": "2.0.0",
        "integrations": {
            "groq": settings.groq_enabled,
            "postgres": bool(settings.DATABASE_URL),
            "tonative": settings.tonative_enabled,
            "elevenlabs": settings.elevenlabs_enabled,
            "twilio": bool(settings.TWILIO_ACCOUNT_SID),
        },
    }


@router.get("/status")
async def live_status():
    """Live status dashboard. Pings each service."""
    results = {}

    # --- Groq ---
    groq_result = await ping_groq()
    results["groq"] = {
        "configured": settings.groq_enabled,
        "reachable": groq_result["ok"],
        "latency_ms": groq_result["latency_ms"],
        "error": groq_result["error"],
    }

    # --- PostgreSQL ---
    db_latency = 0
    db_reachable = False
    db_error = None

    if settings.DATABASE_URL:
        try:
            start = time.monotonic()
            pool = await get_pool()
            if pool:
                async with pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                db_latency = int((time.monotonic() - start) * 1000)
                db_reachable = True
        except Exception as e:
            db_error = str(e)
    else:
        db_reachable = True  # in-memory is always up

    results["database"] = {
        "configured": bool(settings.DATABASE_URL),
        "mode": "postgres" if settings.DATABASE_URL else "in-memory",
        "reachable": db_reachable,
        "latency_ms": db_latency,
        "error": db_error,
    }

    # --- Twilio ---
    twilio_reachable = False
    twilio_latency = 0
    twilio_error = None

    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        try:
            import httpx
            start = time.monotonic()
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}.json",
                    auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                )
                twilio_latency = int((time.monotonic() - start) * 1000)
                twilio_reachable = resp.status_code == 200
                if not twilio_reachable:
                    twilio_error = f"HTTP {resp.status_code}"
        except Exception as e:
            twilio_error = str(e)

    results["twilio"] = {
        "configured": bool(settings.TWILIO_ACCOUNT_SID),
        "reachable": twilio_reachable,
        "latency_ms": twilio_latency,
        "error": twilio_error,
    }

    # --- Tonative ---
    results["tonative"] = {
        "configured": settings.tonative_enabled,
        "fallback_active": not settings.tonative_enabled,
        "note": "Waiting for hackathon docs" if not settings.tonative_enabled else "Connected",
    }

    # --- ElevenLabs ---
    results["elevenlabs"] = {
        "configured": settings.elevenlabs_enabled,
        "note": "Optional for voice replies",
    }

    critical_ok = results["groq"]["reachable"] and results["database"]["reachable"]

    return {
        "status": "operational" if critical_ok else "degraded",
        "services": results,
        "data": {
            "opportunities_loaded": len(FUNDING_OPPORTUNITIES),
        },
    }


@router.get("/opportunities")
async def list_opportunities():
    return {"count": len(FUNDING_OPPORTUNITIES), "opportunities": FUNDING_OPPORTUNITIES}


@router.get("/profile/{phone_number}")
async def get_user_profile(phone_number: str):
    if not phone_number.startswith("whatsapp:"):
        phone_number = f"whatsapp:+{phone_number.lstrip('+')}"
    profile = await get_profile(phone_number)
    if not profile:
        return {"error": "Profile not found", "phone_number": phone_number}
    return profile.model_dump()


@router.get("/profile/{phone_number}/matches")
async def get_user_matches(phone_number: str):
    if not phone_number.startswith("whatsapp:"):
        phone_number = f"whatsapp:+{phone_number.lstrip('+')}"
    profile = await get_profile(phone_number)
    if not profile:
        return {"error": "Profile not found"}
    matches = get_matched_opportunities(profile)
    return {
        "profile": profile.to_summary(),
        "matches": [{"name": m["opportunity"]["name"], "score": m["score"]} for m in matches],
    }


@router.get("/history/{phone_number}")
async def get_user_history(phone_number: str):
    if not phone_number.startswith("whatsapp:"):
        phone_number = f"whatsapp:+{phone_number.lstrip('+')}"
    history = await get_conversation_history(phone_number)
    return {"phone_number": phone_number, "messages": history}


@router.get("/applications/{phone_number}")
async def get_user_applications(phone_number: str):
    """Get application tracking for a user."""
    if not phone_number.startswith("whatsapp:"):
        phone_number = f"whatsapp:+{phone_number.lstrip('+')}"
    from app.services.database import get_applications
    apps = await get_applications(phone_number)
    return {"phone_number": phone_number, "applications": apps}


@router.post("/reminders/send-deadline-alerts")
async def trigger_deadline_reminders():
    """Trigger deadline reminders for all active applications. Call from cron."""
    from app.services.reminders import send_deadline_reminders
    sent = await send_deadline_reminders()
    return {"status": "ok", "reminders_sent": sent}


@router.post("/reminders/send-weekly-digest")
async def trigger_weekly_digest():
    """Send weekly opportunity digest to all profiled users. Call from cron."""
    from app.services.reminders import send_new_opportunity_alerts
    sent = await send_new_opportunity_alerts()
    return {"status": "ok", "notifications_sent": sent}


@router.get("/api/aethex/status")
async def aethex_status():
    """Check AethexAI API health — TTS + transcription."""
    from app.services.aethex import ping_aethex, get_aethex_status
    ping_result = await ping_aethex()
    current = get_aethex_status()
    return {
        "aethex_enabled": settings.aethex_enabled,
        "ping": ping_result,
        "last_transcription": current["transcription"],
        "last_tts": current["tts"],
    }
