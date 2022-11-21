from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from time import sleep

import geopy

from models import Location, Vet
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

    has_address = address is not None
    has_lat_lon = lat is not None and lon is not None

    if has_address and has_lat_lon:
        return vet.copy()

    if has_address and not has_lat_lon:
        geopy_location = _get_geopy_location_from_address(address)
    elif not has_address and has_lat_lon:
        geopy_location = _get_geopy_location_from_lat_lon(lat, lon)
    else:
        raise ValueError(
            f"Expected vet.location={denormalized_location} "
            f"to have an address or latitude and longitude"
        )

    address = geopy_location.address
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

    return _geopy_geolocator().reverse((lat, lon))


@lru_cache(maxsize=1000)
def _get_geopy_location_from_address(address: str) -> geopy.Location:
    _satisfy_geopy_request_ratelimit()

    return _geopy_geolocator().geocode(address)


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
