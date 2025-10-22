from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

import pandas as pd
import yfinance as yf

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def _meta_path(ticker: str) -> Path:
    return DATA_DIR / f"stock_{ticker}.meta.json"


def _data_path(ticker: str) -> Path:
    return DATA_DIR / f"stock_{ticker}.parquet"


def fetch_prices(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetch historical prices using yfinance and return a normalized DataFrame.

    Raises ValueError when no data is returned. Caller should handle network errors.
    """
    if not ticker or not isinstance(ticker, str):
        raise ValueError("ticker must be a non-empty string")

    yf_ticker = yf.Ticker(ticker)
    df = yf_ticker.history(period=period)
    if df is None or df.empty:
        raise ValueError(f"No data for ticker {ticker}")
    df = df.reset_index()
    # normalize column names to lower-case expected names
    df.rename(
        columns={
            "Date": "date",
            "Close": "close",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Volume": "volume",
        },
        inplace=True,
    )
    df["fetched_at"] = datetime.utcnow()
    return df


def write_parquet(ticker: str, df: pd.DataFrame, meta: Dict | None = None) -> Path:
    """Write DataFrame to parquet and write a small JSON sidecar with metadata.

    Returns the path written to.
    """
    if df is None or df.empty:
        raise ValueError("df must be a non-empty DataFrame")
    path = _data_path(ticker)
    # ensure directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)

    meta = meta or {}
    meta.setdefault("written_at", datetime.utcnow().isoformat())
    meta.setdefault("rows", int(len(df)))
    _meta_path(ticker).write_text(json.dumps(meta, ensure_ascii=False))
    return path


def read_parquet(ticker: str) -> pd.DataFrame:
    """Read stored parquet for a ticker. Raises FileNotFoundError when missing."""
    path = _data_path(ticker)
    if not path.exists():
        raise FileNotFoundError(f"No data file for ticker {ticker}")
    df = pd.read_parquet(path)
    # normalize date column type if present
    if "date" in df.columns:
        try:
            df["date"] = pd.to_datetime(df["date"])
        except Exception:
            # keep original if parsing fails
            pass
    return df
