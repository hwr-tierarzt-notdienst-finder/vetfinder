"""Shared pydantic models."""

from datetime import datetime, timedelta
from typing import TypeVar, Generic, Literal, TypeAlias
from typing_extensions import Annotated

from pydantic import BaseModel, Field as PydanticField
from pydantic.generics import GenericModel


__version__ = "1.0"


_T = TypeVar("_T")


class Source(BaseModel):
    id: str
    url: str
    data: dict = PydanticField(default_factory=dict)


class ModelWithMetadata(BaseModel):
    creation_source_id: str = "manual"
    modification_source_id: str = "manual"
    created_at: datetime = PydanticField(
        default_factory=datetime.utcnow
    )
    modified_at: datetime = PydanticField(
        default_factory=datetime.utcnow
    )
    valid_until: datetime = PydanticField(
        default_factory=lambda: datetime.utcnow() + timedelta(days=365 * 1000)
    )


class Field(ModelWithMetadata, GenericModel, Generic[_T]):
    value: _T


class Person(ModelWithMetadata):
    name: str
    rolls: list[Literal["owner"]]


class Location(BaseModel):
    address: Field[str]
    lat: Field[float] | None = None
    lon: Field[float] | None = None


class Contact(ModelWithMetadata):
    type: Literal[
        "tel:landline",
        "tel:mobile",
        "email",
        "website"
    ]
    value: str


class AvailabilityConditionNot(ModelWithMetadata):
    type: Literal["not"]
    child: "AvailabilityCondition"


class AvailabilityConditionAnd(ModelWithMetadata):
    type: Literal["and"]
    children: list["AvailabilityCondition"]


class AvailabilityConditionOr(ModelWithMetadata):
    type: Literal["or"]
    children: list["AvailabilityCondition"]


class AvailabilityConditionAll(ModelWithMetadata):
    type: Literal["all"]


class TimezoneAware(ModelWithMetadata):
    timezone: Literal["Europe/Berlin"]


class Time(BaseModel):
    hour: int
    minute: int


class AvailabilityConditionTimespan(TimezoneAware):
    type: Literal["timespan"]
    start_time: Time
    end_time: Time


Weekday: TypeAlias = Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class AvailabilityConditionWeekdaysSpan(TimezoneAware):
    type: Literal["weekdays"]
    start_day: Weekday
    end_day: Weekday


class AvailabilityConditionHolidays(ModelWithMetadata):
    type: Literal["holidays"]
    region: Literal["Berlin"]


AvailabilityCondition = Annotated[
    AvailabilityConditionNot
    | AvailabilityConditionAnd
    | AvailabilityConditionOr
    | AvailabilityConditionAll
    | AvailabilityConditionTimespan
    | AvailabilityConditionWeekdaysSpan
    | AvailabilityConditionHolidays,
    PydanticField(discriminator="type")
]


AvailabilityConditionNot.update_forward_refs()
AvailabilityConditionOr.update_forward_refs()
AvailabilityConditionAnd.update_forward_refs()


class Vet(BaseModel):
    title: Field[str]
    people: list[Person] = PydanticField(default_factory=list)
    location: Location
    contacts: list[Contact] = PydanticField(default_factory=list)
    available: AvailabilityCondition
    sources: dict[str, Source]


class VetGet(Vet):
    id: str
