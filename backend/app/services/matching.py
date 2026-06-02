import logging
from typing import Optional

from app.models.schemas import SMEProfile
from app.services.llm import match_opportunities
from data.opportunities import FUNDING_OPPORTUNITIES, get_opportunities_text

logger = logging.getLogger(__name__)


def _keyword_score(profile: SMEProfile, opp: dict) -> int:
    """Rule-based scoring — fast, always available."""
    score = 0

    # Sector (30pts)
    if "all" in opp["eligibility_sectors"]:
        score += 30
    elif profile.business_type:
        btype = profile.business_type.lower()
        for sector in opp["eligibility_sectors"]:
            if sector.lower() in btype or btype in sector.lower():
                score += 30
                break

    # Stage (25pts)
    if profile.business_stage and profile.business_stage in opp["eligibility_stages"]:
        score += 25

    # Location (15pts)
    if "all" in opp["eligibility_locations"]:
        score += 15
    elif profile.location_state:
        for loc in opp["eligibility_locations"]:
            if loc.lower() in profile.location_state.lower():
                score += 15
                break

    # Revenue (20pts)
    if profile.monthly_revenue and profile.monthly_revenue in opp["eligibility_revenue"]:
        score += 20

    # CAC penalty (-10pts)
    if opp["requires_cac"] and profile.cac_registered is False:
        score -= 10

    # Already applied bonus — show it first so they can track
    if hasattr(profile, "applied_opportunities") and opp["id"] in profile.applied_opportunities:
        score += 5

    return max(score, 0)


def _semantic_boost(profile: SMEProfile, opp: dict) -> float:
    """
    Semantic similarity boost using embeddings.
    Returns 0.0-1.0 that gets added as a percentage bonus.
    Falls back gracefully if embeddings unavailable.
    """
    try:
        from app.services.embeddings import semantic_score, is_available
        if not is_available():
            return 0.0

        profile_text = (
            f"{profile.business_type or ''} {profile.biggest_challenge or ''} "
            f"{profile.business_stage or ''} {profile.location_city or ''}"
        ).strip()

        opp_text = f"{opp['name']} {opp['description']}"

        score = semantic_score(profile_text, opp_text)
        return score * 15  # max 15 point semantic bonus on top of keyword score
    except Exception as e:
        logger.debug(f"Semantic boost skipped: {e}")
        return 0.0


def get_matched_opportunities(profile: SMEProfile, min_score: int = 25) -> list[dict]:
    """
    Hybrid matching: keyword rules + semantic similarity.
    Returns sorted list with scores.
    """
    scored = []

    for opp in FUNDING_OPPORTUNITIES:
        keyword = _keyword_score(profile, opp)
        semantic = _semantic_boost(profile, opp)
        total = int(keyword + semantic)

        if total >= min_score:
            already_applied = (
                hasattr(profile, "applied_opportunities") and
                opp["id"] in profile.applied_opportunities
            )
            scored.append({
                "opportunity": opp,
                "score": min(total, 100),
                "already_applied": already_applied,
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def format_opportunities_for_whatsapp(matches: list[dict]) -> str:
    if not matches:
        return (
            "Hmm, no strong matches for your profile right now. 🤔\n\n"
            "Here's what can help:\n"
            "• Register your business with CAC if you haven't\n"
            "• Keep growing your revenue\n"
            "• Check back — new opportunities drop regularly\n\n"
            "Type *help* anytime to see what else BizPadi can do! 💪"
        )

    lines = ["Here are funding opportunities that match your business 🎯\n"]

    for i, match in enumerate(matches[:5], 1):
        opp = match["opportunity"]
        applied_tag = " ✅ *Applied*" if match.get("already_applied") else ""
        lines.append(f"*{i}. {opp['name']}*{applied_tag}")
        lines.append(f"   💰 {opp['amount']}")
        lines.append(f"   ⏰ {opp['deadline']}")
        lines.append(f"   📋 CAC: {'Required' if opp['requires_cac'] else 'Not required'}")
        lines.append(f"   Match: {match['score']}%")
        lines.append("")

    lines.append("Reply with a *number* for step-by-step application guide 👇")
    lines.append("Or ask me anything about any of these opportunities!")
    return "\n".join(lines)


def get_opportunity_by_id(opportunity_id: str) -> Optional[dict]:
    for opp in FUNDING_OPPORTUNITIES:
        if opp["id"] == opportunity_id:
            return opp
    return None


async def ai_match_opportunities(profile: SMEProfile) -> Optional[str]:
    profile_summary = profile.to_summary()
    opportunities_text = get_opportunities_text()
    return await match_opportunities(profile_summary, opportunities_text)
