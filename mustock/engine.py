from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .config import AppConfig
from .data_sources.market_api import MarketDataClient
from .data_sources.financial_api import FinancialDataClient
from .data_sources.news_api import NewsClient
from .data_sources.pricing_scraper import PricingScraper


@dataclass
class CycleReport:
    score: float
    trend: str
    alerts: list[str]
    momentum_1m: float
    momentum_5m: float
    capex_acceleration: float
    inventory_growth: float
    sentiment: float


class CycleEngine:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig()
        self.market = MarketDataClient()
        self.financial = FinancialDataClient()
        self.news = NewsClient(api_key=self.config.news_api_key)
        self.pricing = PricingScraper()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def load_all_data(self) -> dict[str, pd.DataFrame]:
        price = self.market.get_price_history(self.config.ticker, self.config.lookback_days)
        relative = self.market.get_relative_performance(
            self.config.ticker,
            self.config.benchmark_ticker,
            self.config.lookback_days,
        )
        fundamentals = self.financial.get_inventory_and_capex(self.config.ticker)

        news_frames = []
        for query in [self.config.dram_query, self.config.ai_capex_query, self.config.hbm_query]:
            frame = self.news.fetch_news(query=query, days_back=self.config.sentiment_window_days)
            if not frame.empty:
                frame["topic"] = query
                news_frames.append(frame)
        news = pd.concat(news_frames, ignore_index=True) if news_frames else pd.DataFrame()

        pricing = self.pricing.collect_dram_price_signals()
        return {
            "price": price,
            "relative": relative,
            "fundamentals": fundamentals,
            "news": news,
            "pricing": pricing,
        }

    @staticmethod
    def compute_momentum(price_df: pd.DataFrame) -> pd.DataFrame:
        df = price_df.copy().sort_values("date")
        df["ret_1d"] = df["close"].pct_change()
        df["mom_5d"] = df["close"].pct_change(5)
        df["mom_21d"] = df["close"].pct_change(21)
        df["mom_105d"] = df["close"].pct_change(105)
        return df

    @staticmethod
    def detect_capex_acceleration(fund_df: pd.DataFrame) -> pd.DataFrame:
        df = fund_df.copy().sort_values("date")
        df["capex_growth"] = df["capex"].pct_change()
        df["inventory_growth"] = df["inventory"].pct_change()
        df["capex_acceleration"] = df["capex_growth"].diff()
        return df

    def score_sentiment(self, news_df: pd.DataFrame, pricing_df: pd.DataFrame) -> float:
        texts: list[str] = []
        if not news_df.empty:
            texts.extend((news_df["title"].fillna("") + ". " + news_df["description"].fillna(""))[:200])
        if not pricing_df.empty:
            texts.extend(pricing_df["headline"].fillna("")[:80])

        if not texts:
            return 0.0

        scores = [self.sentiment_analyzer.polarity_scores(text)["compound"] for text in texts]
        return float(np.mean(scores))

    def build_report(self, data: dict[str, pd.DataFrame]) -> CycleReport:
        momentum = self.compute_momentum(data["price"])
        fund = self.detect_capex_acceleration(data["fundamentals"])
        sentiment = self.score_sentiment(data["news"], data["pricing"])

        latest_mom = momentum.iloc[-1]
        latest_fund = fund.iloc[-1]
        momentum_1m = float(latest_mom["mom_21d"])
        momentum_5m = float(latest_mom["mom_105d"])
        capex_accel = float(latest_fund["capex_acceleration"])
        inventory_growth = float(latest_fund["inventory_growth"])

        composite = 0.45 * momentum_1m + 0.2 * momentum_5m + 0.2 * sentiment - 0.1 * inventory_growth - 0.05 * capex_accel

        alerts: list[str] = []
        if inventory_growth > 0.08:
            alerts.append("Rising inventory detected (>8% QoQ).")
        if capex_accel > 0.15:
            alerts.append("Capex acceleration is high; monitor oversupply risk.")
        if sentiment < -0.15:
            alerts.append("Negative sentiment flow across DRAM/AI capex news.")
        if momentum_1m < -0.08:
            alerts.append("MU short-term momentum has turned bearish.")

        trend = "Bullish" if composite > 0.05 else "Bearish" if composite < -0.05 else "Neutral"

        return CycleReport(
            score=float(composite),
            trend=trend,
            alerts=alerts,
            momentum_1m=momentum_1m,
            momentum_5m=momentum_5m,
            capex_acceleration=capex_accel,
            inventory_growth=inventory_growth,
            sentiment=sentiment,
        )
