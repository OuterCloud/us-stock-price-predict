from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import yfinance as yf
import requests
import io
import os
import time
import tempfile
import random
import logging
# typing imports not required

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def _meta_path(ticker: str) -> Path:
    return DATA_DIR / f"stock_{ticker}.meta.json"


def _data_path(ticker: str) -> Path:
    return DATA_DIR / f"stock_{ticker}.parquet"


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    # normalize column names to lower-case expected names and ensure date
    df = df.reset_index()
    df.rename(
        columns={
            "Date": "date",
            "date": "date",
            "Close": "close",
            "Adj Close": "adj_close",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Volume": "volume",
        },
        inplace=True,
    )
    df["fetched_at"] = datetime.utcnow()
    if "date" in df.columns:
        try:
            df["date"] = pd.to_datetime(df["date"])
        except Exception:
            # leave as-is if parsing fails
            pass
    return df


def fetch_prices(ticker: str, period: str = "1y", max_retries: int = 4) -> pd.DataFrame:
    """Fetch historical prices using yfinance with retries and fallback.

    This function attempts to be resilient to transient network errors and
    provider rate-limiting (HTTP 429). It will retry with exponential backoff
    and jitter. If `Ticker.history` returns empty, it attempts a `yf.download`
    fallback. Raises ValueError when no data is returned after retries.
    """
    if not ticker or not isinstance(ticker, str):
        raise ValueError("ticker must be a non-empty string")

    attempt = 0
    last_exc: Optional[Exception] = None
    while attempt < max_retries:
        attempt += 1
        try:
            yf_ticker = yf.Ticker(ticker)
            df = yf_ticker.history(period=period)
            if df is None or df.empty:
                # try fallback to yf.download which sometimes behaves differently
                df = yf.download(ticker, period=period, progress=False)
            # final fallback: try direct CSV download from Yahoo Finance to detect 429
            if df is None or df.empty:
                try:
                    url = (
                        f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
                        f"?period1=0&period2=9999999999&interval=1d&events=history"
                    )
                    headers = {"User-Agent": "python-requests/1.0"}
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code == 429:
                        # save a small debug copy of the response body to help diagnosis
                        try:
                            dbg = DATA_DIR / f"debug_{ticker}.txt"
                            dbg.write_text(resp.text[:4096])
                        except Exception:
                            pass
                        raise RuntimeError(
                            f"Yahoo Finance rate limited (HTTP 429) when fetching {ticker}"
                        )
                    resp.raise_for_status()
                    text = resp.text
                    if not text:
                        raise ValueError("Empty response from Yahoo download endpoint")
                    df = pd.read_csv(io.StringIO(text), parse_dates=["Date"])
                except Exception:
                    # allow outer handler to process/backoff
                    pass
            if df is None or df.empty:
                raise ValueError(f"No data for ticker {ticker} (attempt {attempt})")
            return _normalize_df(df)
        except Exception as exc:
            last_exc = exc
            # If yfinance failed due to unexpected/empty response (JSON parse),
            # try a direct CSV fetch immediately to detect HTTP 429 or recoverable CSV.
            emsg = str(exc).lower()
            if (
                "expecting value" in emsg
                or "no json object" in emsg
                or "no price data found" in emsg
                or "empty response" in emsg
            ):
                try:
                    url = (
                        f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
                        f"?period1=0&period2=9999999999&interval=1d&events=history"
                    )
                    # use a browser-like user-agent to reduce automated-blocking
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                    }
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code == 429:
                        logging.warning(
                            "Detected HTTP 429 for %s via direct CSV fetch", ticker
                        )
                        raise RuntimeError(
                            f"Yahoo Finance rate limited (HTTP 429) when fetching {ticker}"
                        )
                    resp.raise_for_status()
                    text = resp.text
                    if text:
                        try:
                            df = pd.read_csv(io.StringIO(text), parse_dates=["Date"])
                            return _normalize_df(df)
                        except Exception:
                            # if parsing fails, fall through to retry/backoff
                            pass
                except Exception as csv_exc:
                    # attach additional context but continue with original flow
                    logging.info(
                        "Direct CSV attempt for %s failed: %s", ticker, csv_exc
                    )
                    last_exc = csv_exc
            # detect rate-limit hints in the exception or message
            msg = str(exc).lower()
            if "429" in msg or "too many requests" in msg or "rate" in msg:
                # when rate-limited, wait longer: exponential backoff with a larger cap
                # cap at 30 minutes (1800s) to avoid hammering the endpoint
                wait = min(1800, (60 * (2 ** (attempt - 1))) + random.random())
                logging.warning(
                    "Rate limited when fetching %s (attempt %d), sleeping %.1fs",
                    ticker,
                    attempt,
                    wait,
                )
                time.sleep(wait)
                continue
            # for other transient network issues, backoff and retry
            if attempt < max_retries:
                wait = (2**attempt) + random.random()
                logging.info(
                    "fetch_prices transient error for %s: %s (attempt %d), retrying in %.1fs",
                    ticker,
                    exc,
                    attempt,
                    wait,
                )
                time.sleep(wait)
                continue
            # exhausted retries
            logging.exception(
                "fetch_prices failed for %s after %d attempts", ticker, attempt
            )
            raise
    # if we exit loop without returning, raise the last exception or a generic error
    if last_exc:
        raise last_exc
    raise ValueError(f"Failed to fetch prices for {ticker}")


