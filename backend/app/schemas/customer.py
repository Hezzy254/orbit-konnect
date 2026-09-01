from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    """
    Shared customer fields.

    Request data is normalized by stripping surrounding
    whitespace and unexpected fields are rejected.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    phone: str = Field(
        ...,
        min_length=5,
        max_length=30,
    )

    email: EmailStr | None = None

    address: str | None = Field(
        default=None,
        max_length=255,
    )

    national_id: str | None = Field(
        default=None,
        max_length=50,
    )


class CustomerCreate(CustomerBase):
    """
    Data required to create a customer.
    """

    pass


class CustomerUpdate(BaseModel):
    """
    Fields that can be updated on a customer profile.

    Customer activation state is intentionally excluded.
    Activation and deactivation are handled by dedicated
    lifecycle endpoints.

    Unexpected fields are rejected instead of silently ignored.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    phone: str | None = Field(
        default=None,
        min_length=5,
        max_length=30,
    )

    email: EmailStr | None = None

    address: str | None = Field(
        default=None,
        max_length=255,
    )

    national_id: str | None = Field(
        default=None,
        max_length=50,
    )


class CustomerResponse(CustomerBase):
    """
    Customer returned by the API.
    """

    id: int
    company_id: int
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class CustomerListResponse(BaseModel):
    """
    Paginated customer response.
    """

    items: list[CustomerResponse]

    total: int

    skip: int

    limit: int