from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from mustock.config import AppConfig
from mustock.engine import CycleEngine


RANGE_MAP = {
    "1 Day": 1,
    "5 Days": 5,
    "1 Month": 21,
    "5 Months": 105,
    "1 Year": 252,
}


@st.cache_data(ttl=60)
def load_data_and_report(ticker: str):
    engine = CycleEngine()
    data = engine.load_all_data(ticker=ticker)
    report = engine.build_report(data)
    return data, report


def filter_price_window(price_df: pd.DataFrame, label: str) -> pd.DataFrame:
    window = RANGE_MAP[label]
    return price_df.sort_values("date").tail(window)


def render_link_list(news_df: pd.DataFrame, title: str) -> None:
    st.subheader(title)
    if news_df.empty:
        st.info("No recent items returned from configured sources.")
        return

    for _, row in news_df.head(15).iterrows():
        source = row.get("source", "source")
        published = row.get("published", row.get("date", ""))
        link = row.get("url", "")
        headline = row.get("title", row.get("headline", "headline"))
        st.markdown(f"- [{headline}]({link}) — *{source}* ({published})")


def render_stock_tab(ticker: str, horizon: str) -> None:
    try:
        data, report = load_data_and_report(ticker)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load {ticker} data: {exc}")
        return

    intraday = data["intraday"].sort_values("datetime")
    last_px = float(intraday["close"].iloc[-1]) if not intraday.empty else float(data["price"]["close"].iloc[-1])
    open_px = float(intraday["close"].iloc[0]) if not intraday.empty else float(data["price"]["close"].iloc[-2])
    day_change = (last_px / open_px) - 1 if open_px else 0.0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(
        f"{ticker} Live Price",
        f"${last_px:.2f}",
        f"{day_change:.2%}",
        help="Near real-time 1-minute price feed via yfinance. Auto-refreshes every 60 seconds.",
    )
    c2.metric("Cycle Trend", report.trend, help="Bullish/Neutral/Bearish based on weighted composite score.")
    c3.metric("Composite Score", f"{report.score:.2f}", help=report.explanation)
    c4.metric("1M Momentum", f"{report.momentum_1m:.1%}", help="21-trading-day price return.")
    c5.metric("Sentiment", f"{report.sentiment:.2f}", help="Average VADER sentiment from themed news and pricing headlines.")

    st.caption(report.explanation)

    for alert in report.alerts:
        st.warning(alert)
    if not report.alerts:
        st.success("No critical triggers fired.")

    left, right = st.columns([2, 1])

    with left:
        px_df = filter_price_window(data["price"], horizon)
        fig = px.line(
            px_df,
            x="date",
            y="close",
            title=f"{ticker} Price ({horizon})",
            template="plotly_dark",
            labels={"close": "Price", "date": "Date"},
        )
        fig.update_traces(hovertemplate="Date: %{x}<br>Close: $%{y:.2f}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)

        if not intraday.empty:
            live_fig = px.line(
                intraday,
                x="datetime",
                y="close",
                title=f"{ticker} Intraday (1m)",
                template="plotly_dark",
            )
            live_fig.update_traces(hovertemplate="Time: %{x}<br>Price: $%{y:.2f}<extra></extra>")
            st.plotly_chart(live_fig, use_container_width=True)

    with right:
        st.subheader("Cycle Factors")
        factor_df = pd.DataFrame(
            {
                "Factor": ["Momentum 1M", "Momentum 5M", "CapEx Acceleration", "Inventory Growth", "Sentiment"],
                "Value": [
                    report.momentum_1m,
                    report.momentum_5m,
                    report.capex_acceleration,
                    report.inventory_growth,
                    report.sentiment,
                ],
                "Description": [
                    "21-day return, faster trend.",
                    "105-day return, cycle trend.",
                    "QoQ change in capex growth (higher can imply expansion risk).",
                    "QoQ inventory change (higher can imply demand softness).",
                    "News tone for DRAM spend, AI buildout, semicap cycles.",
                ],
            }
        )
        st.dataframe(factor_df, use_container_width=True, hide_index=True)

    render_link_list(data["news"].sort_values("published", ascending=False), "Signal News (click to open)")
    render_link_list(data["pricing"].sort_values("date", ascending=False), "DRAM/HBM Pricing Headlines (click to open)")


def render_dashboard() -> None:
    st.set_page_config(page_title="MU + AMAT Cycle Monitor", layout="wide")
    st.title("Semiconductor Cycle Monitor")
    st.caption("Tracks DRAM spending, AI datacenter buildout, and semiconductor CapEx-cycle signals.")

    cfg = AppConfig()
    st_autorefresh(interval=cfg.refresh_seconds * 1000, key="market-refresh")
    horizon = st.selectbox("Price window", list(RANGE_MAP.keys()), index=2)

    tabs = st.tabs(cfg.default_tickers)
    for i, ticker in enumerate(cfg.default_tickers):
        with tabs[i]:
            render_stock_tab(ticker.strip().upper(), horizon)


if __name__ == "__main__":
    render_dashboard()
