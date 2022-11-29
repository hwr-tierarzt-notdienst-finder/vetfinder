from __future__ import annotations

import geopy.distance

from constants import VET_COLLECTIONS
from models import VetInDb, VetWithModificationTokenId
import normalization
from ._core import BaseRepository


class Repository(BaseRepository[VetWithModificationTokenId, VetInDb]):
    _IN_DB_CLS = VetInDb

    def insert(
            self,
            vet: VetWithModificationTokenId
    ) -> VetInDb:
        return super().insert(normalization.vet.normalize(vet))

    def in_ring(
            self,
            c_lat: float,
            c_lon: float,
            r_inner: float,
            r_outer: float,
    ) -> list[VetInDb]:
        center_pos = (c_lat, c_lon)

        def is_in_ring(vet: VetInDb) -> bool:
            vet_pos = (vet.location.lat, vet.location.lon)

            dist = geopy.distance.distance(center_pos, vet_pos).km

            return r_inner <= dist <= r_outer

        return [vet for vet in self.all() if is_in_ring(vet)]


def create_repositories() -> dict[str, Repository]:
    repos: dict[str, Repository] = {}

    for collection_name in VET_COLLECTIONS:
        repos[collection_name] = Repository(collection_name)

    return repos


repositories = create_repositories()
