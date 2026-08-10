from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    """
    Shared customer fields.
    """

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
    Fields that can be updated.

    All fields are optional because this endpoint supports
    partial updates.
    """

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

    is_active: bool | None = None


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