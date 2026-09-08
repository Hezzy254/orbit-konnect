from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.models.network_device import (
    NetworkDeviceConnectionType,
    NetworkDeviceStatus,
    NetworkDeviceType,
    NetworkDeviceVendor,
)


class NetworkDeviceBase(BaseModel):
    """
    Shared network device fields.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    vendor: NetworkDeviceVendor

    model: str | None = Field(
        default=None,
        max_length=100,
    )

    device_type: NetworkDeviceType

    ip_address: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    api_port: int = Field(
        ...,
        ge=1,
        le=65535,
    )

    connection_type: NetworkDeviceConnectionType

    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    verify_tls: bool = True

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, value: str) -> str:
        """
        Reject empty management addresses.
        """

        value = value.strip()

        if not value:
            raise ValueError("IP address or hostname is required.")

        return value


class NetworkDeviceCreate(NetworkDeviceBase):
    """
    Data required to create a network device.

    The password is accepted as plaintext only in the request.
    The service layer must encrypt it before database storage.
    """

    password: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )


class NetworkDeviceUpdate(BaseModel):
    """
    Fields that can be safely updated on a network device.

    Credentials are intentionally excluded from this schema.
    Credential rotation will use a dedicated endpoint later.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    vendor: NetworkDeviceVendor | None = None

    model: str | None = Field(
        default=None,
        max_length=100,
    )

    device_type: NetworkDeviceType | None = None

    ip_address: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    api_port: int | None = Field(
        default=None,
        ge=1,
        le=65535,
    )

    connection_type: NetworkDeviceConnectionType | None = None

    username: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    verify_tls: bool | None = None

    location: str | None = Field(
        default=None,
        max_length=255,
    )


class NetworkDeviceResponse(NetworkDeviceBase):
    """
    Network device returned by the API.

    The stored encrypted password is NEVER exposed.
    """

    id: int
    company_id: int
    is_active: bool
    status: NetworkDeviceStatus
    last_seen: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class NetworkDeviceListResponse(BaseModel):
    """
    Paginated network device response.
    """

    items: list[NetworkDeviceResponse]

    total: int
    skip: int
    limit: int