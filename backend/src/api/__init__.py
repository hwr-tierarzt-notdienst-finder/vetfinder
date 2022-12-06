from typing import NoReturn

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import db
import normalization
import utils.string_
import vet_management
from models import Treatments
from . import vets
from . import form
from . import content_management

api = FastAPI()

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


@api.exception_handler(vet_management.AccessDenied)
async def vet_management_access_denied_error_handler(
        request: Request,
        err: vet_management.AccessDenied
) -> NoReturn:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=jsonable_encoder({"detail": "Access denied"})
    )


@api.exception_handler(db.VetDoesNotExist)
async def vet_management_access_denied_error_handler(
        request: Request,
        err: db.VetDoesNotExist
) -> NoReturn:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"detail": str(err)})
    )


@api.exception_handler(normalization.NormalizationError)
async def vet_management_access_denied_error_handler(
        request: Request,
        err: normalization.NormalizationError
) -> NoReturn:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "detail": [
                {
                    "loc": ["body"] + [
                        utils.string_.as_camel_case(segment)
                        for segment in location.split(".")
                    ],
                    "msg": err.msg,
                    "type": "normalization_error"
                }
                for location in err.locations
            ]
        })
    )


@api.get("/treatments")
def get_treatments() -> list[str]:
    return sorted(treatment for treatment in Treatments.__members__.values())
