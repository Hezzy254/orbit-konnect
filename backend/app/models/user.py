from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from backend.app.database.database import Base
from backend.app.models.roles import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    full_name = Column(String, nullable=False)

    role = Column(
        String,
        default=UserRole.TECHNICIAN.value,
        nullable=False,
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
    )

    company = relationship(
        "Company",
        back_populates="users",
    )