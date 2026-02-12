from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import quote_plus
import requests
import feedparser
import pandas as pd


class NewsClient:
    """Collects theme-specific news from NewsAPI (if key provided) or Google News RSS."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def fetch_news(self, query: str, days_back: int = 14, limit: int = 30) -> pd.DataFrame:
        if self.api_key:
            return self._from_newsapi(query=query, days_back=days_back, limit=limit)
        return self._from_google_rss(query=query, limit=limit)

    def _from_newsapi(self, query: str, days_back: int, limit: int) -> pd.DataFrame:
        url = "https://newsapi.org/v2/everything"
        frm = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        params = {
            "q": query,
            "from": frm,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": min(limit, 100),
            "apiKey": self.api_key,
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("articles", [])
        rows = [
            {
                "title": row.get("title", ""),
                "description": row.get("description", ""),
                "source": row.get("source", {}).get("name", ""),
                "published": row.get("publishedAt", ""),
                "url": row.get("url", ""),
            }
            for row in data
        ]
        return pd.DataFrame(rows)

    def _from_google_rss(self, query: str, limit: int) -> pd.DataFrame:
        rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        rows = []
        for entry in feed.entries[:limit]:
            rows.append(
                {
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", ""),
                    "source": entry.get("source", {}).get("title", "Google News"),
                    "published": entry.get("published", ""),
                    "url": entry.get("link", ""),
                }
            )
        return pd.DataFrame(rows)
