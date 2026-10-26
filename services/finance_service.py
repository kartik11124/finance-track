"""Finance Service: Core arithmetic, CRUD for Income, Expenses, Budgets, and Goals.
Implements validation and financial calculations without fake/hard-coded values.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from database.database import execute_insert, execute_one, execute_query, execute_update
from models.expense import VALID_CATEGORIES


# ==================== INCOME OPERATIONS ====================

def add_income(
    user_id: int,
    amount: float,
    source: str,
    date: str,
    description: Optional[str] = None
) -> int:
    """Add new income record and log in transactions audit."""
    if amount <= 0:
        raise ValueError("Income amount must be greater than zero.")
    if not source or not source.strip():
        raise ValueError("Income source is required.")
    if not date or not date.strip():
        date = datetime.now().strftime("%Y-%m-%d")

    income_id = execute_insert(
        """
        INSERT INTO income (user_id, amount, source, date, description)
        VALUES (?, ?, ?, ?, ?);
        """,
        (user_id, amount, source.strip(), date.strip(), description.strip() if description else "")
    )

    # Audit transaction
    execute_insert(
        """
        INSERT INTO transactions (user_id, type, amount, reference_id, category, date, description)
        VALUES (?, 'INCOME', ?, ?, ?, ?, ?);
        """,
        (user_id, amount, income_id, source.strip(), date.strip(), description.strip() if description else "Income Added")
    )
    return income_id


def update_income(
    income_id: int,
    user_id: int,
    amount: float,
    source: str,
    date: str,
    description: Optional[str] = None
) -> bool:
    """Update existing income record."""
    if amount <= 0:
        raise ValueError("Income amount must be greater than zero.")
    if not source or not source.strip():
        raise ValueError("Income source is required.")

    count = execute_update(
        """
        UPDATE income
        SET amount = ?, source = ?, date = ?, description = ?
        WHERE id = ? AND user_id = ?;
        """,
        (amount, source.strip(), date.strip(), description.strip() if description else "", income_id, user_id)
    )
    return count > 0


def delete_income(income_id: int, user_id: int) -> bool:
    """Delete income record."""
    count = execute_update(
        "DELETE FROM income WHERE id = ? AND user_id = ?;",
        (income_id, user_id)
    )
    return count > 0


def get_user_income_list(user_id: int) -> List[Dict[str, Any]]:
    """Get all income entries for a user ordered by date descending."""
    return execute_query(
        """
        SELECT id, user_id, amount, source, date, description, created_at
        FROM income
        WHERE user_id = ?
        ORDER BY date DESC, id DESC;
        """,
        (user_id,)
    )


def get_total_income(user_id: int, month: Optional[str] = None) -> float:
    """Calculate total income, optionally filtered by YYYY-MM month."""
    sql = "SELECT COALESCE(SUM(amount), 0.0) as total FROM income WHERE user_id = ?"
    params = [user_id]

    if month:
        sql += " AND substr(date, 1, 7) = ?"
        params.append(month)

    row = execute_one(sql + ";", tuple(params))
    return float(row["total"]) if row else 0.0

# ==================== EXPENSE OPERATIONS ====================

def add_expense(
    user_id: int,
    amount: float,
    category: str,
    date: str,
    description: Optional[str] = None
) -> int:
    """Add new expense record and log in transactions audit."""
    if amount <= 0:
        raise ValueError("Expense amount must be greater than zero.")
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")
    if not date or not date.strip():
        date = datetime.now().strftime("%Y-%m-%d")

    expense_id = execute_insert(
        """
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?);
        """,
        (user_id, amount, category, date.strip(), description.strip() if description else "")
    )

    # Audit transaction
    execute_insert(
        """
        INSERT INTO transactions (user_id, type, amount, reference_id, category, date, description)
        VALUES (?, 'EXPENSE', ?, ?, ?, ?, ?);
        """,
        (user_id, amount, expense_id, category, date.strip(), description.strip() if description else "Expense Added")
    )
    return expense_id


def update_expense(
    expense_id: int,
    user_id: int,
    amount: float,
    category: str,
    date: str,
    description: Optional[str] = None
) -> bool:
    """Update existing expense record."""
    if amount <= 0:
        raise ValueError("Expense amount must be greater than zero.")
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")

    count = execute_update(
        """
        UPDATE expenses
        SET amount = ?, category = ?, date = ?, description = ?
        WHERE id = ? AND user_id = ?;
        """,
        (amount, category, date.strip(), description.strip() if description else "", expense_id, user_id)
    )
    return count > 0


def delete_expense(expense_id: int, user_id: int) -> bool:
    """Delete expense record."""
    count = execute_update(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?;",
        (expense_id, user_id)
    )
    return count > 0


def get_user_expense_list(user_id: int) -> List[Dict[str, Any]]:
    """Get all expense entries for a user ordered by date descending."""
    return execute_query(
        """
        SELECT id, user_id, amount, category, date, description, created_at
        FROM expenses
        WHERE user_id = ?
        ORDER BY date DESC, id DESC;
        """,
        (user_id,)
    )


def get_total_expenses(user_id: int, month: Optional[str] = None) -> float:
    """Calculate total expenses, optionally filtered by YYYY-MM month."""
    sql = "SELECT COALESCE(SUM(amount), 0.0) as total FROM expenses WHERE user_id = ?"
    params = [user_id]

    if month:
        sql += " AND substr(date, 1, 7) = ?"
        params.append(month)

    row = execute_one(sql + ";", tuple(params))
    return float(row["total"]) if row else 0.0

def get_category_expenses(user_id: int, month: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get category-wise expense totals, optionally filtered by YYYY-MM month."""
    sql = """
        SELECT category, COALESCE(SUM(amount), 0.0) as total, COUNT(*) as count
        FROM expenses
        WHERE user_id = ?
    """
    params = [user_id]

    if month:
        sql += " AND substr(date, 1, 7) = ?"
        params.append(month)

    sql += """
        GROUP BY category
        ORDER BY total DESC;
    """

    rows = execute_query(sql, tuple(params))
    return [dict(r) for r in rows]


