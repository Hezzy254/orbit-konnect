from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.exceptions.payment import (
    CrossCompanyPaymentError,
    CustomerNotFoundForPaymentError,
    DuplicatePaymentReferenceError,
    InvalidPaymentStatusError,
    PaymentCustomerMismatchError,
    PaymentNotFoundError,
    SubscriptionNotFoundForPaymentError,
)
from backend.app.models.payment import PaymentStatus
from backend.app.models.user import User
from backend.app.schemas.payment import (
    PaymentCreate,
    PaymentListResponse,
    PaymentResponse,
)
from backend.app.services.payment_service import PaymentService


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


# ==========================================================
# SERVICE DEPENDENCY
# ==========================================================

def get_payment_service(
    db: Session = Depends(get_db),
) -> PaymentService:
    """
    Create the PaymentService dependency.
    """

    return PaymentService(db)


# ==========================================================
# CREATE PAYMENT
# ==========================================================

@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    request: PaymentCreate,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    """
    Create a new PENDING payment for a subscription.
    """

    try:
        return service.create_payment(
            company_id=current_user.company_id,
            subscription_id=request.subscription_id,
            amount=request.amount,
            payment_method=request.payment_method,
            provider=request.provider,
            currency="OMR",
        )

    except SubscriptionNotFoundForPaymentError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except CustomerNotFoundForPaymentError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InvalidPaymentStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except PaymentCustomerMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except CrossCompanyPaymentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except DuplicatePaymentReferenceError as exc:
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
# LIST PAYMENTS
# ==========================================================

@router.get(
    "",
    response_model=PaymentListResponse,
)
def list_payments(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    status_filter: PaymentStatus | None = Query(
        default=None,
        alias="status",
    ),
    customer_id: int | None = Query(
        default=None,
        gt=0,
    ),
    subscription_id: int | None = Query(
        default=None,
        gt=0,
    ),
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    """
    Return paginated payments belonging to the
    authenticated company.
    """

    items, total = service.list_payments(
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        status=status_filter,
        customer_id=customer_id,
        subscription_id=subscription_id,
    )

    return PaymentListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


# ==========================================================
# GET PAYMENT
# ==========================================================

@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    """
    Get a single payment belonging to the authenticated company.
    """

    try:
        return service.get_payment(
            company_id=current_user.company_id,
            payment_id=payment_id,
        )

    except PaymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# MARK PAYMENT SUCCESS
# ==========================================================

@router.patch(
    "/{payment_id}/success",
    response_model=PaymentResponse,
)
def mark_payment_success(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    """
    Mark a PENDING payment as successful.

    Subscription activation and network provisioning are
    intentionally handled separately.
    """

    try:
        return service.mark_payment_success(
            company_id=current_user.company_id,
            payment_id=payment_id,
        )

    except PaymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InvalidPaymentStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except DuplicatePaymentReferenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# ==========================================================
# MARK PAYMENT FAILED
# ==========================================================

@router.patch(
    "/{payment_id}/failed",
    response_model=PaymentResponse,
)
def mark_payment_failed(
    payment_id: int,
    failure_reason: str = Query(
        ...,
        min_length=1,
        max_length=255,
    ),
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    """
    Mark a PENDING payment as failed.
    """

    try:
        return service.mark_payment_failed(
            company_id=current_user.company_id,
            payment_id=payment_id,
            failure_reason=failure_reason,
        )

    except PaymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InvalidPaymentStatusError as exc:
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
# CANCEL PAYMENT
# ==========================================================

@router.patch(
    "/{payment_id}/cancel",
    response_model=PaymentResponse,
)
def cancel_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    """
    Cancel a PENDING payment.
    """

    try:
        return service.cancel_payment(
            company_id=current_user.company_id,
            payment_id=payment_id,
        )

    except PaymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InvalidPaymentStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )