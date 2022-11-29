import inspect
import json
from collections.abc import Callable, Iterable
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, NoReturn

from dateutil.tz import gettz

from constants import REGIONS
from types_ import Region
from utils import cache, import_, validate

if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

    __package__ = "holidays"

from . import cache_populators
from .types_ import Cache, CreateCacheRegionEntry, CacheRegionEntry
from .constants import CACHE_FOR_N_PAST_YEARS, CACHE_FOR_N_FUTURE_YEARS, CACHE_UPDATE_INTERVAL_IN_SECONDS


def get_by_region(
        lower_bound: datetime,
        upper_bound: datetime,
        region: Region,
) -> Iterable[datetime]:
    validate.datetime_is_timezone_aware(lower_bound)
    validate.datetime_is_timezone_aware(upper_bound)

    lower_bound_year = lower_bound.year
    upper_bound_year = upper_bound.year
    current_year = datetime.now().year

    if lower_bound_year < (min_year := current_year - CACHE_FOR_N_PAST_YEARS):
        raise ValueError(f"Cannot get holidays before the start of {min_year}")

    if upper_bound_year > (max_year := current_year + CACHE_FOR_N_FUTURE_YEARS):
        raise ValueError(f"Cannot get holidays after the end of {max_year}")

    cache = _get_cache()

    if region not in cache:
        _populate_cache(region)

    cache_entry = cache[region]
    if lower_bound < cache_entry["valid_from"] or upper_bound > cache_entry["valid_to"]:
        _populate_cache(region)

    cache_entry = cache[region]
    if lower_bound < cache_entry["valid_from"] or upper_bound > cache_entry["valid_to"]:
        raise ValueError(
            f"Could not get holidays in interval [{lower_bound},{upper_bound}) for region '{region}'"
        )

    updated_at_timestamp = cache_entry["updated_at"].timestamp()
    last_update_cycle_start = updated_at_timestamp - updated_at_timestamp % CACHE_UPDATE_INTERVAL_IN_SECONDS

    next_update_timestamp = last_update_cycle_start + CACHE_UPDATE_INTERVAL_IN_SECONDS + (
        # Stagger updates
        (
            sorted(REGIONS).index(region)
            * CACHE_UPDATE_INTERVAL_IN_SECONDS
            / len(REGIONS)
        ) % CACHE_UPDATE_INTERVAL_IN_SECONDS
    )
    next_update_dt = datetime.utcfromtimestamp(next_update_timestamp).astimezone(timezone.utc)

    if datetime.utcnow().astimezone(timezone.utc) > next_update_dt:
        _populate_cache(region)

    lower_bound_day = lower_bound.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    upper_bound_day = upper_bound.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ) + timedelta(days=1)

    for year in range(lower_bound_year, upper_bound_year + 1):
        for holiday in cache_entry["holidays"][year]:
            if holiday >= upper_bound_day:
                return

            if holiday >= lower_bound_day:
                yield holiday


def _populate_cache(region: Region) -> None:
    populators = _get_cache_populators()

    try:
        populator = populators[region]
    except KeyError as err:
        raise RuntimeError(
            f"No holiday cache populator for region '{region}'"
        ) from err

    new_region_entry = populator()

    _update_cache(region, new_region_entry)


