"""Investment Service.
Interacts with the investment catalog in SQLite and interfaces with DSA
search, sort, and filtering algorithms.
"""

from typing import Any, Dict, List, Optional
from algorithms.filtering import apply_multi_criteria_filter
from algorithms.searching import build_hash_index, linear_search, search_investments
from algorithms.sorting import sort_investments
from database.database import execute_insert, execute_one, execute_query


def get_all_investments() -> List[Dict[str, Any]]:
    """Retrieve full catalog of investment instruments from SQLite."""
    return execute_query(
        """
        SELECT id, name, category, risk_level, minimum_amount, duration,
               expected_return_rate, expected_return_information, liquidity,
               suitable_goal, description
        FROM investments
        ORDER BY risk_level ASC, minimum_amount ASC;
        """
    )


def get_investment_by_id(investment_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve single investment product by ID."""
    return execute_one(
        """
        SELECT id, name, category, risk_level, minimum_amount, duration,
               expected_return_rate, expected_return_information, liquidity,
               suitable_goal, description
        FROM investments
        WHERE id = ?;
        """,
        (investment_id,)
    )


def search_and_filter_investments(
    query: Optional[str] = None,
    risk: Optional[str] = None,
    category: Optional[str] = None,
    duration: Optional[str] = None,
    max_amount: Optional[float] = None,
    sort_by: str = "minimum_amount"
) -> List[Dict[str, Any]]:
    """Combines DSA Search, Filter, and Sort algorithms across investments."""
    items = get_all_investments()

    # 1. DSA Search
    if query and query.strip():
        items = search_investments(items, query.strip())

    # 2. DSA Filtering
    if risk and risk.upper() != "ALL":
        items = [inv for inv in items if inv.get("risk_level", "").upper() == risk.upper()]

    if category and category.upper() != "ALL":
        items = [inv for inv in items if inv.get("category", "").lower() == category.lower()]

    if duration and duration.upper() != "ALL":
        items = [inv for inv in items if inv.get("duration", "").upper() == duration.upper()]

    if max_amount is not None and max_amount > 0:
        items = [inv for inv in items if float(inv.get("minimum_amount", 0)) <= max_amount]

    # 3. DSA Sorting
    items = sort_investments(items, sort_by=sort_by, reverse=(sort_by in ("expected_return", "score")))

    return items
