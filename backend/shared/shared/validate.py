from datetime import datetime
from pathlib import Path
from typing import cast

from .human_readable import human_readable
from .constants import TIMEZONES, WEEKDAYS
from .types import Timezone, Weekday


def weekday(day: str) -> Weekday:
    if day in WEEKDAYS:
        return cast(Weekday, day)

    raise ValueError(
        f"Invalid weekday '{day}'. "
        f"Weekday must be {human_readable(WEEKDAYS).ored().shorten_if_longer_than(7)}'"
    )


def hour(x: int) -> int:
    if 0 <= x <= 23:
        return x

    raise ValueError(f"Hour must be between 0 and 23, not {x}")


def minute(x: int) -> int:
    if 0 <= x <= 60:
        return x

    raise ValueError(f"Minute must be between 0 and 60, not {x}")


def timezone(s: str) -> Timezone:
    if s in TIMEZONES:
        return cast(Timezone, s)

    raise ValueError(
        f"Invalid timezone '{timezone}'. "
        f"Timezone must be {human_readable(TIMEZONES).ored()}"
    )


def datetime_is_timezone_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError(f"Datetime {dt} is not timezone aware")

    return dt


def path_is_dir(path: Path) -> Path:
    if path.is_dir():
        return path

    # Better to give a more specific error message if the path does not exist
    path_exists(path)

    raise ValueError(f"Path '{path}' is not a directory")


def path_exists(path: Path) -> Path:
    if path.exists():
        return path

    raise ValueError(f"Path '{path}' does not exist")