@cache.return_singleton(populate_cache_on="prepopulate_called")
def _get_cache_populators() -> dict[Region, Callable[[], CreateCacheRegionEntry]]:
    code_region_string_to_region = {
        region.lower().replace(" :", "_"): region
        for region in REGIONS
    }

    populators: dict[Region, Callable[[], CreateCacheRegionEntry]] = {}
    for module in import_.iter_submodules(cache_populators):
        found_populators_in_module: bool = False

        for _, member in inspect.getmembers(module):
            member_name = getattr(member, "__name__", None)

            def validate_populator(populator: Any) -> Callable[[], CreateCacheRegionEntry] | NoReturn:
                if callable(populator):
                    return populator

                raise RuntimeError(
                    f"'{populator.__name__}' in '{module.__name__}' "
                    "is an invalid holiday cache populator. "
                    "Populators must be callable"
                )

            if member_name == "create_populators":
                try:
                    for region, populator in member():
                        try:
                            validate.region(region)
                        except ValueError as err:
                            raise RuntimeError(
                                f"'{member_name}' in '{module.__name__}' "
                                f"created a holiday cache populator for an invalid region '{region}'"
                            ) from err

                        populators[region] = validate_populator(populator)

                        found_populators_in_module = True

                except Exception as err:
                    raise RuntimeError(
                        f"'{member_name}' in '{module.__name__}' "
                        f"failed to create holiday cache populators with error: {err}"
                    ) from err

            elif member_name is not None and member_name.startswith("populate_"):
                try:
                    region = code_region_string_to_region[member_name.removeprefix("populate_")]
                except KeyError as err:
                    raise RuntimeError(
                        f"'{member_name}' in '{module.__name__}' "
                        "is an invalid holiday cache populator "
                        f"because the region cannot be inferred from name ending '{member_name.removeprefix('populate_')}'"
                    )

                populators[region] = validate_populator(member)

                found_populators_in_module = True

        if not found_populators_in_module:
            raise RuntimeError(
                f"Found no holiday cache populators in module '{module.__name__}'"
            )

    return populators


@cache.return_singleton(populate_cache_on="prepopulate_called")
def _get_cache() -> Cache:
    cache_dir = _get_cache_dir()

    cache: Cache = {}
    for child in cache_dir.iterdir():
        if child.is_file() and child.suffix == ".json":
            region = validate.region(child.stem)

            with open(child) as f:
                region_entry_json = json.load(f)

            cache[region] = {
                "updated_at": datetime.fromisoformat(region_entry_json["updated_at"]),
                "valid_from": datetime.fromisoformat(region_entry_json["valid_from"]),
                "valid_to": datetime.fromisoformat(region_entry_json["valid_to"]),
                "holidays": {
                    int(year): [
                        datetime.fromisoformat(day_str)
                        for day_str in region_entry_json["holidays"][year]
                    ] for year in region_entry_json["holidays"]
                }
            }

    return cache


def _update_cache(region: Region, region_entry: CreateCacheRegionEntry) -> None:
    cached_region_entry: CacheRegionEntry = {
        **region_entry,
        "updated_at": datetime.now().astimezone(gettz("Europe/Berlin")),
    }

    region_entry_json = {
        "updated_at": datetime.isoformat(cached_region_entry["updated_at"]),
        "valid_to": datetime.isoformat(cached_region_entry["valid_to"]),
        "valid_from": datetime.isoformat(cached_region_entry["valid_from"]),
        "holidays": {
            year: [
                datetime.isoformat(day)
                for day in cached_region_entry["holidays"][year]
            ]
            for year in cached_region_entry["holidays"]
        }
    }

    cache_file = _get_cache_dir() / f"{region}.json"

    with open(cache_file, "w") as f:
        json.dump(region_entry_json, f, indent=True)

    cache = _get_cache()
    cache[region] = cached_region_entry


@cache.return_singleton(populate_cache_on="prepopulate_called")
def _get_cache_dir() -> Path:
    return Path(__file__).resolve().parent / "cache"


def prepopulate_cache() -> None:
    cache.prepopulate()

    utcnow_dt = datetime.utcnow().astimezone(tz=timezone.utc)

    for region in REGIONS:
        list(get_by_region(utcnow_dt, utcnow_dt, region))


prepopulate_cache()


if __name__ == "__main__":
    lower_bound = datetime(year=2021, month=10, day=2).astimezone(timezone.utc)
    upper_bound = datetime(year=2023, month=10, day=2).astimezone(timezone.utc)

    print(list(get_by_region(lower_bound, upper_bound, "Bundesland:Berlin")))