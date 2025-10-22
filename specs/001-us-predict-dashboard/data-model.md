# data-model.md

Date: 2025-10-22
Feature: 美股预测仪表盘

## Entities

### TickerData

- Description: 存储单个股票的历史时序数据
- Storage path: `data/stock_{ticker}.parquet`
- Fields:
  - `date` (date, yyyy-mm-dd) — 交易日日期，按升序
  - `open` (float)
  - `high` (float)
  - `low` (float)
  - `close` (float)
  - `adjusted_close` (float, optional)
  - `volume` (int)
  - `source_updated_at` (datetime) — 数据源返回的时间戳
  - `fetched_at` (datetime) — 本地抓取时间
- Validation rules:
  - `date` must be trading day (weekdays excluding market holidays)
  - No duplicate (`date`) rows
  - `close` must be non-null for rows used in prediction

### PredictionResult

- Description: 返回给前端的预测输出
- Fields:
  - `ticker` (string)
  - `model` (string) — e.g., "sma", "arima", "prophet"
  - `predicted_dates` (List[date]) — only trading days (exclude weekends/holidays)
  - `predicted_prices` (List[float])
  - `confidence_interval` (optional, List[Tuple[float,float]])
  - `generated_at` (datetime)
  - `data_version` (string) — hash or timestamp of input data used
- Validation rules:
  - `len(predicted_dates) == len(predicted_prices)`
  - If `confidence_interval` present, same length as `predicted_prices`

## Relationships

- `TickerData` feeds into `PredictionResult` via model pipeline.

## State & Lifecycle

- `TickerData` updated daily by fetch job; persisted as parquet per ticker.
- Predictions are generated on-demand or by scheduled retrain jobs; prediction metadata recorded with `generated_at` and `data_version`.

## Notes

- Holiday calendar handling MUST be centralized in `utils.py` and used both for data validation and prediction date generation.

\*\*\* End of data-model.md
