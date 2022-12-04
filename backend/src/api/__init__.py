from fastapi import FastAPI

from . import vets
from . import form
from . import content_management


api = FastAPI()
api.include_router(vets.router)
api.include_router(form.router)
api.include_router(content_management.router)
