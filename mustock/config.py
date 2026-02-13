from dataclasses import dataclass, field
import os


@dataclass(frozen=True)
class AppConfig:
    default_tickers: list[str] = field(
        default_factory=lambda: os.getenv("WATCH_TICKERS", "MU,AMAT").split(",")
    )
    benchmark_ticker: str = os.getenv("BENCHMARK_TICKER", "SOXX")
    news_api_key: str | None = os.getenv("NEWS_API_KEY")
    lookback_days: int = int(os.getenv("LOOKBACK_DAYS", "420"))
    sentiment_window_days: int = int(os.getenv("SENTIMENT_WINDOW_DAYS", "21"))
    refresh_seconds: int = int(os.getenv("REFRESH_SECONDS", "60"))
    signal_queries: list[str] = field(
        default_factory=lambda: [
            os.getenv("DRAM_SPENDING_QUERY", "DRAM spending demand outlook"),
            os.getenv("AI_DATACENTER_QUERY", "AI datacenter buildout hyperscaler capex"),
            os.getenv("SEMI_CAPEX_QUERY", "semiconductor capex cycle wafer fab expansion"),
        ]
    )
    dram_pricing_queries: list[str] = field(
        default_factory=lambda: [
            "DRAM spot price",
            "DDR5 price trend",
            "HBM pricing",
            "NAND price trend",
        ]
    )
