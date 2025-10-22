# tasks.md

Date: 2025-10-22
Feature: 美股预测仪表盘

## Overview

This task list is organized by Phase and by User Story (US1 = P1, US2 = P2, US3 = P3). Each task is actionable and includes a file path. Tasks are dependency-ordered; parallelizable tasks are marked with [P]. The suggested MVP scope = User Story 1 (historical chart + reliable data fetch).

---

## Phase 1 — Setup

- [ ] T001 Initialize project structure and create minimal files (`src/`, `data/`, `specs/001-us-predict-dashboard/tasks.md`, `requirements.txt`, `README.md`) — create these paths and add placeholders.
- [ ] T002 Create `requirements.txt` with pinned minimal dependencies (`yfinance`, `pandas`, `numpy`, `pyarrow`, `streamlit`, `pytest`) — file: `requirements.txt` [P]
- [ ] T003 Create a Python 3.11 virtualenv instructions document `specs/001-us-predict-dashboard/quickstart.md` (update with exact commands) — file: `specs/001-us-predict-dashboard/quickstart.md` [P]
- [ ] T004 Add repository-level `.gitignore` entries for `data/*.parquet`, `venv/`, `.pytest_cache/` — file: `.gitignore` [P]

## Phase 2 — Foundational (blocking prerequisites)

- [ ] T005 Implement holiday/trading-day utilities — create `src/utils.py` with functions: `is_trading_day(date) -> bool`, `next_trading_days(start_date, n) -> List[date]`, `load_holiday_calendar()` — file: `src/utils.py`
- [ ] T006 Implement data ingestion module — create `src/data.py` with functions: `fetch_prices(ticker: str) -> pd.DataFrame`, `write_parquet(ticker: str, df: pd.DataFrame)`, `read_parquet(ticker: str) -> pd.DataFrame` (paths: `data/stock_{ticker}.parquet`) — file: `src/data.py`
- [ ] T007 Implement lightweight feature utilities — create `src/features.py` with `sma(prices: pd.Series, window: int) -> pd.Series` and optional `rsi(prices: pd.Series, window: int) -> pd.Series` — file: `src/features.py` [P]
- [ ] T008 Implement prediction interface and stubs — create `src/model.py` with functions signatures: `predict_next_prices(prices: List[float], days: int=3) -> List[float]` and `predict_with_model(prices_df, model_name, days)` (initially implement SMA logic here and leave ARIMA/prophet as optional) — file: `src/model.py`
- [ ] T009 Add basic unit test harness and CI config — create `tests/test_smoke.py` and `pytest.ini`; add a minimal GitHub Actions CI workflow `/.github/workflows/test.yml` that runs pytest — file: `tests/test_smoke.py`, `.github/workflows/test.yml` [P]
- [ ] T010 Implement a small data versioning metadata writer — update `src/data.py` to write `data_version` (timestamp/hash) into parquet metadata or sidecar (e.g., `data/stock_{ticker}.meta.json`) — file: `src/data.py`
- [ ] T011 Create `src/app.py` Streamlit stub that imports modules and renders a simple UI with input for `ticker` and a placeholder chart — file: `src/app.py`

## Phase 3 — User Story Implementation (Priority order)

### US1 — 查询历史与展示 (P1)

Goal: Allow user to input a ticker and see the last 90 days' close prices rendered as a line chart within 1.5s (MVP)
Independent test criteria: Given a valid ticker with >=90 days data, app renders chart and shows last updated timestamp within 1.5s in local dev.

- [ ] T012 [US1] Implement `GET /api/v1/prices/{ticker}` handler (internal function) that reads `data/stock_{ticker}.parquet` and returns last N days as JSON; create function `src/api_prices.py::get_prices(ticker: str, days: int=90) -> dict` — file: `src/api_prices.py`
- [ ] T013 [US1] Wire history fetch into Streamlit UI: update `src/app.py` to call `src/api_prices.get_prices` and render a line chart (use Streamlit `st.line_chart`) — file: `src/app.py`
- [ ] T014 [US1] Implement friendly error handling for invalid tickers or missing data (display user-facing message in Streamlit) — file: `src/app.py` [P]
- [ ] T015 [US1] Unit test: write `tests/test_data_io.py` to validate `read_parquet` and `get_prices` behavior with a small fixture CSV -> parquet — file: `tests/test_data_io.py`
- [ ] T016 [P] Create sample fixture data for tests: `tests/fixtures/aapl_sample.parquet` (generate via `src/data.fetch_prices` or static CSV converted) — file: `tests/fixtures/aapl_sample.parquet`

### US2 — SMA 外推预测 (P2)

Goal: Provide SMA-based 3-day predictions; core function `predict_next_prices(prices, days=3)` must be unit-testable
Independent test criteria: Given a known price sequence, `predict_next_prices` returns expected 3 numeric values and is covered by unit tests.

