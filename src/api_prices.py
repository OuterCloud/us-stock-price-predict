from typing import Dict
from .data import read_parquet


def get_prices(ticker: str, days: int = 90) -> Dict:
    df = read_parquet(ticker)
    if len(df) < days:
        # return whatever available
        subset = df
    else:
        subset = df.tail(days)
    # ensure date column
    if "date" in subset.columns:
        subset = subset.copy()
        subset["date"] = subset["date"].astype(str)
    return {"ticker": ticker, "data": subset.to_dict(orient="records")}
