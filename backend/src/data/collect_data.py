import json
from pathlib import Path
from typing import Iterable

from models import Vet, Location, Contact, AvailabilityCondition, \
    AvailabilityConditionAll, AvailabilityConditionNot, AvailabilityConditionAnd, AvailabilityConditionOr, \
    AvailabilityConditionTimeSpanDuringDay, TimeDuringDay, AvailabilityConditionWeekdaysSpan, AvailabilityConditionHolidays, Person

_DEFAULT_TIMEZONE = "Europe/Berlin"


def collect_vets() -> Iterable[Vet]:
    yield from _collect_vets_from_json("tieraerztekammer_berlin.json")


def _collect_vets_from_json(file_path: Path | str) -> Iterable[Vet]:
    with open(_normalize_file_path(file_path)) as f:
        dct = json.load(f)

    yield from _extract_vets_from_json_dct(dct)


def _normalize_file_path(file_path: Path | str) -> Path:
    file_path = Path(file_path)
    if file_path.is_absolute():
        return file_path.resolve()
    else:
        return (Path(__file__).parent / file_path).resolve()


def _extract_vets_from_json_dct(dct: dict) -> Iterable[Vet]:
    for vet_dct in dct["vets"]:
        yield _extract_vet_from_json_vet_dct(vet_dct)


def _extract_vet_from_json_vet_dct(vet_dct: dict) -> Vet:
    title = vet_dct["title"]
    people = _extract_people_from_json_vet_dct(vet_dct)
    location = _extract_location_from_json_vet_dct(vet_dct)
    contacts = _extract_contacts_from_json_vet_dct(vet_dct)
    availability_condition = _extract_availability_condition_from_json_vet_dct(vet_dct)

    return Vet(
        title=title,
        people=people,
        location=location,
        contacts=contacts,
        available=availability_condition,
    )


def _extract_people_from_json_vet_dct(vet_dct: dict) -> list[Person]:
    return [
        Person(**person_dct)
        for person_dct in vet_dct["people"]
    ]


def _extract_location_from_json_vet_dct(vet_dct: dict) -> Location:
    location_dct = vet_dct["location"]

    address = location_dct["address"]

    lat_value = location_dct.get("lat", None)
    lon_value = location_dct.get("lon", None)

    if lat_value is None:
        lat = None
    else:
        lat = float(lat_value)

    if lon_value is None:
        lon = None
    else:
        lon = float(lon_value)

    return Location(
        address=address,
        lat=lat,
        lon=lon,
    )


def _extract_contacts_from_json_vet_dct(vet_dct: dict) -> list[Contact]:
    return [
        Contact(**contact_dct)
        for contact_dct in vet_dct["contacts"]
    ]


def _extract_availability_condition_from_json_vet_dct(vet_dct: dict) -> AvailabilityCondition:
    return _create_availability_condition_from_dct(vet_dct["available"])


def _create_availability_condition_from_dct(dct: dict) -> AvailabilityCondition:
    type_ = dct["type"]

    if type_ == "not":
        return AvailabilityConditionNot(
            type=type_,
            child=_create_availability_condition_from_dct(dct["child"])
        )
    elif type_ == "and":
        return AvailabilityConditionAnd(
            type=type_,
            children=[
                _create_availability_condition_from_dct(child)
                for child in dct["children"]
            ]
        )
    elif type_ == "or":
        return AvailabilityConditionOr(
            type=type_,
            children=[
                _create_availability_condition_from_dct(child)
                for child in dct["children"]
            ]
        )
    elif type_ == "all":
        return AvailabilityConditionAll(type=type_)
    elif type_ == "time_span_during_day":
        return AvailabilityConditionTimeSpanDuringDay(
            type=type_,
            start_time=TimeDuringDay(
                hour=dct["start_time"]["hour"],
                minute=dct["start_time"].get("minute", None)
            ),
            end_time=TimeDuringDay(
                hour=dct["end_time"]["hour"],
                minute=dct["end_time"].get("minute", None)
            ),
            timezone=dct.get("timezone", _DEFAULT_TIMEZONE)
        )
    elif type_ == "weekdays":
        return AvailabilityConditionWeekdaysSpan(
            type=type_,
            start_day=dct["start_day"],
            end_day=dct["end_day"],
            timezone=dct.get("timezone", _DEFAULT_TIMEZONE)
        )
    elif type_ == "holidays":
        return AvailabilityConditionHolidays(
            type=type_,
            region=dct["region"],
        )


if __name__ == "__main__":
    print(list(collect_vets()))
