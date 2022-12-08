from logging import Logger
from typing import Callable, Any, Iterable, TypeVar, Generic

_T = TypeVar("_T")
_RT = TypeVar("_RT")

_Step = Callable[[Logger], Any] | Callable[[Logger, Any, ...], Any]


class Pipeline(Generic[_T, _RT]):
    _logger: Logger
    _steps: list[tuple[str, _Step]]

    def __init__(
            self,
            logger: Logger,
            steps: Iterable[_Step | tuple[str, _Step]] | None = None,
    ) -> None:
        self._logger = logger
        self._steps = []

        if steps is not None:
            self.add_steps(steps)

    def add_step(
            self,
            step: _Step,
            *,
            name: str = None,
            infer_name: bool = False,
    ) -> None:
        if not callable(step):
            raise ValueError(f"Step '{step}' is not callable")

        if name is None:
            if infer_name:
                name = step.__name__
            else:
                raise ValueError(
                    f"No name for step '{step}' provided. Set 'infer_name' to true to infer the name"
                )

        self._steps.append((name, step))

    def add_steps(
            self,
            steps: Iterable[_Step | tuple[str, _Step]],
            infer_name: bool = False
    ) -> None:
        for item in steps:
            if type(item) is tuple:
                self.add_step(
                    item[1],
                    name=item[0],
                    infer_name=infer_name
                )
            else:
                self.add_step(
                    item[1],
                    infer_name=infer_name,
                )

    def run(self, in_: _T = None) -> _RT:
        dto = in_

        for name, step in self._steps:
            self._logger.info(
                f"Step {name} - Starting"
            )
            try:
                if dto is None:
                    dto = step(self._logger)
                else:
                    dto = step(self._logger, dto)
            except Exception as err:
                self._logger.error(
                    f"Step {name} - Failed with error: {err}"
                )
                raise err
            else:
                self._logger.info(
                    f"Step {name} - Completed successfully"
                )

        return dto

    def __call__(self, in_: _T = None) -> _RT:
        return self.run(in_)
