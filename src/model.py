from __future__ import annotations

from typing import List, Tuple, Optional

import pandas as pd

from src.features import sma


def predict_next_prices(
    prices: List[float], days: int = 3, window: Optional[int] = None
) -> List[float]:
    """Predict next `days` prices using a simple moving-average extrapolation.

    - If prices is empty -> raises ValueError
    - If days < 1 -> returns empty list
    - window: optional int to control SMA window, defaults to min(10, len(prices))
    The function returns a list of floats (length `days`).
    """
    if prices is None:
        raise ValueError("prices must be provided")
    if days <= 0:
        return []
    if len(prices) == 0:
        raise ValueError("Insufficient data")

    series = pd.Series(prices).astype(float)
    if window is None:
        window = min(10, max(1, len(series)))
    else:
        window = max(1, int(window))

    sma_ser = sma(series, window=window)
    last_sma = (
        sma_ser.dropna().iloc[-1] if not sma_ser.dropna().empty else series.mean()
    )
    # fallback to the last observed price if mean is nan
    if pd.isna(last_sma):
        last_sma = float(series.iloc[-1])
    return [float(last_sma) for _ in range(days)]


# Gated/time-consuming models are intentionally not implemented under current governance
def train_arima(df: pd.DataFrame):
    raise NotImplementedError("ARIMA training is gated behind governance approval")


def predict_arima(
    model, days: int
) -> Tuple[List[float], Optional[List[Tuple[float, float]]]]:
    raise NotImplementedError("ARIMA prediction is gated behind governance approval")
