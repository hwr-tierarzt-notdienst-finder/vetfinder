from datetime import datetime, timezone
from typing import Callable

from dateutil import tz

from src.schedulers import Poller, WeeklyScheduler
from src.types_ import Timezone


class SimulatedClock:
    _unix_timestamp: float
    _tick_interval: float
    _on_tick_callbacks: dict[str, Callable[[], None]]
    _is_started = False

    def __init__(
            self,
            start_unix_timestamp: float,
            tick_interval: float,
    ) -> None:
        self._unix_timestamp = start_unix_timestamp
        self._tick_interval = tick_interval
        self._on_tick_callbacks = {}
        self._is_started = False

    def run(self) -> None:
        self._is_started = True

        while self._is_started:
            self.tick()

    def stop(self) -> None:
        self._is_started = False

    def run_until_timestamp(self, end_timestamp: float) -> None:
        def stop_at_end_timestamp() -> None:
            if self.time() >= end_timestamp:
                self.stop()

        self.on_tick(stop_at_end_timestamp)
        self.run()

    def run_until_datetime(self, end_datetime: datetime) -> None:
        self.run_until_timestamp(end_datetime.timestamp())

    def tick(self) -> float:
        self._unix_timestamp += self._tick_interval

        for callback in self._on_tick_callbacks.values():
            callback()

        return self._unix_timestamp

    def on_tick(
            self,
            callback: Callable[[], None],
            id_: str | None = None,
    ) -> None:
        if id_ is None:
            id_ = callback.__qualname__

        self._on_tick_callbacks[id_] = callback

    def remove_on_tick(
            self,
            what: str | Callable[[], None],
    ) -> None:
        if type(what) is str:
            del self._on_tick_callbacks[what]
        elif callable(what):
            del self._on_tick_callbacks[what.__qualname__]
        else:
            raise ValueError(f"No callback registered for '{what}'")

    def time(self) -> float:
        return self._unix_timestamp

    def utcnow(self) -> datetime:
        return datetime.fromtimestamp(self.time(), tz=timezone.utc)


class SimulatedPoller(Poller):
    _clock: SimulatedClock
    _is_started: bool

    def __init__(
            self,
            clock: SimulatedClock,
            poll_when_unix_timestamp_seconds_is_multiple_of: int
    ) -> None:
        super().__init__(poll_when_unix_timestamp_seconds_is_multiple_of)

        self._clock = clock
        self._is_started = False

    def start(self) -> None:
        self._is_started = True

        poll_callback_id = "_poll"

        def get_next_poll_time() -> float:
            t = self._clock.time()
            rest = t % self.poll_when_unix_timestamp_seconds_is_multiple_of

            return t + (self.poll_when_unix_timestamp_seconds_is_multiple_of - rest)

        next_poll_time = get_next_poll_time()

        def poll() -> None:
            nonlocal next_poll_time

            if not self._is_started:
                self._clock.remove_on_tick(poll_callback_id)
                return

            if self._clock.time() >= next_poll_time:
                for callback in self._callbacks:
                    callback(self._clock.utcnow())

                next_poll_time = get_next_poll_time()

        self._clock.on_tick(
            poll,
            poll_callback_id
        )

    def stop(self) -> None:
        self._is_started = False


def test_scheduler() -> None:

    # Setup
    # ----------------------------------------------------------------------

    timezone_: Timezone = "Europe/Berlin"

    start_dt = datetime(
        year=2022,
        month=9,
        day=5,  # Monday, 1st week
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=tz.gettz(timezone_),
    )
    end_dt = datetime(
        year=2022,
        month=9,
        day=19,  # Monday, 3rd week
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=tz.gettz(timezone_),
    )
    clock = SimulatedClock(
        start_unix_timestamp=start_dt.timestamp(),
        tick_interval=60,
    )
    poller = SimulatedPoller(
        clock,
        poll_when_unix_timestamp_seconds_is_multiple_of=60 * 5
    )
    scheduler = WeeklyScheduler(
        default_weekday="Tue",
        default_hour=3,
        default_minute=30,
        default_timezone=timezone_,
        poller=poller,
        get_utcnow=clock.utcnow
    )

    # Schedule tasks
    # ----------------------------------------------------------------------

    task1_expected_execution_dts = [
        datetime(
            year=2022,
            month=9,
            day=weekday,
            hour=3,
            minute=30,
            second=0,
            microsecond=0,
            tzinfo=tz.gettz(timezone_),
        )
        for weekday in [6, 13]  # Tuesdays
    ]
    task1_actual_execution_dts = []

    def task1() -> None:
        task1_actual_execution_dts.append(clock.utcnow())

    scheduler.schedule(task1, infer_name=True)

    task2_expected_execution_dts = [
        datetime(
            year=2022,
            month=9,
            day=weekday,
            hour=22,
            minute=minute,
            second=0,
            microsecond=0,
            tzinfo=tz.gettz(timezone_),
        )
        for weekday in [10, 11, 17, 18]  # Weekends
        for minute in [0, 30]
    ]
    task2_actual_execution_dts = []

    def task2() -> None:
        task2_actual_execution_dts.append(clock.utcnow())

    scheduler.schedule(
        task2,
        infer_name=True,
        weekdays=["Sat", "Sun"],
        hour=22,
        minutes=[0, 30],
    )

    # Run
    # ----------------------------------------------------------------------

    scheduler.start()
    clock.run_until_datetime(end_dt)

    # Test results
    # ----------------------------------------------------------------------

    for expected_execution_dts, actual_execution_dts in [
        (task1_expected_execution_dts, task1_actual_execution_dts),
        (task2_expected_execution_dts, task2_actual_execution_dts)
    ]:
        assert len(actual_execution_dts) == len(expected_execution_dts)
        for expected_dt, actual_dt in zip(
                expected_execution_dts,
                actual_execution_dts,
        ):
            assert expected_dt == actual_dt
