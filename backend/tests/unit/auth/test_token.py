import pytest

from pathlib import Path

from auth import token
from utils import file_system


def test_generate_and_authenticate() -> None:
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

        token1 = token.generate(id1, hashes_file_dir_path=dir_path)
        token2 = token.generate(id2, hashes_file_dir_path=dir_path)

        assert token.is_authentic(id1, "", hashes_file_dir_path=dir_path) is False
        assert token.is_authentic(id2, "", hashes_file_dir_path=dir_path) is False
        assert token.is_authentic(id1, "pref" + token1, hashes_file_dir_path=dir_path) is False
        assert token.is_authentic(id1, token1 + "suff", hashes_file_dir_path=dir_path) is False
        assert token.is_authentic(id2, "pref" + token2, hashes_file_dir_path=dir_path) is False
        assert token.is_authentic(id2, token2 + "suff", hashes_file_dir_path=dir_path) is False
        with pytest.raises(token.Error):
            token.authenticate(id1, "")
        assert token.is_authentic(id1, token1)
        assert token.is_authentic(id2, token2)
