from typing import Any

import pymongo
from pymongo import MongoClient
from pymongo.database import Database, Mapping, Collection
from pymongo.results import InsertOneResult

from models import Vet, Location, VetGet
from .normalization import normalize_vet
from . import config


def create_vet(vet: Vet) -> InsertOneResult:
    vet = normalize_vet(vet)

    vets = get_vets_collection()
    result = vets.insert_one(vet.dict())

    return result


def get_vets() -> list[VetGet]:
    vets = get_vets_collection()

    return [
        VetGet(
            id=str(vet_db_obj["_id"]),
            **vet_db_obj
        )
        for vet_db_obj in vets.find({})
    ]


_vets_collection = None
def get_vets_collection() -> Collection[Mapping[str, Any]]:
    global _vets_collection

    if _vets_collection is None:
        db = get_db()
        _vets_collection = db["vets"]

    return _vets_collection


_db: Database[Mapping[str, Any]] | None = None
def get_db() -> Database[Mapping[str, Any]]:
    global _db

    if _db is None:
        client = create_mongo_client()

        _db = client["db"]

    return _db


def create_mongo_client() -> MongoClient:
    connection_str = get_connection_string()

    with pymongo.timeout(config.get().db.connection_ping_timeout):
        # Test connection to client
        client = MongoClient(connection_str)
        client.admin.command("ping")

    return client


def get_connection_string() -> str:
    db_config = config.get().db

    return f"mongodb://{db_config.root_username}:{db_config.root_password}@127.0.0.1:{db_config.port}"
