from __future__ import annotations

import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple moving average. Returns a Series with the same index as input.

    window must be >= 1. If window > len(series) the result will be NaN except
    where pandas can compute partial windows.
    """
    if window < 1:
        raise ValueError("window must be >= 1")
    if series is None or len(series) == 0:
        return pd.Series(dtype=float)
    return series.rolling(window=window, min_periods=1).mean()


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Compute Relative Strength Index (RSI).

    window must be >= 1. Returns empty Series for empty input.
    """
    if window < 1:
        raise ValueError("window must be >= 1")
    if series is None or len(series) == 0:
        return pd.Series(dtype=float)
    delta = series.diff()
    up = delta.clip(lower=0).rolling(window=window, min_periods=1).mean()
    down = -delta.clip(upper=0).rolling(window=window, min_periods=1).mean()
    # avoid division by zero
    rs = up / down.replace(0, float("nan"))
    rsi_ser = 100 - (100 / (1 + rs))
    return rsi_ser.fillna(0)
