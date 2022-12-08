from collections.abc import Callable
from functools import wraps
from typing import TypeVar, Protocol, overload, Literal, Any

from .human_readable import human_readable

_T = TypeVar("_T")


class _CallableWithInvalidateCacheKwargReturningSingleton(Protocol[_T]):

    def __call__(self, *, invalidate_cache: bool = False) -> _T: ...


_PrepopulateOnMode = Literal[
    "decorated",
    "prepopulate_called",
    "first_called",
]

_PREPOPULATE_ON_MODE_DECORATED: _PrepopulateOnMode = "decorated"
_PREPOPULATE_ON_MODE_PREPOPULATE_CALLED: _PrepopulateOnMode = "prepopulate_called"
_PREPOPULATE_ON_MODE_FIRST_CALLED: _PrepopulateOnMode = "first_called"
_VALID_PREPOPULATE_ON_MODES: set[_PrepopulateOnMode] = {
    _PREPOPULATE_ON_MODE_DECORATED,
    _PREPOPULATE_ON_MODE_PREPOPULATE_CALLED,
    _PREPOPULATE_ON_MODE_FIRST_CALLED,
}


_populate_cache_callbacks: list[Callable[[], Any]] = []


def prepopulate() -> None:
    for callback in _populate_cache_callbacks:
        callback()

    _populate_cache_callbacks.clear()


@overload
def return_singleton(
        func: Callable[[], _T]
) -> Callable[[], _T]: ...


@overload
def return_singleton(
        *,
        add_invalidate_cache_kwarg: Literal[True],
        should_invalidate_cache: Callable[[], bool] | None = None,
        populate_cache_on: _PrepopulateOnMode = "decorated",
) -> Callable[[], _CallableWithInvalidateCacheKwargReturningSingleton[_T]]: ...


@overload
def return_singleton(
        *,
        add_invalidate_cache_kwarg: bool = False,
        should_invalidate_cache: Callable[[], bool] | None = None,
        populate_cache_on: _PrepopulateOnMode = "decorated",
) -> Callable[[], Callable[[], _T]]: ...


def return_singleton(
        *args: Callable[[], _T],
        add_invalidate_cache_kwarg: bool = False,
        should_invalidate_cache: Callable[[], bool] | None = None,
        populate_cache_on: _PrepopulateOnMode = "decorated",
):
    """
    Decorator to cache the return value of a function without and arguments
    and a single return value.

    The return value should be unchanging (or the cache should be invalidated every time
    the return value changes).

    :param should_invalidate_cache:
        If this callback returns True, the cached singleton will be invalidated.
    :param add_invalidate_cache_kwarg:
        The decorated function now has the <code>invalidate_cache</code> keyword argument.
    :param populate_cache_on:
        Specifies when the singleton should be created and cached.
    """
    def decorator(
            func: Callable[[], _T]
    ) -> Callable[[], _T] | _CallableWithInvalidateCacheKwargReturningSingleton[_T]:
        singleton: _T | None = None

        if should_invalidate_cache is None:

            @wraps(func)
            def wrapper() -> _T:
                nonlocal singleton

                if singleton is None:
                    singleton = func()

                return singleton
        else:

            @wraps(func)
            def wrapper() -> _T:
                nonlocal singleton

                if should_invalidate_cache():
                    singleton = None

                if singleton is None:
                    singleton = func()

                return singleton

        if add_invalidate_cache_kwarg:
            original_wrapper = wrapper

            def wrapper_with_kwarg(*, invalidate_cache: bool = False) -> _T:
                nonlocal singleton

                if invalidate_cache:
                    singleton = None

                return original_wrapper()

            wrapper = wrapper_with_kwarg

        if populate_cache_on == _PREPOPULATE_ON_MODE_DECORATED:
            wrapper()
        elif populate_cache_on == _PREPOPULATE_ON_MODE_PREPOPULATE_CALLED:
            _populate_cache_callbacks.append(wrapper)
        elif populate_cache_on == _PREPOPULATE_ON_MODE_FIRST_CALLED:
            pass
        else:
            raise ValueError(
                "Argument 'populate_cache_on' must be one of "
                f"{human_readable(_VALID_PREPOPULATE_ON_MODES).quoted().ored()}"
            )

        return wrapper

    if len(args) == 0:
        return decorator
    elif len(args) == 1 and callable(arg := args[0]):
        return decorator(arg)

    raise ValueError(
        "No positional arguments should be passed to decorator"
    )
