from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.database import Base
from backend.app.models.base_model import BaseModel


class NetworkDeviceVendor(str, Enum):
    MIKROTIK = "MIKROTIK"
    TP_LINK = "TP_LINK"
    UBIQUITI = "UBIQUITI"
    OTHER = "OTHER"


class NetworkDeviceType(str, Enum):
    ROUTER = "ROUTER"
    ACCESS_POINT = "ACCESS_POINT"
    CPE = "CPE"
    SWITCH = "SWITCH"
    OTHER = "OTHER"


class NetworkDeviceConnectionType(str, Enum):
    API = "API"
    API_SSL = "API_SSL"
    REST = "REST"
    SNMP = "SNMP"


class NetworkDeviceStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"


class NetworkDevice(Base, BaseModel):
    __tablename__ = "network_devices"

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

    vendor: Mapped[NetworkDeviceVendor] = mapped_column(
        SQLEnum(NetworkDeviceVendor),
        nullable=False,
        index=True,
    )

    model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    device_type: Mapped[NetworkDeviceType] = mapped_column(
        SQLEnum(NetworkDeviceType),
        nullable=False,
        index=True,
    )

    ip_address: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    api_port: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    connection_type: Mapped[NetworkDeviceConnectionType] = mapped_column(
        SQLEnum(NetworkDeviceConnectionType),
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    encrypted_password: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    verify_tls: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    status: Mapped[NetworkDeviceStatus] = mapped_column(
        SQLEnum(NetworkDeviceStatus),
        nullable=False,
        default=NetworkDeviceStatus.UNKNOWN,
        index=True,
    )

    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    company = relationship(
        "Company",
        back_populates="network_devices",
    )