# ==================== BUDGET OPERATIONS ====================

def set_budget(
    user_id: int,
    category: str,
    amount: float,
    month_year: str = "DEFAULT"
) -> int:
    """Create or update category budget for user."""
    if amount <= 0:
        raise ValueError("Budget amount must be greater than zero.")
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")

    existing = execute_one(
        "SELECT id FROM budgets WHERE user_id = ? AND category = ? AND month_year = ?;",
        (user_id, category, month_year)
    )

    if existing:
        execute_update(
            "UPDATE budgets SET amount = ? WHERE id = ?;",
            (amount, existing["id"])
        )
        return existing["id"]
    else:
        return execute_insert(
            """
            INSERT INTO budgets (user_id, category, amount, month_year)
            VALUES (?, ?, ?, ?);
            """,
            (user_id, category, amount, month_year)
        )


def delete_budget(budget_id: int, user_id: int) -> bool:
    """Delete a budget entry."""
    count = execute_update(
        "DELETE FROM budgets WHERE id = ? AND user_id = ?;",
        (budget_id, user_id)
    )
    return count > 0


def apply_batch_budgets(user_id: int, budget_allocations: Dict[str, float]) -> int:
    """Batch apply or update category budgets from algorithmic or custom allocation."""
    applied = 0
    for category, amount in budget_allocations.items():
        if category in VALID_CATEGORIES and amount > 0:
            set_budget(user_id, category, float(amount))
            applied += 1
    return applied


def get_user_budgets(user_id: int) -> List[Dict[str, Any]]:
    """Retrieve all budget allocations for user."""
    return execute_query(
        """
        SELECT id, category, amount, month_year, created_at
        FROM budgets
        WHERE user_id = ?
        ORDER BY category ASC;
        """,
        (user_id,)
    )


def get_budget_comparison(
    user_id: int,
    month: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Compare budgeted amount vs actual spent for each category."""
    budgets = get_user_budgets(user_id)

    category_expenses = {
        r["category"]: float(r["total"])
        for r in get_category_expenses(user_id, month)
    }

    comparison = []

    for b in budgets:
        cat = b["category"]
        budgeted = float(b["amount"])
        spent = category_expenses.get(cat, 0.0)
        remaining = budgeted - spent
        usage_pct = round((spent / budgeted) * 100, 1) if budgeted > 0 else 0.0

        if usage_pct < 80.0:
            status = "Under Budget"
            badge_class = "success"
        elif 80.0 <= usage_pct <= 100.0:
            status = "Near Limit"
            badge_class = "warning"
        else:
            status = "Over Budget"
            badge_class = "danger"

        comparison.append({
            "id": b["id"],
            "category": cat,
            "budgeted": budgeted,
            "spent": spent,
            "remaining": remaining,
            "usage_pct": min(100.0, usage_pct),
            "actual_pct": usage_pct,
            "status": status,
            "badge_class": badge_class
        })

    return comparison

# ==================== FINANCIAL GOALS ====================

def add_financial_goal(
    user_id: int,
    name: str,
    target_amount: float,
    current_amount: float,
    target_date: str,
    category: str = "Wealth Creation"
) -> int:
    """Add a new financial goal."""
    if target_amount <= 0:
        raise ValueError("Target amount must be greater than zero.")
    if current_amount < 0:
        raise ValueError("Current savings amount cannot be negative.")
    if not name or not name.strip():
        raise ValueError("Goal name cannot be empty.")
    if not target_date or not target_date.strip():
        raise ValueError("Target date cannot be empty.")

    return execute_insert(
        """
        INSERT INTO financial_goals (user_id, name, target_amount, current_amount, target_date, category)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (user_id, name.strip(), target_amount, current_amount, target_date.strip(), category.strip())
    )


