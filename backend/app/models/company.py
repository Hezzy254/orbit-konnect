from datetime import datetime
from sqlalchemy.orm import relationship

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from backend.app.database.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(30), nullable=True)
    address = Column(String(255), nullable=True)

    logo = Column(String(255), nullable=True)

    country = Column(String(50), nullable=False, default="Oman")
    currency = Column(String(10), nullable=False, default="OMR")
    timezone = Column(String(50), nullable=False, default="Asia/Muscat")

    subscription_plan = Column(String(30), nullable=False, default="Free")

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    
    users = relationship(
    "User",
    back_populates="company",
    cascade="all, delete-orphan"
)
