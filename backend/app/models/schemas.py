from pydantic import BaseModel
from typing import Optional
from enum import Enum


class UserState(str, Enum):
    NEW = "new"
    LANGUAGE_SELECT = "language_select"   # NEW: waiting for language choice
    ONBOARDING = "onboarding"
    CONFIRMING = "confirming"
    PROFILED = "profiled"
    SUPPORT = "support"


class SMEProfile(BaseModel):
    phone_number: str
    state: UserState = UserState.NEW
    language: str = "en"                  # persisted language preference
    owner_name: Optional[str] = None
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    business_stage: Optional[str] = None
    monthly_revenue: Optional[str] = None
    employee_count: Optional[int] = None
    cac_registered: Optional[bool] = None
    biggest_challenge: Optional[str] = None
    applied_opportunities: list[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def is_profile_complete(self) -> bool:
        return all([
            self.business_name,
            self.business_type,
            self.location_city,
            self.business_stage,
            self.monthly_revenue,
        ])

    def to_summary(self) -> str:
        parts = []
        if self.owner_name:
            parts.append(f"Name: {self.owner_name}")
        if self.business_name:
            parts.append(f"Business: {self.business_name}")
        if self.business_type:
            parts.append(f"Type: {self.business_type}")
        if self.location_city:
            loc = self.location_city
            if self.location_state:
                loc += f", {self.location_state}"
            parts.append(f"Location: {loc}")
        if self.business_stage:
            parts.append(f"Stage: {self.business_stage}")
        if self.monthly_revenue:
            rev_map = {
                "under_100k": "Under N100k/month",
                "100k_500k": "N100k-500k/month",
                "500k_2m": "N500k-2M/month",
                "2m_10m": "N2M-10M/month",
                "above_10m": "Above N10M/month",
            }
            parts.append(f"Revenue: {rev_map.get(self.monthly_revenue, self.monthly_revenue)}")
        if self.employee_count is not None:
            parts.append(f"Staff: {self.employee_count}")
        if self.cac_registered is not None:
            parts.append(f"CAC: {'Yes' if self.cac_registered else 'No'}")
        if self.biggest_challenge:
            parts.append(f"Challenge: {self.biggest_challenge}")
        if self.language:
            parts.append(f"Language: {self.language}")
        return "\n".join(parts) if parts else "Profile not yet complete."

    def to_confirmation_message(self) -> str:
        lines = ["Let me confirm what I have so far:\n"]
        if self.owner_name:
            lines.append(f"Name: {self.owner_name}")
        if self.business_name:
            lines.append(f"Business: {self.business_name}")
        if self.business_type:
            lines.append(f"Type: {self.business_type}")
        if self.location_city:
            loc = self.location_city
            if self.location_state:
                loc += f", {self.location_state}"
            lines.append(f"Location: {loc}")
        if self.business_stage:
            lines.append(f"Stage: {self.business_stage.capitalize()}")
        if self.monthly_revenue:
            rev_map = {
                "under_100k": "Under N100k/month",
                "100k_500k": "N100k-500k/month",
                "500k_2m": "N500k-2M/month",
                "2m_10m": "N2M-10M/month",
                "above_10m": "Above N10M/month",
            }
            lines.append(f"Revenue: {rev_map.get(self.monthly_revenue, self.monthly_revenue)}")
        if self.employee_count is not None:
            lines.append(f"Staff: {self.employee_count}")
        if self.cac_registered is not None:
            lines.append(f"CAC Registered: {'Yes' if self.cac_registered else 'No'}")
        if self.biggest_challenge:
            lines.append(f"Challenge: {self.biggest_challenge}")
        lines.append("\nIs this correct? Reply *yes* to see your funding matches, or tell me what to fix.")
        return "\n".join(lines)


class ApplicationTracking(BaseModel):
    phone_number: str
    opportunity_id: str
    opportunity_name: str
    status: str = "applied"
    applied_at: Optional[str] = None
    updated_at: Optional[str] = None
    notes: Optional[str] = None
