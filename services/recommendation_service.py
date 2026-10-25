"""Recommendation Service: Orchestrates capacity calculations, user profile
retrieval, and DSA Priority Queue ranking.
Ensures transparent explainability and disclaimers.
"""

from typing import Any, Dict, List, Optional
from algorithms.recommendation import generate_recommendations
from database.database import execute_insert, execute_query
from services.auth_service import get_user_profile
from services.finance_service import get_financial_summary, get_user_goals
from services.investment_service import get_all_investments


def calculate_investment_capacity(user_id: int) -> Dict[str, Any]:
    """Calculates disciplined investment capacity accounting for expenses,
    emergency fund reserve, and ongoing financial goal obligations.

    Formula:
      Surplus = Monthly Income - Monthly Expenses
      Emergency Buffer = Surplus * (Emergency Months * 5%) [typically 15% - 25%]
      Net Capacity = Surplus - Emergency Buffer - Ongoing Goal Commitments
    """
    summary = get_financial_summary(user_id)
    profile = get_user_profile(user_id)
    goals = get_user_goals(user_id)

    total_income = summary["total_income"]
    total_expenses = summary["total_expenses"]
    surplus = max(0.0, total_income - total_expenses)

    # Emergency buffer deduction: 5% per month of target buffer, max 30%
    emergency_months = profile.get("emergency_fund_months", 3)
    buffer_ratio = min(0.30, max(0.10, emergency_months * 0.05))
    emergency_reserve = round(surplus * buffer_ratio, 2)

    # Goal commitments
    total_goal_monthly = sum(g["monthly_contribution"] for g in goals)

    # Final available capacity
    available_capacity = max(0.0, round(surplus - emergency_reserve - total_goal_monthly, 2))

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "monthly_surplus": surplus,
        "emergency_months": emergency_months,
        "buffer_ratio": buffer_ratio,
        "buffer_percentage": round(buffer_ratio * 100, 1),
        "emergency_reserve": emergency_reserve,
        "goal_commitments": total_goal_monthly,
        "available_capacity": available_capacity,
        "has_financial_data": summary["has_financial_data"],
        "explanation": (
            f"From total monthly income of ₹{total_income:,.0f} and expenses of ₹{total_expenses:,.0f}, "
            f"your surplus is ₹{surplus:,.0f}. After allocating ₹{emergency_reserve:,.0f} ({round(buffer_ratio*100)}%) "
            f"to emergency reserves and ₹{total_goal_monthly:,.0f} to active goals, "
            f"your safe investment capacity is ₹{available_capacity:,.0f}."
        )
    }


def get_personalized_recommendations(
    user_id: int,
    override_risk: Optional[str] = None,
    override_duration: Optional[str] = None,
    override_goal: Optional[str] = None,
    override_capacity: Optional[float] = None
) -> Dict[str, Any]:
    """Generates personalized investment recommendations matching user profile and capacity.
    Uses DSA Max-Heap Priority Queue for ranking.
    """
    profile = get_user_profile(user_id)
    capacity_info = calculate_investment_capacity(user_id)

    risk = override_risk or profile.get("risk_tolerance", "MEDIUM")
    duration = override_duration or profile.get("investment_horizon", "LONG")
    goal = override_goal or profile.get("primary_goal", "Wealth Creation")
    capacity = override_capacity if override_capacity is not None else capacity_info["available_capacity"]

    investments = get_all_investments()

    # Run DSA Priority Queue Recommendation Engine
    recommendations = generate_recommendations(
        investments=investments,
        user_risk=risk,
        user_horizon=duration,
        user_goal=goal,
        available_capacity=capacity,
        top_k=6
    )

    # Log recommendations to SQLite for audit history
    for rec in recommendations:
        try:
            execute_insert(
                """
                INSERT INTO recommendations (user_id, investment_id, score, match_reasons, calculated_capacity)
                VALUES (?, ?, ?, ?, ?);
                """,
                (user_id, rec["id"], rec["score"], "; ".join(rec["reasons"]), capacity)
            )
        except Exception:
            pass

    return {
        "recommendations": recommendations,
        "user_profile": {
            "risk_tolerance": risk,
            "investment_horizon": duration,
            "primary_goal": goal,
        },
        "capacity_info": capacity_info,
        "disclaimer": (
            "Financial Disclosure: Recommendations represent investment options matching entered criteria "
            "based on algorithmic compatibility scoring. This is not guaranteed financial advice or a return prediction."
        )
    }
