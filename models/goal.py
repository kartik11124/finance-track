"""Financial Goal model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FinancialGoal:
    id: Optional[int]
    user_id: int
    name: str
    target_amount: float
    current_amount: float
    target_date: str  # YYYY-MM-DD
    category: str = "Wealth Creation"
    status: str = "IN_PROGRESS"
    created_at: Optional[str] = None

    def validate(self) -> None:
        if self.target_amount <= 0:
            raise ValueError("Target amount must be greater than zero.")
        if self.current_amount < 0:
            raise ValueError("Current amount cannot be negative.")
        if not self.name or not self.name.strip():
            raise ValueError("Goal name cannot be empty.")
        if not self.target_date or not self.target_date.strip():
            raise ValueError("Target date cannot be empty.")

    @property
    def remaining_amount(self) -> float:
        return max(0.0, self.target_amount - self.current_amount)

    @property
    def progress_percentage(self) -> float:
        if self.target_amount <= 0:
            return 0.0
        return min(100.0, round((self.current_amount / self.target_amount) * 100, 2))

    @property
    def months_remaining(self) -> int:
        try:
            target = datetime.strptime(self.target_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            months = (target.year - today.year) * 12 + (target.month - today.month)
            return max(1, months)
        except Exception:
            return 12

    @property
    def required_monthly_contribution(self) -> float:
        rem = self.remaining_amount
        if rem <= 0:
            return 0.0
        return round(rem / self.months_remaining, 2)
