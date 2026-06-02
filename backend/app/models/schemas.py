from pydantic import BaseModel
from typing import Optional
from enum import Enum


class UserState(str, Enum):
    NEW = "new"
    ONBOARDING = "onboarding"
    CONFIRMING = "confirming"   # new: waiting for profile confirmation
    PROFILED = "profiled"
    SUPPORT = "support"


class SMEProfile(BaseModel):
    phone_number: str
    state: UserState = UserState.NEW
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    business_stage: Optional[str] = None
    monthly_revenue: Optional[str] = None
    employee_count: Optional[int] = None
    cac_registered: Optional[bool] = None
    biggest_challenge: Optional[str] = None
    language: str = "en"
    # Application tracking
    applied_opportunities: list[str] = []   # list of opp IDs user said they applied to
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def is_profile_complete(self) -> bool:
        required = [
            self.business_name,
            self.business_type,
            self.location_city,
            self.business_stage,
            self.monthly_revenue,
        ]
        return all(field is not None for field in required)

    def to_summary(self) -> str:
        parts = []
        if self.business_name:
            parts.append(f"Business: {self.business_name}")
        if self.business_type:
            parts.append(f"Type: {self.business_type}")
        if self.location_city:
            city = self.location_city
            if self.location_state:
                city += f", {self.location_state}"
            parts.append(f"Location: {city}")
        if self.business_stage:
            parts.append(f"Stage: {self.business_stage}")
        if self.monthly_revenue:
            parts.append(f"Revenue: {self.monthly_revenue}")
        if self.employee_count is not None:
            parts.append(f"Employees: {self.employee_count}")
        if self.cac_registered is not None:
            parts.append(f"CAC Registered: {'Yes' if self.cac_registered else 'No'}")
        if self.biggest_challenge:
            parts.append(f"Challenge: {self.biggest_challenge}")
        return "\n".join(parts) if parts else "No profile data yet."

    def to_confirmation_message(self) -> str:
        """Build a WhatsApp confirmation message of what was extracted."""
        lines = ["Let me confirm what I've got so far:\n"]
        if self.business_name:
            lines.append(f"🏪 *Business:* {self.business_name}")
        if self.business_type:
            lines.append(f"💼 *Type:* {self.business_type}")
        if self.location_city:
            loc = self.location_city
            if self.location_state:
                loc += f", {self.location_state}"
            lines.append(f"📍 *Location:* {loc}")
        if self.business_stage:
            lines.append(f"📈 *Stage:* {self.business_stage.capitalize()}")
        if self.monthly_revenue:
            rev_map = {
                "under_100k": "Under ₦100k/month",
                "100k_500k": "₦100k–500k/month",
                "500k_2m": "₦500k–2M/month",
                "2m_10m": "₦2M–10M/month",
                "above_10m": "Above ₦10M/month",
            }
            lines.append(f"💰 *Revenue:* {rev_map.get(self.monthly_revenue, self.monthly_revenue)}")
        if self.employee_count is not None:
            lines.append(f"👥 *Staff:* {self.employee_count}")
        if self.cac_registered is not None:
            lines.append(f"📋 *CAC:* {'Registered ✅' if self.cac_registered else 'Not registered'}")
        if self.biggest_challenge:
            lines.append(f"⚡ *Challenge:* {self.biggest_challenge}")

        lines.append("\nIs this correct? Reply *yes* to find your matches, or tell me what to fix! 🙏")
        return "\n".join(lines)


class ConversationMessage(BaseModel):
    phone_number: str
    role: str
    content: str
    created_at: Optional[str] = None


class FundingOpportunity(BaseModel):
    id: str
    name: str
    description: str
    amount: str
    deadline: str
    eligibility_sectors: list[str]
    eligibility_stages: list[str]
    eligibility_locations: list[str]
    eligibility_revenue: list[str]
    requires_cac: bool
    application_link: str
    application_steps: list[str]


class ApplicationTracking(BaseModel):
    phone_number: str
    opportunity_id: str
    opportunity_name: str
    status: str = "applied"   # applied / pending / approved / rejected
    applied_at: Optional[str] = None
    updated_at: Optional[str] = None
    notes: Optional[str] = None
