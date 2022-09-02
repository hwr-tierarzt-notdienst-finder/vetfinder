from dataclasses import dataclass


@dataclass(frozen=True)
class VetLocation:
    address: str
    lat: float | None = None
    lon: float | None = None


@dataclass(frozen=True)
class VetContact:
    tel: str
    email: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class VetCreate:
    name: str
    location: VetLocation
    contact: VetContact


@dataclass(frozen=True)
class VetGet(VetCreate):
    id: str

