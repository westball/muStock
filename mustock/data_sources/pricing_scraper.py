from __future__ import annotations

from datetime import datetime
from urllib.parse import quote_plus
import pandas as pd
import feedparser


class PricingScraper:
    """Collects DRAM/HBM pricing headlines from query-based news RSS feeds."""

    def collect_dram_price_signals(self, queries: list[str]) -> pd.DataFrame:
        rows: list[dict] = []
        for query in queries:
            rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:15]:
                rows.append(
                    {
                        "date": entry.get("published", datetime.utcnow().strftime("%Y-%m-%d")),
                        "headline": entry.get("title", ""),
                        "source": entry.get("source", {}).get("title", "Google News"),
                        "url": entry.get("link", ""),
                        "query": query,
                    }
                )
        if not rows:
            return pd.DataFrame(columns=["date", "headline", "source", "url", "query"])
        return pd.DataFrame(rows).drop_duplicates(subset=["headline", "url"])
