import os
import secrets
import shutil
import string
from functools import lru_cache
from pathlib import Path
from typing import NoReturn

import bcrypt

from ..utils.human_readable import human_readable
from ._errors import Error as AuthError


_TOKEN_LENGTH = 32
_TOKEN_HASHES_FILE_NAME = "token_hashes.secret.txt"
_TOKEN_HASHES_FILE_BACKUP_SUFFIX = ".back"
_TOKEN_HASHES_FILE_KEY_VALUE_DELIMITER = ":"


_hashes_cache: dict[str, str] | None = None


class Error(AuthError):
    pass


class ValidationError(Error):
    pass


class KeyError_(Error, KeyError):
    pass


def generate(
        id_: str,
        *,
        dir_path: Path | None = None,
) -> str:
    if dir_path is None:
        dir_path = Path(__file__).resolve().parent

    token = _generate_token()

    token_hashes = _get_token_hashes(dir_path)

    hash_ = bcrypt.hashpw(token.encode("utf8"), bcrypt.gensalt()).decode("utf8")

    new_token_hashes = _overwrite_token_hashes(
        dir_path,
        {id_: hash_, **token_hashes}
    )

    assert len(new_token_hashes[id_]) > 0

    return token


def validate(
        id_: str,
        token: str
) -> tuple[str, str] | NoReturn:
    if not is_valid(id_, token):
        raise ValidationError(
            f"Token with id '{id_}' did not match hash"
        )

    return id_, token


def is_valid(
        id_: str,
        token: str,
        *,
        dir_path: Path | None = None,
) -> bool:
    if dir_path is None:
        dir_path = Path(__file__).resolve().parent

    token_hashes = _get_token_hashes(dir_path)

    try:
        hash_ = token_hashes[id_]
    except KeyError as err:
        raise KeyError_(
            f"No hash for token with id '{id_}'"
        ) from err

    return bcrypt.checkpw(token.encode("utf8"), hash_.encode("utf8"))


def validate_id(id_: str) -> str:
    for white_space_char in string.whitespace:
        if white_space_char in id_:
            raise ValueError(
                "Token ID cannot contain whitespace characters. "
                f"Found {repr(white_space_char)} in {repr(id_)}"
            )

    if _TOKEN_HASHES_FILE_KEY_VALUE_DELIMITER in id_:
        raise ValueError(
            f"Token ID cannot contain key/value delimiter character '{_TOKEN_HASHES_FILE_KEY_VALUE_DELIMITER}'. "
            f"Found in name '{id_}'"
        )

    if not id_.replace("_", "").replace(".", "").isalnum():
        invalid_chars = [
            char
            for char in id_
            if not (char.isalnum() or char in {"_", "."})
        ]

        raise ValueError(
            f"Token name must only contain alpha-numeric characters, '_' or '.'. "
            f"Found {human_readable(invalid_chars).quoted().anded()} in '{id_}'"
        )

    return id_


def _generate_token() -> str:
    return secrets.token_hex(_TOKEN_LENGTH)


def _get_token_hashes(dir_path: Path) -> dict[str, str]:
    global _hashes_cache

    if _hashes_cache is not None:
        return _hashes_cache

    path = _get_tokens_hashes_file_path(dir_path)

    token_hashes: dict[str, str] = {}

    with open(path, "r") as f:
        for line in f.readlines():
            id_, token = line.strip().split(_TOKEN_HASHES_FILE_KEY_VALUE_DELIMITER)

            token_hashes[id_] = token

    _hashes_cache = token_hashes

    return token_hashes


def _invalidate_cache() -> None:
    global _hashes_cache

    _hashes_cache = None


def _overwrite_token_hashes(
        dir_path: Path,
        new_token_hashes: dict[str, str]
) -> dict[str, str]:
    tokens_str = os.linesep.join(
        f"{id_}{_TOKEN_HASHES_FILE_KEY_VALUE_DELIMITER}{token}"
        for id_, token in new_token_hashes.items()
    )

    file_path = _get_tokens_hashes_file_path(dir_path)
    backup_file_path = _get_tokens_hashes_backup_file_path(dir_path)

    # Transactional write
    shutil.copyfile(file_path, backup_file_path)

    try:
        with open(file_path, "w") as f:
            f.write(tokens_str)

        _invalidate_cache()

        new_token_hashes = _get_token_hashes(dir_path)
    except Exception as err:
        # Rollback
        shutil.copyfile(backup_file_path, file_path)

        raise RuntimeError(
            f"Could not write token hashes to '{file_path}' with error: {repr(err)}"
        ) from err
    finally:
        backup_file_path.unlink()

    return new_token_hashes


@lru_cache(maxsize=1)
def _get_tokens_hashes_file_path(dir_path: Path) -> Path:
    return _get_secrets_file_path_in_current_dir_or_create_if_does_not_exist(
        dir_path,
        _TOKEN_HASHES_FILE_NAME,
    )


@lru_cache(maxsize=1)
def _get_tokens_hashes_backup_file_path(dir_path: Path) -> Path:
    return _get_secrets_file_path_in_current_dir_or_create_if_does_not_exist(
        dir_path,
        f"{_TOKEN_HASHES_FILE_NAME}{_TOKEN_HASHES_FILE_BACKUP_SUFFIX}"
    )


def _get_secrets_file_path_in_current_dir_or_create_if_does_not_exist(
        dir_path: Path,
        file_name: str
) -> Path:
    path = dir_path / file_name

    file_is_ignored_by_git = False
    gitignore_file_path = dir_path / ".gitignore"
    with open(gitignore_file_path) as f:
        for line in f.readlines():
            if line.strip() == file_name:
                file_is_ignored_by_git = True
                break

    if not file_is_ignored_by_git:
        raise RuntimeError(
            f"Secrets file name '{file_name}' must be in gitignore '{gitignore_file_path}'!"
        )

    if not path.exists():
        path.touch()

    return path
