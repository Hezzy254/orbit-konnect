from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Boolean,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.database import Base
from backend.app.models.base_model import BaseModel


class PackageDurationUnit(str, Enum):
    """
    Supported package duration units.
    """

    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"


class Package(Base, BaseModel):
    __tablename__ = "packages"

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "name",
            name="uq_package_company_name",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    download_speed_mbps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    upload_speed_mbps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    duration_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    duration_unit: Mapped[PackageDurationUnit] = mapped_column(
        SQLEnum(PackageDurationUnit),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    company = relationship(
        "Company",
        back_populates="packages",
    )

    subscriptions = relationship(
        "Subscription",
        back_populates="package",
    )