from typing import Dict
from .data import read_parquet, fetch_and_update_parquet


def get_prices(ticker: str, days: int = 90, refresh: bool = False) -> Dict:
    """Return last `days` records for `ticker`.

    If `refresh` is True, force a fetch-and-update of parquet from remote.
    """
    if refresh:
        df = fetch_and_update_parquet(ticker, period="1y")
    else:
        try:
            df = read_parquet(ticker)
        except FileNotFoundError:
            # auto-fetch and create parquet if missing
            df = fetch_and_update_parquet(ticker, period="1y")

    if len(df) < days:
        subset = df
    else:
        subset = df.tail(days)
    # ensure date column
    if "date" in subset.columns:
        subset = subset.copy()
        subset["date"] = subset["date"].astype(str)
    return {"ticker": ticker, "data": subset.to_dict(orient="records")}
