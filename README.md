# MU Stock Cycle Monitor

A Python + Streamlit app that aggregates market, financial, and internet/news indicators to help evaluate whether Micron (MU) is likely to continue up or down.

## What it tracks
- **Stock price + momentum** (1 day, 5 days, 1 month, 5 months, 1 year views)
- **Financial statement stress** proxies:
  - Rising **inventory**
  - **Capex acceleration** (oversupply warning)
- **Internet/news signals**:
  - DRAM pricing headlines
  - AI capex slowdown headlines
  - Industry capacity expansion headlines (e.g., HBM4)
- **Sentiment score** from themed news flow
- **Trigger alerts** when warning thresholds are crossed

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL printed by Streamlit (typically <http://localhost:8501>).

## Optional configuration
Use environment variables:

- `MU_TICKER` (default `MU`)
- `BENCHMARK_TICKER` (default `SOXX`)
- `NEWS_API_KEY` (optional; if unset, Google News RSS is used)
- `LOOKBACK_DAYS` (default `420`)
- `SENTIMENT_WINDOW_DAYS` (default `14`)
- `DRAM_QUERY`, `AI_CAPEX_QUERY`, `HBM_QUERY`

## Notes
- Financial statement field names can vary by ticker/provider; this app uses robust matching but may need extension.
- Web scraping targets can change HTML structures; update selectors/targets in `pricing_scraper.py` if needed.
