from pathlib import Path

from src.auth import tokens
from src.utils import file_system


def test_get() -> None:
    with file_system.temp_dir(
            Path(__file__).resolve().parent / "temp_dir",
            [
                {
                    "type": "file",
                    "name": ".gitignore",
                    "contents": [
                        "tokens.secret.txt",
                        "tokens.secret.txt.back",
                    ]
                },
            ],
    ) as dir_path:
        id1 = "id1"
        id2 = "test_id.num2"

        id1_result1 = tokens.get(id1, dir_path=dir_path)
        id2_result1 = tokens.get(id2, dir_path=dir_path)
        id1_result2 = tokens.get(id1, dir_path=dir_path)
        id2_result2 = tokens.get(id2, dir_path=dir_path)

        assert id1_result1 == id1_result2
        assert id2_result1 == id2_result2
        assert (token1_len := len(id1_result1)) > 20
        assert (token2_len := len(id2_result1)) > 20
        assert token1_len == token2_len
