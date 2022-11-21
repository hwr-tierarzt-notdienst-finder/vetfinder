from contextlib import contextmanager, AbstractContextManager
import os
from typing import Callable

import pytest

from src import config
from src import env


@pytest.fixture
def override_env_context() -> Callable[[env.Context], AbstractContextManager[env.Context]]:
    @contextmanager
    def override(ctx: env.Context) -> env.Context:
        original_ctx = os.environ["ENV"]

        try:
            config.reset_cache()
            os.environ["ENV"] = ctx
            yield ctx

            config.reset_cache()
        finally:
            os.environ["ENV"] = original_ctx

    return override
