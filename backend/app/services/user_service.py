from sqlalchemy.orm import Session

from backend.app.repositories.user_repository import (
    get_user_by_username,
)


def find_user(
    db: Session,
    username: str,
):
    return get_user_by_username(
        db,
        username,
    )