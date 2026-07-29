from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    company_id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str | None = None
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    company_id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str | None = None
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"