from datetime import datetime, tzinfo
from pathlib import Path
from typing import cast

import dateutil.tz

from constants import WEEKDAYS, REGIONS
from types_ import Timezone, Weekday, Region
from .human_readable import human_readable


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
    try:
        if not isinstance(dateutil.tz.gettz(s), tzinfo):
            raise TypeError

        return cast(Timezone, s)
    except Exception as err:
        raise ValueError(
            f"Invalid timezone '{timezone}'"
        ) from err


def region(s: str) -> Region:
    if s in REGIONS:
        return cast(Region, s)

    raise ValueError(
        f"Invalid region '{region}'. "
        f"Region must be {human_readable(Region).quoted().ored()}"
    )


def datetime_is_timezone_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError(f"Datetime {dt} is not timezone aware")

    return dt


def path_is_file(path: Path) -> Path:
    if path.is_file():
        return path

    # Better to give a more specific error message if the path does not exist
    path_exists(path)

    raise ValueError(f"Path '{path}' is not a file")


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
