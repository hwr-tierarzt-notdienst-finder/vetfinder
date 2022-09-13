from pathlib import Path
from typing import Iterable

from shared import log
from shared import file_system


def test_log() -> None:
    with file_system.temp_dir(Path(__file__).parent / "test_logs") as log_dir:
        logger_factory = log.LoggerFactoryTimeBasedRolloverSingleDirDotDelimitedFiles(
            log_dir
        )

        logger1 = log.create_logger("logger1", factory=logger_factory)
        logger2 = log.create_logger("logger2", factory=logger_factory)
        logger3 = log.create_logger("logger", "num3", factory=logger_factory)

        loggers = [logger1, logger2, logger3]

        for i in range(3):
            for logger in loggers:
                logger.critical(f"critical {i}")
                logger.error(f"error {i}")
                logger.warning(f"warning {i}")
                logger.info(f"info {i}")
                logger.debug(f"debug {i}")

        def expected_dir_contents() -> Iterable[dict]:
            general_log_line_matcher = (
                "regex:full",
                r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}\] .*"
            )

            for expected_logger_file_start in [
                "logger1",
                "logger2",
                "logger.num3"
            ]:
                for log_level in [
                    "critical",
                    "error",
                    "warning",
                    "info",
                    "debug",
                ]:
                    yield {
                        "type": "file",
                        "match_name": f"{expected_logger_file_start}.{log_level}",
                        "match_contents": [
                            (
                                "all",
                                [
                                    general_log_line_matcher,
                                    ("end", f"{log_level} 0"),
                                ]
                            ),
                            (
                                "all",
                                [
                                    general_log_line_matcher,
                                    ("end", f"{log_level} 1"),
                                ]
                            ),
                            (
                                "all",
                                [
                                    general_log_line_matcher,
                                    ("end", f"{log_level} 2")
                                ]
                            )
                        ]
                    }

        file_system.matching_dir_contents(
            log_dir,
            expected_dir_contents(),
        )
