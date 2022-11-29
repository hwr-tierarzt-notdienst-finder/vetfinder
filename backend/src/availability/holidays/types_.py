from datetime import datetime
from typing import TypedDict

from types_ import Region


class CreateCacheRegionEntry(TypedDict):
    valid_from: datetime
    valid_to: datetime
    holidays: dict[int, list[datetime]]  # Integer key is year


class CacheRegionEntry(CreateCacheRegionEntry):
    updated_at: datetime


Cache = dict[Region, CacheRegionEntry]
