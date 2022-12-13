from contextlib import contextmanager, AbstractContextManager
import os
from typing import Callable

from fastapi.testclient import TestClient
import pytest

import api
import config
import env


def pytest_addoption(parser):
    parser.addoption(
        "--run-prod-only", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "prod_only: mark test as only being able to run in production environment"
    )
    config.addinivalue_line(
        "markers", "non_prod: mark test as only being able to run in non-production environment"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-prod-only"):
        skip_non_prod = pytest.mark.skip(reason="need to remove --run-prod-only option to run")
        for item in items:
            if "non_prod" in item.keywords:
                item.add_marker(skip_non_prod)
    else:
        skip_prod_only = pytest.mark.skip(reason="need --run-prod-only option to run")
        for item in items:
            if "prod_only" in item.keywords:
                item.add_marker(skip_prod_only)


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


@pytest.fixture(scope="module")
def fastapi_client() -> TestClient:
    return TestClient(api.api)
