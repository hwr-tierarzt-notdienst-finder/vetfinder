import os
import secrets
import string
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path
from typing import NoReturn

import bcrypt

from constants import VET_COLLECTIONS
import config
import env
from utils.human_readable import human_readable
from utils import file_system, path, validate, cache
from ._errors import Error as AuthError


# Entropy: E = log_2((26 + 10)^48) ~= 248 -> Very strong
_TOKEN_LENGTH = 48
_FILE_BACKUP_SUFFIX = ".back"
_FILE_KEY_VALUE_DELIMITER = ":"
_TOKEN_HASHES_FILE_NAME = "token_hashes.secret.txt"


_hashes_cache: dict[str, str] | None = None


class Error(AuthError):
    pass


class ValidationError(Error):
    pass


class KeyError_(Error, KeyError):
    pass


def ensure_system_has_tokens_and_token_hashes_saved() -> None:
    tokens_file_path = config.get().auth.tokens_file_path
    expected_token_ids = _collect_system_token_ids()

    _ensure_complete_token_file(
        file_path=tokens_file_path,
        expected_ids=expected_token_ids,
        ensure_ignored_by_git=(
                env.get_context() == "prod"
                or env.get_context() not in {"dev", "test"}
        )
    )

    _save_hashes_from_tokens_file(tokens_file_path)


@cache.return_singleton(populate_cache_on="prepopulate_called")
def get_vets_collection_token_ids() -> set[str]:
    return set(_get_token_ids_to_vets_collection().keys())


def get_vets_collection_by_token_id(id_: str) -> str:
    return _get_token_ids_to_vets_collection()[id_]


def generate(
        id_: str,
        *,
        hashes_file_dir_path: Path | None = None,
) -> str:
    hashes_file_dir_path = _normalize_hashes_file_dir_path(hashes_file_dir_path)

    token = _generate_token()

    hash_ = _generate_token_hash(token)

    _update_token_hashes(
        hashes_file_dir_path,
        {id_: hash_}
    )

    return token


def authenticate(
        id_: str,
        token: str,
        *,
        hashes_file_dir_path: Path | None = None,
) -> tuple[str, str] | NoReturn:
    hashes_file_dir_path = _normalize_hashes_file_dir_path(hashes_file_dir_path)

    if not is_authentic(id_, token, hashes_file_dir_path=hashes_file_dir_path):
        raise ValidationError(
            f"Token with id '{id_}' did not match hash"
        )

    return id_, token


