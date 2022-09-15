from datetime import datetime

from fastapi import FastAPI, HTTPException, status

from .models import VetInDb, VetResponse
from . import db
from .data import collect_vets
from . import availability

app = FastAPI()


@app.on_event("startup")
def startup() -> None:
    db.get_vets_collection().drop()
    for vet in collect_vets():
        db.create_vet(vet)


@app.get("/vets", response_model=list[VetResponse])
def get_vets(
        min_radius_in_km: int,
        max_radius_in_km: int,
        availability_from: datetime | None = None,
        availability_to: datetime | None = None,
) -> list[VetInDb]:
    vets = db.get_vets()

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
                **vet.dict()
            )
            for vet in vets
        ]
