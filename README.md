# MU + AMAT Cycle Monitor

A Python + Streamlit app that aggregates market, financial, and internet/news indicators to evaluate Micron (`MU`) and Applied Materials (`AMAT`) cycle direction.

## What it tracks
- **Multi-stock tabs** (MU and AMAT by default)
- **Near real-time stock performance** (1-minute intraday with auto-refresh)
- **Time windows**: 1 day, 5 days, 1 month, 5 months, 1 year
- **Signal themes for scoring**:
  - DRAM spending
  - AI datacenter buildout
  - Semiconductor CapEx cycles
- **Financial stress proxies**:
  - inventory growth
  - capex acceleration
- **DRAM/HBM pricing headlines** with clickable links
- **Composite score explanations** and hover help on dashboard metrics
- **Trigger alerts** when warning thresholds are crossed

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional configuration
Use environment variables:

- `WATCH_TICKERS` (default `MU,AMAT`)
- `BENCHMARK_TICKER` (default `SOXX`)
- `NEWS_API_KEY` (optional; if unset, Google News RSS is used)
- `LOOKBACK_DAYS` (default `420`)
- `SENTIMENT_WINDOW_DAYS` (default `21`)
- `REFRESH_SECONDS` (default `60`)
- `DRAM_SPENDING_QUERY`, `AI_DATACENTER_QUERY`, `SEMI_CAPEX_QUERY`

## Notes
- Intraday data quality depends on upstream market data availability.
- Financial statement field names can vary by ticker/provider.
