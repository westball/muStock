from __future__ import annotations

from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf


class MarketDataClient:
    """Fetches stock history and benchmark-relative data using yfinance."""

    def get_price_history(self, ticker: str, lookback_days: int = 420) -> pd.DataFrame:
        end = datetime.utcnow()
        start = end - timedelta(days=lookback_days)
        frame = yf.download(ticker, start=start.date(), end=end.date(), progress=False, auto_adjust=True)
        if frame.empty:
            raise ValueError(f"No market data returned for {ticker}")

        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = [col[0] for col in frame.columns]

        frame = frame.reset_index().rename(columns=str.lower)
        required = ["date", "open", "high", "low", "close", "volume"]
        missing = [c for c in required if c not in frame.columns]
        if missing:
            raise KeyError(f"Missing expected market fields: {missing}")
        return frame[required]

    def get_relative_performance(
        self,
        ticker: str,
        benchmark: str,
        lookback_days: int = 420,
    ) -> pd.DataFrame:
        stock = self.get_price_history(ticker, lookback_days).set_index("date")
        bench = self.get_price_history(benchmark, lookback_days).set_index("date")
        merged = stock[["close"]].join(bench[["close"]], how="inner", lsuffix="_stock", rsuffix="_benchmark")
        merged["relative_strength"] = merged["close_stock"] / merged["close_benchmark"]
        return merged.reset_index()
