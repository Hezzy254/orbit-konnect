from datetime import UTC, datetime

from backend.app.models.company import Company
from backend.app.models.roles import UserRole
from backend.app.models.user import User
from backend.app.repositories.company_repository import CompanyRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import RegisterRequest
from backend.app.security.hashing import (
    hash_password,
    verify_password,
)
from backend.app.security.jwt import (
    create_access_token,
    create_refresh_token,
)


class AuthService:
    """
    Authentication and Registration business logic.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        company_repository: CompanyRepository,
    ):
        self.user_repository = user_repository
        self.company_repository = company_repository

    # ==========================================================
    # LOGIN
    # ==========================================================

    def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> User | None:

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

        user = self.authenticate_user(
            email,
            password,
        )

        if user is None:
            return None

        user.last_login = datetime.now(UTC)
        self.user_repository.update(user)

        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": user,
        }

    # ==========================================================
    # REGISTER
    # ==========================================================

    def register(
        self,
        request: RegisterRequest,
    ):

        if self.user_repository.email_exists(request.email):
            raise ValueError("Email already registered.")

        if self.company_repository.get_by_name(request.company_name):
            raise ValueError("Company already exists.")

        company = Company(
            name=request.company_name,
            email=request.email,
            phone=request.phone,
            country=request.country,
            currency=request.currency,
            timezone=request.timezone,
        )

        company = self.company_repository.create(company)

        owner = User(
            company_id=company.id,
            full_name=request.owner_name,
            email=request.email,
            hashed_password=hash_password(request.password),
            role=UserRole.OWNER,
            is_active=True,
        )

        owner = self.user_repository.create(owner)

        access_token = create_access_token(owner)
        refresh_token = create_refresh_token(owner)

        return {
            "company_id": company.id,
            "company_name": company.name,
            "owner_id": owner.id,
            "owner_name": owner.full_name,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
        }