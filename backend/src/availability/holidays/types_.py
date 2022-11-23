from datetime import datetime
from typing import TypedDict

from shared.utils.constants import Region


class CreateCacheRegionEntry(TypedDict):
    valid_from: datetime
    valid_to: datetime
    holidays: dict[int, list[datetime]]  # Integer key is year


class CacheRegionEntry(CreateCacheRegionEntry):
    updated_at: datetime


Cache = dict[Region, CacheRegionEntry]
