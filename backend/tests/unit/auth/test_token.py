import pytest

from pathlib import Path

from src.auth import token
from src.utils import file_system


def test_generate_and_validate() -> None:
    with file_system.temp_dir(
            Path(__file__).resolve().parent / "temp_dir",
            [
                {
                    "type": "file",
                    "name": ".gitignore",
                    "contents": [
                        "token_hashes.secret.txt",
                        "token_hashes.secret.txt.back",
                    ]
                },
            ],
    ) as dir_path:
        id1 = "id1"
        id2 = "test_id.num2"

        token1 = token.generate(id1, dir_path=dir_path)
        token2 = token.generate(id2, dir_path=dir_path)

        assert token.is_valid(id1, "") is False
        assert token.is_valid(id2, "") is False
        assert token.is_valid(id1, "pref" + token1) is False
        assert token.is_valid(id1, token1 + "suff") is False
        assert token.is_valid(id2, "pref" + token2) is False
        assert token.is_valid(id2, token2 + "suff") is False
        with pytest.raises(token.Error):
            token.validate(id1, "")
        assert token.is_valid(id1, token1)
        assert token.is_valid(id2, token2)
