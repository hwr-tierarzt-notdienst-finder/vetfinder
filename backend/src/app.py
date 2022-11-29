import logging
from datetime import datetime
from typing import TypeVar, ParamSpec, NoReturn

from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import auth
from models import Vet, VetInDb, VetResponse, VetWithId, VetWithModificationTokenId
import db
import availability


_T = TypeVar('_T')
_P = ParamSpec('_P')


app = FastAPI()

security = HTTPBasic()


@app.get(
    "/vets",
    response_model=list[VetResponse],
    description=(
        "Returns vets in a ring around a central coordinate."
    )
)
def get_vets(
        token: str,
        c_lat: float = Query(
            description="The latitude of the ring center.",
            example=52.52437,
        ),
        c_lon: float = Query(
            description="The longitude of the ring center.",
            example=13.41053,
        ),
        r_inner: float = Query(
            description="The inner radius of the ring in km.",
            example=0,
        ),
        r_outer: float = Query(
            description="The outer radius of the ring in km.",
            example=100,
        ),
        availability_from: datetime | None = Query(
            default=None,
            description=(
                    "If this parameter is provided together with 'availability_to', "
                    "the availability time spans of the emergency service will returned "
                    "for the provided interval. "
                    "The value must be an ISO date time with offset."
            ),
            example="2022-09-19T11:04:07.252439+02:00"
        ),
        availability_to: datetime | None = Query(
            default=None,
            description=(
                    "If this parameter is provided together with 'availability_from', "
                    "the availability time spans of the emergency service will returned "
                    "for the provided interval. "
                    "The value must be an ISO date time with offset."
            ),
            example="2022-09-23T11:04:07.252439+02:00"
        ),
) -> list[VetInDb]:
    _validate_get_vets_query_parameters(
        token,
        c_lat,
        c_lon,
        r_inner,
        r_outer,
        availability_from,
        availability_to,
    )

    for token_id in auth.token.get_vets_collection_token_ids():
        if auth.token.is_authentic(token_id, token):
            collection = auth.token.get_vets_collection_by_token_id(token_id)
            vets = db.vets[collection].in_ring(
                c_lat,
                c_lon,
                r_inner,
                r_outer,
            )

            break
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if availability_from is not None and availability_to is not None:
        return [
            VetResponse(
                availability=list(availability.get_time_spans(
                    lower_bound=availability_from,
                    upper_bound=availability_to,
                    vet=vet,
                )),
                **vet.dict()
            )
            for vet in vets
        ]
    else:
        return [VetResponse(**vet.dict()) for vet in vets]


def _validate_get_vets_query_parameters(
        token: str,
        c_lat: float,
        c_lon: float,
        r_inner: float,
        r_outer: float,
        availability_from: datetime,
        availability_to: datetime,
) -> None:
    error_strings: list[str] = []

    _add_error_strings_get_vets_ring_center_coordinate_query_parameters(
        error_strings,
        c_lat,
        c_lon,
    )
    _add_error_strings_get_vets_ring_radii_query_parameters(
        error_strings,
        r_inner,
        r_outer,
    )
    _add_error_strings_get_vets_availability_query_parameters(
        error_strings,
        availability_from,
        availability_to
    )

    if error_strings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_strings,
        )


def _add_error_strings_get_vets_ring_center_coordinate_query_parameters(
        error_strings: list[str],
        c_lat: float,
        c_lon: float,
) -> None | NoReturn:
    if c_lat < -90 or c_lat > 90:
        error_strings.append(f"{c_lat=} is not between -90 and 90")

    if c_lon < -180 or c_lon > 180:
        error_strings.append(f"{c_lon=} is not between -180 and 180")


def _add_error_strings_get_vets_ring_radii_query_parameters(
        error_strings: list[str],
        r_inner: float,
        r_outer: float,
) -> None | NoReturn:
    if r_inner < 0:
        error_strings.append(f"{r_inner=} is not greater than 0")

    if r_outer < 0:
        error_strings.append(f"{r_outer=} is not greater than 0")

    if r_inner > r_outer:
        error_strings.append(f"{r_inner=} is not smaller than {r_outer=}")


def _add_error_strings_get_vets_availability_query_parameters(
        error_strings: list[str],
        availability_from: datetime,
        availability_to: datetime,
) -> None | NoReturn:
    if availability_from is None and availability_to is None:
        return
    if availability_from is not None and availability_to is None:
        error_strings.append(
            "If query parameter 'availability_from' is provided, "
            "'availability_to' must also be provided"
        )
    elif availability_from is None and availability_to is not None:
        error_strings.append(
            "If query parameter 'availability_to' is provided, "
            "'availability_from' must also be provided"
        )
    elif availability_from > availability_to:
        error_strings.append(
            f"availability_from='{availability_from}' datetime "
            f"must be earlier than availability_from='{availability_from}'"
        )


@app.get("/form")
def form_get_vet(
        credentials: HTTPBasicCredentials = Depends(security),
) -> VetWithId:
    modification_token_id = authenticate_form_request(credentials)

    try:
        return db.vets["hidden"].exactly_one({
            "modification_token_id": modification_token_id
        })
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vet has not been created yet. Use POST to create"
        )


@app.post("/form")
def form_create_vet(
        vet: Vet,
        credentials: HTTPBasicCredentials = Depends(security),
) -> VetWithId:
    modification_token_id = authenticate_form_request(credentials)

    if len(db.vets["hidden"].find({"modification_token_id": modification_token_id})) != 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vet has already been created. Use PUT to update"
        )

    vet_in_db = db.vets["hidden"].insert(
        VetWithModificationTokenId(**vet.dict() | {"modification_token_id": modification_token_id})
    )

    vet_with_id_kwargs = vet_in_db.dict()
    del vet_with_id_kwargs["modification_token_id"]
    return VetWithId(**vet_with_id_kwargs)


@app.put("/form")
def form_update_vet(
        vet: VetWithId,
        credentials: HTTPBasicCredentials = Depends(security),
) -> VetWithId:
    modification_token_id = authenticate_form_request(credentials)

    vet_in_db = db.vets["hidden"].update(
        VetInDb(**vet.dict() | {"modification_token_id": modification_token_id})
    )

    vet_with_id_kwargs = vet_in_db.dict()
    del vet_with_id_kwargs["modification_token_id"]
    return VetWithId(**vet_with_id_kwargs)


def authenticate_form_request(
        credentials: HTTPBasicCredentials
) -> str | NoReturn:
    token_id = f"vet_email:{credentials.username}"
    token = credentials.password

    if not auth.token.is_authentic(token_id, token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return token_id
