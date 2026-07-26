from sqlalchemy import Column, Integer, String, Float

from backend.app.database.database import Base


class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    speed = Column(String(50), nullable=False)

    duration = Column(String(50), nullable=False)

    price = Column(Float, nullable=False)

    description = Column(String(255), nullable=True)
    