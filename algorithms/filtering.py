"""Filtering algorithm module for investment options.
Implements multi-criteria predicates based on user risk tolerance,
financial capacity, duration, category, and goals.
"""

from typing import Any, Dict, List, Optional, Set


# Risk hierarchy: Higher risk levels can tolerate lower risk options, but not vice-versa
RISK_COMPATIBILITY_MAP = {
    "LOW": {"LOW"},
    "MEDIUM": {"LOW", "MEDIUM"},
    "HIGH": {"LOW", "MEDIUM", "HIGH"},
}


def filter_by_risk(
    investments: List[Dict[str, Any]],
    user_risk: str
) -> List[Dict[str, Any]]:
    """Filter out investments exceeding the user's risk tolerance.
    LOW tolerance -> only LOW risk investments
    MEDIUM tolerance -> LOW and MEDIUM risk investments
    HIGH tolerance -> LOW, MEDIUM, and HIGH risk investments
    """
    allowed_risks: Set[str] = RISK_COMPATIBILITY_MAP.get(user_risk.upper(), {"LOW", "MEDIUM"})
    return [inv for inv in investments if inv.get("risk_level", "").upper() in allowed_risks]


def filter_by_capacity(
    investments: List[Dict[str, Any]],
    available_capacity: float
) -> List[Dict[str, Any]]:
    """Filter out investments where the minimum required amount exceeds the available capacity.
    If available capacity is zero or minimal, options with low minimums are retained.
    """
    if available_capacity <= 0:
        # Return only micro-savings / lowest barrier options (e.g. min <= ₹500)
        return [inv for inv in investments if float(inv.get("minimum_amount", 0)) <= 1000]

    return [
        inv for inv in investments
        if float(inv.get("minimum_amount", 0)) <= available_capacity
    ]


def filter_by_duration(
    investments: List[Dict[str, Any]],
    target_duration: str
) -> List[Dict[str, Any]]:
    """Filter or match investments by duration (SHORT, MEDIUM, LONG)."""
    if not target_duration or target_duration.upper() == "ALL":
        return investments

    dur = target_duration.upper()
    return [inv for inv in investments if inv.get("duration", "").upper() == dur]


def filter_by_category(
    investments: List[Dict[str, Any]],
    category: str
) -> List[Dict[str, Any]]:
    """Filter investments by asset class category."""
    if not category or category.upper() == "ALL":
        return investments

    return [inv for inv in investments if inv.get("category", "").lower() == category.lower()]


def apply_multi_criteria_filter(
    investments: List[Dict[str, Any]],
    user_risk: str = "MEDIUM",
    available_capacity: float = 10000.0,
    duration: Optional[str] = None,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Applies pipeline of filters in sequence.
    Time Complexity: O(k * n) where k is number of filter stages.
    """
    results = filter_by_risk(investments, user_risk)
    results = filter_by_capacity(results, available_capacity)

    if duration and duration.upper() != "ALL":
        dur_filtered = filter_by_duration(results, duration)
        # Fall back to results if strict duration filter yields empty set
        if dur_filtered:
            results = dur_filtered

    if category and category.upper() != "ALL":
        cat_filtered = filter_by_category(results, category)
        if cat_filtered:
            results = cat_filtered

    return results
