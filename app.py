from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from mustock.engine import CycleEngine


RANGE_MAP = {
    "1 Day": 1,
    "5 Days": 5,
    "1 Month": 21,
    "5 Months": 105,
    "1 Year": 252,
}


@st.cache_data(ttl=600)
def load_data_and_report():
    engine = CycleEngine()
    data = engine.load_all_data()
    report = engine.build_report(data)
    return engine, data, report


def filter_price_window(price_df: pd.DataFrame, label: str) -> pd.DataFrame:
    window = RANGE_MAP[label]
    return price_df.sort_values("date").tail(window)


def render_dashboard() -> None:
    st.set_page_config(page_title="MU Cycle Monitor", layout="wide")
    st.title("Micron (MU) Cycle Monitor")
    st.caption("Tracks momentum, inventory/capex shifts, DRAM pricing signals, and AI-capex news sentiment.")

    try:
        _engine, data, report = load_data_and_report()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load market/fundamental/news data: {exc}")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cycle Trend", report.trend)
    col2.metric("Composite Score", f"{report.score:.2f}")
    col3.metric("1M Momentum", f"{report.momentum_1m:.1%}")
    col4.metric("Sentiment", f"{report.sentiment:.2f}")

    if report.alerts:
        for alert in report.alerts:
            st.warning(alert)
    else:
        st.success("No critical triggers fired.")

    left, right = st.columns([2, 1])

    with left:
        horizon = st.selectbox("Price window", list(RANGE_MAP.keys()), index=2)
        px_df = filter_price_window(data["price"], horizon)
        fig = px.line(px_df, x="date", y="close", title=f"MU Price ({horizon})")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Cycle Factors")
        factor_df = pd.DataFrame(
            {
                "Factor": ["Momentum 1M", "Momentum 5M", "Capex Acceleration", "Inventory Growth", "Sentiment"],
                "Value": [
                    report.momentum_1m,
                    report.momentum_5m,
                    report.capex_acceleration,
                    report.inventory_growth,
                    report.sentiment,
                ],
            }
        )
        st.dataframe(factor_df, use_container_width=True)

    st.subheader("Theme News")
    if data["news"].empty:
        st.info("No recent themed news items returned from the configured sources.")
    else:
        st.dataframe(
            data["news"][["published", "source", "title", "topic", "url"]].sort_values("published", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("DRAM Pricing Signal Headlines")
    if data["pricing"].empty:
        st.info("Could not scrape DRAM/HBM signal headlines in this run.")
    else:
        st.dataframe(data["pricing"], use_container_width=True, hide_index=True)


if __name__ == "__main__":
    render_dashboard()
