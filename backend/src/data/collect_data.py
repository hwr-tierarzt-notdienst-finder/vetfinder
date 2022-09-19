import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, Any, TypeVar, Type

from models import Vet, Source, Field, Location, Contact, ModelWithMetadata, AvailabilityCondition, \
    AvailabilityConditionAll, AvailabilityConditionNot, AvailabilityConditionAnd, AvailabilityConditionOr, \
    AvailabilityConditionTimeSpanDuringDay, TimeDuringDay, AvailabilityConditionWeekdaysSpan, AvailabilityConditionHolidays, Person

_DEFAULT_TIMEZONE = "Europe/Berlin"


def collect_vets() -> Iterable[Vet]:
    dt = datetime.utcnow()

    yield from _collect_vets_from_json("tieraerztekammer_berlin.json", dt)


def _collect_vets_from_json(
        file_path: Path | str,
        dt: datetime
) -> Iterable[Vet]:
    with open(_normalize_file_path(file_path)) as f:
        dct = json.load(f)

    source = _extract_source_from_json_dct(dct)

    yield from _extract_vets_from_json_dct(dct, source, dt)


def _normalize_file_path(file_path: Path | str) -> Path:
    file_path = Path(file_path)
    if file_path.is_absolute():
        return file_path.resolve()
    else:
        return (Path(__file__).parent / file_path).resolve()


def _extract_source_from_json_dct(dct: dict) -> Source:
    source_dct = dct["source"]
    return Source(
        id=source_dct["id"],
        url=source_dct["url"],
    )


def _extract_vets_from_json_dct(
        dct: dict,
        source: Source,
        dt: datetime,
) -> Iterable[Vet]:
    for vet_dct in dct["vets"]:
        yield _extract_vet_from_json_vet_dct(vet_dct, source, dt)


def _extract_vet_from_json_vet_dct(
        vet_dct: dict,
        source: Source,
        dt: datetime,
) -> Vet:
    title = _create_field(vet_dct["title"], source, dt)
    people = _extract_people_from_json_vet_dct(vet_dct, source, dt)
    location = _extract_location_from_json_vet_dct(vet_dct, source, dt)
    contacts = _extract_contacts_from_json_vet_dct(vet_dct, source, dt)
    availability_condition = _extract_availability_condition_from_json_vet_dct(
        vet_dct,
        source,
        dt,
    )

    return Vet(
        title=title,
        people=people,
        location=location,
        contacts=contacts,
        available=availability_condition,
        sources={source.id: source}
    )


def _extract_people_from_json_vet_dct(
        vet_dct: dict,
        source: Source,
        dt: datetime,
) -> list[Person]:
    return [
        _create_person_from_dct(person_dct, source, dt)
        for person_dct in vet_dct["people"]
    ]


def _create_person_from_dct(
        dct: dict,
        source: Source,
        dt: datetime,
) -> Person:
    return _create_model_with_metadata(
        Person,
        dct,
        source,
        dt
    )


def _extract_location_from_json_vet_dct(
        vet_dct: dict,
        source: Source,
        dt: datetime,
) -> Location:
    location_dct = vet_dct["location"]

    address = _create_field(location_dct["address"], source, dt)

    lat_value = location_dct.get("lat", None)
    lon_value = location_dct.get("lon", None)

    if lat_value is None:
        lat = None
    else:
        lat = _create_field(float(lat_value), source, dt)

    if lon_value is None:
        lon = None
    else:
        lon = _create_field(float(lon_value), source, dt)

    return Location(
        address=address,
        lat=lat,
        lon=lon,
    )


def _extract_contacts_from_json_vet_dct(
        vet_dct: dict,
        source: Source,
        dt: datetime,
) -> list[Contact]:
    return [
        _create_contact_from_dct(contact_dct, source, dt)
        for contact_dct in vet_dct["contacts"]
    ]


def _create_contact_from_dct(
        contact_dct: dict,
        source: Source,
        dt: datetime,
) -> Contact:
    return _create_model_with_metadata(
        Contact,
        contact_dct,
        source,
        dt
    )


def _extract_availability_condition_from_json_vet_dct(
        vet_dct: dict,
        source: Source,
        dt: datetime
) -> AvailabilityCondition:
    return _create_availability_condition_from_dct(
        vet_dct["available"],
        source,
        dt,
    )


def _create_availability_condition_from_dct(
        dct: dict,
        source: Source,
        dt: datetime,
) -> AvailabilityCondition:
    type_ = dct["type"]

    if type_ == "not":
        return _create_model_with_metadata(
            AvailabilityConditionNot,
            {
                "type": type_,
                "child": _create_availability_condition_from_dct(
                    dct["child"],
                    source,
                    dt
                )
            },
            source,
            dt,
        )
    elif type_ == "and":
        return _create_model_with_metadata(
            AvailabilityConditionAnd,
            {
                "type": type_,
                "children": [
                    _create_availability_condition_from_dct(child, source, dt)
                    for child in dct["children"]
                ]
            },
            source,
            dt,
        )
    elif type_ == "or":
        return _create_model_with_metadata(
            AvailabilityConditionOr,
            {
                "type": type_,
                "children": [
                    _create_availability_condition_from_dct(child, source, dt)
                    for child in dct["children"]
                ]
            },
            source,
            dt,
        )
    elif type_ == "all":
        return _create_model_with_metadata(
            AvailabilityConditionAll,
            {"type": type_},
            source,
            dt,
        )
    elif type_ == "time_span_during_day":
        return _create_model_with_metadata(
            AvailabilityConditionTimeSpanDuringDay,
            {
                "type": type_,
                "start_time": TimeDuringDay(
                    hour=dct["start_time"]["hour"],
                    minute=dct["start_time"].get("minute", None)
                ),
                "end_time": TimeDuringDay(
                    hour=dct["end_time"]["hour"],
                    minute=dct["end_time"].get("minute", None)
                ),
                "timezone": dct.get("timezone", _DEFAULT_TIMEZONE)
            },
            source,
            dt,
        )
    elif type_ == "weekdays":
        return _create_model_with_metadata(
            AvailabilityConditionWeekdaysSpan,
            {
                "type": type_,
                "start_day": dct["start_day"],
                "end_day": dct["end_day"],
                "timezone": dct.get("timezone", _DEFAULT_TIMEZONE)
            },
            source,
            dt,
        )
    elif type_ == "holidays":
        return _create_model_with_metadata(
            AvailabilityConditionHolidays,
            {
                "type": type_,
                "region": dct["region"]
            },
            source,
            dt
        )


def _create_field(
        value: Any,
        source: Source,
        dt: datetime,
) -> Field:
    return _create_model_with_metadata(
        Field,
        {"value": value},
        source,
        dt,
    )


_TModelWithMetadata = TypeVar("_TModelWithMetadata", bound=ModelWithMetadata)


def _create_model_with_metadata(
        cls: Type[_TModelWithMetadata],
        values: dict[str, Any],
        source: Source,
        dt: datetime,
) -> _TModelWithMetadata:
    return cls(
        **values,
        **{
            "creation_source_id": source.id,
            "modification_source_id": source.id,
            "created_at": dt,
            "modified_at": dt,
        }
    )


if __name__ == "__main__":
    print(list(collect_vets()))
