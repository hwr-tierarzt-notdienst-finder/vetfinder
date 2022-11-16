import secrets
import string
from typing import NoReturn

import bcrypt

from constants import VET_COLLECTIONS
import db
from models import Secret
from utils.human_readable import human_readable
from utils import cache
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
    expected_token_ids = _collect_system_token_ids()

    for id_ in expected_token_ids:
        if not db.secrets.find({"secret_id": id_}):
            generate(id_)


@cache.return_singleton(populate_cache_on="prepopulate_called")
def get_vets_collection_token_ids() -> set[str]:
    return set(_get_token_ids_to_vets_collection().keys())


def get_vets_collection_by_token_id(id_: str) -> str:
    return _get_token_ids_to_vets_collection()[id_]


def generate(id_: str) -> str:
    token = _generate_token()

    with open("tokens.txt", "a") as f:
        f.writelines([f"id={id_} token={token}"])

    hash_ = _generate_token_hash(token)

    db.secrets.insert(Secret(secret_id=id_, hash_=hash_))

    return token


def authenticate(id_: str, token: str) -> tuple[str, str] | NoReturn:
    if not is_authentic(id_, token):
        raise ValidationError(
            f"Token with id '{id_}' did not match hash"
        )

    return id_, token


def is_authentic(id_: str, token: str) -> bool:
    # all_ = db.secrets.all()
    # breakpoint()

    try:
        secret = db.secrets.exactly_one({"secret_id": id_})
    except Exception as err:
        raise KeyError_(
            f"No hash for token with id '{id_}'"
        ) from err

    return bcrypt.checkpw(token.encode("utf8"), secret.hash_.encode("utf8"))


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


def _generate_token() -> str:
    char_set = string.ascii_lowercase + string.digits

    return "".join(char_set[secrets.randbelow(len(char_set))] for _ in range(_TOKEN_LENGTH))


def _generate_token_hash(token: str) -> str:
    token = validate_token(token)

    return bcrypt.hashpw(token.encode("utf8"), bcrypt.gensalt()).decode("utf8")


cache.prepopulate()
