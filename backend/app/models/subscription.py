from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.database import Base
from backend.app.models.base_model import BaseModel
from backend.app.models.package import PackageDurationUnit


class SubscriptionStatus(str, Enum):
    """
    Lifecycle states for a customer subscription.
    """

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class Subscription(Base, BaseModel):
    """
    Represents a customer's purchased service subscription.

    Package information is snapshotted at subscription creation
    so historical subscription terms remain unchanged if the
    original package is modified later.
    """

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    package_id: Mapped[int] = mapped_column(
        ForeignKey("packages.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus),
        nullable=False,
        default=SubscriptionStatus.PENDING,
        index=True,
    )

    # ---------------------------------------------------------
    # Historical package snapshot
    # ---------------------------------------------------------

    package_name: Mapped[str] = mapped_column(
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

    # ---------------------------------------------------------
    # Service lifecycle
    # ---------------------------------------------------------

    start_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    end_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    auto_renew: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    company = relationship(
        "Company",
        back_populates="subscriptions",
    )

    customer = relationship(
        "Customer",
        back_populates="subscriptions",
    )

    package = relationship(
        "Package",
        back_populates="subscriptions",
    )