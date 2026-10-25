"""Transaction audit model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    id: Optional[int]
    user_id: int
    type: str  # INCOME, EXPENSE, INVESTMENT, GOAL_CONTRIBUTION
    amount: float
    reference_id: Optional[int]
    category: Optional[str]
    date: str
    description: Optional[str] = None
    created_at: Optional[str] = None
