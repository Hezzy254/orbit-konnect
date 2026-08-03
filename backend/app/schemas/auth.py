from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==========================================================
# LOGIN
# ==========================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ==========================================================
# REGISTER
# ==========================================================

class RegisterRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100)

    owner_name: str = Field(..., min_length=2, max_length=100)

    email: EmailStr

    password: str = Field(..., min_length=8)

    country: str = Field(..., max_length=50)

    currency: str = Field(default="OMR", max_length=10)

    timezone: str = Field(default="Asia/Muscat", max_length=50)

    phone: str | None = None


class RegisterResponse(BaseModel):
    company_id: int
    company_name: str

    owner_id: int
    owner_name: str

    access_token: str
    refresh_token: str

    token_type: str = "bearer"
    expires_in: int


# ==========================================================
# TOKEN
# ==========================================================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ==========================================================
# CURRENT USER
# ==========================================================

class CurrentUserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

    company_id: int
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )