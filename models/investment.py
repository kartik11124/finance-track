"""Investment catalog item model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Investment:
    id: Optional[int]
    name: str
    category: str
    risk_level: str  # LOW, MEDIUM, HIGH
    minimum_amount: float
    duration: str  # SHORT, MEDIUM, LONG
    expected_return_rate: Optional[float]
    expected_return_information: str
    liquidity: str  # HIGH, MEDIUM, LOW
    suitable_goal: str
    description: str
