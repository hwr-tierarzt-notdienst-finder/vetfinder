import os
from typing import Literal, cast

from .utils.human_readable import human_readable

Context = Literal["prod", "dev", "test"]


_ENV_VAR_NAME = "ENV"
_VALID_CONTEXTS: set[Context] = {"prod", "dev", "test"}


def get_context() -> Context:
    return _ensure_context(os.environ[_ENV_VAR_NAME])


def _ensure_context(context: str) -> Context:
    if context not in _VALID_CONTEXTS:
        raise ValueError(
            f"Invalid environment context ${_ENV_VAR_NAME}='{context}', "
            f"expected one of {human_readable(_VALID_CONTEXTS).items_quoted().ored()}"
        )

    return cast(Context, context)
