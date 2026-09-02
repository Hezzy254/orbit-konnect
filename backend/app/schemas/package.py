from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PackageDurationUnit(str, Enum):
    """
    Supported package duration units.
    """

    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"


class PackageBase(BaseModel):
    """
    Shared package fields.

    Request data is normalized by stripping surrounding
    whitespace and unexpected fields are rejected.
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

    download_speed_mbps: int = Field(
        ...,
        gt=0,
    )

    upload_speed_mbps: int = Field(
        ...,
        gt=0,
    )

    duration_value: int = Field(
        ...,
        gt=0,
    )

    duration_unit: PackageDurationUnit

    price: Decimal = Field(
        ...,
        ge=0,
        max_digits=12,
        decimal_places=3,
    )

    description: str | None = Field(
        default=None,
        max_length=255,
    )


class PackageCreate(PackageBase):
    """
    Data required to create a package.
    """

    pass


class PackageUpdate(BaseModel):
    """
    Fields that can be updated on a package.

    Package activation state is intentionally excluded.
    Activation and deactivation are handled by dedicated
    lifecycle endpoints.

    Unexpected fields are rejected instead of silently ignored.
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

    download_speed_mbps: int | None = Field(
        default=None,
        gt=0,
    )

    upload_speed_mbps: int | None = Field(
        default=None,
        gt=0,
    )

    duration_value: int | None = Field(
        default=None,
        gt=0,
    )

    duration_unit: PackageDurationUnit | None = None

    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=3,
    )

    description: str | None = Field(
        default=None,
        max_length=255,
    )


class PackageResponse(PackageBase):
    """
    Package returned by the API.
    """

    id: int
    company_id: int
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class PackageListResponse(BaseModel):
    """
    Paginated package response.
    """

    items: list[PackageResponse]

    total: int

    skip: int

    limit: int