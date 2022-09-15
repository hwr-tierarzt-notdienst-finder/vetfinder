from datetime import datetime, timedelta
from typing import Iterable, TypeVar

from dateutil.tz import gettz

from shared.constants import WEEKDAYS
from shared.models import (
    TimeSpan,
    AvailabilityConditionTimeSpanDuringDay,
    AvailabilityConditionWeekdaysSpan,
    AvailabilityConditionHolidays,
)

from .holidays import get_by_region as get_holidays_by_region


_T = TypeVar("_T")


def time_span_during_day(
        lower_bound: datetime,
        upper_bound: datetime,
        time_span_during_day_condition: AvailabilityConditionTimeSpanDuringDay,
) -> Iterable[TimeSpan]:
    tz_obj = gettz(time_span_during_day_condition.timezone)

    # Not choosing 0 as hour may help with daylight savings bugs
    current_day = _get_start_of_hour_in_day(6, lower_bound.astimezone(tz_obj))
    last_day = _get_start_of_hour_in_day(18, upper_bound.astimezone(tz_obj))

    while current_day < last_day:
        yield TimeSpan(
            start=current_day.replace(
                hour=time_span_during_day_condition.start_time.hour,
                minute=time_span_during_day_condition.start_time.minute,
            ),
            end=current_day.replace(
                hour=time_span_during_day_condition.end_time.hour,
                minute=time_span_during_day_condition.end_time.minute,
            )
        )

        current_day += timedelta(days=1)


def weekdays(
        lower_bound: datetime,
        upper_bound: datetime,
        weekdays_span_condition: AvailabilityConditionWeekdaysSpan,
) -> Iterable[TimeSpan]:
    weekday_start_index = WEEKDAYS.index(weekdays_span_condition.start_day)
    weekday_end_index = WEEKDAYS.index(weekdays_span_condition.end_day)

    tz_obj = gettz(weekdays_span_condition.timezone)

    # Not choosing 0 as hour may help with daylight savings bugs
    current_day = _get_start_of_hour_in_day(6, lower_bound.astimezone(tz_obj))
    last_day = _get_start_of_hour_in_day(18, upper_bound.astimezone(tz_obj))

    while current_day <= last_day:
        if weekday_start_index <= (weekday_index := current_day.weekday()) <= weekday_end_index:
            days_until_end_of_span = weekday_end_index - weekday_index + 1

            start = _get_day_start(current_day)
            end = _get_day_start(
                current_day
                + timedelta(days=days_until_end_of_span)
            )

            yield TimeSpan(
                start=start,
                end=end
            )

            # Jump to end of weekend
            current_day += timedelta(days=days_until_end_of_span)
        else:
            # Jump to next day
            current_day += timedelta(days=1)


def holidays(
        lower_bound: datetime,
        upper_bound: datetime,
        holiday_span_condition: AvailabilityConditionHolidays,
) -> Iterable[TimeSpan]:
    for day in get_holidays_by_region(
            lower_bound,
            upper_bound,
            holiday_span_condition.region
    ):
        yield TimeSpan(
            start=day.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            ),
            end=(day + timedelta(days=1)).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        )


def _get_start_of_hour_in_day(hour: int, dt: datetime) -> datetime:
    return dt.replace(
        hour=hour,
        minute=0,
        second=0,
        microsecond=0,
    )


def _get_day_start(dt: datetime) -> datetime:
    return _get_start_of_hour_in_day(0, dt)
