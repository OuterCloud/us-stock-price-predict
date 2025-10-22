import pytest

from src.model import predict_next_prices


def test_predict_basic():
    prices = [10, 11, 12, 13, 14]
    preds = predict_next_prices(prices, days=3, window=3)
    assert len(preds) == 3
    # window=3 -> last SMA = mean(12,13,14)=13
    assert all(abs(p - 13.0) < 1e-6 for p in preds)


def test_predict_short_series():
    prices = [100]
    preds = predict_next_prices(prices, days=2)
    assert preds == [100.0, 100.0]


def test_predict_days_zero():
    prices = [1, 2, 3]
    assert predict_next_prices(prices, days=0) == []


def test_predict_insufficient():
    with pytest.raises(ValueError):
        predict_next_prices([], days=3)
