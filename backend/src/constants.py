from typing import cast

from types_ import Weekday, Timezone, Region, VetVisibility, VetVerificationStatus
from utils import typing_

WEEKDAYS = cast(
    list[Weekday],
    list(typing_.extract_strings_from_type(Weekday))
)
TIMEZONES = cast(
    set[Timezone],
    set(typing_.extract_strings_from_type(Timezone))
)
REGIONS = cast(
    set[Region],
    set(typing_.extract_strings_from_type(Region))
)
VET_VISIBILITIES = cast(
    set[VetVisibility],
    set(typing_.extract_strings_from_type(VetVisibility))
)
VET_VERIFICATION_STATUSES = cast(
    set[VetVerificationStatus],
    set(typing_.extract_strings_from_type(VetVerificationStatus))
)
