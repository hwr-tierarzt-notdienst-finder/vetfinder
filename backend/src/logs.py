from logging import Logger

import paths
from shared.utils import cache
from shared.utils import log


def create_logger(
        *path_: str,
        factory: log.LoggerFactory | None = None
) -> Logger:
    if factory is None:
        factory = _create_default_logger_factory()

    return factory.create(*path_)


@cache.return_singleton
def _create_default_logger_factory() -> log.LoggerFactory:
    return log.LoggerFactoryTimeBasedRolloverSingleDirDotDelimitedFiles(
        paths.find_logs()
    )
