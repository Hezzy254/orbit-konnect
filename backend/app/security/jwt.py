from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import JWTError, jwt

from backend.app.core.config import settings
from backend.app.models.user import User

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


def _create_token(
    user: User,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    """
    Internal helper for creating JWT tokens.
    """

    now = datetime.now(UTC)
    expire = now + expires_delta

    payload = {
        "sub": user.email,
        "company_id": user.company_id,
        "role": user.role.value,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_access_token(user: User) -> str:
    """
    Create an access token.
    """
    return _create_token(
        user=user,
        token_type="access",
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        ),
    )


def create_refresh_token(user: User) -> str:
    """
    Create a refresh token.
    """
    return _create_token(
        user=user,
        token_type="refresh",
        expires_delta=timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS,
        ),
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return payload

    except JWTError:
        return {}