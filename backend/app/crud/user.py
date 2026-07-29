from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.schemas.user import UserCreate
from backend.app.auth.hashing import (
    hash_password,
    verify_password,
)


def get_user_by_username(
    db: Session,
    username: str,
):
    """
    Find a user by username.
    """
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str,
):
    """
    Find a user by email.
    """
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def create_user(
    db: Session,
    user: UserCreate,
):
    """
    Create a new user.
    """

    hashed_password = hash_password(user.password)

    db_user = User(
        company_id=user.company_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        phone=user.phone,
        password_hash=hashed_password,
        role="Admin",
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(
    db: Session,
    username: str,
    password: str,
):
    """
    Verify username and password.
    """

    user = get_user_by_username(
        db,
        username,
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user