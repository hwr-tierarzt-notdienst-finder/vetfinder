import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TypeAlias, Literal, Callable, cast, Iterable, TypeVar, Type, Union

from dateutil import tz
from dateutil.relativedelta import relativedelta

_T = TypeVar("_T")
_Weekday: TypeAlias = Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_Timezone: TypeAlias = Literal["Europe/Berlin"]


_WEEKDAYS: list[_Weekday] = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_TIMEZONES: set[_Timezone] = {"Europe/Berlin"}


@dataclass(init=False, frozen=True)
class WeeklyExecutionTarget:
    weekday: _Weekday
    hour: int
    minute: int
    timezone: Literal["Europe/Berlin"]

    def __init__(
            self,
            *,
            weekday: _Weekday,
            hour: int,
            minute: int,
            timezone: Literal["Europe/Berlin"]
    ) -> None:
        # We need to use object.__setattr__ because object is frozen
        object.__setattr__(self, "weekday", validate_weekday(weekday))
        object.__setattr__(self, "hour", validate_hour(hour))
        object.__setattr__(self, "minute", validate_minute(minute))
        object.__setattr__(self, "timezone", validate_timezone(timezone))


@dataclass(frozen=True)
class Task:
    id: int
    name: str
    callback: Callable[[], None]


@dataclass(frozen=True)
class PendingTask(Task):
    execution_target: "WeeklyExecutionTarget"
    start_target_datetime: datetime


@dataclass(frozen=True)
class StartedTask(PendingTask):
    start_datetime: datetime


@dataclass(frozen=True)
class FinishedTask(StartedTask):
    finish_datetime: datetime
    result: Literal["success"] | Exception

    def was_success(self) -> bool:
        return self.result == "success"

    def was_failure(self) -> bool:
        return not self.was_success()


class Poller(ABC):
    _callbacks: list[Callable[[datetime], None]]
    _poll_when_unix_timestamp_seconds_is_multiple_of: int

    def __init__(self, poll_when_unix_timestamp_seconds_is_multiple_of: int) -> None:
        self._callbacks = []
        self._poll_when_unix_timestamp_seconds_is_multiple_of = poll_when_unix_timestamp_seconds_is_multiple_of

    def on_poll(self, callback: Callable[[], None]) -> None:
        """
        Register a callback that will be called when polling.

        Important: Polling must be stopped while callback is executed.
        """
        self._callbacks.append(callback)

    @property
    def poll_when_unix_timestamp_seconds_is_multiple_of(self) -> int:
        return self._poll_when_unix_timestamp_seconds_is_multiple_of

    @abstractmethod
    def start(self) -> None:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...


