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


class ModelWithId(BaseModel):
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
    roles: list[Literal["owner"]]


class Address(ApiBaseModel):
    street: str
    zip_code: int
    city: str
    number: str | None = None

    def __hash__(self) -> int:
        return hash(
            f"{self.street}:{self.number}:{self.zip_code}:{self.city}"
        )


class Location(ApiBaseModel):
    address: Address
    lat: float | None = None
    lon: float | None = None

    def __hash__(self) -> int:
        return hash(
            f"{hash(self.address)}:{self.lat}:{self.lon}"
        )


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
    DOGS = "dogs"
    CATS = "cats"
    HORSES = "horses"
    SMALL_ANIMALS = "small_animals"
    MISC = "misc"


class TimeSpan(ApiBaseModel):
    """
    Object representing the half-open datetime interval: [start,end).
    """
    start: datetime
    end: datetime

    def __hash__(self) -> int:
        return hash(self.start) + hash(self.end)


class RegistrationEmailInfo(ApiBaseModel):
    email_address: str


class VetCreateOrOverwrite(ApiBaseModel):
    clinic_name: str
    title: str
    location: Location
    contacts: list[Contact] = PydanticField(default_factory=list)
    available: AvailabilityCondition
    categories: list[Category] = PydanticField(default_factory=list)


class Vet(VetCreateOrOverwrite):
    id: str


class VetResponse(Vet):
    availability: list[TimeSpan] | None = None
