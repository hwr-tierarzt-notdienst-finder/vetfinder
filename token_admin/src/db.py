from __future__ import annotations

import dataclasses
import json
import secrets
import string
from contextlib import contextmanager
from datetime import datetime
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO, Literal
import bcrypt


# Entropy: E = log_2((26 + 10)^48) ~= 248 -> Very strong
_TOKEN_LENGTH = 48
_FILE_BACKUP_SUFFIX = ".back"
_DB_FILE = "../db/tokens.json"
_HASHES_FILE = "../db/hashes.json"
_EVENT_LOG_FILE = "../db/token_event_log.txt"
_EVENT_LOG_LINE_SEPERATOR = "|"


_Operation = Literal[
    "create",
    "replace",
    "change_type",
    "change_id",
    "delete",
]


@dataclass(frozen=True)
class _Event:
    datetime: datetime
    operation: _Operation
    token_type: str
    token_id: str
    value: str


@dataclass(frozen=True)
class _Token:
    type_: str
    id_: str
    value: str


class DB:
    vet_email: Repository
    _events: list[_Event]
    _tokens: list[_Token]

    def __init__(self):
        self._events = []
        self._tokens = []

        self._populate_events_from_file()
        self._populate_tokens_from_file()
        self._check_integrity()

        self.vet_email = Repository(self, "vet_email")
        self.vet_collection = Repository(self, "vet_collection")

    def find(self, token_type: str, token_id: str) -> _Token:
        for token in self._tokens:
            if token.type_ == token_type and token.id_ == token_id:
                return token

        raise TokenDoesNotExist(
            f"Could not find token with type='{token_type}' and id '{token_id}'"
        )

    def all(self, token_type: str | None = None) -> list[_Token]:
        if token_type is None:
            return self._tokens[:]

        return [token for token in self._tokens if token.type_ == token_type]

    def generate_token(self, token_type: str, token_id: str) -> str:
        value = self._generate_token_value()

        self.submit_event(
            _Event(
                datetime=datetime.now(),
                operation="create",
                token_type=token_type,
                token_id=token_id,
                value=value,
            )
        )

        return value

    def replace_token(self, token_type: str, token_id: str) -> str:
        value = self._generate_token_value()

        self.submit_event(
            _Event(
                datetime=datetime.now(),
                operation="replace",
                token_type=token_type,
                token_id=token_id,
                value=value,
            )
        )

        return value

    def change_token_type(self, old_token_type: str, new_token_type: str, token_id: str) -> None:
        self.submit_event(
            _Event(
                datetime=datetime.now(),
                operation="change_type",
                token_type=old_token_type,
                token_id=token_id,
                value=new_token_type,
            )
        )

    def change_token_id(self, token_type: str, old_token_id: str, new_token_id: str) -> None:
        self.submit_event(
            _Event(
                datetime=datetime.now(),
                operation="change_id",
                token_type=token_type,
                token_id=old_token_id,
                value=new_token_id,
            )
        )

    def delete_token(self, token_type: str, token_id: str) -> None:
        self.submit_event(
            _Event(
                datetime=datetime.now(),
                operation="delete",
                token_type=token_type,
                token_id=token_id,
                value="",
            )
        )

    def submit_event(self, event: _Event) -> None:
        _apply_event(self._tokens, event)

        self._events.append(event)

    def flush(self) -> None:
        self._check_integrity()
        self._write_events_to_file()
        self._write_tokens_to_file()
        self._generate_hashes_and_write_to_file()

    def _populate_events_from_file(self) -> None:
        lines: list[str]
        with _open_event_log_file("r") as f:
            lines = f.readlines()

        for line in lines:
            iso_datetime, operation, token_type, token_id, value = line.split(
                _EVENT_LOG_LINE_SEPERATOR,
                maxsplit=5,
            )
            self._events.append(
                _Event(
                    datetime=datetime.fromisoformat(iso_datetime.strip()),
                    operation=operation.strip(),
                    token_type=token_type.strip(),
                    token_id=token_id.strip(),
                    value=value.strip(),
                )
            )

    def _populate_tokens_from_file(self) -> None:
        json_tokens: list[dict[str, str]]
        with _open_db_file("r") as f:
            json_tokens = json.load(f)

        for json_token in json_tokens:
            type_ = json_token["type"]
            id_ = json_token["id"]
            value = json_token["value"]

            self._tokens.append(_Token(type_=type_, id_=id_, value=value))

    def _check_integrity(self) -> None:
        _ensure_tokens_are_created_from_events(self._tokens, self._events)

    def _write_events_to_file(self) -> None:
        lines = [
            _EVENT_LOG_LINE_SEPERATOR.join((
                event.datetime.isoformat(),
                event.operation,
                event.token_type,
                event.token_id,
                event.value,
            )) + "\n"
            for event in self._events
        ]

        with _open_event_log_file("w") as f:
            f.writelines(lines)

    def _write_tokens_to_file(self) -> None:
        json_tokens: list[dict[str, str]] = []
        for token in self._tokens:
            json_tokens.append({
                "type": token.type_,
                "id": token.id_,
                "value": token.value,
            })

        with _open_db_file("w") as f:
            json.dump(json_tokens, f, indent=4)

    def _generate_hashes_and_write_to_file(self) -> None:
        json_hashes: list[dict[str, str]] = []
        for token in self._tokens:
            json_hashes.append({
                "type": token.type_,
                "id": token.id_,
                "value": self._generate_token_hash(token.value),
            })

        with _open_hashes_file("w") as f:
            json.dump(json_hashes, f, indent=4)

    def _generate_token_value(self) -> str:
        char_set = string.ascii_lowercase + string.digits
        return self._validate_token_value(
            "".join(char_set[secrets.randbelow(len(char_set))] for _ in range(_TOKEN_LENGTH))
        )

    def _validate_token_value(self, token: str) -> str:
        if len(token) != _TOKEN_LENGTH:
            raise BadDatabaseIntegrity(
                f"Token must be {_TOKEN_LENGTH} characters long"
            )

        if not token.isalnum():
            raise BadDatabaseIntegrity("Token must be alpha-numeric")

        if not token.islower():
            raise BadDatabaseIntegrity("Token must be lowercase")

        return token

    def _generate_token_hash(self, token_value: str) -> str:
        token_value = self._validate_token_value(token_value)

        return bcrypt.hashpw(token_value.encode("utf8"), bcrypt.gensalt()).decode("utf8")


