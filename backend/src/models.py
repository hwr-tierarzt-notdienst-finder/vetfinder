"""Shared pydantic models."""
from datetime import datetime, timedelta
from enum import Enum
from typing import TypeVar, Generic, Literal, TypeAlias
from typing_extensions import Annotated

from pydantic import BaseModel, Field as PydanticField
from pydantic.generics import GenericModel

from .types_ import Timezone, Region


__version__ = "1.0"


_T = TypeVar("_T")


class TimeSpan(BaseModel):
    """
    Object representing the half-open datetime interval: [start,end).
    """
    start: datetime
    end: datetime

    def __hash__(self) -> int:
        return hash(self.start) + hash(self.end)


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
    timezone: Timezone


class TimeDuringDay(BaseModel):
    hour: int
    minute: int


class AvailabilityConditionTimeSpanDuringDay(TimezoneAware):
    type: Literal["time_span_during_day"]
    start_time: TimeDuringDay
    end_time: TimeDuringDay


Weekday: TypeAlias = Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class AvailabilityConditionWeekdaysSpan(TimezoneAware):
    type: Literal["weekdays"]
    start_day: Weekday
    end_day: Weekday


class AvailabilityConditionHolidays(ModelWithMetadata):
    type: Literal["holidays"]
    region: Region


AvailabilityCondition = Annotated[
    AvailabilityConditionNot
    | AvailabilityConditionAnd
    | AvailabilityConditionOr
    | AvailabilityConditionAll
    | AvailabilityConditionTimeSpanDuringDay
    | AvailabilityConditionWeekdaysSpan
    | AvailabilityConditionHolidays,
    PydanticField(discriminator="type")
]


AvailabilityConditionNot.update_forward_refs()
AvailabilityConditionOr.update_forward_refs()
AvailabilityConditionAnd.update_forward_refs()


class Category(str, Enum):
    ALL = "all"


class Vet(BaseModel):
    title: Field[str]
    people: list[Person] = PydanticField(default_factory=list)
    location: Location
    contacts: list[Contact] = PydanticField(default_factory=list)
    available: AvailabilityCondition
    sources: dict[str, Source]
    categories: Field[list[Category]] = PydanticField(
        default_factory=lambda: Field(value=[])
    )


class VetInDb(Vet):
    id: str


class VetResponse(VetInDb):
    availability: list[TimeSpan] | None = None
