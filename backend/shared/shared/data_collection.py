import inspect
import itertools
from collections.abc import Iterable, Callable
from logging import Logger
from types import ModuleType
from typing import NoReturn, cast, Any

from .models import Vet, VetInDb
from .pipeline import Pipeline
from .human_readable import human_readable


_CollectStep = Callable[[Logger], Iterable[Vet]]
_NormalizeStep = Callable[[Logger, Iterable[Vet]], Iterable[Vet]]
_ValidateStep = Callable[[Logger, Iterable[Vet]], NoReturn | None]
_ReplaceStep = Callable[[Logger, Iterable[VetInDb], Iterable[Vet]], tuple[VetInDb, Vet]]
_Step = _CollectStep | _NormalizeStep | _ValidateStep
_PipelineStep = Callable[[Logger, Iterable[Vet]], Iterable[Vet]]


class PipelineFactory:
    _COLLECT_STEP_TYPE = "collect"
    _NORMALIZE_STEP_TYPE = "normalize"
    _VALIDATE_STEP_TYPE = "validate"
    _REPLACE_STEP_TYPE = "replace"
    _STEP_TYPES = [
        _COLLECT_STEP_TYPE,
        _NORMALIZE_STEP_TYPE,
        _VALIDATE_STEP_TYPE,
        _REPLACE_STEP_TYPE,
    ]

    _get_all_vets_from_db: Callable[[], Iterable[VetInDb]]
    _create_vets_in_db: Callable[[Iterable[Vet]], None]
    _replace_vets_in_db: Callable[[Iterable[VetInDb]], None]
    _create_logger: Callable[[str], Logger]
    _shared_pipeline_steps: list[tuple[str, _PipelineStep]]

    def __init__(
            self,
            *,
            get_all_vets_from_db: Callable[[], Iterable[VetInDb]],
            replace_vets_in_db: Callable[[Iterable[VetInDb]], None],
            shared_steps: Iterable[
                              _NormalizeStep
                              | _ValidateStep
                              | tuple[str, _NormalizeStep | _ValidateStep]
                              ] | None = None,
            infer_shared_step_names: bool = False,
            create_logger: Callable[[str], Logger] | None = None,
    ) -> None:
        self._get_all_vets_from_db = get_all_vets_from_db
        self._replace_vets_in_db = replace_vets_in_db
        self._create_logger = create_logger

        self._shared_pipeline_steps = [
            self._create_valid_pipeline_name_step_pair(
                item[1],
                name=item[0],
                infer_name=infer_shared_step_names,
            ) if type(item) is tuple
            else self._create_valid_pipeline_name_step_pair(
                item,
                infer_name=infer_shared_step_names
            )
            for item in (shared_steps or [])
        ]

    def create_from_module(
            self,
            module: ModuleType,
    ) -> Pipeline[Iterable[Vet], Iterable[Vet]]:
        names_and_steps: list[tuple[str, _PipelineStep]] = []

        def getmembers_sort_key(item: tuple[str, Any]) -> int:
            member = item[1]
            try:
                return inspect.getsourcelines(member)[1]
            except:
                return -1

        for _, member in sorted(inspect.getmembers(module), key=getmembers_sort_key):
            if callable(member):
                try:
                    name_and_step = self._create_valid_pipeline_name_step_pair(
                        member,
                        infer_name=True
                    )
                    names_and_steps.append(
                        name_and_step
                    )
                except ValueError:
                    pass

        step_names = [name for name, _ in names_and_steps]

        self._validate_steps_order(step_names)

        has_replace_step = any(
            step_name.startswith(self._REPLACE_STEP_TYPE)
            for step_name in step_names
        )

        if has_replace_step:
            names_and_steps = (
                    names_and_steps[:-1]
                    + self._shared_pipeline_steps
                    + [names_and_steps[-1]]
            )
        else:
            names_and_steps = names_and_steps + self._shared_pipeline_steps

        pipeline: Pipeline[Iterable[Vet], Iterable[Vet]] = Pipeline(
            self._create_logger(module.__name__.split(".")[-1]),
            names_and_steps
        )

        return pipeline

    def _validate_steps_order(
            self,
            step_names: Iterable[str]
    ) -> None | NoReturn:
        step_names = list(step_names)

        for i, step_name in enumerate(step_names):
            step_type = self._get_step_type_from_name(step_name)
            if i == 0 and step_type != self._COLLECT_STEP_TYPE:
                raise ValueError(
                    f"First step must be a {self._COLLECT_STEP_TYPE} step. "
                    f"Found {step_type} step"
                )
            if i < len(step_names) - 1 and step_type == self._REPLACE_STEP_TYPE:
                raise ValueError(
                    f"{self._REPLACE_STEP_TYPE} step must come last"
                )

    def _create_valid_pipeline_name_step_pair(
            self,
            step: _Step,
            *,
            name: str | None = None,
            infer_name: bool = False,
    ) -> tuple[str, _PipelineStep] | NoReturn:
        name = self._create_valid_step_name(
            step,
            name=name,
            infer_name=infer_name,
        )

        pipeline_step = self._create_pipeline_step(step, name)

        return name, pipeline_step

    def _create_valid_step_name(
            self,
            step: _Step,
            *,
            name: str | None,
            infer_name: bool = False,
    ) -> str | NoReturn:
        if name is None:
            if infer_name:
                name = self._infer_step_name_from_callable(step)
            else:
                raise ValueError(
                    f"Name for step '{step}' was not provided. "
                    "Set 'infer_name' to true to infer the name from the step callable"
                )

        return self._validate_step_name(name)

    def _infer_step_name_from_callable(
            self,
            step: _Step,
    ) -> str:
        callable_name = cast(str, step.__name__)

        for step_type in self._STEP_TYPES:
            if callable_name == step_type:
                return callable_name
            elif callable_name.startswith(f"{step_type}_"):
                name_end = callable_name.removeprefix(
                    f"{step_type}_"
                )
                return f"{step_type}:{name_end}"

        raise ValueError(
            f"Could not infer step name from callable name '{callable_name}'. "
            f"Callable name must be {human_readable(self._STEP_TYPES).quoted().ored().shorten_if_longer_than(len(self._STEP_TYPES))} "
            f"or start with {human_readable(f'{step_type}_' for step_type in self._STEP_TYPES).quoted().ored().shorten_if_longer_than(len(self._STEP_TYPES))}"
        )

    def _validate_step_name(self, name: str) -> str | NoReturn:
        for step_type in self._STEP_TYPES:
            if name == step_type or name.startswith(f"{step_type}:"):
                return name

        raise ValueError(
            f"Invalid step name '{name}'. "
            f"Name must be {human_readable(self._STEP_TYPES).quoted().ored().shorten_if_longer_than(len(self._STEP_TYPES))} "
            f"or start with {human_readable(f'{step_type}:' for step_type in self._STEP_TYPES).quoted().ored().shorten_if_longer_than(len(self._STEP_TYPES))}"
        )

    def _create_pipeline_step(self, step: _Step, name: str) -> _PipelineStep:
        step_type = self._get_step_type_from_name(name)

        if step_type == self._COLLECT_STEP_TYPE:

            def pipeline_step(
                    logger: Logger,
                    already_collected_vets: Iterable[Vet]
            ) -> Iterable[Vet]:
                newly_collected_vets = step(logger, already_collected_vets)

                return itertools.chain(
                    already_collected_vets,
                    newly_collected_vets
                )

            return pipeline_step
        elif step_type == self._NORMALIZE_STEP_TYPE:
            return step
        elif step_type == self._VALIDATE_STEP_TYPE:

            def pipeline_step(
                    logger: Logger,
                    vets: Iterable[Vet]
            ) -> Iterable[Vet]:
                # Raises an error if validation fails
                step(logger, vets)

                return vets

            return pipeline_step
        elif step_type == self._REPLACE_STEP_TYPE:

            def pipeline_step(
                    logger: Logger,
                    collected_vets: Iterable[Vet],
            ) -> Iterable[Vet]:
                all_vets_in_db = self._get_all_vets_from_db()

                old_vets, new_vets = step(logger, all_vets_in_db, collected_vets)

                if len(list(old_vets)) != len(list(new_vets)):
                    raise ValueError(
                        f"Replace step must return the same amount of old vets as new"
                    )

                self._replace_vets_in_db(
                    [
                        VetInDb(
                            id=old_vet.id,
                            **new_vet
                        )
                        for old_vet, new_vet in zip(old_vets, new_vets)
                    ]
                )

                return new_vets

            return pipeline_step

        else:
            raise ValueError(
                f"Unexpected type '{step_type}' of step '{step}'"
            )

    def _get_step_type_from_name(self, name: str) -> str:
        return name.split(":")[0]
