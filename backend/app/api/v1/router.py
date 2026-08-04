from fastapi import APIRouter

from backend.app.api.v1 import auth
from backend.app.api.v1 import company

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(company.router)