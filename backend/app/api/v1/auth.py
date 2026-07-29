from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.auth import create_access_token
from backend.app.crud.user import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from backend.app.database.dependencies import get_db
from backend.app.schemas.user import (
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/test")
def test_auth():
    return {
        "message": "Authentication API is working!"
    }


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user.
    """

    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="Username already exists.",
        )

    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="Email already exists.",
        )

    return create_user(db, user)


@router.post(
    "/login",
    response_model=Token,
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return JWT token.
    """

    user = authenticate_user(
        db,
        credentials.username,
        credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token = create_access_token(
        {
            "sub": user.username,
            "role": user.role,
            "company_id": user.company_id,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }