from src.config import get_config


class TestGetConfig:

    def test_can_get(self) -> None:
        get_config()

    def test_can_get_with_cached(self) -> None:
        get_config()
        get_config()
