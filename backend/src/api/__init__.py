from fastapi import FastAPI

from models import Treatments
from . import vets
from . import form
from . import content_management


api = FastAPI()
api.include_router(vets.router)
api.include_router(form.router)
api.include_router(content_management.router)


@api.get("/treatments")
def get_treatments() -> list[str]:
    return sorted(treatment for treatment in Treatments.__members__.values())
