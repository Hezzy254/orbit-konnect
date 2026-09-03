from fastapi import APIRouter

from backend.app.api.v1 import auth
from backend.app.api.v1 import company
from backend.app.api.v1 import customer
from backend.app.api.v1 import packages
from backend.app.api.v1 import subscriptions


api_router = APIRouter()


# ==========================================================
# AUTHENTICATION
# ==========================================================

api_router.include_router(
    auth.router,
)


# ==========================================================
# COMPANY
# ==========================================================

api_router.include_router(
    company.router,
)


# ==========================================================
# CUSTOMERS
# ==========================================================

api_router.include_router(
    customer.router,
)


# ==========================================================
# PACKAGES
# ==========================================================

api_router.include_router(
    packages.router,
)


# ==========================================================
# SUBSCRIPTIONS
# ==========================================================

api_router.include_router(
    subscriptions.router,
)