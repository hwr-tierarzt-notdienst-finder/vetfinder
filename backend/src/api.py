from fastapi import FastAPI

from . import db
from .models import VetGet

app = FastAPI()


@app.get("/vets")
def get_vets() -> list[VetGet]:
    return db.get_vets()
