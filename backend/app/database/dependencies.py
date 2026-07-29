from sqlalchemy.orm import Session

from backend.app.database.database import SessionLocal


def get_db():
    """
    Database dependency.
    Creates a new database session for each request.
    """

    db: Session = SessionLocal()

    try:
        yield db

    finally:
        db.close()