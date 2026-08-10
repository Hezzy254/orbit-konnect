from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.exceptions.customer import (
    CustomerNotFoundError,
    DuplicateCustomerEmailError,
    DuplicateCustomerPhoneError,
)
from backend.app.models.user import User
from backend.app.repositories.customer_repository import CustomerRepository
from backend.app.schemas.customer import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from backend.app.services.customer_service import CustomerService


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


# ==========================================================
# SERVICE DEPENDENCY
# ==========================================================

def get_customer_service(
    db: Session = Depends(get_db),
) -> CustomerService:
    """
    Create the CustomerService dependency.
    """

    repository = CustomerRepository(db)

    return CustomerService(repository)


# ==========================================================
# CREATE CUSTOMER
# ==========================================================

@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    request: CustomerCreate,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    """
    Create a new customer for the authenticated company.
    """

    try:
        return service.create_customer(
            data=request,
            company_id=current_user.company_id,
        )

    except DuplicateCustomerPhoneError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except DuplicateCustomerEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ==========================================================
# LIST CUSTOMERS
# ==========================================================

@router.get(
    "",
    response_model=CustomerListResponse,
)
def list_customers(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    """
    Return paginated customers belonging to the
    authenticated company.
    """

    return service.list_customers(
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
    )


# ==========================================================
# GET CUSTOMER
# ==========================================================

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def get_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    """
    Get a single customer belonging to the authenticated company.
    """

    try:
        return service.get_customer(
            customer_id=customer_id,
            company_id=current_user.company_id,
        )

    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# UPDATE CUSTOMER
# ==========================================================

@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def update_customer(
    customer_id: int,
    request: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    """
    Update a customer belonging to the authenticated company.
    """

    try:
        return service.update_customer(
            customer_id=customer_id,
            company_id=current_user.company_id,
            data=request,
        )

    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except DuplicateCustomerPhoneError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except DuplicateCustomerEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ==========================================================
# DEACTIVATE CUSTOMER
# ==========================================================

@router.patch(
    "/{customer_id}/deactivate",
    response_model=CustomerResponse,
)
def deactivate_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    """
    Deactivate a customer instead of permanently
    deleting the database record.
    """

    try:
        return service.deactivate_customer(
            customer_id=customer_id,
            company_id=current_user.company_id,
        )

    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# ACTIVATE CUSTOMER
# ==========================================================

@router.patch(
    "/{customer_id}/activate",
    response_model=CustomerResponse,
)
def activate_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    """
    Reactivate a previously deactivated customer.
    """

    try:
        return service.activate_customer(
            customer_id=customer_id,
            company_id=current_user.company_id,
        )

    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )