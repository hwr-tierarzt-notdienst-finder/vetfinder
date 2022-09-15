import dataclasses
import itertools
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from dateutil.tz import gettz
import requests

from ....utils import cache
from ....types_ import Region
from ....constants import REGIONS

from ..types_ import CreateCacheRegionEntry
from ..constants import CACHE_FOR_N_PAST_YEARS, CACHE_FOR_N_FUTURE_YEARS


@dataclass(frozen=True)
class SkipHolidayRule:
    holiday_name: str
    only_for_regions: set[Region] =\
        dataclasses.field(default_factory=lambda: set(REGIONS))  # All regions by default


_FEIERTAGE_API_HOST = "https://feiertage-api.de/api/"
_GERMAN_STATE_ABBR_TO_REGION: dict[str, Region] = {
    "BE": "Bundesland:Berlin",
    "BW": "Bundesland:Baden-Württemberg",
    "BY": "Bundesland:Bayern",
    "BB": "Bundesland:Brandenburg",
    "HB": "Bundesland:Bremen",
    "HH": "Bundesland:Hamburg",
    "HE": "Bundesland:Hessen",
    "MV": "Bundesland:Mecklenburg-Vorpommern",
    "NI": "Bundesland:Niedersachsen",
    "NW": "Bundesland:Nordrhein-Westfalen",
    "RP": "Bundesland:Rheinland-Pfalz",
    "SL": "Bundesland:Saarland",
    "SN": "Bundesland:Sachsen",
    "ST": "Bundesland:Sachsen-Anhalt",
    "SH": "Bundesland:Schleswig-Holstein",
    "TH": "Bundesland:Thüringen",
}
_REGION_TO_GERMAN_STATE_ABBR = {
    region: abbr
    for abbr, region in _GERMAN_STATE_ABBR_TO_REGION.items()
}
# Source https://de.wikipedia.org/wiki/Gesetzliche_Feiertage_in_Deutschland
_SKIP_HOLIDAYS_RULES: list[SkipHolidayRule] = [
    # Omit school holidays
    SkipHolidayRule(
        holiday_name="Gründonnerstag",
    ),
    SkipHolidayRule(
        holiday_name="Reformationstag",
        only_for_regions={"Bundesland:Baden-Württemberg"},
    ),
    SkipHolidayRule(
        holiday_name="Buß- und Bettag",
        only_for_regions={"Bundesland:Bayern"},
    ),
    # Only public holidays in specific parts of german states.
    # Currently, fully omitted for specified.
    SkipHolidayRule(
        holiday_name="Fronleichnam",
        only_for_regions={"Bundesland:Sachsen", "Bundesland:Thüringen"},
    ),
    SkipHolidayRule(
        holiday_name="Augsburger Friedensfest",
        only_for_regions={"Bundesland:Bayern"},
    ),
    SkipHolidayRule(
        holiday_name="Mariä Himmelfahrt",
        only_for_regions={"Bundesland:Bayern"},
    ),
]
_GERMAN_TIMEZONE_OBJ = gettz("Europe/Berlin")


def create_populators() -> list[tuple[Region, Callable[[], CreateCacheRegionEntry]]]:
    return [
        (region, _create_region_populator(region))
        for region in REGIONS
    ]


def _create_region_populator(region: Region) -> Callable[[], CreateCacheRegionEntry]:
    current_year = datetime.now().year

    def populator() -> CreateCacheRegionEntry:
        return _get_region_cache_entry(
            region,
            from_year=current_year - CACHE_FOR_N_PAST_YEARS,
            to_year=current_year + CACHE_FOR_N_FUTURE_YEARS,
        )

    return populator


def _get_region_cache_entry(
        region: Region,
        *,
        from_year: int,
        to_year: int,
) -> CreateCacheRegionEntry:
    german_state_abbr = _REGION_TO_GERMAN_STATE_ABBR[region]
    skip_holidays = _create_region_to_skipped_holidays_map()[region]

    year_to_holidays: dict[int, list[datetime]] = {}
    for year, api_response_json in _get_json_for_year_interval_from_api(from_year, to_year):
        national_holidays_entries: Iterable[tuple[str, dict]] = (
            (key, value)
            for key, value in api_response_json["NATIONAL"].items()
        )
        state_specific_holidays_entries: Iterable[tuple[str, dict]] = (
            (key, value)
            for key, value in api_response_json[german_state_abbr].items()
        )

        holidays_for_year: list[datetime] = []
        for name, entry in itertools.chain(
                national_holidays_entries,
                state_specific_holidays_entries
        ):
            if name in skip_holidays:
                continue

            holiday_dt = datetime.fromisoformat(
                entry["datum"]
            ).astimezone(tz=_GERMAN_TIMEZONE_OBJ)

            holidays_for_year.append(holiday_dt)

        year_to_holidays[year] = holidays_for_year

    return {
        "valid_from": datetime(year=from_year, month=1, day=1).astimezone(_GERMAN_TIMEZONE_OBJ),
        "valid_to": datetime(year=to_year + 1, month=1, day=1).astimezone(_GERMAN_TIMEZONE_OBJ),
        "holidays": year_to_holidays,
    }


def _get_json_for_year_interval_from_api(from_year: int, to_year: int) -> Iterable[tuple[int, dict]]:
    for year in range(from_year, to_year + 1):
        yield year, _get_json_from_api(year)


def _get_json_from_api(year: int) -> dict:
    url = f"{_FEIERTAGE_API_HOST}?jahr={year}"

    return requests.get(url).json()


@cache.return_singleton
def _create_region_to_skipped_holidays_map() -> dict[Region, set[str]]:
    mapping: dict[Region, set[str]] = {}

    for skip_rule in _SKIP_HOLIDAYS_RULES:
        for region in skip_rule.only_for_regions:
            if region in mapping:
                mapping[region].add(skip_rule.holiday_name)
            else:
                mapping[region] = {skip_rule.holiday_name}

    return mapping