- [ ] T017 [US2] Implement SMA extrapolation in `src/model.py::predict_next_prices` using `src/features.sma` and a deterministic extrapolation strategy; return List[float] — file: `src/model.py`
- [ ] T018 [US2] Integrate SMA option into Streamlit UI: add a control to select model=`sma` and trigger prediction call to `src/model.predict_next_prices` then display predicted points on the chart — file: `src/app.py`
- [ ] T019 [US2] Add unit tests `tests/test_model_sma.py` to exercise `predict_next_prices` with deterministic inputs — file: `tests/test_model_sma.py`
- [ ] T020 [US2] Update API contract `specs/001-us-predict-dashboard/contracts/prediction.yaml` to ensure `model: sma` is supported and document `include_after_hours: false` default — file: `specs/001-us-predict-dashboard/contracts/prediction.yaml` [P]

### US3 — 时间序列预测 (P3, 可选/受限)

Goal: Provide 5-day time-series forecast with confidence intervals, gated by governance approval for heavy deps.
Independent test criteria: In a mock environment, model returns `predicted_prices` and `confidence_interval` of length 5.

- [ ] T021 [US3] Add gating task: create `specs/001-us-predict-dashboard/CONSTITUTION-APPROVAL.md` to record approval decision for `statsmodels`/`prophet`; do not implement ARIMA/Prophet until approved — file: `specs/001-us-predict-dashboard/CONSTITUTION-APPROVAL.md`
- [ ] T022 [US3] (conditional) Implement ARIMA pipeline in `src/model.py` if governance permits: `train_arima(df)`, `predict_arima(model, days)` and return confidence intervals — file: `src/model.py`
- [ ] T023 [US3] (conditional) Implement Prophet wrapper in `src/model.py` behind a plugin flag (only enable when `requirements.txt` contains `prophet` and `CONSTITUTION-APPROVAL.md` is present) — file: `src/model.py`
- [ ] T024 [US3] Add unit/integration tests for time-series model (mocked data) `tests/test_model_timeseries.py` — file: `tests/test_model_timeseries.py`

## Phase 4 — Scheduling, Retrain & Operations

- [ ] T025 Implement GitHub Actions workflow for daily fetch job: create `/.github/workflows/fetch.yml` to run `src/data.fetch` daily and write parquet — file: `.github/workflows/fetch.yml`
- [ ] T026 Implement GitHub Actions workflow for nightly retrain (daily) and manual workflow_dispatch to enable manual trigger — file: `.github/workflows/retrain.yml`
- [ ] T027 Create admin retrain API or control hook used by Streamlit admin UI that triggers workflow_dispatch (or call to retrain script) — file: `src/admin.py` and `src/app.py` UI element
- [ ] T028 Add logging/monitoring basics: write simple metrics to `logs/` and record `data_version`, `training_metrics` after retrain — file: `src/model.py`, `logs/` [P]

## Phase 5 — Polish & Cross-cutting Concerns

- [ ] T029 Add UI disclaimer and last-updated timestamp prominently in `src/app.py` — file: `src/app.py` [P]
- [ ] T030 Write developer docs: `specs/001-us-predict-dashboard/README-DEV.md` describing how to run tests, fetch data, and run app locally — file: `specs/001-us-predict-dashboard/README-DEV.md` [P]
- [ ] T031 Ensure all public functions have type annotations and Google-style docstrings; run `mypy --strict` and fix issues — file: `src/` (all modules)
- [ ] T032 Create a checklist task to perform a constitution compliance review before merging (verify no banned deps) — file: `specs/001-us-predict-dashboard/checklists/requirements.md`

---

## Dependencies & Execution Order

1. Phase 1 tasks (T001-T004) must complete first.
2. Phase 2 foundational tasks (T005-T011) block User Story phases.
3. US1 (T012-T016) should be delivered first (MVP).
4. US2 (T017-T020) depends on T005,T006,T007,T008 and US1 completion.
5. US3 (T021-T024) is conditional on governance approval and depends on T005-T011.
6. Scheduling tasks (T025-T027) can be partially parallelized but require T006 (data IO) in place.

## Parallel Opportunities

- Tasks marked [P] are parallelizable (e.g., creating `requirements.txt`, fixtures, and some tests).
- Feature implementation (US1 UI wiring) and CI workflow creation can run in parallel after foundational tasks.

## Counts & Summary

- Total tasks: 32
- Tasks per story:
  - US1: 5 tasks (T012-T016)
  - US2: 4 tasks (T017-T020)
  - US3: 4 tasks (T021-T024) — conditional
  - Setup + Foundational + Ops + Polish: 19 tasks (T001-T011, T025-T032)
- Suggested MVP scope: Complete Phase 1 + Phase 2 + US1 (T001-T016). This provides a working Streamlit app that displays historical charts and passes core tests.

## Implementation strategy

1. Deliver MVP quickly (US1): ensure `data.fetch`, `read_parquet`, and `src/app.py` chart render. Use sample fixtures and unit tests.
2. Add SMA prediction (US2) next and include unit tests.
3. Gate heavier time-series models (US3) behind governance approval (explicit approval file). If approved, implement ARIMA/Prophet pipelines.
4. Use GitHub Actions for scheduled fetch & retrain — keep operational complexity minimal in MVP.

\*\*\* End of tasks.md
