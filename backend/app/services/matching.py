import logging
from typing import Optional

from app.models.schemas import SMEProfile
from data.opportunities import FUNDING_OPPORTUNITIES, get_opportunities_text

logger = logging.getLogger(__name__)


def _keyword_score(profile: SMEProfile, opp: dict) -> int:
    score = 0

    if "all" in opp["eligibility_sectors"]:
        score += 30
    elif profile.business_type:
        btype = profile.business_type.lower()
        for sector in opp["eligibility_sectors"]:
            if sector.lower() in btype or btype in sector.lower():
                score += 30
                break

    if profile.business_stage and profile.business_stage in opp["eligibility_stages"]:
        score += 25

    if "all" in opp["eligibility_locations"]:
        score += 15
    elif profile.location_state:
        for loc in opp["eligibility_locations"]:
            if loc.lower() in profile.location_state.lower():
                score += 15
                break
    elif profile.location_city:
        for loc in opp["eligibility_locations"]:
            if loc.lower() in profile.location_city.lower():
                score += 10
                break

    if profile.monthly_revenue and profile.monthly_revenue in opp["eligibility_revenue"]:
        score += 20

    if opp["requires_cac"] and profile.cac_registered is False:
        score -= 10

    if hasattr(profile, "applied_opportunities") and opp["id"] in profile.applied_opportunities:
        score += 5

    return max(score, 0)


def get_matched_opportunities(profile: SMEProfile, min_score: int = 20) -> list[dict]:
    scored = []
    for opp in FUNDING_OPPORTUNITIES:
        score = _keyword_score(profile, opp)
        already_applied = (
            hasattr(profile, "applied_opportunities")
            and opp["id"] in profile.applied_opportunities
        )
        if score >= min_score:
            scored.append({
                "opportunity": opp,
                "score": min(score, 100),
                "already_applied": already_applied,
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def format_opportunities_for_whatsapp(matches: list[dict]) -> str:
    if not matches:
        return (
            "No strong matches for your profile right now.\n\n"
            "Things that will help:\n"
            "Register your business with CAC\n"
            "Build up 6 months of bank statements\n"
            "Check back — new opportunities come in regularly\n\n"
            "Type *find new* to search for the latest opportunities."
        )

    lines = ["Here are funding opportunities that match your business:\n"]
    for i, match in enumerate(matches[:5], 1):
        opp = match["opportunity"]
        applied_tag = " (Applied)" if match.get("already_applied") else ""
        lines.append(f"*{i}. {opp['name']}* ({match['score']}% match){applied_tag}")
        lines.append(f"   Amount: {opp['amount']}")
        lines.append(f"   Deadline: {opp['deadline']}")
        lines.append(f"   CAC required: {'Yes' if opp['requires_cac'] else 'No'}")
        lines.append("")

    lines.append("Reply with a *number* for the full guide and document checklist.")
    lines.append("Type *find new* to search for more opportunities live.")
    return "\n".join(lines)


def get_opportunity_by_id(opportunity_id: str) -> Optional[dict]:
    for opp in FUNDING_OPPORTUNITIES:
        if opp["id"] == opportunity_id:
            return opp
    return None