class WeeklyScheduler:
    _default_weekday: _Weekday
    _default_hour: int
    _default_minute: int
    _default_timezone: _Timezone
    _poller: Poller
    _get_utcnow: Callable[[], datetime]
    _task_id: int
    _task_is_running: bool
    _pending_tasks: list[PendingTask]
    _on_start_task_callbacks: list[Callable[[StartedTask], None]]
    _on_finish_task_callbacks: list[Callable[[FinishedTask], None]]

    def __init__(
            self,
            *,
            default_weekday: _Weekday,
            default_hour: int,
            default_timezone: _Timezone,
            default_minute: int = 0,
            poller: Poller | None = None,
            poll_when_unix_timestamp_seconds_is_multiple_of: int | None = None,
            event_loop: asyncio.AbstractEventLoop | None = None,
            get_utcnow: Callable[[], datetime] = datetime.utcnow
    ) -> None:
        self._default_weekday = default_weekday
        self._default_hour = default_hour
        self._default_minute = default_minute
        self._default_timezone = default_timezone
        self._get_utcnow = get_utcnow

        if poller:
            if poll_when_unix_timestamp_seconds_is_multiple_of is not None:
                raise ValueError(
                    "'poll_when_unix_timestamp_seconds_is_multiple_of' must be None if 'poller' is provided"
                )
            if event_loop is not None:
                raise ValueError(
                    "'event_loop' must be None if 'poller' is provided"
                )

            self._poller = poller
        else:
            if type(poll_when_unix_timestamp_seconds_is_multiple_of) is not int:
                raise TypeError(
                    "'poll_when_unix_timestamp_seconds_is_multiple_of' must be an integer if 'poller' is not provided"
                )

            poller_cls = create_async_event_loop_poller_cls(event_loop)
            self._poller = poller_cls(poll_when_unix_timestamp_seconds_is_multiple_of)

        self._poller.on_poll(self._handle_poll)

        self._task_id = 0
        self._task_is_running = False
        self._pending_tasks = []
        self._on_start_task_callbacks = []
        self._on_finish_task_callbacks = []

    def schedule(
            self,
            callback: Callable[[], None],
            name: str | None = None,
            *,
            infer_name: bool = False,
            weekday: _Weekday | None = None,
            weekdays: Literal["*"] | Iterable[_Weekday] | None = None,
            hour: int | None = None,
            hours: Literal["*"] | Iterable[int] | None = None,
            minute: int | None = None,
            minutes: Literal["*"] | Iterable[int] | None = None,
            timezone: _Timezone | None = None
    ) -> list[PendingTask]:
        if name is None:
            if infer_name:
                name = callback.__name__
            else:
                raise ValueError(
                    "If 'infer_name' is set to False, 'name' must be provided"
                )

        if weekday is None and weekdays is None:
            weekday = self._default_weekday

        if weekdays == "*":
            weekdays = _WEEKDAYS

        if hour is None and hours is None:
            hour = self._default_hour

        if hours == "*":
            hours = list(range(24))

        if minute is None and minutes is None:
            minute = self._default_minute

        if minutes == "*":
            minutes = list(range(60))

        if timezone is None:
            timezone = self._default_timezone

        result: list[PendingTask] = []
        for execution_target in create_weekly_execution_targets(
                weekday=weekday,
                weekdays=weekdays,
                hour=hour,
                hours=hours,
                minute=minute,
                minutes=minutes,
                timezone=timezone
        ):
            result.append(self._schedule_task(
                name=name,
                callback=callback,
                execution_target=execution_target
            ))

        return result

    def start(self) -> None:
        self._poller.start()

    def on_start_task(self, callback: Callable[[StartedTask], None]) -> None:
        self._on_start_task_callbacks.append(callback)

    def on_finish_task(self, callback: Callable[[FinishedTask], None]) -> None:
        self._on_finish_task_callbacks.append(callback)

    def _schedule_task(
            self,
            *,
            name: str,
            callback: Callable[[], None],
            execution_target: "WeeklyExecutionTarget"
    ) -> "PendingTask":
        self._task_id += 1
        start_target_datetime = create_datetime_from_weekly_execution_target(
            execution_target,
            self._get_utcnow
        )

        task = PendingTask(
            id=self._task_id,
            name=name,
            callback=callback,
            execution_target=execution_target,
            start_target_datetime=start_target_datetime,
        )

        self._pending_tasks.append(task)

        return task

    def _handle_poll(self, dt: datetime) -> None:
        dt = ensure_datetime_is_timezone_aware(dt)

        if not any(
            task.start_target_datetime <= dt
            for task in self._pending_tasks
        ):
            return

        tasks_to_be_run: list[PendingTask] = []
        new_pending_tasks: list[PendingTask] = []
        for task in self._pending_tasks:
            if task.start_target_datetime <= dt:
                tasks_to_be_run.append(task)
            else:
                new_pending_tasks.append(task)

        self._pending_tasks = new_pending_tasks

        for finished_task in self._run_tasks(tasks_to_be_run, dt):
            # Reschedule tasks
            self.schedule(
                finished_task.callback,
                name=finished_task.name,
                weekday=finished_task.execution_target.weekday,
                hour=finished_task.execution_target.hour,
                minute=finished_task.execution_target.minute,
                timezone=finished_task.execution_target.timezone
            )

    def _run_tasks(self, pending_tasks: list[PendingTask], dt: datetime) -> Iterable[FinishedTask]:
        for task in pending_tasks:
            if task.start_target_datetime >= dt:
                yield self._run_task(task, dt)

    def _run_task(self, pending_task: PendingTask, dt: datetime) -> FinishedTask:
        started_task = StartedTask(
            id=pending_task.id,
            name=pending_task.name,
            callback=pending_task.callback,
            execution_target=pending_task.execution_target,
            start_target_datetime=pending_task.start_target_datetime,
            start_datetime=dt
        )

        for on_start_callback in self._on_start_task_callbacks:
            on_start_callback(started_task)

        try:
            started_task.callback()
        except Exception as err:
            finished_dt = self._get_utcnow()
            result = err
        else:
            finished_dt = self._get_utcnow()
            result = "success"

        finished_task = FinishedTask(
            id=started_task.id,
            name=started_task.name,
            callback=started_task.callback,
            execution_target=started_task.execution_target,
            start_target_datetime=started_task.start_target_datetime,
            start_datetime=started_task.start_datetime,
            finish_datetime=finished_dt,
            result=result
        )

        for on_finish_callback in self._on_finish_task_callbacks:
            on_finish_callback(finished_task)

        return finished_task


