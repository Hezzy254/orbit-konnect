from fastapi import FastAPI

from backend.app.api.v1.router import api_router


app = FastAPI(
    title="Orbit Konnect API",
    version="1.0.0",
)


app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    return {
        "message": "Orbit Konnect API is running"
    }