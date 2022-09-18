import os
import secrets
import shutil
import string
from functools import lru_cache
from pathlib import Path

from ..utils.human_readable import human_readable


_TOKEN_LENGTH = 32
_TOKENS_FILE_NAME = "tokens.secret.txt"
_TOKENS_FILE_BACKUP_SUFFIX = ".back"
_TOKENS_FILE_KEY_VALUE_DELIMITER = ":"


_cache: dict[str, str] | None = None


def get(id_: str, *, dir_path: Path | None = None) -> str:
    """
    Returns a securely generated random token, specific to a given ID.

    If the ID has not been encountered before, a new token is generated.
    If a token already exists with the given ID, that token will be returned.

    TODO:
        In future tokens should expire, be revoked and regenerated
        for extra security.

    Current implementation details:
        Tokens are stored in a text file. If this file does not
        exist, it will be created. The first time a token is request,
        all tokens are read from the file and cached in memory.
        Subsequent requests will use the cache unless it has been invalidated.
        When a token is request by an ID that is not stored, the file is
        overwritten, adding the new ID and the cache is invalidated.
        Before the file is overwritten, its contents is copied to a backup
        file. If the file is successfully overwritten, the backup file is
        deleted, otherwise the old contents of the file are restored from
        the backup file and the backup file is deleted.

        The full file names of file and backup file must be contained in
        this directory's .gitignore.
    """
    if dir_path is None:
        dir_path = Path(__file__).resolve().parent

    tokens = _get_tokens(dir_path)

    try:
        return tokens[id_]
    except KeyError:
        pass

    id_ = validate_id(id_)
    token = _generate_token()

    new_tokens = _overwrite_tokens(dir_path, {id_: token, **tokens})

    return new_tokens[id_]


def validate_id(id_: str) -> str:
    for white_space_char in string.whitespace:
        if white_space_char in id_:
            raise ValueError(
                "Token ID cannot contain whitespace characters. "
                f"Found {repr(white_space_char)} in {repr(id_)}"
            )

    if _TOKENS_FILE_KEY_VALUE_DELIMITER in id_:
        raise ValueError(
            f"Token ID cannot contain key/value delimiter character '{_TOKENS_FILE_KEY_VALUE_DELIMITER}'. "
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


def _get_tokens(dir_path: Path) -> dict[str, str]:
    global _cache

    if _cache is not None:
        return _cache

    path = _get_tokens_file_path(dir_path)

    tokens: dict[str, str] = {}

    with open(path, "r") as f:
        for line in f.readlines():
            id_, token = line.strip().split(_TOKENS_FILE_KEY_VALUE_DELIMITER)

            tokens[id_] = token

    _cache = tokens

    return tokens


def _invalidate_cache() -> None:
    global _cache

    _cache = None


def _overwrite_tokens(
        dir_path: Path,
        new_tokens: dict[str, str]
) -> dict[str, str]:
    tokens_str = os.linesep.join(
        f"{id_}{_TOKENS_FILE_KEY_VALUE_DELIMITER}{token}"
        for id_, token in new_tokens.items()
    )

    file_path = _get_tokens_file_path(dir_path)
    backup_file_path = _get_tokens_backup_file_path(dir_path)

    # Transactional write
    shutil.copyfile(file_path, backup_file_path)

    try:
        with open(file_path, "w") as f:
            f.write(tokens_str)

        _invalidate_cache()

        new_tokens = _get_tokens(dir_path)
    except Exception as err:
        # Rollback
        shutil.copyfile(backup_file_path, file_path)

        raise RuntimeError(
            f"Could not write tokens to '{file_path}' with error: {repr(err)}"
        ) from err
    finally:
        backup_file_path.unlink()

    return new_tokens


@lru_cache(maxsize=1)
def _get_tokens_file_path(dir_path: Path) -> Path:
    return _get_secrets_file_path_in_current_dir_or_create_if_does_not_exist(
        dir_path,
        _TOKENS_FILE_NAME,
    )


@lru_cache(maxsize=1)
def _get_tokens_backup_file_path(dir_path: Path) -> Path:
    return _get_secrets_file_path_in_current_dir_or_create_if_does_not_exist(
        dir_path,
        f"{_TOKENS_FILE_NAME}{_TOKENS_FILE_BACKUP_SUFFIX}"
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
