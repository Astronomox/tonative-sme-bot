# BizPadi build: 2026-06-06 22:17:17
import logging
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings
from app.models.schemas import SMEProfile, UserState, ApplicationTracking

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory fallback
# ---------------------------------------------------------------------------
_memory_profiles: dict[str, dict] = {}
_memory_conversations: dict[str, list[dict]] = {}
_memory_applications: dict[str, list[dict]] = {}  # phone -> list of tracking records


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Connection pool (asyncpg)
# ---------------------------------------------------------------------------
_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        if not settings.database_url:
            return None
        try:
            import asyncpg
            _pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=1,
                max_size=5,
                command_timeout=10,
            )
            logger.info("PostgreSQL pool created")
        except Exception as e:
            logger.warning(f"PostgreSQL pool failed, using in-memory: {e}")
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def get_db_status() -> dict:
    return {
        "mode": "postgres" if settings.database_url else "in-memory",
        "connected": _pool is not None,
        "url": settings.database_url[:40] + "..." if settings.database_url else None,
    }


# ---------------------------------------------------------------------------
# Schema (auto-created on first connect)
# ---------------------------------------------------------------------------
_schema_applied = False


async def _ensure_schema():
    global _schema_applied
    if _schema_applied:
        return
    pool = await get_pool()
    if not pool:
        return
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sme_profiles (
                phone_number TEXT PRIMARY KEY,
                state TEXT NOT NULL DEFAULT 'onboarding',
                business_name TEXT,
                business_type TEXT,
                location_city TEXT,
                location_state TEXT,
                business_stage TEXT,
                monthly_revenue TEXT,
                employee_count INTEGER,
                cac_registered BOOLEAN,
                biggest_challenge TEXT,
                language TEXT DEFAULT 'en',
                applied_opportunities TEXT[] DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id BIGSERIAL PRIMARY KEY,
                phone_number TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS application_tracking (
                id BIGSERIAL PRIMARY KEY,
                phone_number TEXT NOT NULL,
                opportunity_id TEXT NOT NULL,
                opportunity_name TEXT NOT NULL,
                status TEXT DEFAULT 'applied',
                applied_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                notes TEXT,
                UNIQUE(phone_number, opportunity_id)
            );

            CREATE INDEX IF NOT EXISTS idx_conversations_phone
                ON conversations (phone_number, created_at);

            CREATE INDEX IF NOT EXISTS idx_applications_phone
                ON application_tracking (phone_number);

            CREATE INDEX IF NOT EXISTS idx_applications_deadline
                ON application_tracking (opportunity_id, status);
        """)
    _schema_applied = True
    logger.info("Database schema ready")


# ===================================================================
# PROFILE OPERATIONS
# ===================================================================

async def get_profile(phone_number: str) -> Optional[SMEProfile]:
    pool = await get_pool()
    if pool:
        try:
            await _ensure_schema()
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM sme_profiles WHERE phone_number = $1",
                    phone_number,
                )
            if row:
                data = dict(row)
                data["applied_opportunities"] = list(data.get("applied_opportunities") or [])
                return SMEProfile(**data)
        except Exception as e:
            logger.warning(f"Postgres get_profile failed, trying memory: {e}")

    data = _memory_profiles.get(phone_number)
    return SMEProfile(**data) if data else None


async def upsert_profile(profile: SMEProfile) -> SMEProfile:
    profile.updated_at = _now()
    if not profile.created_at:
        profile.created_at = _now()

    data = profile.model_dump()
    data["state"] = profile.state.value
    _memory_profiles[profile.phone_number] = data

    pool = await get_pool()
    if pool:
        try:
            await _ensure_schema()
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO sme_profiles (
                        phone_number, state, business_name, business_type,
                        location_city, location_state, business_stage,
                        monthly_revenue, employee_count, cac_registered,
                        biggest_challenge, language, applied_opportunities,
                        created_at, updated_at
                    ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)
                    ON CONFLICT (phone_number) DO UPDATE SET
                        state = EXCLUDED.state,
                        business_name = EXCLUDED.business_name,
                        business_type = EXCLUDED.business_type,
                        location_city = EXCLUDED.location_city,
                        location_state = EXCLUDED.location_state,
                        business_stage = EXCLUDED.business_stage,
                        monthly_revenue = EXCLUDED.monthly_revenue,
                        employee_count = EXCLUDED.employee_count,
                        cac_registered = EXCLUDED.cac_registered,
                        biggest_challenge = EXCLUDED.biggest_challenge,
                        language = EXCLUDED.language,
                        applied_opportunities = EXCLUDED.applied_opportunities,
                        updated_at = EXCLUDED.updated_at
                """,
                    profile.phone_number, profile.state.value,
                    profile.business_name, profile.business_type,
                    profile.location_city, profile.location_state,
                    profile.business_stage, profile.monthly_revenue,
                    profile.employee_count, profile.cac_registered,
                    profile.biggest_challenge, profile.language,
                    profile.applied_opportunities,
                    profile.created_at, profile.updated_at,
                )
        except Exception as e:
            logger.warning(f"Postgres upsert_profile failed, memory only: {e}")

    return profile


async def update_profile_fields(phone_number: str, fields: dict) -> Optional[SMEProfile]:
    profile = await get_profile(phone_number)
    if not profile:
        profile = SMEProfile(phone_number=phone_number, state=UserState.ONBOARDING)

    for key, value in fields.items():
        if hasattr(profile, key) and value is not None:
            setattr(profile, key, value)

    return await upsert_profile(profile)


# ===================================================================
# CONVERSATION OPERATIONS
# ===================================================================

