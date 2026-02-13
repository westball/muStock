from __future__ import annotations

import re
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup


class PricingScraper:
    """Scrapes DRAM-pricing related headlines as a directional proxy signal."""

    TARGETS = [
        "https://www.trendforce.com/presscenter/news",
        "https://www.anandtech.com/tag/memory",
    ]

    def collect_dram_price_signals(self) -> pd.DataFrame:
        rows: list[dict] = []
        for url in self.TARGETS:
            try:
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
            except requests.RequestException:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup.find_all(["a", "h2", "h3"])[:100]:
                text = " ".join(tag.get_text(" ", strip=True).split())
                if len(text) < 25:
                    continue
                if re.search(r"dram|memory|hbm", text, re.IGNORECASE):
                    rows.append(
                        {
                            "date": datetime.utcnow().strftime("%Y-%m-%d"),
                            "headline": text,
                            "source_url": url,
                        }
                    )
        return pd.DataFrame(rows).drop_duplicates(subset=["headline"])
