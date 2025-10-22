# research.md

Date: 2025-10-22
Feature: 美股预测仪表盘

## Decisions, Rationale, Alternatives

### Decision: Data Source — `yfinance`

- Decision: Use `yfinance` for MVP data fetching.
- Rationale: Free, widely used for prototyping, easy to integrate with pandas.
- Alternatives considered:
  - Paid market data APIs (IEX Cloud, AlphaVantage paid tiers) — more reliable and lower latency but add cost and keys to manage.
  - Direct exchange feeds — out of scope for MVP.

### Decision: Storage — Parquet files under `data/stock_{ticker}.parquet`

- Decision: Store daily fetched data as parquet files per ticker.
- Rationale: Parquet is compact, columnar, and fast for time-series reads with pandas/pyarrow.
- Alternatives:
  - SQLite/Postgres — adds infra complexity; suitable for larger scale.
  - CSV — simpler but slower and less efficient.

### Decision: Feature engineering

- Decision: Implement SMA (mandatory) and RSI (optional) in `features.py`.
- Rationale: SMA is required by spec; RSI provides extra signal without heavy dependencies.
- Alternatives:
  - More complex features (momentum, volatility) can be added later.

### Decision: Model

- Decision: Primary: ARIMA/SARIMAX (statsmodels). Optional plugin: Prophet (subject to governance approval).
- Rationale: ARIMA is lightweight, deterministic, testable and well-understood. Prophet is convenient for holidays but is heavier and requires governance approval per constitution.
- Alternatives:
  - Prophet as primary: easier holiday handling but heavier dependency (approval needed).
  - ML models (LSTM): out of scope for MVP due to complexity and infra needs.

### Decision: UI & Deployment

- Decision: Streamlit single-file `app.py` for MVP, deploy on Streamlit Community Cloud.
- Rationale: Fast to iterate, free tier available, matches single-file UI constraint for MVP.
- Alternatives:
  - Lightweight Flask + static front-end — more control but more initial work.

### Decision: Scheduling & Retrain

- Decision: Use GitHub Actions for scheduled daily fetch and nightly retrain; provide manual retrain trigger (GitHub workflow dispatch or admin UI button invoking an API).
- Rationale: Low-ops, integrates with repo, easy to audit and reproduce runs.
- Alternatives:
  - External scheduler (e.g., Cloud Run cron) — more infra complexity.

### Decision: Testing

- Decision: Use `pytest` for unit tests covering data ingestion, SMA logic, model predict function, and edge cases (insufficient data, invalid tickers).
- Rationale: Standard Python testing toolchain, integrates with CI.

## Open Items / NEEDS CLARIFICATION

- Prophet governance approval (license/CVE/security review) — deferred until requested.
- Data licensing for production usage if moving beyond MVP — recommend review before production.

## Next steps (Phase 1 prerequisites)

- Implement data ingestion module `src/data.py` with functions:
  - `fetch_prices(ticker: str) -> pd.DataFrame` (uses yfinance)
  - `write_parquet(ticker: str, df: pd.DataFrame)`
  - `read_parquet(ticker: str) -> pd.DataFrame`
- Implement `src/features.py` (SMA, RSI)
- Implement `src/model.py` with ARIMA training/predict API and plugin hook for Prophet
- Create GitHub Actions workflows for fetch and retrain
- Create `src/app.py` minimal Streamlit front-end wiring the pieces
- Write pytest unit tests for `data.py`, `features.py`, `model.py`

\*\*\* End of research.md