async def save_message(phone_number: str, role: str, content: str):
    msg = {"phone_number": phone_number, "role": role, "content": content, "created_at": _now()}

    pool = await get_pool()
    if pool:
        try:
            await _ensure_schema()
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO conversations (phone_number, role, content) VALUES ($1, $2, $3)",
                    phone_number, role, content,
                )
            return
        except Exception as e:
            logger.warning(f"Postgres save_message failed, saving to memory: {e}")

    if phone_number not in _memory_conversations:
        _memory_conversations[phone_number] = []
    _memory_conversations[phone_number].append(msg)


async def get_conversation_history(phone_number: str, limit: int = 20) -> list[dict]:
    pool = await get_pool()
    if pool:
        try:
            await _ensure_schema()
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """SELECT role, content, created_at FROM conversations
                       WHERE phone_number = $1
                       ORDER BY created_at ASC LIMIT $2""",
                    phone_number, limit,
                )
            if rows:
                return [dict(r) for r in rows]
        except Exception as e:
            logger.warning(f"Postgres get_history failed, trying memory: {e}")

    msgs = _memory_conversations.get(phone_number, [])
    return msgs[-limit:]


async def format_history_for_llm(
    phone_number: str,
    max_messages: int = 10,
    max_chars: int = 4000,
) -> list[dict]:
    history = await get_conversation_history(phone_number, limit=max_messages)
    formatted = []
    total_chars = 0

    for msg in reversed(history):
        content = msg["content"]
        if total_chars + len(content) > max_chars:
            break
        formatted.insert(0, {"role": msg["role"], "content": content})
        total_chars += len(content)

    return formatted


# ===================================================================
# APPLICATION TRACKING
# ===================================================================

async def track_application(
    phone_number: str,
    opportunity_id: str,
    opportunity_name: str,
    status: str = "applied",
    notes: str = None,
) -> ApplicationTracking:
    now = _now()
    tracking = ApplicationTracking(
        phone_number=phone_number,
        opportunity_id=opportunity_id,
        opportunity_name=opportunity_name,
        status=status,
        applied_at=now,
        updated_at=now,
        notes=notes,
    )

    # Save to memory
    if phone_number not in _memory_applications:
        _memory_applications[phone_number] = []

    # Update existing or append
    existing = [a for a in _memory_applications[phone_number] if a["opportunity_id"] == opportunity_id]
    if existing:
        existing[0]["status"] = status
        existing[0]["updated_at"] = now
        if notes:
            existing[0]["notes"] = notes
    else:
        _memory_applications[phone_number].append(tracking.model_dump())

    pool = await get_pool()
    if pool:
        try:
            await _ensure_schema()
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO application_tracking
                        (phone_number, opportunity_id, opportunity_name, status, applied_at, updated_at, notes)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (phone_number, opportunity_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        updated_at = EXCLUDED.updated_at,
                        notes = COALESCE(EXCLUDED.notes, application_tracking.notes)
                """,
                    phone_number, opportunity_id, opportunity_name,
                    status, now, now, notes,
                )
        except Exception as e:
            logger.warning(f"Postgres track_application failed: {e}")

    # Also update the profile's applied_opportunities list
    profile = await get_profile(phone_number)
    if profile and opportunity_id not in profile.applied_opportunities:
        profile.applied_opportunities.append(opportunity_id)
        await upsert_profile(profile)

    return tracking


async def get_applications(phone_number: str) -> list[dict]:
    pool = await get_pool()
    if pool:
        try:
            await _ensure_schema()
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """SELECT * FROM application_tracking
                       WHERE phone_number = $1
                       ORDER BY applied_at DESC""",
                    phone_number,
                )
            if rows:
                return [dict(r) for r in rows]
        except Exception as e:
            logger.warning(f"Postgres get_applications failed: {e}")

    return _memory_applications.get(phone_number, [])


async def update_application_status(
    phone_number: str,
    opportunity_id: str,
    status: str,
    notes: str = None,
):
    return await track_application(phone_number, opportunity_id, "", status, notes)


async def get_all_active_applications() -> list[dict]:
    """For deadline reminders   get all pending applications across all users."""
    pool = await get_pool()
    if pool:
        try:
            await _ensure_schema()
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """SELECT * FROM application_tracking
                       WHERE status IN ('applied', 'pending')
                       ORDER BY applied_at DESC"""
                )
            return [dict(r) for r in rows]
        except Exception as e:
            logger.warning(f"Postgres get_all_active_applications failed: {e}")

    # Flatten all in-memory applications
    all_apps = []
    for apps in _memory_applications.values():
        all_apps.extend([a for a in apps if a.get("status") in ("applied", "pending")])
    return all_apps


# ===================================================================
# DOCUMENT FLOW SESSION PERSISTENCE
# ===================================================================

async def save_doc_session(phone_number: str, session: dict):
    """Persist document flow session so it survives Render restarts."""
    import json
    await save_message(phone_number, "system", f"[DOC_SESSION:{json.dumps(session)}]")


async def load_doc_session(phone_number: str) -> dict:
    """Load the most recent document flow session for a user."""
    import json
    history = await get_conversation_history(phone_number, limit=30)
    for msg in reversed(history):
        content = msg.get("content", "")
        if content.startswith("[DOC_SESSION:"):
            try:
                return json.loads(content[len("[DOC_SESSION:"):].rstrip("]"))
            except Exception:
                pass
    return {}


async def clear_doc_session(phone_number: str):
    """Clear document session by saving an empty marker."""
    await save_message(phone_number, "system", "[DOC_SESSION:{}]")
