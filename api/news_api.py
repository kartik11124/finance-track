"""NewsAPI Client.
Retrieves financial and business news headlines.
Caches summaries in SQLite without copying full articles.
Provides reliable offline fallbacks.
"""

from typing import Any, Dict, List
import requests
from config.config import NEWS_API_KEY, is_configured
from database.database import execute_insert, execute_query, execute_update


def fetch_financial_news(limit: int = 10) -> Dict[str, Any]:
    """Retrieve financial/business news headlines from NewsAPI or SQLite cache.
    Returns:
      {
        "articles": [...],
        "is_cached": bool,
        "notice": Optional[str],
        "count": int
      }
    """
    if not is_configured(NEWS_API_KEY):
        cached = get_cached_news(limit)
        return {
            "articles": cached,
            "is_cached": True,
            "notice": "NEWS_API_KEY not configured in .env. Displaying cached financial headlines.",
            "count": len(cached)
        }

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": "business",
        "country": "in",
        "apiKey": NEWS_API_KEY,
        "pageSize": limit
    }

    try:
        response = requests.get(url, params=params, timeout=6)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])

            if articles:
                # Cache fresh articles into SQLite
                cache_news_articles(articles)

                formatted = []
                for a in articles[:limit]:
                    formatted.append({
                        "title": a.get("title") or "Financial Update",
                        "source": a.get("source", {}).get("name", "Financial News"),
                        "published_at": (a.get("publishedAt") or "")[:10],
                        "description": a.get("description") or "Click to read full coverage on publisher site.",
                        "url": a.get("url") or "#"
                    })
                return {
                    "articles": formatted,
                    "is_cached": False,
                    "notice": None,
                    "count": len(formatted)
                }

        # If country=in returned empty, try general business query
        return fallback_news_response("NewsAPI request completed with no articles. Displaying cached news.", limit)

    except requests.exceptions.Timeout:
        return fallback_news_response("NewsAPI timed out. Displaying cached headlines.", limit)
    except requests.exceptions.RequestException:
        return fallback_news_response("Network issue contacting NewsAPI. Displaying cached headlines.", limit)
    except Exception as e:
        return fallback_news_response(f"Error reading news: {str(e)}", limit)


def cache_news_articles(articles: List[Dict[str, Any]]) -> None:
    """Store up to 10 recent headlines in SQLite cache."""
    for a in articles[:10]:
        title = a.get("title")
        if not title:
            continue
        source_name = a.get("source", {}).get("name", "Market News")
        pub_date = (a.get("publishedAt") or "")[:10]
        desc = a.get("description") or ""
        url = a.get("url") or ""

        # Avoid duplicates
        existing = execute_query("SELECT id FROM news WHERE title = ?;", (title,))
        if not existing:
            execute_insert(
                """
                INSERT INTO news (title, source, published_at, description, url)
                VALUES (?, ?, ?, ?, ?);
                """,
                (title, source_name, pub_date, desc, url)
            )


def get_cached_news(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve articles from SQLite cache ordered by recency."""
    rows = execute_query(
        """
        SELECT title, source, published_at, description, url
        FROM news
        ORDER BY id DESC
        LIMIT ?;
        """,
        (limit,)
    )
    return [dict(r) for r in rows]


def fallback_news_response(message: str, limit: int = 10) -> Dict[str, Any]:
    """Return cached news with an informational notice."""
    cached = get_cached_news(limit)
    return {
        "articles": cached,
        "is_cached": True,
        "notice": message,
        "count": len(cached)
    }