class Repository:
    _db: DB
    _token_type: str

    def __init__(self, db: DB, token_type: str) -> None:
        self._db = db
        self._token_type = token_type

    def find(self, token_id: str) -> _Token:
        return self._db.find(self._token_type, token_id)

    def all(self) -> list[_Token]:
        return self._db.all(self._token_type)

    def generate_token(self, token_id: str) -> str:
        return self._db.generate_token(self._token_type, token_id)

    def replace_token(self, token_id: str) -> str:
        return self._db.replace_token(self._token_type, token_id)

    def change_token_id(self, old_token_id: str, new_token_id: str) -> None:
        self._db.change_token_id(self._token_type, old_token_id, new_token_id)

    def delete_token(self, token_id: str) -> None:
        self._db.delete_token(self._token_type, token_id)


def _apply_event(tokens: list[_Token], event: _Event) -> None:

    def find_token(type_: str, id_: str) -> tuple[int, _Token] | None:
        for i, token in enumerate(tokens):
            if token.id_ == id_ and token.type_ == type_:
                return i, token

        return None

    if event.operation == "create":

        if find_token(event.token_type, event.token_id):
            raise TokenAlreadyExists(
                f"Cannot create token with type='{event.token_type}' and id='{event.token_id}'. "
                f"It already exists"
            )

        tokens.append(_Token(type_=event.token_type, id_=event.token_id, value=event.value))

    elif event.operation == "replace":

        if not (find_result := find_token(event.token_type, event.token_id)):
            raise TokenDoesNotExist(
                f"Cannot replace token with type='{event.token_type}' and id='{event.token_id}'. "
                f"It does not exist"
            )

        index, original_token = find_result

        tokens[index] = _Token(**(dataclasses.asdict(original_token) | {"value": event.value}))

    elif event.operation == "change_type":

        if not (find_result := find_token(event.token_type, event.token_id)):
            raise TokenDoesNotExist(
                f"Cannot change token type with original type='{event.token_type}' and id='{event.token_id}'. "
                f"It does not exist"
            )

        index, original_token = find_result

        tokens[index] = _Token(**(dataclasses.asdict(original_token) | {"type_": event.value}))

    elif event.operation == "change_id":

        if not (find_result := find_token(event.token_type, event.token_id)):
            raise TokenDoesNotExist(
                f"Cannot change token id with type='{event.token_type}' and original id='{event.token_id}'. "
                f"It does not exist"
            )

        index, original_token = find_result

        tokens[index] = _Token(**(dataclasses.asdict(original_token) | {"id_": event.value}))

    elif event.operation == "delete":

        if not (find_result := find_token(event.token_type, event.token_id)):
            raise TokenDoesNotExist(
                f"Cannot delete token with type='{event.token_type}' and original id='{event.token_id}'. "
                f"It does not exist"
            )

        index, _ = find_result

        del tokens[index]

    else:
        raise RuntimeError(f"Event with unexpected operation='{event.operation}'")


