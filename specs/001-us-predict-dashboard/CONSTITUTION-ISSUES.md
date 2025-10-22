# Constitution Gate: Conflicts & Remediation

Date: 2025-10-22
Feature: 美股预测仪表盘

During Phase 0 checks we detected a governance conflict between the chosen technical stack and the project's constitution:

- Conflict A: `statsmodels` was selected for ARIMA/SARIMAX, but the project constitution explicitly lists `statsmodels` as a prohibited dependency.
- Conflict B: `prophet` (Meta/Prophet) is proposed as an optional plugin for better holiday modeling, but the constitution prohibits Prophet and similar large ML libraries without explicit approval.

These conflicts prevent an unconditional pass of the constitution gate. Recommended remediation options:

1. Amend the constitution to permit `statsmodels` and optionally `prophet` after a review (requires governance approval and CVE/license checks). This is recommended if time-series modeling is required for MVP.
2. Drop `statsmodels`/`prophet` and implement a strictly lightweight approach (SMA-only for MVP) to remain fully compliant with the current constitution.
3. Isolate heavy modeling in a separate repository/service that can adopt heavier dependencies; keep the main repo constitution-compliant and call the model service via an API.

Please choose one of the above remediation paths so Phase 1 design can proceed without governance violations.
