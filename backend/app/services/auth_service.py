from datetime import datetime, UTC

from backend.app.repositories.user_repository import UserRepository
from backend.app.security.hashing import verify_password
from backend.app.security.jwt import (
    create_access_token,
    create_refresh_token,
)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate_user(
        self,
        email: str,
        password: str,
    ):
        """
        Authenticate a user using email and password.
        """

        user = self.user_repository.get_by_email(email)

        if not user:
            return None

        if not verify_password(
            password,
            user.hashed_password,
        ):
            return None

        return user

    def login(
        self,
        email: str,
        password: str,
    ):
        """
        Authenticate and generate tokens.
        """

        user = self.authenticate_user(
            email,
            password,
        )

        if not user:
            return None

        access_token = create_access_token(
            user=user,
        )

        refresh_token = create_refresh_token(
            user=user,
        )

        user.last_login = datetime.now(UTC)

        self.user_repository.update(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": user,
        }