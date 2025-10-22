from datetime import date, timedelta

# Minimal trading day utilities
WEEKENDS = (5, 6)


def is_trading_day(d: date) -> bool:
    return d.weekday() not in WEEKENDS


def next_trading_days(start_date: date, n: int):
    days = []
    d = start_date
    while len(days) < n:
        d += timedelta(days=1)
        if is_trading_day(d):
            days.append(d)
    return days


def load_holiday_calendar():
    # Placeholder: in production, load from exchange calendar or package
    return []
