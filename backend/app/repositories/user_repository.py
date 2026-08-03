from sqlalchemy.orm import Session

from backend.app.models.user import User


class UserRepository:
    """
    Repository responsible for all User database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by ID.
        """
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by email.
        """
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def email_exists(self, email: str) -> bool:
        """
        Check whether an email already exists.
        """
        return self.get_by_email(email) is not None

    def create(self, user: User) -> User:
        """
        Create a new user.
        """
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        """
        Update an existing user.
        """
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """
        Delete a user.
        """
        self.db.delete(user)
        self.db.commit()

    def list_by_company(self, company_id: int) -> list[User]:
        """
        Return all users belonging to a company.
        """
        return (
            self.db.query(User)
            .filter(User.company_id == company_id)
            .all()
        )