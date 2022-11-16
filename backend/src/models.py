"""Shared pydantic models."""
from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import TypeVar, Generic, Literal, TypeAlias

from pydantic.config import BaseConfig
from pydantic.main import BaseModel
from typing_extensions import Annotated

from pydantic import Field as PydanticField
from pydantic.generics import GenericModel

from utils import string_
from types_ import Timezone, Region


_T = TypeVar("_T")


class InDbModel(BaseModel):
    id: str


# API Models
# ============================================================================

class ApiBaseModel(BaseModel):
    class Config(BaseConfig):
        orm_mode = True
        allow_population_by_field_name = True
        alias_generator = string_.as_camel_case


class ModelWithApiMetadata(ApiBaseModel):
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


class ApiField(ModelWithApiMetadata, GenericModel, Generic[_T]):
    value: _T


# Vet
# ----------------------------------------------------------------------------

class Person(ModelWithApiMetadata):
    name: str
    rolls: list[Literal["owner"]]


class Location(ApiBaseModel):
    address: ApiField[str]
    lat: ApiField[float] | None = None
    lon: ApiField[float] | None = None


class Contact(ModelWithApiMetadata):
    type: Literal[
        "tel:landline",
        "tel:mobile",
        "email",
        "website"
    ]
    value: str


class AvailabilityConditionNot(ModelWithApiMetadata):
    type: Literal["not"]
    child: "AvailabilityCondition"


class AvailabilityConditionAnd(ModelWithApiMetadata):
    type: Literal["and"]
    children: list["AvailabilityCondition"]


class AvailabilityConditionOr(ModelWithApiMetadata):
    type: Literal["or"]
    children: list["AvailabilityCondition"]


class AvailabilityConditionAll(ModelWithApiMetadata):
    type: Literal["all"]


class TimezoneAware(ModelWithApiMetadata):
    timezone: Timezone


class TimeDuringDay(ApiBaseModel):
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


class AvailabilityConditionHolidays(ModelWithApiMetadata):
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


class Source(ApiBaseModel):
    id: str
    url: str
    data: dict = PydanticField(default_factory=dict)


class TimeSpan(ApiBaseModel):
    """
    Object representing the half-open datetime interval: [start,end).
    """
    start: datetime
    end: datetime

    def __hash__(self) -> int:
        return hash(self.start) + hash(self.end)


class Vet(ApiBaseModel):
    title: ApiField[str]
    people: list[Person] = PydanticField(default_factory=list)
    location: Location
    contacts: list[Contact] = PydanticField(default_factory=list)
    available: AvailabilityCondition
    categories: ApiField[list[Category]] = PydanticField(
        default_factory=lambda: ApiField(value=[])
    )
    sources: dict[str, Source]


class VetInDb(Vet, InDbModel):
    id: str


class VetResponse(VetInDb):
    availability: list[TimeSpan] | None = None


# Internal Models
# ============================================================================

class Secret(BaseModel):
    secret_id: str
    # We obviously don't store plaintext
    # -> must be cryptographically strong for short text (no md5!!!!!!!! or sha!) and salted
    hash_: str


class SecretInDb(Secret, InDbModel):
    pass
