"""Expense model."""

from dataclasses import dataclass
from typing import Optional

VALID_CATEGORIES = [
    "Food",
    "Rent",
    "Transport",
    "Education",
    "Shopping",
    "Utilities",
    "Healthcare",
    "Entertainment",
    "Other",
]


@dataclass
class Expense:
    id: Optional[int]
    user_id: int
    amount: float
    category: str
    date: str
    description: Optional[str] = None
    created_at: Optional[str] = None

    def validate(self) -> None:
        if self.amount <= 0:
            raise ValueError("Expense amount must be greater than zero.")
        if self.category not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")
        if not self.date or not self.date.strip():
            raise ValueError("Date cannot be empty.")
