from typing import Any

import pymongo
from pymongo import MongoClient
from pymongo.database import Database, Mapping, Collection
from pymongo.results import InsertOneResult

from shared import cache
from shared.models import Vet, VetInDb, Location
from .normalization import normalize_vet
from . import config


def create_vet(vet: Vet) -> InsertOneResult:
    vet = normalize_vet(vet)

    vets = get_vets_collection()
    result = vets.insert_one(vet.dict())

    return result


def get_vets() -> list[VetInDb]:
    vets = get_vets_collection()

    return [
        VetInDb(
            id=str(vet_db_obj["_id"]),
            **vet_db_obj
        )
        for vet_db_obj in vets.find({})
    ]


@cache.return_singleton(populate_cache_on="prepopulate_called")
def get_vets_collection() -> Collection[Mapping[str, Any]]:
    db = get_db()
    return db["vets"]


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


def get_normalized_locations_cache() -> dict[str, Location]:
    collection = get_normalized_locations_cache_collection()

    return {
        dct["key"]: Location(**dct["location"])
        for dct in collection.find({})
    }


@cache.return_singleton(populate_cache_on="prepopulate_called")
def get_normalized_locations_cache_collection() -> Collection[Mapping[str, str]]:
    db = get_db()
    return db["normalized_location_cache"]


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
