from datetime import datetime
from typing import TypeVar, ParamSpec

from fastapi import FastAPI, HTTPException, status

import auth
from models import VetInDb, VetResponse
import db
from data import collect_vets
import availability


_T = TypeVar('_T')
_P = ParamSpec('_P')


app = FastAPI()


@app.on_event("startup")
def startup() -> None:
    db.get_vets_collection("hidden").drop()

    for vet in collect_vets():
        db.create_vet("hidden", vet)


@app.get("/vets", response_model=list[VetResponse])
def get_vets(
        min_radius_in_km: int,
        max_radius_in_km: int,
        token: str,
        availability_from: datetime | None = None,
        availability_to: datetime | None = None,
) -> list[VetInDb]:
    for token_id in auth.token.get_vets_collection_token_ids():
        if auth.token.is_authentic(token_id, token):
            collection = auth.token.get_vets_collection_by_token_id(token_id)
            vets = db.get_vets(collection)

            break
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if availability_from is None and availability_to is None:
        return [
            VetResponse(**vet.dict())
            for vet in vets
        ]
    elif availability_from is not None and availability_to is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "If query parameter 'availability_from' is provided, "
                "'availability_to' must also be provided"
            )
        )
    elif availability_from is None and availability_to is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "If query parameter 'availability_to' is provided, "
                "'availability_from' must also be provided"
            )
        )
    elif availability_from > availability_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "'availability_from' datetime must be earlier than 'availability_from'"
            )
        )
    else:
        return [
            VetResponse(
                availability=list(availability.get_time_spans(
                    lower_bound=availability_from,
                    upper_bound=availability_to,
                    vet=vet,
                )),
                **vet.dict(by_alias=False)
            )
            for vet in vets
        ]