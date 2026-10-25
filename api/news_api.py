"""NewsAPI Client.
Retrieves financial and business news headlines.
Caches summaries in SQLite without copying full articles.
Provides reliable offline fallbacks.
"""

from typing import Any, Dict, List
import requests
from config.config import get_api_key, is_configured
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
    api_key = get_api_key("NEWS_API_KEY")
    if not is_configured(api_key):
        cached = get_cached_news(limit)
        return {
            "articles": cached,
            "is_cached": True,
            "notice": "NEWS_API_KEY not configured in .env. Displaying cached financial headlines.",
            "count": len(cached)
        }

    # This is the NewsAPI data endpoint.  The previous registration-success
    # page always returned non-news content, so a valid key still fell back to
    # SQLite cache.
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": "business",
        "country": "in",
        "apiKey": api_key,
        "pageSize": limit
    }

    try:
        response = requests.get(url, params=params, timeout=6)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") != "ok":
                return fallback_news_response(
                    _news_api_error_message(data),
                    limit,
                )
            articles = data.get("articles", [])

            if articles:
                # Cache fresh articles into SQLite
                cache_news_articles(articles)
                formatted = _format_articles(articles, limit)
                return {
                    "articles": formatted,
                    "is_cached": False,
                    "notice": None,
                    "count": len(formatted)
                }

            # NewsAPI can validly return an empty India-business result.  Use
            # its broader finance search before considering the SQLite cache.
            fallback_response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": "finance OR stock market OR economy",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": limit,
                    "apiKey": api_key,
                },
                timeout=6,
            )
            if fallback_response.status_code == 200:
                fallback_data = fallback_response.json()
                fallback_articles = fallback_data.get("articles", []) if fallback_data.get("status") == "ok" else []
                if fallback_articles:
                    cache_news_articles(fallback_articles)
                    formatted = _format_articles(fallback_articles, limit)
                    return {
                        "articles": formatted,
                        "is_cached": False,
                        "notice": "Showing the latest live finance headlines.",
                        "count": len(formatted),
                    }

            return fallback_news_response(
                "NewsAPI returned no current finance headlines. Displaying cached news.",
                limit,
            )

        if response.status_code in (401, 403):
            return fallback_news_response(
                "NewsAPI rejected the configured API key. Check NEWS_API_KEY in .env. Displaying cached news.",
                limit,
            )
        if response.status_code == 429:
            return fallback_news_response("NewsAPI request limit reached. Displaying cached news.", limit)
        return fallback_news_response(_http_error_message(response), limit)

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


def _format_articles(articles: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    """Convert NewsAPI articles to the template's safe display structure."""
    return [
        {
            "title": article.get("title") or "Financial Update",
            "source": article.get("source", {}).get("name", "Financial News"),
            "published_at": (article.get("publishedAt") or "")[:10],
            "description": article.get("description") or "Click to read full coverage on publisher site.",
            "url": article.get("url") or "#",
        }
        for article in articles[:limit]
    ]


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


def _news_api_error_message(data: Dict[str, Any]) -> str:
    """Convert NewsAPI's successful-HTTP error payload into a useful notice."""
    provider_message = str(data.get("message") or "").strip()
    provider_code = str(data.get("code") or "").strip()
    if provider_message:
        detail = f" ({provider_code})" if provider_code else ""
        return f"NewsAPI could not serve live headlines{detail}: {provider_message}. Displaying cached news."
    return "NewsAPI returned an invalid live-data response. Displaying cached news."


def _http_error_message(response: requests.Response) -> str:
    """Use a provider message when one is available, without exposing credentials."""
    try:
        data = response.json()
    except ValueError:
        data = {}
    if isinstance(data, dict):
        provider_message = str(data.get("message") or "").strip()
        if provider_message:
            return f"NewsAPI error: {provider_message}. Displaying cached news."
    return f"NewsAPI returned HTTP status {response.status_code}. Displaying cached news."
