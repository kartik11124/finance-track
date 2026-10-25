"""Income model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Income:
    id: Optional[int]
    user_id: int
    amount: float
    source: str
    date: str
    description: Optional[str] = None
    created_at: Optional[str] = None

    def validate(self) -> None:
        if self.amount <= 0:
            raise ValueError("Income amount must be greater than zero.")
        if not self.source or not self.source.strip():
            raise ValueError("Income source cannot be empty.")
        if not self.date or not self.date.strip():
            raise ValueError("Date cannot be empty.")
