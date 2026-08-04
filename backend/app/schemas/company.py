from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CompanyResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    logo: str | None = None
    country: str
    currency: str
    timezone: str
    subscription_plan: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CompanyUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=255)
    country: str = Field(min_length=2, max_length=50)
    currency: str = Field(min_length=3, max_length=10)
    timezone: str = Field(min_length=3, max_length=50)