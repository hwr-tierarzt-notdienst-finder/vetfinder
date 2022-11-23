from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, Protocol, TypeVar

_T = TypeVar("_T")
_P = ParamSpec("_P")


class _WithUsesUserGeneratedContentKwarg(Protocol[_P, _T]):

    def __call__(
            self,
            *args: _P.args,
            uses_user_generated_content: bool = True,
            **kwargs: _P.kwargs,
    ) -> _T: ...


def not_with_user_generated_content(
        func: Callable[_P, _T]
) -> _WithUsesUserGeneratedContentKwarg[_P, _T]:

    @wraps(func)
    def wrapper(
            *args: _P.args,
            uses_user_generated_content: bool = True,
            **kwargs: _P.kwargs,
    ) -> _T:
        if uses_user_generated_content:
            raise RuntimeError(
                f"It is unsafe for function '{func.__name__}' to "
                "use user generated content. "
                "Set kwarg 'uses_user_generated_content' to true if the function "
                "is not passed user generated content and does not use "
                "user generated content internally."
            )

        return func(*args, **kwargs)

    return wrapper
