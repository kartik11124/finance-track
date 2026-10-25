"""GoldAPI Client.
Retrieves real-time gold rates in Indian Rupees (INR) per gram and troy ounce.
Caches quotes in SQLite and provides graceful fallback if offline or key is unconfigured.
"""

from typing import Any, Dict, Optional
import requests
from config.config import get_api_key, is_configured
from database.database import execute_insert, execute_one, execute_update


def fetch_gold_price() -> Dict[str, Any]:
    """Fetch live Gold rate (XAU/INR) or return the latest cached SQLite record.
    Returns:
      price_per_gram, price_per_ounce, currency, unit, source, updated_at
    """
    api_key = get_api_key("GOLD_API_KEY")

    # Check if API key is configured
    if not is_configured(api_key):
        cached = get_cached_gold_price()
        if cached:
            cached["notice"] = "GOLD_API_KEY not configured in .env. Displaying cached gold rate."
            cached["is_cached"] = True
            return cached
        return {
            "error": "Gold API key is not configured and no cached data is available.",
            "is_unconfigured": True
        }

    url = "https://www.goldapi.io/api/price/XAU/INR"
    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=6)
        if response.status_code == 200:
            data = response.json()
            price_ounce = float(data.get("price", 0.0))
            # 1 Troy Ounce = 31.1034768 grams
            price_gram = float(data.get("price_gram_24k", price_ounce / 31.1034768 if price_ounce > 0 else 0.0))
            currency = data.get("currency", "INR")

            # Store in SQLite cache
            cache_gold_price(price_gram, price_ounce, currency, "gram", "GoldAPI Live")

            return {
                "price_per_gram": round(price_gram, 2),
                "price_per_ounce": round(price_ounce, 2),
                "currency": currency,
                "unit": "gram",
                "source": "GoldAPI Live",
                "is_cached": False,
                "timestamp": data.get("timestamp")
            }
        else:
            return fallback_gold_response(_gold_api_error_message(response))

    except requests.exceptions.Timeout:
        return fallback_gold_response("Connection to GoldAPI timed out. Displaying cached rate.")
    except requests.exceptions.RequestException:
        return fallback_gold_response("Network issue contacting GoldAPI. Displaying cached rate.")
    except Exception as e:
        return fallback_gold_response(f"Error reading GoldAPI data: {str(e)}")


def cache_gold_price(
    price_gram: float,
    price_ounce: float,
    currency: str = "INR",
    unit: str = "gram",
    source: str = "GoldAPI Live"
) -> None:
    """Insert or update gold record in SQLite."""
    existing = execute_one("SELECT id FROM gold_data ORDER BY id DESC LIMIT 1;")
    if existing:
        execute_update(
            """
            UPDATE gold_data
            SET price_per_gram = ?, price_per_ounce = ?, currency = ?, unit = ?,
                source = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (price_gram, price_ounce, currency, unit, source, existing["id"])
        )
    else:
        execute_insert(
            """
            INSERT INTO gold_data (price_per_gram, price_per_ounce, currency, unit, source)
            VALUES (?, ?, ?, ?, ?);
            """,
            (price_gram, price_ounce, currency, unit, source)
        )


def get_cached_gold_price() -> Optional[Dict[str, Any]]:
    """Retrieve the most recent gold price from SQLite cache."""
    row = execute_one(
        """
        SELECT price_per_gram, price_per_ounce, currency, unit, source, updated_at
        FROM gold_data
        ORDER BY updated_at DESC
        LIMIT 1;
        """
    )
    if row:
        result = dict(row)
        result["price_per_gram"] = round(result["price_per_gram"], 2)
        result["price_per_ounce"] = round(result["price_per_ounce"], 2)
        return result
    return None


def fallback_gold_response(message: str) -> Dict[str, Any]:
    """Return cached gold rate or friendly error."""
    cached = get_cached_gold_price()
    if cached:
        cached["notice"] = message
        cached["is_cached"] = True
        return cached
    return {"error": message}


def _gold_api_error_message(response: requests.Response) -> str:
    """Translate GoldAPI failures into an actionable, safe user message."""
    if response.status_code in (401, 403):
        return (
            "GoldAPI rejected the configured API key. Generate or copy the active "
            "key from your GoldAPI dashboard and save it as GOLD_API_KEY in .env. "
            "Displaying the latest cached rate."
        )
    if response.status_code == 429:
        return (
            "GoldAPI request limit reached. Displaying the latest cached rate; "
            "try again after the provider's limit resets."
        )
    return f"GoldAPI returned status {response.status_code}. Displaying cached rate."
