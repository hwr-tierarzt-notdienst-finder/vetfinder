from geopy.geocoders import Nominatim

from models import Vet, Location, Field

NOMINATIM_USER_AGENT = "nominatim.openstreetmap.org"


geolocator = Nominatim(user_agent="vetfinder")


def normalize_vet(vet: Vet) -> Vet:
    vet = normalize_location(vet)
    return vet


def normalize_location(vet: Vet) -> Vet:
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

    return Vet(
        **{**vet.dict(), "location": normalized_location},
    )
