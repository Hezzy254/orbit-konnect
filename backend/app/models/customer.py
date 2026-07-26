from sqlalchemy import Column, Integer, String

from backend.app.database.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(30), unique=True)
    email = Column(String(100), unique=True)
    address = Column(String(255))
    status = Column(String(20), default="Active")