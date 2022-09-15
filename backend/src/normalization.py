from geopy.geocoders import Nominatim
from shared.models import Vet, Location, Field
from . import db

NOMINATIM_USER_AGENT = "nominatim.openstreetmap.org"


geolocator = Nominatim(user_agent="vetfinder")


def normalize_vet(vet: Vet) -> Vet:
    vet = normalize_location(vet)
    return vet


def normalize_location(vet: Vet) -> Vet:
    cache_key = f"addr={vet.location.address};lat={vet.location.lat};lon={vet.location.lon}"

    cache = _get_normalized_cache()

    if cache_key in cache:
        normalized_location = cache[cache_key]
    else:
        geopy_location = geolocator.geocode(vet.location.address.value)

        normalized_address = Field(
            value=geopy_location.address
        )
        if vet.location.lat is None:
            normalized_lat = Field(
                value=geopy_location.latitude
            )
        else:
            normalized_lat = vet.location.lat
        if vet.location.lon is None:
            normalized_lon = Field(
                value=geopy_location.longitude
            )
        else:
            normalized_lon = vet.location.lon

        normalized_location = Location(
            address=normalized_address,
            lat=normalized_lat,
            lon=normalized_lon,
        )

        cache[cache_key] = normalized_location

    return Vet(
        **{**vet.dict(), "location": normalized_location},
    )


_normalized_locations_cache: dict[str, Location] | None = None
def _get_normalized_cache() -> dict[str, Location]:
    global _normalized_locations_cache

    if _normalized_locations_cache is None:
        _normalized_locations_cache = db.get_normalized_locations_cache()

    return _normalized_locations_cache
