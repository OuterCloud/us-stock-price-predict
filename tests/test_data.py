import pandas as pd
import os
from pathlib import Path

from src.data import write_parquet, fetch_and_update_parquet


def make_df(dates, vals):
    return pd.DataFrame({"date": pd.to_datetime(dates), "close": vals})


def test_fetch_and_update_creates(tmp_path, monkeypatch):
    # ensure data dir is tmp
    root = Path.cwd()
    try:
        os.chdir(tmp_path)

        # mock fetch_prices to return a small df
        def fake_fetch(ticker, period="1y"):
            return make_df(["2025-01-01", "2025-01-02"], [10, 11])

        monkeypatch.setattr("src.data.fetch_prices", fake_fetch)
        df = fetch_and_update_parquet("TEST")
        assert len(df) == 2
        # file exists
        assert (Path("data") / "stock_TEST.parquet").exists()

    finally:
        os.chdir(root)


def test_fetch_and_update_merges(tmp_path, monkeypatch):
    root = Path.cwd()
    try:
        os.chdir(tmp_path)
        # existing data
        existing = make_df(["2025-01-01", "2025-01-02"], [10, 11])
        write_parquet("TEST", existing)

        # fetch returns overlapping and new date
        def fake_fetch(ticker, period="1y"):
            return make_df(["2025-01-02", "2025-01-03"], [12, 13])

        monkeypatch.setattr("src.data.fetch_prices", fake_fetch)
        merged = fetch_and_update_parquet("TEST")
        # merged should have dates 01,02,03 and keep last value for 2025-01-02 (12)
        assert len(merged) == 3
        assert (
            merged[merged["date"] == pd.to_datetime("2025-01-02")]["close"].iloc[0]
            == 12
        )

    finally:
        os.chdir(root)


def test_fetch_ionq(tmp_path, monkeypatch):
    """Simulate fetching IONQ prices and ensure parquet is created and contains expected rows."""
    root = Path.cwd()
    try:
        os.chdir(tmp_path)

        # mock fetch_prices to return IonQ-like time series
        def fake_fetch_ionq(ticker, period="1y"):
            assert ticker == "IONQ"
            return make_df(["2025-02-01", "2025-02-02", "2025-02-03"], [3.1, 3.2, 3.3])

        monkeypatch.setattr("src.data.fetch_prices", fake_fetch_ionq)
        df = fetch_and_update_parquet("IONQ")
        assert len(df) == 3
        # parquet file exists
        assert (Path("data") / "stock_IONQ.parquet").exists()
        # values preserved
        assert df["close"].iloc[0] == 3.1

    finally:
        os.chdir(root)
