from functools import lru_cache
from typing import Any

import pymongo
from pymongo import MongoClient
from pymongo.database import Database, Mapping, Collection
from pymongo.results import InsertOneResult

from constants import VET_COLLECTIONS
from utils import cache
from models import Vet, VetInDb, Location
from normalization import normalize_vet
import config


def create_vet(collection: str, vet: Vet) -> InsertOneResult:
    vet = normalize_vet(vet)

    vets = get_vets_collection(collection)
    result = vets.insert_one(vet.dict())

    return result


def get_vets(collection: str) -> list[VetInDb]:
    vets = get_vets_collection(collection)

    return [
        VetInDb(
            id=str(vet_db_obj["_id"]),
            **vet_db_obj
        )
        for vet_db_obj in vets.find({})
    ]


@lru_cache(maxsize=10)
def get_vets_collection(collection: str) -> Collection[Mapping[str, Any]]:
    if collection not in VET_COLLECTIONS:
        raise ValueError(f"No vet collection '{collection}'")

    db = get_db()
    return db[f"vets_{collection}"]


def overwrite_normalized_locations_cache(
        cache: dict[str, Location]
) -> list[InsertOneResult]:
    collection = get_normalized_locations_cache_collection()
    collection.drop()

    return [
        create_normalized_locations_cache_entry(
            key,
            location
        )
        for key, location in cache.items()
    ]


def create_normalized_locations_cache_entry(
        key: str,
        location: Location,
) -> InsertOneResult:
    collection = get_normalized_locations_cache_collection()
    result = collection.insert_one({
        "key": key,
        "location": location,
    })

    return result


@cache.return_singleton(populate_cache_on="prepopulate_called")
def get_db() -> Database[Mapping[str, Any]]:
    client = create_mongo_client()

    return client["db"]


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


cache.prepopulate()
