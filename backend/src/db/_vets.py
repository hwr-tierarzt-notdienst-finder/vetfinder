from __future__ import annotations

from collections.abc import Iterable, Callable
from dataclasses import dataclass
from typing import Any, Protocol

import geopy.distance

from constants import VET_COLLECTIONS
from models import Vet, VetInDb
from ._core import BaseRepository, create_repo


@dataclass(frozen=True)
class Repository(BaseRepository[Vet, VetInDb]):
    in_ring: _InRing


class _InRing(Protocol):

    def __call__(
            self,
            c_lat: float,
            c_lon: float,
            r_inner: float,
            r_outer: float,
    ) -> list[VetInDb]:
        ...


def create_repo_methods(base_repo: BaseRepository) -> Iterable[
    Callable[[Any], Any],
    Callable[[Any, ...], Any]
]:

    def in_ring(
            c_lat: float,
            c_lon: float,
            r_inner: float,
            r_outer: float,
    ) -> list[VetInDb]:
        center_pos = (c_lat, c_lon)

        def is_in_ring(vet: VetInDb) -> bool:
            vet_pos = (vet.location.lat.value, vet.location.lon.value)

            dist = geopy.distance.distance(center_pos, vet_pos).km

            return r_inner <= dist <= r_outer

        return [vet for vet in base_repo.all() if is_in_ring(vet)]

    yield in_ring


def create_repos() -> dict[str, Repository]:
    repos: dict[str, Repository] = {}

    for collection in VET_COLLECTIONS:
        repos[collection] = create_repo(
            VetInDb,
            collection,
            repo_cls=Repository,
            create_extra_methods=create_repo_methods
        )

    return repos


repos = create_repos()
