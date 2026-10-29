from datetime import date, datetime, timedelta
from typing import Generator


def date_range_generator(start_date: date, end_date: date) -> Generator[date, None, None]:
    """Generates all dates inclusive between start_date and end_date."""
    curr = start_date
    while curr <= end_date:
        yield curr
        curr += timedelta(days=1)


def parse_date_safe(val, default=None) -> date | None:
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str) and val.strip():
        try:
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        except ValueError:
            return default
    return default