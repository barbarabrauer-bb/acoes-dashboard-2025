# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the app
/Users/barbarasoaresbrauer/Library/Python/3.9/bin/streamlit run app.py

# Run with headless mode (no browser auto-open)
/Users/barbarasoaresbrauer/Library/Python/3.9/bin/streamlit run app.py --server.headless true
```

The app runs at `http://localhost:8501`.

## Architecture

Single-file Streamlit app (`app.py`). No backend/frontend split — Streamlit renders everything server-side in Python.

**Data flow:**
1. User selects stocks and date range in the sidebar
2. `carregar_dados()` fetches OHLCV data from Yahoo Finance via `yfinance` (cached for 1 hour with `@st.cache_data`)
3. Three Plotly charts render from the cached DataFrames: line (closing price), line (cumulative % return), bar (daily R$ change)
4. A summary table is computed inline from the same DataFrames

**Key constants:**
- `ACOES` — maps display name → Yahoo Finance ticker (e.g. `"VALE3"` → `"VALE3.SA"`)
- `CORES` — hex color per stock used across all charts

**Adding a new stock:** add an entry to both `ACOES` and `CORES` in `app.py` — the rest of the rendering loops pick it up automatically.

**Data note:** `yfinance` returns a MultiIndex DataFrame when downloading multiple tickers at once; here each ticker is fetched individually, so `.squeeze()` is used to flatten the single-column result.