def update_financial_goal(
    goal_id: int,
    user_id: int,
    name: str,
    target_amount: float,
    current_amount: float,
    target_date: str,
    category: str,
    status: str = "IN_PROGRESS"
) -> bool:
    """Update an existing financial goal."""
    if target_amount <= 0:
        raise ValueError("Target amount must be greater than zero.")
    if current_amount < 0:
        raise ValueError("Current amount cannot be negative.")

    count = execute_update(
        """
        UPDATE financial_goals
        SET name = ?, target_amount = ?, current_amount = ?, target_date = ?, category = ?, status = ?
        WHERE id = ? AND user_id = ?;
        """,
        (name.strip(), target_amount, current_amount, target_date.strip(), category.strip(), status, goal_id, user_id)
    )
    return count > 0


def delete_financial_goal(goal_id: int, user_id: int) -> bool:
    """Delete a goal."""
    count = execute_update(
        "DELETE FROM financial_goals WHERE id = ? AND user_id = ?;",
        (goal_id, user_id)
    )
    return count > 0


def get_user_goals(user_id: int) -> List[Dict[str, Any]]:
    """Retrieve financial goals and calculate real-time progress metrics."""
    rows = execute_query(
        """
        SELECT id, user_id, name, target_amount, current_amount, target_date, category, status, created_at
        FROM financial_goals
        WHERE user_id = ?
        ORDER BY target_date ASC;
        """,
        (user_id,)
    )

    enriched_goals = []
    today = datetime.now().date()

    for r in rows:
        g = dict(r)
        target = float(g["target_amount"])
        current = float(g["current_amount"])
        remaining = max(0.0, target - current)
        progress = min(100.0, round((current / target) * 100, 1)) if target > 0 else 0.0

        # Compute months remaining
        try:
            target_dt = datetime.strptime(g["target_date"], "%Y-%m-%d").date()
            months = (target_dt.year - today.year) * 12 + (target_dt.month - today.month)
            months = max(1, months)
        except Exception:
            months = 12

        monthly_req = round(remaining / months, 2) if remaining > 0 else 0.0

        g["remaining_amount"] = remaining
        g["progress_percentage"] = progress
        g["months_remaining"] = months
        g["monthly_contribution"] = monthly_req
        enriched_goals.append(g)

    return enriched_goals


# ==================== SUMMARY & ARITHMETIC ====================

def get_financial_summary(
    user_id: int,
    month: Optional[str] = None
) -> Dict[str, Any]:
    """Calculate aggregate financial health metrics for a selected month."""
    total_income = get_total_income(user_id, month)
    total_expenses = get_total_expenses(user_id, month)
    total_savings = round(total_income - total_expenses, 2)

    savings_rate = 0.0
    if total_income > 0:
        savings_rate = round((total_savings / total_income) * 100, 1)

    # Budget totals
    budget_comparison = get_budget_comparison(user_id, month)
    total_budgeted = sum(b["budgeted"] for b in budget_comparison)
    total_budget_spent = sum(b["spent"] for b in budget_comparison)

    budget_usage_pct = 0.0
    if total_budgeted > 0:
        budget_usage_pct = round(
            (total_budget_spent / total_budgeted) * 100,
            1
        )

    # Goals totals
    goals = get_user_goals(user_id)
    total_goal_monthly_req = sum(
        g["monthly_contribution"] for g in goals
    )

    has_financial_data = (total_income > 0 or total_expenses > 0)

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "total_savings": total_savings,
        "savings_rate": savings_rate,
        "total_budgeted": total_budgeted,
        "total_budget_spent": total_budget_spent,
        "budget_usage_pct": budget_usage_pct,
        "total_goal_monthly_req": total_goal_monthly_req,
        "has_financial_data": has_financial_data,
        "goals_count": len(goals),
    }
