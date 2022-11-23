from src.utils import string_


def test_as_camel_case() -> None:
    assert string_.as_camel_case("snake_case_to_camel") == "snakeCaseToCamel"
