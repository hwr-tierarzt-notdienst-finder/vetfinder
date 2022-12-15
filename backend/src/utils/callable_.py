from collections.abc import Iterable
from typing import ParamSpec, TypeVar, Callable, NoReturn, Any

_T = TypeVar("_T")
_P = ParamSpec("_P")


def aggregated(
        *callables: Iterable[Callable[_P, _T]] | Callable[_P, _T] | None,
        allow_none: bool = False,
) -> Callable[_P, list[_T]]:
    """Creates an aggregate callable from multiple callables."""

    callables_ = _normalize_callable_args(*callables, allow_none=allow_none)

    def func(*args: _P.args, **kwargs: _P.kwargs) -> list[_T]:
        return [
            callable_(*args, **kwargs)
            for callable_ in callables_
        ]

    return func


def chained_transforms(
        *callables: Iterable[Callable[[_T], _T]] | Callable[[_T], _T] | None,
        allow_none: bool = False,
) -> Callable[[_T], _T]:
    """Creates a large transformation from a sequence of transformations."""

    callables_ = _normalize_callable_args(*callables, allow_none=allow_none)

    def func(in_: _T) -> _T:
        dto = in_
        for callable_ in callables_:
            dto = callable_(dto)

        return dto

    return func


def _normalize_callable_args(
        *callables: Iterable[Callable[_P, _T]] | Callable[_P, _T] | None,
        allow_none: bool = False,
) -> list[Callable[_P, _T]]:
    callables_: list[Callable[_P, _T]] = []

    none_not_allowed_err = ValueError(
        "None is not allowed in callable aggregate. "
        "Set 'allow_none' to true if this is not the desired behaviour"
    )

    def create_not_a_callable_err(item_: Any) -> NoReturn:
        return ValueError(f"Callable aggregate item '{item_}' is not callable.")

    for item in callables:
        if item is None:
            if not allow_none:
                raise none_not_allowed_err
        elif isinstance(item, Iterable):
            for nested_item in item:
                if nested_item is None:
                    if not allow_none:
                        raise none_not_allowed_err
                elif isinstance(item, Callable):
                    callables_.append(nested_item)
                else:
                    raise create_not_a_callable_err(nested_item)
        else:
            raise create_not_a_callable_err(item)

    return callables_