def create_async_event_loop_poller_cls(event_loop: asyncio.AbstractEventLoop | None = None) -> Type["Poller"]:
    if event_loop is None:
        event_loop = asyncio.get_event_loop()

    class AsyncEventLoopPoller(Poller):
        _is_started: bool

        def __init__(self, poll_when_unix_timestamp_seconds_is_multiple_of: int) -> None:
            super().__init__(poll_when_unix_timestamp_seconds_is_multiple_of)

            self._is_started = False

        def start(self) -> None:
            self._is_started = True

            self._schedule_next_poll()

        def stop(self) -> None:
            self._is_started = False

        def _schedule_next_poll(self) -> None:
            unix_timestamp = time.time()
            delay_until_next_poll = (
                self.poll_when_unix_timestamp_seconds_is_multiple_of
                - unix_timestamp % self.poll_when_unix_timestamp_seconds_is_multiple_of
            )

            event_loop.call_later(delay_until_next_poll, self._poll)

        def _poll(self) -> None:
            if not self._is_started:
                return

            self.stop()
            self._call_callbacks()
            self.start()

            self._schedule_next_poll()

        def _call_callbacks(self) -> None:
            dt = datetime.utcnow()

            for callback in self._callbacks:
                callback(dt)

    return AsyncEventLoopPoller


def create_weekly_execution_targets(
        *,
        weekday: _Weekday | None = None,
        weekdays: Iterable[_Weekday] | None = None,
        hour: int | None = None,
        hours: Iterable[int] | None = None,
        minute: int | None = None,
        minutes: Iterable[int] | None = None,
        timezone: _Timezone = None
) -> Iterable[WeeklyExecutionTarget]:
    weekdays = create_list_from_single_obj_exclusively_or_iter(
        weekday,
        "weekday",
        weekdays,
        "weekdays"
    )
    hours = create_list_from_single_obj_exclusively_or_iter(
        hour,
        "hour",
        hours,
        "hours"
    )
    minutes = create_list_from_single_obj_exclusively_or_iter(
        minute,
        "minute",
        minutes,
        "minutes"
    )

    for weekday in weekdays:
        for hour in hours:
            for minute in minutes:
                yield WeeklyExecutionTarget(
                    weekday=weekday,
                    hour=hour,
                    minute=minute,
                    timezone=timezone
                )


def create_list_from_single_obj_exclusively_or_iter(
        single: _T | None,
        single_name: str,
        iter_: Iterable[_T] | None,
        iter_name: str,
) -> list[_T]:
    if single is None and iter_ is None:
        raise ValueError(
            f"Neither '{single_name}' nor '{iter_name}' where provided. One must be provided"
        )
    elif single is None and iter_ is not None:
        return list(iter_)
    elif single is not None and iter_ is None:
        return [single]
    else:
        raise ValueError(f"Either '{single_name}' or '{iter_name}' must be provided, not both")


def create_datetime_from_weekly_execution_target(
        execution_target: WeeklyExecutionTarget,
        get_utcnow: Callable[[], datetime]
) -> datetime:
    timezone_obj = tz.gettz(execution_target.timezone)

    now = ensure_datetime_is_timezone_aware(get_utcnow()).astimezone(timezone_obj)

    dt = (
        ensure_datetime_is_timezone_aware(get_utcnow()).astimezone(timezone_obj)
        + relativedelta(
            weekday=_WEEKDAYS.index(execution_target.weekday),
            hour=execution_target.hour,
            minute=execution_target.minute,
            second=0,
            microsecond=0
        )
    )

    while dt <= now:
        dt += relativedelta(weeks=1)

    return dt


def validate_weekday(day: str) -> _Weekday:
    if day in _WEEKDAYS:
        return cast(_Weekday, day)

    raise ValueError(f"Invalid weekday '{day}'")


def validate_hour(hour: int) -> int:
    if 0 <= hour <= 23:
        return hour

    raise ValueError(f"Hour must be between 0 and 23, not {hour}")


def validate_minute(minute: int) -> int:
    if 0 <= minute <= 60:
        return minute

    raise ValueError(f"Minute must be between 0 and 60, not {minute}")


def validate_timezone(timezone: str) -> _Timezone:
    if timezone in _TIMEZONES:
        return cast(_Timezone, timezone)

    raise ValueError(f"Invalid timezone '{timezone}'")


def ensure_datetime_is_timezone_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError(f"Datetime {dt} is not timezone aware")

    return dt
