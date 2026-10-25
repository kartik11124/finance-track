"""Dashboard Service.
Aggregates live SQLite metrics, external API data, and algorithmic recommendations
for the central dashboard view. Ensures real data, zero fake values, and clean empty states.
"""

from typing import Any, Dict
from api.alpha_vantage import get_all_cached_stocks
from api.gold_api import fetch_gold_price
from api.news_api import fetch_financial_news
from services.finance_service import (
    get_budget_comparison,
    get_category_expenses,
    get_financial_summary,
    get_user_goals
)
from services.recommendation_service import calculate_investment_capacity, get_personalized_recommendations


def get_dashboard_data(user_id: int) -> Dict[str, Any]:
    """Compiles complete dashboard payload for the specified user."""
    summary = get_financial_summary(user_id)
    capacity_info = calculate_investment_capacity(user_id)
    category_expenses = get_category_expenses(user_id)
    budget_comparison = get_budget_comparison(user_id)
    goals = get_user_goals(user_id)

    # Recommendations (Top 3 for dashboard quick glance)
    rec_payload = get_personalized_recommendations(user_id)
    top_recommendations = rec_payload["recommendations"][:3]

    # External APIs
    gold_data = fetch_gold_price()
    market_stocks = get_all_cached_stocks()
    news_payload = fetch_financial_news(limit=3)

    # Prepare chart-ready JSON structures
    chart_category_labels = [c["category"] for c in category_expenses]
    chart_category_data = [c["total"] for c in category_expenses]

    # Budget chart data
    budget_labels = [b["category"] for b in budget_comparison]
    budget_allocated = [b["budgeted"] for b in budget_comparison]
    budget_spent = [b["spent"] for b in budget_comparison]

    return {
        "summary": summary,
        "capacity_info": capacity_info,
        "category_expenses": category_expenses,
        "budget_comparison": budget_comparison,
        "goals": goals,
        "top_recommendations": top_recommendations,
        "gold_data": gold_data,
        "market_stocks": market_stocks,
        "news_articles": news_payload.get("articles", []),
        "news_notice": news_payload.get("notice"),
        "chart_data": {
            "income": summary["total_income"],
            "expenses": summary["total_expenses"],
            "savings": summary["total_savings"],
            "category_labels": chart_category_labels,
            "category_values": chart_category_data,
            "budget_labels": budget_labels,
            "budget_allocated": budget_allocated,
            "budget_spent": budget_spent,
        },
        "has_financial_data": summary["has_financial_data"],
        "user_profile": rec_payload["user_profile"],
    }
