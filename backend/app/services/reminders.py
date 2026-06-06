"""
Proactive deadline reminder system.
Runs on a schedule and sends WhatsApp messages to users
who have applied for opportunities with approaching deadlines.
"""
import logging
from datetime import datetime, timezone

from data.opportunities import FUNDING_OPPORTUNITIES
from app.services.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)

# Deadline keywords that indicate urgency
DEADLINE_SOON_KEYWORDS = [
    "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december",
    "2025", "2026",
]


def _parse_deadline_urgency(deadline_str: str) -> str:
    """
    Classify deadline urgency.
    Returns: 'urgent' | 'soon' | 'rolling' | 'unknown'
    """
    lower = deadline_str.lower()
    if "always open" in lower or "rolling" in lower or "ongoing" in lower:
        return "rolling"

    current_month = datetime.now(timezone.utc).month
    current_year = datetime.now(timezone.utc).year

    # Check for specific months
    month_map = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }

    for month_name, month_num in month_map.items():
        if month_name in lower:
            if month_num == current_month:
                return "urgent"
            elif month_num == current_month + 1 or (current_month == 12 and month_num == 1):
                return "soon"

    return "unknown"


async def send_deadline_reminders():
    """
    Check all profiles with pending applications and send
    WhatsApp reminders for opportunities with approaching deadlines.

    Call this from a scheduled endpoint (e.g., daily cron).
    """
    from app.services.database import get_all_active_applications, get_profile

    try:
        active_apps = await get_all_active_applications()
        reminders_sent = 0

        for app in active_apps:
            phone = app["phone_number"]
            opp_id = app["opportunity_id"]

            # Find the opportunity
            opp = next((o for o in FUNDING_OPPORTUNITIES if o["id"] == opp_id), None)
            if not opp:
                continue

            urgency = _parse_deadline_urgency(opp["deadline"])

            if urgency == "urgent":
                message = (
                    f"⚠️ *BizPadi Reminder*\n\n"
                    f"The deadline for *{opp['name']}* is *this month*!\n\n"
                    f"⏰ Deadline: {opp['deadline']}\n"
                    f"💰 Amount: {opp['amount']}\n\n"
                    f"Have you submitted your application yet? Reply *yes* or *no* and I'll help you out! 🙏"
                )
                await send_whatsapp_message(phone, message)
                reminders_sent += 1

            elif urgency == "soon":
                message = (
                    f"📅 *BizPadi Update*\n\n"
                    f"Quick heads up   *{opp['name']}* deadline is coming up next month.\n\n"
                    f"⏰ Deadline: {opp['deadline']}\n"
                    f"💰 Amount: {opp['amount']}\n\n"
                    f"Reply *steps* to get the application guide again, or tell me where you're stuck! 💪"
                )
                await send_whatsapp_message(phone, message)
                reminders_sent += 1

        logger.info(f"Deadline reminders sent: {reminders_sent}")
        return reminders_sent

    except Exception as e:
        logger.error(f"Error sending deadline reminders: {e}")
        return 0


async def send_new_opportunity_alerts():
    """
    Send weekly digest of matched opportunities to all profiled users.
    Call from a weekly cron job.
    """
    from app.services.database import get_profile
    from app.services.matching import get_matched_opportunities, format_opportunities_for_whatsapp
    from app.services.database import _memory_profiles

    notified = 0

    for phone_number, profile_data in _memory_profiles.items():
        try:
            profile_obj = await get_profile(phone_number)
            if not profile_obj or not profile_obj.is_profile_complete():
                continue

            matches = get_matched_opportunities(profile_obj)
            if not matches:
                continue

            match_text = format_opportunities_for_whatsapp(matches)

            message = (
                f"👋 *BizPadi Weekly Update*\n\n"
                f"Here are this week's funding opportunities for your business:\n\n"
                f"{match_text}\n\n"
                f"Reply with a number to get application steps!"
            )

            await send_whatsapp_message(phone_number, message)
            notified += 1

        except Exception as e:
            logger.warning(f"Failed to notify {phone_number}: {e}")

    logger.info(f"Weekly opportunity alerts sent: {notified}")
    return notified


async def send_followup_check(phone_number: str, opportunity_name: str):
    """
    Send a follow-up 3 days after someone gets application steps.
    """
    message = (
        f"Hey! 👋 BizPadi checking in.\n\n"
        f"Did you get a chance to apply for *{opportunity_name}*? 🤞\n\n"
        f"Reply:\n"
        f"• *applied*   I'll track it for you\n"
        f"• *help*   if you're stuck somewhere\n"
        f"• *skip*   if you decided not to apply\n\n"
        f"We're rooting for you! 💪"
    )
    await send_whatsapp_message(phone_number, message)
