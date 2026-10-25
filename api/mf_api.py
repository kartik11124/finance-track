"""MFAPI Client for Indian Mutual Funds.
Public free REST API (https://api.mfapi.in). No API key required.
Fetches mutual fund scheme search, historical NAVs, and caches results in SQLite.
"""

from typing import Any, Dict, List, Optional
import requests
from database.database import execute_insert, execute_one, execute_query, execute_update


BASE_URL = "https://api.mfapi.in/mf"


def search_mutual_funds(query: str) -> List[Dict[str, Any]]:
    """Search mutual funds by keyword (e.g. 'Nifty', 'HDFC', 'Parag Parikh', 'Index')."""
    clean_q = query.strip()
    if not clean_q:
        return get_cached_mutual_funds()

    url = f"{BASE_URL}/search"
    params = {"q": clean_q}

    try:
        response = requests.get(url, params=params, timeout=6)
        if response.status_code == 200:
            results = response.json()
            formatted = []
            for item in results[:15]:
                formatted.append({
                    "scheme_code": item.get("schemeCode"),
                    "scheme_name": item.get("schemeName"),
                })
            return formatted
    except Exception:
        pass

    # Fallback to local SQLite search if offline
    return search_cached_mutual_funds(clean_q)


def fetch_mutual_fund_details(scheme_code: int) -> Dict[str, Any]:
    """Retrieve metadata and latest NAV for a mutual fund scheme code."""
    url = f"{BASE_URL}/{scheme_code}"

    try:
        response = requests.get(url, timeout=6)
        if response.status_code == 200:
            data = response.json()
            meta = data.get("meta", {})
            nav_history = data.get("data", [])

            latest_nav = 0.0
            nav_date = "N/A"
            if nav_history:
                latest_entry = nav_history[0]
                latest_nav = float(latest_entry.get("nav", 0.0))
                nav_date = latest_entry.get("date", "N/A")

            scheme_name = meta.get("scheme_name", f"Scheme {scheme_code}")
            category = meta.get("scheme_category", "Mutual Fund")

            # Cache in SQLite
            cache_mutual_fund(scheme_code, scheme_name, latest_nav, nav_date, category)

            return {
                "scheme_code": scheme_code,
                "scheme_name": scheme_name,
                "fund_house": meta.get("fund_house", "N/A"),
                "category": category,
                "nav": latest_nav,
                "date": nav_date,
                "history": nav_history[:10],
                "is_cached": False,
            }
    except Exception:
        pass

    # Fallback to SQLite cache
    cached = get_cached_fund_by_code(scheme_code)
    if cached:
        cached["is_cached"] = True
        cached["notice"] = "MFAPI unreachable. Showing cached NAV information."
        return cached

    return {"error": f"Unable to fetch details for scheme code {scheme_code}."}


def cache_mutual_fund(
    scheme_code: int,
    scheme_name: str,
    nav: float,
    date: str,
    category: str
) -> None:
    """Store or update mutual fund in SQLite."""
    existing = execute_one("SELECT id FROM mutual_funds WHERE scheme_code = ?;", (scheme_code,))
    if existing:
        execute_update(
            """
            UPDATE mutual_funds
            SET scheme_name = ?, nav = ?, date = ?, category = ?, updated_at = CURRENT_TIMESTAMP
            WHERE scheme_code = ?;
            """,
            (scheme_name, nav, date, category, scheme_code)
        )
    else:
        execute_insert(
            """
            INSERT INTO mutual_funds (scheme_code, scheme_name, nav, date, category)
            VALUES (?, ?, ?, ?, ?);
            """,
            (scheme_code, scheme_name, nav, date, category)
        )


def get_cached_mutual_funds(limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieve mutual funds from SQLite cache."""
    rows = execute_query(
        """
        SELECT scheme_code, scheme_name, nav, date, category, updated_at
        FROM mutual_funds
        ORDER BY updated_at DESC
        LIMIT ?;
        """,
        (limit,)
    )
    return [dict(r) for r in rows]


def get_cached_fund_by_code(scheme_code: int) -> Optional[Dict[str, Any]]:
    """Retrieve single mutual fund from cache by scheme code."""
    row = execute_one(
        """
        SELECT scheme_code, scheme_name, nav, date, category, updated_at
        FROM mutual_funds
        WHERE scheme_code = ?;
        """,
        (scheme_code,)
    )
    return dict(row) if row else None


def search_cached_mutual_funds(query: str) -> List[Dict[str, Any]]:
    """Search locally cached mutual funds using SQL LIKE."""
    q_param = f"%{query}%"
    rows = execute_query(
        """
        SELECT scheme_code, scheme_name, nav, date, category
        FROM mutual_funds
        WHERE scheme_name LIKE ?
        LIMIT 10;
        """,
        (q_param,)
    )
    return [dict(r) for r in rows]
