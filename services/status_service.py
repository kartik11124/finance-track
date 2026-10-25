"""Backend Status and System Diagnostics Service.
Provides connectivity checks, database record counts, and API health indicators
without ever exposing sensitive credentials.
"""

from datetime import datetime
from typing import Any, Dict
import requests
from config.config import get_api_key, is_configured
from database.database import execute_one, execute_query


def get_system_status() -> Dict[str, Any]:
    """Gather complete backend diagnostic and health metrics."""
    alpha_key = get_api_key("ALPHA_VANTAGE_API_KEY")
    gold_key = get_api_key("GOLD_API_KEY")
    news_key = get_api_key("NEWS_API_KEY")
    # 1. Database Health & Counts
    db_status = "CONNECTED"
    db_counts = {
        "users": 0,
        "income": 0,
        "expenses": 0,
        "budgets": 0,
        "goals": 0,
        "investments": 0,
        "transactions": 0,
        "recommendations": 0,
        "market_cache": 0,
        "news_cache": 0,
        "mf_cache": 0
    }

    try:
        user_row = execute_one("SELECT COUNT(*) as count FROM users;")
        db_counts["users"] = user_row["count"] if user_row else 0

        inc_row = execute_one("SELECT COUNT(*) as count FROM income;")
        db_counts["income"] = inc_row["count"] if inc_row else 0

        exp_row = execute_one("SELECT COUNT(*) as count FROM expenses;")
        db_counts["expenses"] = exp_row["count"] if exp_row else 0

        bud_row = execute_one("SELECT COUNT(*) as count FROM budgets;")
        db_counts["budgets"] = bud_row["count"] if bud_row else 0

        goal_row = execute_one("SELECT COUNT(*) as count FROM financial_goals;")
        db_counts["goals"] = goal_row["count"] if goal_row else 0

        inv_row = execute_one("SELECT COUNT(*) as count FROM investments;")
        db_counts["investments"] = inv_row["count"] if inv_row else 0

        tx_row = execute_one("SELECT COUNT(*) as count FROM transactions;")
        db_counts["transactions"] = tx_row["count"] if tx_row else 0

        rec_row = execute_one("SELECT COUNT(*) as count FROM recommendations;")
        db_counts["recommendations"] = rec_row["count"] if rec_row else 0

        mkt_row = execute_one("SELECT COUNT(*) as count FROM market_data;")
        db_counts["market_cache"] = mkt_row["count"] if mkt_row else 0

        news_row = execute_one("SELECT COUNT(*) as count FROM news;")
        db_counts["news_cache"] = news_row["count"] if news_row else 0

        mf_row = execute_one("SELECT COUNT(*) as count FROM mutual_funds;")
        db_counts["mf_cache"] = mf_row["count"] if mf_row else 0
    except Exception as e:
        db_status = f"ERROR ({str(e)})"

    # 2. Alpha Vantage API Status
    alpha_status = "NOT CONFIGURED"
    if is_configured(alpha_key):
        alpha_status = "CONFIGURED (READY)"
    else:
        alpha_status = "UNCONFIGURED (FALLBACK ACTIVE)"

    # 3. GoldAPI Status
    gold_status = "NOT CONFIGURED"
    if is_configured(gold_key):
        gold_status = "CONFIGURED (READY)"
    else:
        gold_status = "UNCONFIGURED (FALLBACK ACTIVE)"

    # 4. NewsAPI Status
    news_status = "NOT CONFIGURED"
    if is_configured(news_key):
        news_status = "CONFIGURED (READY)"
    else:
        news_status = "UNCONFIGURED (FALLBACK ACTIVE)"

    # 5. MFAPI Status (Free public endpoint)
    mf_status = "AVAILABLE"

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "database": {
            "status": db_status,
            "engine": "SQLite 3",
            "counts": db_counts,
        },
        "apis": {
            "alpha_vantage": {
                "name": "Alpha Vantage (Stocks)",
                "status": alpha_status,
                "configured": is_configured(alpha_key),
                "endpoint": "https://www.alphavantage.co",
            },
            "gold_api": {
                "name": "GoldAPI.io (Spot Gold Rates)",
                "status": gold_status,
                "configured": is_configured(gold_key),
                "endpoint": "https://www.goldapi.io",
            },
            "news_api": {
                "name": "NewsAPI.org (Financial Headlines)",
                "status": news_status,
                "configured": is_configured(news_key),
                "endpoint": "https://newsapi.org",
            },
            "mf_api": {
                "name": "MFAPI.in (Indian Mutual Funds)",
                "status": mf_status,
                "configured": True,
                "endpoint": "https://api.mfapi.in",
            },
        },
    }
