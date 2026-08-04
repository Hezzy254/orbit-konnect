from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.models.roles import UserRole
from backend.app.models.user import User
from backend.app.repositories.company_repository import CompanyRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from backend.app.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from backend.app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# ==========================================================
# REGISTER
# ==========================================================

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    auth_service = AuthService(
        user_repository=UserRepository(db),
        company_repository=CompanyRepository(db),
    )

    try:
        result = auth_service.register(request)
        return RegisterResponse(**result)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ==========================================================
# LOGIN (JSON - React / Flutter)
# ==========================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    auth_service = AuthService(
        user_repository=UserRepository(db),
        company_repository=CompanyRepository(db),
    )

    result = auth_service.login(
        email=request.email,
        password=request.password,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return TokenResponse(**result)


# ==========================================================
# TOKEN (Swagger OAuth2)
# ==========================================================

@router.post(
    "/token",
    response_model=TokenResponse,
    include_in_schema=False,
)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    auth_service = AuthService(
        user_repository=UserRepository(db),
        company_repository=CompanyRepository(db),
    )

    result = auth_service.login(
        email=form_data.username,
        password=form_data.password,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return TokenResponse(**result)


# ==========================================================
# REFRESH
# ==========================================================

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_token(
    request: RefreshTokenRequest,
):
    payload = decode_token(request.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type.",
        )

    user = User(
        company_id=payload["company_id"],
        full_name="",
        email=payload["sub"],
        hashed_password="",
        role=UserRole(payload["role"]),
        is_active=True,
    )

    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
        token_type="bearer",
        expires_in=3600,
    )


# ==========================================================
# CURRENT USER
# ==========================================================

@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return CurrentUserResponse.model_validate(current_user)