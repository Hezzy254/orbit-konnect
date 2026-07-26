from pydantic import BaseModel


class PackageCreate(BaseModel):
    name: str
    speed: str
    duration: str
    price: float
    description: str | None = None


class PackageResponse(PackageCreate):
    id: int

    class Config:
        from_attributes = True