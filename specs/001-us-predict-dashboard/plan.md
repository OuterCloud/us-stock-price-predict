# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

实现一个极简的美股预测仪表盘：用户输入美股代码，展示过去 90 天收盘价并提供 SMA（3 天）外推和可选的时间序列（5 天）预测。技术方案以“依赖最小化”和“可测性”为优先，采用 `yfinance` 获取数据、将每日原始数据以 Parquet 存储于 `data/stock_{ticker}.parquet`，前端采用 Streamlit 单文件 `app.py`（MVP），调度与自动重训练通过 GitHub Actions（每日夜间 + 支持手动触发）。预测主模型采用轻量可审计的 ARIMA/SARIMAX（statsmodels）；将 Prophet 标记为可选/插件式方案，仅在治理审批通过后启用（用于更完善的节假日建模）。

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (recommend)
**Primary Dependencies**: `yfinance`, `pandas`, `numpy`, `statsmodels` (ARIMA/SARIMAX), `streamlit`, `pyarrow` (parquet), `pytest`.
**Optional/Plugin Dependencies**: `prophet` (Meta/Prophet) — marked as optional and subject to governance approval.
**Storage**: Local parquet files under `data/stock_{ticker}.parquet` for time-series storage; parquet chosen for compactness and fast columnar reads.
**Testing**: `pytest` for unit and integration tests; tests for data load, SMA logic, prediction function outputs and boundary cases.
**Target Platform**: Deploy on Streamlit Community Cloud (MVP) or lightweight container on cloud VM for more control.
**Project Type**: Single web-app (MVP) with a small backend-like data pipeline executed via GitHub Actions for scheduled fetch/train.
**Performance Goals**: 95% of valid requests render initial chart within 1.5s (SC-001). Prediction functions must run quickly enough for pre-computation or on-demand with caching.
**Constraints**: Minimize third-party heavy ML libraries; model implementations must be testable and mockable; single-file UI constraint for MVP (keep `app.py` concise — consider moving heavy logic to modules under `src/` if exceeding limits).
**Scale/Scope**: Initially low traffic (developer/early users); design for modest scale (hundreds daily). Use GitHub Actions for scheduled jobs; avoid operational heavy infra in MVP.

## Constitution Check

GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.

Review of chosen technologies vs. project constitution (high level):

- Dependency minimization: `yfinance`, `pandas`, `numpy`, `statsmodels`, `pyarrow`, `streamlit`, `pytest` are lightweight/common and acceptable under the constitution's emphasis on minimal dependencies. PASS (justify using known, widely used packages).
- Use of `prophet` (optional): CONCERN — constitution previously flagged large ML libraries like Prophet as restricted and requiring additional approval. ACTION: treat `prophet` as an optional plugin that is NOT enabled by default. To include `prophet` the plan must document justification, license review, and security/CVE check. Gate: PASS only after approval and CVE check.
- Storage & infra: parquet + Streamlit Community Cloud are low-footprint choices; acceptable. PASS.

Result: Phase 0 may proceed, but the `prophet` choice is considered a gated optional dependency and requires governance approval before enabling in production.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: Use a single web-app layout with small supporting modules.
Project structure (concrete):

```text
specs/001-us-predict-dashboard/
├── plan.md
├── research.md
├── data-model.md    # (Phase 1)
├── quickstart.md    # (Phase 1)
├── contracts/       # (Phase 1)
└── tasks.md         # (Phase 2)

src/
├── app.py           # Streamlit entry (minimal glue)
├── data.py          # data fetch (yfinance), read/write parquet
├── features.py      # feature engineering (SMA, RSI)
├── model.py         # model training/predict interfaces (ARIMA primary, prophet optional)
├── utils.py         # helpers (trading day calendar, holiday handling)
└── tests/           # pytest tests

data/
└── stock_{ticker}.parquet
```

Rationale: keeps UI minimal, places heavier logic in testable modules, satisfies single-file UI constraint while allowing modularity for testing and clarity.

## Phase 0 Output

- research.md created: `specs/001-us-predict-dashboard/research.md`

## Phase 1: Planned artifacts

- `data-model.md` — entities and fields, validation rules (to be generated)
- `contracts/` — API contract files (OpenAPI minimal endpoints for data/predict)
- `quickstart.md` — how to run locally and deploy to Streamlit Community Cloud

Phase 1 prerequisites: `research.md` complete (done). Proceed to generate `data-model.md` and `contracts/`.
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation                  | Why Needed         | Simpler Alternative Rejected Because |
| -------------------------- | ------------------ | ------------------------------------ |
| [e.g., 4th project]        | [current need]     | [why 3 projects insufficient]        |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient]  |
