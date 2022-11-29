from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from time import sleep

import geopy

from models import Location, Vet, Address
from utils import cache

_NOMINATIM_GEOLOCATOR_USER_AGENT = "hwr_tierarzt_notdienst"
_GEOPY_LAST_REQUEST_DATETIME_FILE_NAME = "geopy_last_request_datetime.txt"
_GEOPY_REQUEST_RATELIMIT_IN_SECONDS = 2


def normalize(vet: Vet) -> Vet:
    vet = _normalize_location(vet)

    return vet


def _normalize_location(vet: Vet) -> Vet:
    denormalized_location = vet.location

    address = denormalized_location.address
    lat = denormalized_location.lat
    lon = denormalized_location.lon

    if lat is not None and lon is not None:
        geopy_location = _get_geopy_location_from_lat_lon(lat, lon)
    else:
        geopy_location = _get_geopy_location_from_address(address)

    address = _normalize_address_from_geopy_location(address, geopy_location)
    lat = geopy_location.latitude
    lon = geopy_location.longitude

    return vet.copy(
        update={
            "location": Location(
                address=address,
                lat=lat,
                lon=lon,
            )
        }
    )


@lru_cache(maxsize=1000)
def _get_geopy_location_from_lat_lon(
        lat: float,
        lon: float
) -> geopy.Location:
    _satisfy_geopy_request_ratelimit()

    return _geopy_geolocator().reverse((lat, lon), addressdetails=True)


@lru_cache(maxsize=1000)
def _get_geopy_location_from_address(address: Address) -> geopy.Location:
    _satisfy_geopy_request_ratelimit()

    # See https://nominatim.org/release-docs/develop/api/Search/
    return _geopy_geolocator().geocode(
        {
            "street": f"{address.number} {address.street}".strip(),
            "postalcode": str(address.zip_code),
            "city": address.city,
        },
        addressdetails=True
    )


def _normalize_address_from_geopy_location(
        unnormalized_address: Address,
        geopy_location: geopy.Location,
) -> Address:
    geopy_raw_address = geopy_location.raw.get("address", {})

    street = str(geopy_raw_address.get("road", unnormalized_address.street))
    house_number = geopy_raw_address.get("house_number", unnormalized_address.number)
    zip_code = int(geopy_raw_address.get("postalcode", unnormalized_address.zip_code))
    city = str(geopy_raw_address.get("city", unnormalized_address.city))

    return Address(
        street=street,
        number=house_number,
        zip_code=zip_code,
        city=city,
    )


@cache.return_singleton
def _geopy_geolocator() -> geopy.Nominatim:
    return geopy.Nominatim(user_agent=_NOMINATIM_GEOLOCATOR_USER_AGENT)


def _satisfy_geopy_request_ratelimit() -> None:
    """
    Delay the execution of synchronous code to meet the rate limit specified.

    If the period between two calls is below the specified rate limit,
    we sleep for remaining time.
    """
    _wait_until_next_geopy_request_allowed()
    _set_geopy_last_request_datetime_to_current()

    # Yes, this is a somewhat crude synchronization primitive,
    # but it works and is simple.

    return


def _set_geopy_last_request_datetime_to_current() -> None:
    with open(_geopy_last_request_datetime_file_path(), "w") as f:
        f.write(datetime.now().isoformat())


def _wait_until_next_geopy_request_allowed() -> None:
    with open(_geopy_last_request_datetime_file_path(), "r") as f:
        last_datetime = datetime.fromisoformat(f.read().strip())

    seconds_since_last_request = (datetime.now() - last_datetime).seconds

    if seconds_since_last_request < _GEOPY_REQUEST_RATELIMIT_IN_SECONDS:
        seconds_left_to_wait = _GEOPY_REQUEST_RATELIMIT_IN_SECONDS - seconds_since_last_request
        sleep(seconds_left_to_wait)

    return


@cache.return_singleton
def _geopy_last_request_datetime_file_path() -> Path:
    current_dir = Path(__file__).parent.resolve()

    file_path = current_dir / _GEOPY_LAST_REQUEST_DATETIME_FILE_NAME

    # Create file containing initial datetime if it does not exist
    if not file_path.exists():
        file_path.touch()

        with open(file_path, "w") as f:
            initial_datetime = datetime.now() - timedelta(seconds=_GEOPY_REQUEST_RATELIMIT_IN_SECONDS)
            f.write(initial_datetime.isoformat())

    return file_path


cache.prepopulate()
