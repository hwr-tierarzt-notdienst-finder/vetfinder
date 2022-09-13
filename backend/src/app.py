from fastapi import FastAPI

from shared.models import VetInDb

from . import db
from .data import collect_vets

app = FastAPI()


@app.on_event("startup")
def startup() -> None:
    db.get_vets_collection().drop()
    for vet in collect_vets():
        db.create_vet(vet)


@app.get("/vets", response_model=list[VetInDb])
def get_vets(
        min_radius_in_km: int,
        max_radius_in_km: int
) -> list[VetInDb]:
    return db.get_vets()
