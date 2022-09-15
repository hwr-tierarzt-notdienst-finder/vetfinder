from datetime import datetime
from typing import TypedDict

from shared.types import Region


class CreateCacheRegionEntry(TypedDict):
    valid_from: datetime
    valid_to: datetime
    holidays: dict[int, list[datetime]]  # Integer key is year


class CacheRegionEntry(CreateCacheRegionEntry):
    last_update: datetime


Cache = dict[Region, CacheRegionEntry]
