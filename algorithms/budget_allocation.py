"""Smart Algorithmic Budget Allocation Engine.
Provides algorithmic recommendations for how an individual should allocate their income
across essential living expenses (Rent, Food, Utilities, Transport), lifestyle wants
(Shopping, Entertainment, Healthcare, Other), and wealth creation / investments.

Supports both:
1. Algorithmic Suggestion Mode (e.g. 50/30/20 Balanced, 40/20/40 Wealth Builder, 60/20/20 Conservative)
2. Custom User-Defined Allocation Mode (user adjusts each category manually).
"""

from typing import Any, Dict, List, Optional


ALLOCATION_STRATEGIES = {
    "balanced_50_30_20": {
        "name": "Balanced 50/30/20 Rule",
        "description": "Recommended global standard: 50% Essential Needs, 30% Lifestyle Wants, 20% Investments & Savings.",
        "needs_pct": 50.0,
        "wants_pct": 30.0,
        "invest_pct": 20.0,
        "breakdown": {
            # Needs (50%)
            "Rent": 0.25,        # 25% of income
            "Food": 0.12,        # 12% of income
            "Utilities": 0.07,   # 7% of income
            "Transport": 0.06,   # 6% of income
            # Wants (30%)
            "Shopping": 0.10,    # 10% of income (Personal/Clothing)
            "Entertainment": 0.08, # 8% of income
            "Healthcare": 0.06,  # 6% of income
            "Other": 0.06,       # 6% of income (Discretionary/Education)
            # Wealth & Savings (20%)
            "Investments": 0.20, # 20% of income
        }
    },
    "wealth_builder_40_20_40": {
        "name": "Aggressive Wealth Builder (40/20/40)",
        "description": "Frugal lifestyle prioritizing compounding: 40% Needs, 20% Wants, 40% Investments.",
        "needs_pct": 40.0,
        "wants_pct": 20.0,
        "invest_pct": 40.0,
        "breakdown": {
            # Needs (40%)
            "Rent": 0.20,
            "Food": 0.10,
            "Utilities": 0.05,
            "Transport": 0.05,
            # Wants (20%)
            "Shopping": 0.07,
            "Entertainment": 0.05,
            "Healthcare": 0.04,
            "Other": 0.04,
            # Wealth & Savings (40%)
            "Investments": 0.40,
        }
    },
    "conservative_60_20_20": {
        "name": "High Living Cost / Conservative (60/20/20)",
        "description": "Suitable for high-rent or metropolitan areas: 60% Needs, 20% Wants, 20% Investments.",
        "needs_pct": 60.0,
        "wants_pct": 20.0,
        "invest_pct": 20.0,
        "breakdown": {
            # Needs (60%)
            "Rent": 0.30,
            "Food": 0.15,
            "Utilities": 0.08,
            "Transport": 0.07,
            # Wants (20%)
            "Shopping": 0.07,
            "Entertainment": 0.05,
            "Healthcare": 0.04,
            "Other": 0.04,
            # Wealth & Savings (20%)
            "Investments": 0.20,
        }
    }
}


def calculate_algorithmic_budget(
    monthly_income: float,
    strategy_key: str = "balanced_50_30_20"
) -> Dict[str, Any]:
    """Calculates suggested allocation amounts across categories and investments
    based on the entered monthly income.
    """
    income = max(0.0, float(monthly_income))
    strategy = ALLOCATION_STRATEGIES.get(strategy_key, ALLOCATION_STRATEGIES["balanced_50_30_20"])
    breakdown_ratios = strategy["breakdown"]

    category_allocations: Dict[str, Dict[str, Any]] = {}
    total_allocated = 0.0

    needs_total = 0.0
    wants_total = 0.0
    invest_total = 0.0

    needs_categories = {"Rent", "Food", "Utilities", "Transport"}

    for cat, ratio in breakdown_ratios.items():
        amount = round(income * ratio, 2)
        pct = round(ratio * 100, 1)
        total_allocated += amount

        group = "Needs" if cat in needs_categories else ("Investments" if cat == "Investments" else "Wants")

        if group == "Needs":
            needs_total += amount
        elif group == "Investments":
            invest_total += amount
        else:
            wants_total += amount

        category_allocations[cat] = {
            "amount": amount,
            "percentage": pct,
            "group": group,
            "ratio": ratio,
        }

    advice: List[str] = []
    if income <= 0:
        advice.append("Enter your monthly income to generate an algorithmic allocation blueprint.")
    else:
        advice.append(
            f"From ₹{income:,.0f} monthly income, reserve ₹{invest_total:,.0f} ({strategy['invest_pct']}%) "
            f"directly for disciplined wealth investments."
        )
        advice.append(
            f"Cap living essentials (Rent, Food, Utilities, Transport) at ₹{needs_total:,.0f} ({strategy['needs_pct']}%)."
        )
        advice.append(
            f"Discretionary lifestyle & personal spending should not exceed ₹{wants_total:,.0f} ({strategy['wants_pct']}%)."
        )

    return {
        "monthly_income": income,
        "strategy_key": strategy_key,
        "strategy_name": strategy["name"],
        "strategy_description": strategy["description"],
        "needs_total": round(needs_total, 2),
        "needs_percentage": strategy["needs_pct"],
        "wants_total": round(wants_total, 2),
        "wants_percentage": strategy["wants_pct"],
        "invest_total": round(invest_total, 2),
        "invest_percentage": strategy["invest_pct"],
        "categories": category_allocations,
        "advice": advice,
        "available_strategies": [
            {"key": k, "name": v["name"], "desc": v["description"]}
            for k, v in ALLOCATION_STRATEGIES.items()
        ]
    }
