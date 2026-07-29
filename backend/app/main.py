from fastapi import FastAPI

from backend.app.core.config import settings

from backend.app.database.database import engine
from backend.app.database.base import Base
from backend.app.api.v1 import auth
from backend.app.api.v1 import customers
from backend.app.api.v1 import packages

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

#Base.metadata.create_all(bind=engine)#

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} 🚀",
        "version": settings.APP_VERSION
    }

app.include_router(customers.router)
app.include_router(packages.router)
app.include_router(auth.router)