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

class NameInformation(ApiBaseModel):
    form_of_address: Literal["mr", "ms", "divers"] | None = None
    title: Literal[
        "dr_med",
        "dr_med_dent",
        "dr_med_vent",
        "dr_phil",
        "dr_paed",
        "dr_rer_nat",
        "dr_rer_pol",
        "dr_ing",
    ] | None = None
    first_name: str
    last_name: str


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
    type: Literal["not"] = "not"
    child: AvailabilityCondition

    def __hash__(self) -> int:
        return hash(
            f"type='{self.type}';"
            f"child='{hash(self.child)}'"
        )


class AvailabilityConditionAnd(ApiBaseModel):
    type: Literal["and"] = "and"
    children: list[AvailabilityCondition]

    def __hash__(self) -> int:
        return hash(
            f"type='{self.type}';"
            f"children='{','.join(str(hash(child)) for child in self.children)}'"
        )


class AvailabilityConditionOr(ApiBaseModel):
    type: Literal["or"] = "or"
    children: list[AvailabilityCondition]

    def __hash__(self) -> int:
        return hash(
            f"type='{self.type}';"
            f"children='{','.join(str(hash(child)) for child in self.children)}'"
        )


class AvailabilityConditionAll(ApiBaseModel):
    type: Literal["all"]

    def __hash__(self) -> int:
        return hash(self.type)


class TimezoneAware(ApiBaseModel):
    timezone: Timezone


class TimeDuringDay(ApiBaseModel):
    hour: int
    minute: int


class AvailabilityConditionTimeSpan(ApiBaseModel):
    type: Literal["time_span"] = "time_span"
    start: datetime
    end: datetime

    def __hash__(self) -> int:
        return hash(
            f"type='{self.type}';"
            f"start='{self.start}';"
            f"end='{self.end}'"
        )


class AvailabilityConditionTimeSpanDuringDay(TimezoneAware):
    type: Literal["time_span_during_day"] = "time_span_during_day"
    start_time: TimeDuringDay
    end_time: TimeDuringDay

    def __hash__(self) -> int:
        return hash(
            f"type='{self.type}';"
            f"start_time='{self.start_time}';"
            f"end_time='{self.end_time}';"
            f"timezone='{self.timezone}'"
        )


Weekday: TypeAlias = Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class AvailabilityConditionWeekdaysSpan(TimezoneAware):
    type: Literal["weekdays"] = "weekdays"
    start_day: Weekday
    end_day: Weekday

    def __hash__(self) -> int:
        return hash(
            f"type='{self.type}';"
            f"start_day='{self.start_day}';"
            f"end_day='{self.end_day}';"
            f"timezone='{self.timezone}'"
        )


class AvailabilityConditionHolidays(ApiBaseModel):
    type: Literal["holidays"] = "holidays"
    region: Region

    def __hash__(self) -> int:
        return hash(
            f"type='{self.type}';"
            f"region='{self.region}'"
        )


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


class Treatments(str, Enum):
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


class Time24HourClock(ApiBaseModel):
    hour: int
    minute: int = 0
    second: int = 0
    digital_clock_string: str


class TimeSpan24HourClock(ApiBaseModel):
    start_time: Time24HourClock
    end_time: Time24HourClock
    digital_clock_string: str


TimesDuringWeek24HourClock = dict[Weekday, list[TimeSpan24HourClock]]


class RegistrationEmailInfo(ApiBaseModel):
    email_address: str


class VetCreateOrOverwrite(ApiBaseModel):
    clinic_name: str
    name_information: NameInformation
    location: Location
    contacts: list[Contact] = PydanticField(default_factory=list)
    availability_condition: AvailabilityCondition
    emergency_availability_condition: AvailabilityCondition
    categories: list[Treatments] = PydanticField(default_factory=list)


class Vet(VetCreateOrOverwrite):
    id: str


class VetResponse(Vet):
    availability: list[TimeSpan] | None = None
    emergency_availability: list[TimeSpan] | None = None
    availability_during_week: TimesDuringWeek24HourClock | None = None
    emergency_availability_during_week: TimesDuringWeek24HourClock | None = None
