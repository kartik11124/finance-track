"""Alpha Vantage API Client.
Retrieves stock quotes, market data, and performs caching in SQLite.
Implements graceful error handling for timeouts, rate limits, and missing keys.
"""

import time
from typing import Any, Dict, Optional
import requests
from config.config import get_api_key, is_configured
from database.database import execute_insert, execute_one, execute_query, execute_update


DEFAULT_SYMBOLS = ["RELIANCE", "TCS", "INFY", "HDFCBANK"]


def fetch_stock_quote(symbol: str) -> Dict[str, Any]:
    """Fetch real-time stock quote from Alpha Vantage or return cached data.
    Gracefully handles rate limits, invalid symbols, and network failures.
    """
    clean_sym = symbol.strip().upper()
    if not clean_sym:
        return {"error": "Please provide a valid stock symbol."}

    api_key = get_api_key("ALPHA_VANTAGE_API_KEY")

    # If API key is not configured, directly return cached data with notice
    if not is_configured(api_key):
        cached = get_cached_stock(clean_sym)
        if cached:
            cached["notice"] = "API key not configured in .env. Showing cached market data."
            cached["is_cached"] = True
            return cached
        return {
            "error": f"API key not configured in .env and no cached record for '{clean_sym}'.",
            "is_unconfigured": True
        }

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": clean_sym,
        "apikey": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=7)
        if response.status_code != 200:
            return fallback_response(clean_sym, f"Alpha Vantage returned HTTP status {response.status_code}")

        data = response.json()

        # Handle API rate limiting notices from Alpha Vantage
        if "Note" in data:
            return fallback_response(clean_sym, "Alpha Vantage free tier rate limit reached (5 calls/min). Showing cached data.")
        if "Information" in data:
            return fallback_response(clean_sym, "Alpha Vantage API rate limit. Showing cached data.")
        if "Error Message" in data:
            return fallback_response(
                clean_sym,
                "Alpha Vantage rejected the request or symbol. Check the API key and symbol. Showing cached data.",
            )

        quote = data.get("Global Quote", {})
        if not quote or "05. price" not in quote:
            # Check if symbol might need extension or if symbol is invalid
            cached = get_cached_stock(clean_sym)
            if cached:
                cached["notice"] = f"No live quote for '{clean_sym}'. Displaying last cached data."
                cached["is_cached"] = True
                return cached
            return {"error": f"Symbol '{clean_sym}' not found or market is closed."}

        price = float(quote.get("05. price", 0.0))
        previous_close = float(quote.get("08. previous close", price))
        change = float(quote.get("09. change", 0.0))
        change_pct = quote.get("10. change percent", "0.0%").strip()
        latest_day = quote.get("07. latest trading day", time.strftime("%Y-%m-%d"))

        # Cache in SQLite
        cache_stock(clean_sym, price, previous_close, change, change_pct, latest_day, "Alpha Vantage Live")

        return {
            "symbol": clean_sym,
            "price": price,
            "previous_close": previous_close,
            "change": change,
            "change_percent": change_pct,
            "latest_trading_day": latest_day,
            "source": "Alpha Vantage Live",
            "is_cached": False,
        }

    except requests.exceptions.Timeout:
        return fallback_response(clean_sym, "Connection to Alpha Vantage timed out. Displaying cached data.")
    except requests.exceptions.RequestException as e:
        return fallback_response(clean_sym, f"Network error contacting market API. Displaying cached data.")
    except Exception as e:
        return fallback_response(clean_sym, f"Error processing market response: {str(e)}")


def cache_stock(
    symbol: str,
    price: float,
    previous_close: float,
    change: float,
    change_percent: str,
    latest_day: str,
    source: str
) -> None:
    """Store or update stock data in SQLite cache."""
    existing = execute_one("SELECT id FROM market_data WHERE symbol = ?;", (symbol,))
    if existing:
        execute_update(
            """
            UPDATE market_data
            SET price = ?, previous_close = ?, change = ?, change_percent = ?,
                latest_trading_day = ?, source = ?, updated_at = CURRENT_TIMESTAMP
            WHERE symbol = ?;
            """,
            (price, previous_close, change, change_percent, latest_day, source, symbol)
        )
    else:
        execute_insert(
            """
            INSERT INTO market_data (symbol, price, previous_close, change, change_percent, latest_trading_day, source)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (symbol, price, previous_close, change, change_percent, latest_day, source)
        )


def get_cached_stock(symbol: str) -> Optional[Dict[str, Any]]:
    """Retrieve stock from SQLite cache."""
    return execute_one(
        """
        SELECT symbol, price, previous_close, change, change_percent, latest_trading_day, source, updated_at
        FROM market_data
        WHERE symbol = ?
        ORDER BY updated_at DESC
        LIMIT 1;
        """,
        (symbol,)
    )


def get_all_cached_stocks() -> list:
    """Retrieve all cached stocks for market overview."""
    return execute_query(
        """
        SELECT symbol, price, previous_close, change, change_percent, latest_trading_day, source, updated_at
        FROM market_data
        ORDER BY symbol ASC;
        """
    )


def fallback_response(symbol: str, message: str) -> Dict[str, Any]:
    """Retrieve cached data if available; otherwise return informational error."""
    cached = get_cached_stock(symbol)
    if cached:
        cached["notice"] = message
        cached["is_cached"] = True
        return cached
    return {"error": message, "symbol": symbol}
