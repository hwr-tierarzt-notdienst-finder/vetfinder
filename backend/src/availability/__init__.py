from datetime import datetime, timedelta
from functools import wraps
from typing import Iterable, TypeVar, Callable

from dateutil.tz import gettz

from .. import validate
from .. import cache
from ..models import (
    AvailabilityCondition,
    Vet,
    TimeSpan,
)
from ..types_ import Timezone

from . import time_spans_from_non_primitive_conditions


_T = TypeVar("_T")


# We don't use UTC because it's easier to debug
# when stuff is in your local timezone
_REFERENCE_TIMEZONE: Timezone = "Europe/Berlin"
_CONDITIONS = {
    "not",
    "and",
    "or",
    "all",
    "time_span_during_day",
    "weekdays",
    "holidays",
}
_PRIMITIVE_CONDITIONS = {
    "not",
    "and",
    "or",
    "all",
}


def get_time_spans(
        lower_bound: datetime,
        upper_bound: datetime,
        vet: Vet,
) -> Iterable[TimeSpan]:
    """
    Returns a list of time spans generated from the `vet.available` decision tree.

    The time spans fit in the half-open interval [lower_bound,upper_bound).
    """
    validate.datetime_is_timezone_aware(lower_bound)
    validate.datetime_is_timezone_aware(upper_bound)

    lower_bound = _datetime_in_reference_tz(lower_bound)
    upper_bound = _datetime_in_reference_tz(upper_bound)

    return _get_time_spans_from_condition(
        lower_bound,
        upper_bound,
        vet.available,
    )


def _get_time_spans_from_condition(
        lower_bound: datetime,
        upper_bound: datetime,
        condition: AvailabilityCondition,
) -> Iterable[TimeSpan]:
    if condition.type == "not":
        yield from _not_operation(
            lower_bound,
            upper_bound,
            _get_time_spans_from_condition(
                lower_bound,
                upper_bound,
                condition.child
            )
        )
    elif condition.type == "or":
        yield from _or_operation(
            lower_bound,
            upper_bound,
            _chain_and_sort_timespans(
                _get_time_spans_from_condition(
                    lower_bound,
                    upper_bound,
                    child_condition,
                )
                for child_condition in condition.children
            ),
        )
    elif condition.type == "and":
        # We use de morgan's laws
        yield from _not_operation(
            lower_bound,
            upper_bound,
            _or_operation(
                lower_bound,
                upper_bound,
                _chain_and_sort_timespans(
                    _not_operation(
                        lower_bound,
                        upper_bound,
                        _get_time_spans_from_condition(
                            lower_bound,
                            upper_bound,
                            child_condition
                        ),
                    )
                    for child_condition in condition.children
                )
            )
        )
    elif condition.type == "all":
        yield TimeSpan(
            start=lower_bound,
            end=upper_bound,
        )
    else:
        yield from _get_time_spans_from_non_primitive_condition(
            lower_bound,
            upper_bound,
            condition,
        )


def _not_operation(
        lower_bound: datetime,
        upper_bound: datetime,
        time_spans: Iterable[TimeSpan],
) -> Iterable[TimeSpan]:
    last_time_span = TimeSpan(start=lower_bound, end=lower_bound)

    for time_span in time_spans:
        start = last_time_span.end
        end = time_span.start

        if end - start > timedelta(milliseconds=0):
            yield TimeSpan(
                start=last_time_span.end,
                end=time_span.start,
            )

        last_time_span = time_span

    start = last_time_span.end
    end = upper_bound

    if end - start > timedelta(milliseconds=0):
        yield TimeSpan(
            start=last_time_span.end,
            end=upper_bound,
        )


def _or_operation(
        lower_bound: datetime,
        upper_bound: datetime,
        time_spans: Iterable[TimeSpan],
) -> Iterable[TimeSpan]:
    result: list[TimeSpan] = []

    for time_span in time_spans:
        result = _apply_or_single(
            lower_bound,
            upper_bound,
            result,
            time_span,
        )

    return result


def _apply_or_single(
        lower_bound: datetime,
        upper_bound: datetime,
        time_spans: list[TimeSpan],
        time_span: TimeSpan
) -> list[TimeSpan]:
    time_span = _trim_time_span_to_bounds(
        lower_bound,
        upper_bound,
        time_span
    )

    new_time_spans: list[TimeSpan] = []

    for existing_ts in time_spans:
        is_joined = (
                time_span.start <= existing_ts.start <= time_span.end
                or time_span.start <= existing_ts.end <= time_span.end
        )

        if is_joined:
            time_span = TimeSpan(
                start=min(existing_ts.start, time_span.start),
                end=max(existing_ts.end, time_span.end),
            )
        else:
            new_time_spans.append(existing_ts)

    new_time_spans.append(time_span)

    return new_time_spans


def _get_time_spans_from_non_primitive_condition(
        lower_bound: datetime,
        upper_bound: datetime,
        condition: AvailabilityCondition,
) -> Iterable[TimeSpan]:
    condition_type_to_get_func = _get_non_primitive_condition_type_to_get_funcs_map()

    yield from condition_type_to_get_func[condition.type](
        lower_bound,
        upper_bound,
        condition
    )


def _apply_trim_yielded_time_spans(
        func: Callable[[datetime, datetime, AvailabilityCondition], Iterable[TimeSpan]]
) -> Callable[[datetime, datetime, AvailabilityCondition], Iterable[TimeSpan]]:

    @wraps(func)
    def wrapped_func(
            lower_bound: datetime,
            upper_bound: datetime,
            condition: AvailabilityCondition,
    ) -> Iterable[TimeSpan]:
        for time_span in func(
                lower_bound,
                upper_bound,
                condition,
        ):
            yield _trim_time_span_to_bounds(
                lower_bound,
                upper_bound,
                time_span
            )

    return wrapped_func


@cache.return_singleton
def _get_non_primitive_condition_type_to_get_funcs_map() -> dict[
    str,
    Callable[[datetime, datetime, AvailabilityCondition], Iterable[TimeSpan]]
]:
    result: dict[
        str,
        Callable[[datetime, datetime, AvailabilityCondition], Iterable[TimeSpan]]
    ] = {}
    for condition_type in _CONDITIONS - _PRIMITIVE_CONDITIONS:
        original_func = time_spans_from_non_primitive_conditions.__dict__[condition_type]

        result[condition_type] = _apply_trim_yielded_time_spans(original_func)

    return result


def _trim_time_span_to_bounds(
        lower_bound: datetime,
        upper_bound: datetime,
        time_span: TimeSpan,
) -> TimeSpan:
    return TimeSpan(
        start=max(lower_bound, time_span.start),
        end=min(time_span.end, upper_bound),
    )


_reference_tz_object = None
def _datetime_in_reference_tz(dt: datetime) -> datetime:
    global _reference_tz_object

    if _reference_tz_object is None:
        _reference_tz_object = gettz(_REFERENCE_TIMEZONE)

    return dt.astimezone(_reference_tz_object)


def _chain_and_sort_timespans(
        iters: Iterable[Iterable[TimeSpan]]
) -> Iterable[_T]:
    unsorted_timespans: set[TimeSpan] = set()

    for iter_ in iters:
        for time_span in iter_:
            unsorted_timespans.add(time_span)

    def sort_key_func(time_span: TimeSpan) -> datetime:
        return time_span.start

    return sorted(unsorted_timespans, key=sort_key_func)
