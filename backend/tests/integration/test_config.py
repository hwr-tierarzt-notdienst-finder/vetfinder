import pytest

import config


class TestGetConfig:

    def test_can_get_in_prod_env_context(self, override_env_context) -> None:
        with override_env_context("prod"):
            # Get twice to test caching
            conf1 = config.get()
            conf2 = config.get()

            assert conf1 == conf2

    def test_can_get_in_dev_env_context(self, override_env_context) -> None:
        with override_env_context("dev"):
            # Get twice to test caching
            conf1 = config.get()
            conf2 = config.get()

            assert conf1 == conf2

    def test_can_get_in_test_env_context(self, override_env_context) -> None:
        # 'test' environment context should be automatically inferred
        # because this is running as a test
        conf1 = config.get()

        with override_env_context("test"):
            conf2 = config.get()

        assert conf1 == conf2


