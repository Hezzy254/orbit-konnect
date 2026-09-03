from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    """
    Data required to create a new payment.

    A newly created payment always starts as PENDING.

    Company, customer identity, currency, transaction reference,
    and initial status are controlled by the backend.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    subscription_id: int = Field(..., gt=0)

    amount: Decimal = Field(
        ...,
        gt=0,
        max_digits=12,
        decimal_places=3,
    )

    payment_method: PaymentMethod

    provider: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )


class PaymentResponse(BaseModel):
    """
    Payment data returned by the API.
    """

    id: int
    company_id: int
    customer_id: int
    subscription_id: int

    amount: Decimal
    currency: str

    payment_method: PaymentMethod
    provider: str

    status: PaymentStatus

    transaction_reference: str
    provider_reference: str | None

    paid_at: datetime | None
    failure_reason: str | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class PaymentListResponse(BaseModel):
    """
    Paginated payment response.
    """

    items: list[PaymentResponse]
    total: int
    skip: int
    limit: int