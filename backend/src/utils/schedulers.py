import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Callable, Iterable, TypeVar, Type

from dateutil import tz
from dateutil.relativedelta import relativedelta

from ..constants import WEEKDAYS
from ..types_ import Weekday, Timezone
from . import validate

_T = TypeVar("_T")


@dataclass(init=False, frozen=True)
class WeeklyExecutionTarget:
    weekday: Weekday
    hour: int
    minute: int
    timezone: Timezone

    def __init__(
            self,
            *,
            weekday: Weekday,
            hour: int,
            minute: int,
            timezone: Timezone
    ) -> None:
        # We need to use object.__setattr__ because object is frozen
        object.__setattr__(self, "weekday", validate.weekday(weekday))
        object.__setattr__(self, "hour", validate.hour(hour))
        object.__setattr__(self, "minute", validate.minute(minute))
        object.__setattr__(self, "timezone", validate.timezone(timezone))


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
    """

    """

    _default_weekdays: list[Weekday]
    _default_hour: int
    _default_minute: int
    _default_timezone: Timezone
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
            default_timezone: Timezone,
            default_hour: int,
            default_minute: int,
            default_weekday: Weekday | None = None,
            default_weekdays: Literal["*"] | Iterable[Weekday] | None = None,
            poller: Poller | None = None,
            poll_when_unix_timestamp_seconds_is_multiple_of: int | None = None,
            event_loop: asyncio.AbstractEventLoop | None = None,
            get_utcnow: Callable[[], datetime] = datetime.utcnow
    ) -> None:
        if default_weekday is not None and default_weekdays is not None:
            raise ValueError(
                "Either 'default_weekday' or 'default_weekdays' must be provided, not both"
            )
        elif default_weekday is not None:
            self._default_weekdays = [validate.weekday(default_weekday)]
        elif default_weekdays == "*":
            self._default_weekdays = WEEKDAYS
        elif default_weekdays is not None:
            self._default_weekdays = [
                validate.weekday(weekday) for weekday in default_weekdays
            ]
        else:
            raise ValueError(
                "Neither 'default_weekday' nor 'default_weekdays' was provided"
            )
        self._default_hour = validate.hour(default_hour)
        self._default_minute = validate.minute(default_minute)
        self._default_timezone = validate.timezone(default_timezone)
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

            poller_cls = _create_async_event_loop_poller_cls(event_loop)
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
            weekday: Weekday | None = None,
            weekdays: Literal["*"] | Iterable[Weekday] | None = None,
            hour: int | None = None,
            hours: Literal["*"] | Iterable[int] | None = None,
            minute: int | None = None,
            minutes: Literal["*"] | Iterable[int] | None = None,
            timezone: Timezone | None = None
    ) -> list[PendingTask]:
        if name is None:
            if infer_name:
                name = callback.__name__
            else:
                raise ValueError(
                    "If 'infer_name' is set to False, 'name' must be provided"
                )

        if weekday is not None:
            weekday = validate.weekday(weekday)

        if weekday is None and weekdays is None:
            weekdays = self._default_weekdays
        if weekdays == "*":
            weekdays = WEEKDAYS
        if weekdays is not None:
            weekdays = [validate.weekday(weekday) for weekday in weekdays]

        if hour is None and hours is None:
            hour = self._default_hour
        if hour is not None:
            hour = validate.hour(hour)

        if hours == "*":
            hours = list(range(24))
        if hours is not None:
            hours = [validate.hour(hour) for hour in hours]

        if minute is None and minutes is None:
            minute = self._default_minute
        if minute is not None:
            minute = validate.minute(minute)

        if minutes == "*":
            minutes = list(range(60))
        if minutes is not None:
            minutes = [validate.minute(minute) for minute in minutes]

        if timezone is None:
            timezone = self._default_timezone
        if timezone is not None:
            timezone = validate.timezone(timezone)

        result: list[PendingTask] = []
        for execution_target in _create_weekly_execution_targets(
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
        start_target_datetime = _create_datetime_from_weekly_execution_target(
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
        dt = validate.datetime_is_timezone_aware(dt)

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


def _create_async_event_loop_poller_cls(event_loop: asyncio.AbstractEventLoop | None = None) -> Type["Poller"]:
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


def _create_weekly_execution_targets(
        *,
        weekday: Weekday | None = None,
        weekdays: Iterable[Weekday] | None = None,
        hour: int | None = None,
        hours: Iterable[int] | None = None,
        minute: int | None = None,
        minutes: Iterable[int] | None = None,
        timezone: Timezone = None
) -> Iterable[WeeklyExecutionTarget]:
    weekdays = _create_list_from_single_obj_exclusively_or_iter(
        weekday,
        "weekday",
        weekdays,
        "weekdays"
    )
    hours = _create_list_from_single_obj_exclusively_or_iter(
        hour,
        "hour",
        hours,
        "hours"
    )
    minutes = _create_list_from_single_obj_exclusively_or_iter(
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


def _create_list_from_single_obj_exclusively_or_iter(
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


def _create_datetime_from_weekly_execution_target(
        execution_target: WeeklyExecutionTarget,
        get_utcnow: Callable[[], datetime]
) -> datetime:
    timezone_obj = tz.gettz(execution_target.timezone)

    now = validate.datetime_is_timezone_aware(get_utcnow()).astimezone(timezone_obj)

    dt = (
            validate.datetime_is_timezone_aware(get_utcnow()).astimezone(timezone_obj)
            + relativedelta(
            weekday=WEEKDAYS.index(execution_target.weekday),
            hour=execution_target.hour,
            minute=execution_target.minute,
            second=0,
            microsecond=0
        )
    )

    while dt <= now:
        dt += relativedelta(weeks=1)

    return dt
