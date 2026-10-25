"""Budget model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Budget:
    id: Optional[int]
    user_id: int
    category: str
    amount: float
    month_year: str
    created_at: Optional[str] = None

    def validate(self) -> None:
        if self.amount <= 0:
            raise ValueError("Budget amount must be greater than zero.")
        if not self.category or not self.category.strip():
            raise ValueError("Category cannot be empty.")
        if not self.month_year or not self.month_year.strip():
            raise ValueError("Month/Year cannot be empty.")
