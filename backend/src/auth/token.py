import json
from typing import NoReturn

import bcrypt

from constants import VET_COLLECTIONS
import db
from models import Secret
import paths
from shared.utils import cache
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
    overwrite_secrets_from_token_hashes_file()

    expected_token_ids = _collect_system_token_ids()
    for id_ in expected_token_ids:
        if not db.secrets.find({"secret_id": id_}):
            raise RuntimeError(
                f"No secret with id='{id_}'. "
                "Please add it using the token admin"
            )


def overwrite_secrets_from_token_hashes_file() -> None:
    json_hashes: list[dict[str, str]]
    with open(paths.find_secrets() / "token_hashes.json", "r") as f:
        json_hashes = json.load(f)

    db.secrets.delete_all()
    for entry in json_hashes:
        db.secrets.insert(
            Secret(secret_id=f"{entry['type']}.{entry['id']}", hash_=entry['value'])
        )


@cache.return_singleton(populate_cache_on="prepopulate_called")
def get_vets_collection_token_ids() -> set[str]:
    return set(_get_token_ids_to_vets_collection().keys())


def get_vets_collection_by_token_id(id_: str) -> str:
    return _get_token_ids_to_vets_collection()[id_]


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


@cache.return_singleton(populate_cache_on="prepopulate_called")
def _get_token_ids_to_vets_collection() -> dict[str, str]:
    return {
        f"vet_collection.{collection}": collection
        for collection in VET_COLLECTIONS
    }


def _collect_system_token_ids() -> set[str]:
    return get_vets_collection_token_ids()


cache.prepopulate()