def is_authentic(
        id_: str,
        token: str,
        *,
        hashes_file_dir_path: Path | None = None,
) -> bool:
    hashes_file_dir_path = _normalize_hashes_file_dir_path(hashes_file_dir_path)

    token_hashes = _get_token_hashes(hashes_file_dir_path)

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

    if _FILE_KEY_VALUE_DELIMITER in id_:
        raise ValueError(
            f"Token ID cannot contain key/value delimiter character '{_FILE_KEY_VALUE_DELIMITER}'. "
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


def validate_token(token: str) -> str:
    if len(token) != _TOKEN_LENGTH:
        raise ValueError(
            f"Token must be {_TOKEN_LENGTH} characters long"
        )

    if not token.isalnum():
        raise ValueError("Token must be alpha-numeric")

    if not token.islower():
        raise ValueError("Token must be lowercase")

    return token


@cache.return_singleton(populate_cache_on="prepopulate_called")
def _get_token_ids_to_vets_collection() -> dict[str, str]:
    return {
        f"vets.{collection}": collection
        for collection in VET_COLLECTIONS
    }


def _collect_system_token_ids() -> set[str]:
    return get_vets_collection_token_ids()


def _ensure_complete_token_file(
        file_path: Path,
        expected_ids: Iterable[str],
        *,
        ensure_ignored_by_git: bool = True,
) -> Path:
    file_path = path.from_(file_path)
    backup_file_path = file_path.parent / f"{file_path.name}{_FILE_BACKUP_SUFFIX}"

    if ensure_ignored_by_git:
        file_system.ensure_secrets_file_is_ignored_by_git(file_path)
        file_system.ensure_secrets_file_is_ignored_by_git(backup_file_path)

    tokens: dict[str, str] = {}

    if file_path.exists():
        with file_system.open_transactional(file_path, "r") as f:
            for line in f.readlines():
                if line.strip() == "":
                    continue

                id_, token = line.strip().split(_FILE_KEY_VALUE_DELIMITER)
                tokens[validate_id(id_)] = validate_token(token)

    with file_system.open_transactional(file_path, "w+") as f:
        for new_id in sorted(set(expected_ids) - tokens.keys()):
            tokens[validate_id(new_id)] = _generate_token()

        new_file_contents = os.linesep.join(
            f"{id_}{_FILE_KEY_VALUE_DELIMITER}{token}"
            for id_, token in tokens.items()
        )

        f.write(new_file_contents)

    return file_path


def _save_hashes_from_tokens_file(
        file_path: Path,
        *,
        hashes_file_dir_path: Path | None = None,
) -> dict[str, str]:
    hashes_file_dir_path = _normalize_hashes_file_dir_path(hashes_file_dir_path)

    file_path = validate.path_is_file(file_path)

    token_hashes_from_file: dict[str, str] = {}

    with open(file_path) as f:
        for line in f.readlines():
            if line.strip() == "":
                continue

            id_, token = line.strip().split(_FILE_KEY_VALUE_DELIMITER)

            token_hashes_from_file[validate_id(id_)] = _generate_token_hash(token)

    return _update_token_hashes(
        hashes_file_dir_path,
        token_hashes_from_file,
    )


def _normalize_hashes_file_dir_path(path: Path | None) -> Path:
    if path is None:
        return Path(__file__).resolve().parent

    return validate.path_is_dir(path)


def _generate_token() -> str:
    char_set = string.ascii_lowercase + string.digits

    return "".join(char_set[secrets.randbelow(len(char_set))] for _ in range(_TOKEN_LENGTH))


def _generate_token_hash(token: str) -> str:
    token = validate_token(token)

    return bcrypt.hashpw(token.encode("utf8"), bcrypt.gensalt()).decode("utf8")


def _get_token_hashes(hashes_file_dir_path: Path) -> dict[str, str]:
    global _hashes_cache

    if _hashes_cache is not None:
        return _hashes_cache

    path_ = _get_tokens_hashes_file_path(hashes_file_dir_path)

    token_hashes: dict[str, str] = {}

    with open(path_, "r") as f:
        for line in f.readlines():
            if line.strip() == "":
                continue

            id_, hash_ = line.strip().split(_FILE_KEY_VALUE_DELIMITER)

            token_hashes[id_] = hash_

    _hashes_cache = token_hashes

    return token_hashes


def _invalidate_cache() -> None:
    global _hashes_cache

    _hashes_cache = None


def _update_token_hashes(
        hashes_file_dir_path: Path,
        updated_token_hashes: dict[str, str]
) -> dict[str, str]:
    current_token_hashes = _get_token_hashes(hashes_file_dir_path)

    _overwrite_token_hashes(
        hashes_file_dir_path,
        current_token_hashes | updated_token_hashes
    )

    return updated_token_hashes


def _overwrite_token_hashes(
        hashes_file_dir_path: Path,
        new_token_hashes: dict[str, str]
) -> dict[str, str]:
    tokens_str = os.linesep.join(
        f"{id_}{_FILE_KEY_VALUE_DELIMITER}{token}"
        for id_, token in new_token_hashes.items()
    )

    file_path = _get_tokens_hashes_file_path(hashes_file_dir_path)

    file_system.ensure_secrets_file_is_ignored_by_git(
        hashes_file_dir_path / f"{_TOKEN_HASHES_FILE_NAME}{_FILE_BACKUP_SUFFIX}"
    )

    try:
        with file_system.open_transactional(
                file_path,
                "w",
                backup_file_suffix=_FILE_BACKUP_SUFFIX,
        ) as f:
            f.write(tokens_str)

            _invalidate_cache()
    except IOError as err:
        raise RuntimeError(
            f"Could not write token hashes to '{file_path}' with error: {repr(err)}"
        ) from err

    return new_token_hashes


@lru_cache(maxsize=1)
def _get_tokens_hashes_file_path(hashes_file_dir_path: Path) -> Path:
    return _get_secrets_file_path_in_current_dir_or_create_if_does_not_exist(
        hashes_file_dir_path,
        _TOKEN_HASHES_FILE_NAME,
    )


@lru_cache(maxsize=1)
def _get_tokens_hashes_backup_file_path(hashes_file_dir_path: Path) -> Path:
    return _get_secrets_file_path_in_current_dir_or_create_if_does_not_exist(
        hashes_file_dir_path,
        f"{_TOKEN_HASHES_FILE_NAME}{_FILE_BACKUP_SUFFIX}"
    )


def _get_secrets_file_path_in_current_dir_or_create_if_does_not_exist(
        hashes_file_dir_path: Path,
        file_name: str
) -> Path:
    path_ = hashes_file_dir_path / file_name

    file_system.ensure_secrets_file_is_ignored_by_git(path_)

    if not path_.exists():
        path_.touch()

    return path_


cache.prepopulate()
