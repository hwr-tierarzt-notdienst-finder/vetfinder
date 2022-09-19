from functools import lru_cache
from typing import Any

import geopy.distance
import pymongo
from pymongo import MongoClient
from pymongo.database import Database, Mapping, Collection
from pymongo.results import InsertOneResult

from constants import VET_COLLECTIONS
from utils import cache
from models import Vet, VetInDb
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


def get_vets_in_ring(
        collection: str,
        c_lat: float,
        c_lon: float,
        r_inner: float,
        r_outer: float,
) -> list[VetInDb]:
    center = (c_lat, c_lon)

    vets = get_vets_collection(collection)

    result: list[VetInDb] = []

    for vet_db_obj in vets.find({}):
        dist = geopy.distance.distance(
            center,
            (vet_db_obj["location"]["lat"]["value"], vet_db_obj["location"]["lon"]["value"])
        ).km

        if r_inner <= dist <= r_outer:
            result.append(
                VetInDb(
                    id=str(vet_db_obj["_id"]),
                    **vet_db_obj
                )
            )

    return result


@lru_cache(maxsize=10)
def get_vets_collection(collection: str) -> Collection[Mapping[str, Any]]:
    if collection not in VET_COLLECTIONS:
        raise ValueError(f"No vet collection '{collection}'")

    db = get_db()
    return db[f"vets_{collection}"]


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
