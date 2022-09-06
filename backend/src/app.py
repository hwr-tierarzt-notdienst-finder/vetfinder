from fastapi import FastAPI

from . import db
from .data import collect_vets
from models import VetGet

app = FastAPI()


@app.on_event("startup")
def startup() -> None:
    db.get_vets_collection().drop()
    for vet in collect_vets():
        db.create_vet(vet)


@app.get("/vets", response_model=list[VetGet])
def get_vets() -> list[VetGet]:
    return db.get_vets()
