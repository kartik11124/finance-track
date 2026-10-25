"""User and UserProfile data models."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    name: str
    email: str
    password_hash: str
    created_at: Optional[str] = None


@dataclass
class UserProfile:
    id: Optional[int]
    user_id: int
    risk_tolerance: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    investment_horizon: str = "MEDIUM"  # SHORT, MEDIUM, LONG
    primary_goal: str = "Wealth Creation"
    emergency_fund_months: int = 3
    updated_at: Optional[str] = None

    @property
    def emergency_buffer_ratio(self) -> float:
        """Returns the recommended buffer ratio based on emergency months (e.g. 15-30%)."""
        return min(0.30, max(0.10, self.emergency_fund_months * 0.05))
