import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Logger, Handler, Formatter, Filter, LogRecord
from pathlib import Path
from typing import Literal, cast, TypeAlias, TypedDict, Iterable, Protocol

from . import path
from . import cache


# Standard library does not have type hints for levels
LevelCritical = Literal[50]
LevelError = Literal[40]
LevelWarn = Literal[30]
LevelInfo = Literal[20]
LevelDebug = Literal[10]

Level = Literal[
    LevelCritical,
    LevelError,
    LevelWarn,
    LevelInfo,
    LevelDebug,
]

LevelNameCritical = Literal["CRITICAL"]
LevelNameError = Literal["ERROR"]
LevelNameWarn = Literal["WARNING"]
LevelNameInfo = Literal["INFO"]
LevelNameDebug = Literal["DEBUG"]

LevelName: TypeAlias = Literal[
    LevelNameCritical,
    LevelNameError,
    LevelNameWarn,
    LevelNameInfo,
    LevelNameDebug
]

CRITICAL: LevelCritical = 50
ERROR: LevelError = 40
WARNING: LevelWarn = 30
INFO: LevelInfo = 20
DEBUG: LevelDebug = 10

assert CRITICAL == logging.CRITICAL
assert ERROR == logging.ERROR
assert WARNING == logging.WARNING
assert INFO == logging.INFO
assert DEBUG == logging.DEBUG

LEVELS: list[Level] = [
    CRITICAL,
    ERROR,
    WARNING,
    INFO,
    DEBUG,
]
LEVEL_NAMES: list[LevelName] = [
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
]
_NAME_TO_LEVEL: dict[str, Level] = dict(zip(
    LEVEL_NAMES,
    LEVELS
))
_LEVEL_TO_NAME: dict[Level, str] = dict(zip(LEVELS, LEVEL_NAMES))
_FORMAT = "[%(asctime)s] %(message)s"


def level_to_str(level: Level) -> str:
    return _LEVEL_TO_NAME[level]


def level_to_lower_str(level: Level) -> str:
    return level_to_str(level).lower()


def level_from_name(name: LevelName) -> Level:
    return _NAME_TO_LEVEL[name]


def level_from_lower_name(name: str) -> Level:
    if not name.islower():
        raise ValueError(f"Name '{name}' does not contain only lowercase letters")

    return level_from_name(cast(LevelName, name.upper()))


def level_normalized(level: str | int) -> Level:
    if type(level) is int:
        if level in LEVELS:
            return cast(Level, level)

        raise ValueError(f"Unknown level with integer value {level}")

    # Try string lookup
    try:
        return level_from_name(cast(LevelName, level))
    except KeyError as err:
        err1 = err

    # Try string lookup with uppercase string if all characters are lower
    try:
        if level.islower():
            return level_from_lower_name(level)
        else:
            raise err1
    except KeyError as err:
        raise ValueError(
            f"'{level}' could not be converted to a level integer"
        ) from err


class LoggerFactory(Protocol):

    def create(self, *path_: str) -> Logger: ...


class LoggerFactoryTimeBasedRolloverSingleDirDotDelimitedFiles(LoggerFactory):
    _LEVEL_TO_SAVE_CONFIG: dict[
        LevelName,
        TypedDict("Config", {
            "rollover_period": int,
            "rollover_unit": Literal["day", "hour"],
            "keep_n_old_after_rollover": int,
        })
    ] = {
        "CRITICAL": {
            "rollover_period": 1,
            "rollover_unit": "day",
            # Save old logs for ~year
            "keep_n_old_after_rollover": 365,
        },
        "ERROR": {
            "rollover_period": 1,
            "rollover_unit": "day",
            # Save old logs for ~month
            "keep_n_old_after_rollover": 31,
        },
        "WARNING": {
            "rollover_period": 1,
            "rollover_unit": "day",
            "keep_n_old_after_rollover": 31,
        },
        "INFO": {
            "rollover_period": 1,
            "rollover_unit": "day",
            # Save old logs for week
            "keep_n_old_after_rollover": 7,
        },
        "DEBUG": {
            "rollover_period": 1,
            "rollover_unit": "hour",
            # Don't save old logs
            "keep_n_old_after_rollover": 1,
        }
    }

    _logs_dir: Path

    def __init__(self, logs_dir: str | Path) -> None:
        self._logs_dir = path.dir_from(logs_dir)

    def create(self, *path_: str) -> Logger:
        name = ".".join(path_)

        logger = logging.getLogger(name)
        logger.setLevel(DEBUG)

        formatter = Formatter(_FORMAT)

        for handler in self._create_handlers(name, formatter):
            logger.addHandler(handler)

        return logger

    def _create_handlers(self, logger_name: str, formatter: Formatter) -> Iterable[Handler]:
        for level_name in LEVEL_NAMES:
            save_config = self._LEVEL_TO_SAVE_CONFIG[level_name]

            when_arg: str
            if (rollover_unit := save_config["rollover_unit"]) == "day":
                when_arg = "D"
            elif rollover_unit == "hour":
                when_arg = "H"
            else:
                raise ValueError(f"Invalid rollover unit '{rollover_unit}'")

            handler = TimedRotatingFileHandler(
                self._logs_dir / f"{logger_name}.{level_name.lower()}",
                when=when_arg,
                interval=save_config["rollover_period"],
                backupCount=save_config["keep_n_old_after_rollover"],
            )
            handler.addFilter(_SpecificLogLevelFilter(log_level=level_name))
            handler.setFormatter(formatter)

            yield handler


class _SpecificLogLevelFilter(Filter):
    _log_level: LevelName

    def __init__(self, log_level: LevelName) -> None:
        super().__init__()

        self._log_level = log_level

    def filter(self, record: LogRecord) -> bool:
        return record.levelname == self._log_level


def create_logger(
        *path_: str,
        factory: LoggerFactory | None = None
) -> Logger:
    if factory is None:
        factory = _create_default_logger_factory()

    return factory.create(*path_)


@cache.return_singleton
def _create_default_logger_factory() -> LoggerFactory:
    return LoggerFactoryTimeBasedRolloverSingleDirDotDelimitedFiles(
        path.find_logs()
    )

