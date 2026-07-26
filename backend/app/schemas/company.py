from pydantic import BaseModel, EmailStr


class CompanyCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    logo: str | None = None

    country: str = "Oman"
    currency: str = "OMR"
    timezone: str = "Asia/Muscat"

    subscription_plan: str = "Free"


class CompanyResponse(CompanyCreate):
    id: int
    is_active: bool

    class Config:
        from_attributes = True