def _ensure_tokens_are_created_from_events(
        expected_tokens: list[_Token],
        events: list[_Event]
) -> None:
    actual_tokens = _create_tokens_from_events(events)

    error = BadDatabaseIntegrity(
        "The tokens created from the events do not match the existing tokens!"
    )

    if len(actual_tokens) != len(expected_tokens):
        raise error

    for expected_token, actual_token in zip(expected_tokens, actual_tokens):
        if expected_token != actual_token:
            raise error


def _create_tokens_from_events(events: list[_Event]) -> list[_Token]:
    tokens: list[_Token] = []

    for event in events:
        _apply_event(tokens, event)

    return tokens


class TokenAlreadyExists(Exception):
    pass


class TokenDoesNotExist(Exception):
    pass


class BadDatabaseIntegrity(RuntimeError):
    pass


@contextmanager
def _open_db_file(mode: Literal["r", "w", "a"]) -> TextIO:
    file_path = _current_dir() / _DB_FILE
    if not file_path.exists():
        with open(file_path, "w") as f:
            f.write("[]")

    with _open_backed_up_file(file_path, mode) as f:
        yield f


@contextmanager
def _open_hashes_file(mode: Literal["w"]) -> TextIO:
    file_path = _current_dir() / _HASHES_FILE
    if not file_path.exists():
        with open(file_path, "w") as f:
            f.write("[]")

    with _open_backed_up_file(file_path, mode) as f:
        yield f


@contextmanager
def _open_event_log_file(mode: Literal["r", "w", "a"]) -> TextIO:
    file_path = _current_dir() / _EVENT_LOG_FILE
    if not file_path.exists():
        file_path.touch()

    with _open_backed_up_file(file_path, mode) as f:
        yield f


def _current_dir() -> Path:
    return Path(__file__).resolve().parent


@contextmanager
def _open_backed_up_file(file_path: Path, mode: Literal["r", "w", "a"]) -> TextIO:
    backup_file_path = file_path.parent / f"{file_path.name}{_FILE_BACKUP_SUFFIX}"

    shutil.copyfile(file_path, backup_file_path)

    with open(file_path, mode) as f:
        yield f

    backup_file_path.unlink()
