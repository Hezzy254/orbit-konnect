from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.package import PackageDurationUnit
from backend.app.models.subscription import SubscriptionStatus


class SubscriptionCreate(BaseModel):
    """
    Data required to create a new subscription.

    A newly created subscription always starts as PENDING.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    customer_id: int = Field(..., gt=0)
    package_id: int = Field(..., gt=0)
    auto_renew: bool = False


class SubscriptionResponse(BaseModel):
    """
    Subscription data returned by the API.
    """

    id: int
    company_id: int
    customer_id: int
    package_id: int

    status: SubscriptionStatus

    # Historical package snapshot
    package_name: str
    download_speed_mbps: int
    upload_speed_mbps: int
    duration_value: int
    duration_unit: PackageDurationUnit
    price: Decimal

    # Service lifecycle
    start_at: datetime | None
    end_at: datetime | None
    auto_renew: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class SubscriptionListResponse(BaseModel):
    """
    Paginated subscription response.
    """

    items: list[SubscriptionResponse]
    total: int
    skip: int
    limit: int