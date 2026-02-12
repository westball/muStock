from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    ticker: str = os.getenv("MU_TICKER", "MU")
    benchmark_ticker: str = os.getenv("BENCHMARK_TICKER", "SOXX")
    news_api_key: str | None = os.getenv("NEWS_API_KEY")
    lookback_days: int = int(os.getenv("LOOKBACK_DAYS", "420"))
    sentiment_window_days: int = int(os.getenv("SENTIMENT_WINDOW_DAYS", "14"))
    dram_query: str = os.getenv("DRAM_QUERY", "DRAM spot price trendforce")
    ai_capex_query: str = os.getenv("AI_CAPEX_QUERY", "AI capex slowdown hyperscaler")
    hbm_query: str = os.getenv("HBM_QUERY", "Samsung HBM4 capacity expansion")
