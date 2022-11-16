"""Shared pydantic models."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TypeVar, Literal, TypeAlias

from pydantic.config import BaseConfig
from pydantic.main import BaseModel
from typing_extensions import Annotated

from pydantic import Field as PydanticField

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


# Vet
# ----------------------------------------------------------------------------

class Person(ApiBaseModel):
    name: str
    rolls: list[Literal["owner"]]


class Location(ApiBaseModel):
    address: str
    lat: float | None = None
    lon: float | None = None


class Contact(ApiBaseModel):
    type: Literal[
        "tel:landline",
        "tel:mobile",
        "email",
        "website"
    ]
    value: str


class AvailabilityConditionNot(ApiBaseModel):
    type: Literal["not"]
    child: "AvailabilityCondition"


class AvailabilityConditionAnd(ApiBaseModel):
    type: Literal["and"]
    children: list["AvailabilityCondition"]


class AvailabilityConditionOr(ApiBaseModel):
    type: Literal["or"]
    children: list["AvailabilityCondition"]


class AvailabilityConditionAll(ApiBaseModel):
    type: Literal["all"]


class TimezoneAware(ApiBaseModel):
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


class AvailabilityConditionHolidays(ApiBaseModel):
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


class TimeSpan(ApiBaseModel):
    """
    Object representing the half-open datetime interval: [start,end).
    """
    start: datetime
    end: datetime

    def __hash__(self) -> int:
        return hash(self.start) + hash(self.end)


class Vet(ApiBaseModel):
    title: str
    people: list[Person] = PydanticField(default_factory=list)
    location: Location
    contacts: list[Contact] = PydanticField(default_factory=list)
    available: AvailabilityCondition
    categories: list[Category] = PydanticField(default_factory=list)


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