def write_parquet(ticker: str, df: pd.DataFrame, meta: Dict | None = None) -> Path:
    """Write DataFrame to parquet and write a small JSON sidecar with metadata.

    Returns the path written to.
    """
    if df is None or df.empty:
        raise ValueError("df must be a non-empty DataFrame")
    path = _data_path(ticker)
    # ensure directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Write to temp file then atomically move into place to avoid half-written files
    tmp_fd, tmp_path = tempfile.mkstemp(
        suffix=".parquet", prefix=f"{ticker}-", dir=DATA_DIR
    )
    os.close(tmp_fd)
    try:
        df.to_parquet(tmp_path, index=False)
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

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


def fetch_and_update_parquet(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetch latest data for `ticker` and merge with existing parquet.

    - If parquet exists: read it, fetch remote, concat, deduplicate by `date` and overwrite parquet.
    - If parquet does not exist: fetch and write a new parquet file.

    Returns the up-to-date DataFrame that was written.
    """
    # Fetch remote data (may raise ValueError on no data). Add simple retry/backoff.
    retries = 3
    delay = 1.0
    new_df = None
    for attempt in range(1, retries + 1):
        try:
            new_df = fetch_prices(ticker, period=period)
            break
        except Exception:
            if attempt == retries:
                raise
            time.sleep(delay)
            delay *= 2
    # Ensure date column is datetime
    if "date" in new_df.columns:
        new_df["date"] = pd.to_datetime(new_df["date"])

    path = _data_path(ticker)
    if path.exists():
        try:
            existing = read_parquet(ticker)
        except Exception:
            # if read failed for any reason, treat as missing
            existing = pd.DataFrame()

        if existing is None or existing.empty:
            merged = new_df.copy()
        else:
            # concat and deduplicate by date, prefer newest rows
            merged = pd.concat([existing, new_df], ignore_index=True, sort=False)
            if "date" in merged.columns:
                merged["date"] = pd.to_datetime(merged["date"])
                merged.sort_values(by="date", inplace=True)
                merged = merged.drop_duplicates(
                    subset=["date"], keep="last"
                ).reset_index(drop=True)
            else:
                # fallback: drop exact-duplicate rows
                merged = merged.drop_duplicates().reset_index(drop=True)
    else:
        merged = new_df.copy()

    # write back
    write_parquet(ticker, merged, meta={"merged_at": datetime.utcnow().isoformat()})
    return merged
