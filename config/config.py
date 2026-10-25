"""Configuration module for Smart Personal Finance & Budget Management System.
Automatically loads environment variables from the single .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of Project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file automatically
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    load_dotenv()

# Application Settings
SECRET_KEY = os.getenv("SECRET_KEY", "smart_finance_budget_secret_key_2026")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Database Paths
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "finance.db"
SCHEMA_PATH = DB_DIR / "schema.sql"

# API Keys (Loaded from .env)
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()
GOLD_API_KEY = os.getenv("GOLD_API_KEY", "").strip()
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()


def is_configured(api_key: str) -> bool:
    """Helper to check if an API key is provided and not a placeholder."""
    return bool(api_key and api_key != "YOUR_KEY_HERE" and len(api_key) > 3)


def get_api_status() -> dict:
    """Get status overview of external API configurations."""
    return {
        "alpha_vantage": {
            "name": "Alpha Vantage (Stock Market)",
            "configured": is_configured(ALPHA_VANTAGE_API_KEY),
            "key_present": bool(ALPHA_VANTAGE_API_KEY),
        },
        "gold_api": {
            "name": "GoldAPI (Gold Rates)",
            "configured": is_configured(GOLD_API_KEY),
            "key_present": bool(GOLD_API_KEY),
        },
        "news_api": {
            "name": "NewsAPI (Financial News)",
            "configured": is_configured(NEWS_API_KEY),
            "key_present": bool(NEWS_API_KEY),
        },
        "mf_api": {
            "name": "MFAPI (Indian Mutual Funds)",
            "configured": True,  # Free public API, no key required
            "key_present": True,
        },
    }
