from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import Treatments
from . import vets
from . import form
from . import content_management


origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
    "http://127.0.0.1",
    "https://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5173",
]

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api.include_router(vets.router)
api.include_router(form.router)
api.include_router(content_management.router)


@api.get("/treatments")
def get_treatments() -> list[str]:
    return sorted(treatment for treatment in Treatments.__members__.values())
