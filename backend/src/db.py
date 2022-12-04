from __future__ import annotations

from typing import Any, Iterable

import geopy.distance
import pymongo
from pymongo import MongoClient
from pymongo.database import Collection, Database, Mapping

from constants import VET_VISIBILITIES, VET_VERIFICATION_STATUSES
from types_ import VetVisibility, VetVerificationStatus
from utils import cache
from models import Vet, VetCreateOrOverwrite
import config


class VetDoesNotExist(Exception):
    pass


def get_all_verified_vets(
        visibility: VetVisibility,
) -> Iterable[Vet]:
    collection = _get_vet_collection(visibility, "verified")

    for vet_document in collection.find({}):
        yield _convert_vet_mongo_document_to_model(vet_document)


def get_all_verified_vets_in_ring(
        visibility: VetVisibility,
        c_lat: float,
        c_lon: float,
        r_inner: float,
        r_outer: float,
) -> list[Vet]:
    center_pos = (c_lat, c_lon)

    def is_in_ring(vet: Vet) -> bool:
        vet_pos = (vet.location.lat, vet.location.lon)

        dist = geopy.distance.distance(center_pos, vet_pos).km

        return r_inner <= dist <= r_outer

    return [
        vet
        for vet in get_all_verified_vets(visibility)
        if is_in_ring(vet)
    ]


def create_or_overwrite_vet(
        visibility: VetVisibility,
        verification_status: VetVerificationStatus,
        id_: str,
        vet: VetCreateOrOverwrite,
) -> Vet:
    delete_vet_by_id_if_exists(visibility, id_)

    collection = _get_vet_collection(visibility, verification_status)

    collection.insert_one({
        "_id": id_,
        **vet.dict()
    })

    return Vet(
        **(vet.dict() | {"id": id_})
    )


def change_vet_verification_status_by_id_if_exists(
        visibility: VetVisibility,
        id_: str,
        new_verification_status: VetVerificationStatus,
) -> Vet:
    vet: Vet | None = None
    for old_verification_status in VET_VERIFICATION_STATUSES:
        collection = _get_vet_collection(visibility, old_verification_status)

        if document := collection.find_one_and_delete({"_id": id_}):
            vet = _convert_vet_mongo_document_to_model(document)
            break

    if vet is None:
        raise VetDoesNotExist

    create_or_overwrite_vet(
        visibility,
        new_verification_status,
        id_,
        vet,
    )

    return vet


def delete_vet_by_id_if_exists(
        visibility: VetVisibility,
        id_: str,
) -> None:
    for verification_status in VET_VERIFICATION_STATUSES:
        collection = _get_vet_collection(visibility, verification_status)

        collection.delete_many({"_id": id_})


def _get_vet_collection(
        visibility: VetVisibility,
        verification_status: VetVerificationStatus,
) -> Collection:
    collection_name = _get_vet_collection_name(visibility, verification_status)

    return _get_vet_collections()[collection_name]


@cache.return_singleton(populate_cache_on="prepopulate_called")
def _get_vet_collections() -> dict[str, Collection]:
    collections: dict[str, Collection] = {}

    for visibility in VET_VISIBILITIES:
        for verification_status in VET_VERIFICATION_STATUSES:
            collection_name = _get_vet_collection_name(visibility, verification_status)

            collections[collection_name] = _get_db()[collection_name]

    return collections


def _get_vet_collection_name(
        visibility: VetVisibility,
        verification_status: VetVerificationStatus,
) -> str:
    return f"{visibility}_{verification_status}"


def _convert_vet_mongo_document_to_model(document: dict) -> Vet:
    dct = {
        **document,
        "id": document["_id"],
    }
    del dct["_id"]

    return Vet(**dct)


def _convert_vet_model_to_mongo_document(model: Vet) -> dict:
    dct = model.dict()

    document = {
        **dct,
        "_id": dct["id"]
    }
    del document["id"]

    return document


@cache.return_singleton(populate_cache_on="prepopulate_called")
def _get_db() -> Database[Mapping[str, Any]]:
    client = _create_mongo_client()

    return client["db"]


def _create_mongo_client() -> MongoClient:
    connection_str = _get_connection_string()

    with pymongo.timeout(config.get().db.connection_ping_timeout):
        # Test connection to client
        client = MongoClient(connection_str)
        client.admin.command("ping")

    return client


def _get_connection_string() -> str:
    db_config = config.get().db

    return f"mongodb://{db_config.root_username}:{db_config.root_password}@0.0.0.0:{db_config.port}"


cache.prepopulate()
