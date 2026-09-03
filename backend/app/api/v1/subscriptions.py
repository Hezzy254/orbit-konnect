from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.exceptions.subscription import (
    CrossCompanySubscriptionError,
    CustomerNotFoundForSubscriptionError,
    InactiveCustomerError,
    InactivePackageError,
    InvalidSubscriptionStatusError,
    PackageNotFoundForSubscriptionError,
    SubscriptionNotFoundError,
)
from backend.app.models.subscription import SubscriptionStatus
from backend.app.models.user import User
from backend.app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionListResponse,
    SubscriptionResponse,
)
from backend.app.services.subscription_service import SubscriptionService


router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
)


# ==========================================================
# SERVICE DEPENDENCY
# ==========================================================

def get_subscription_service(
    db: Session = Depends(get_db),
) -> SubscriptionService:
    """
    Create the SubscriptionService dependency.
    """

    return SubscriptionService(db)


# ==========================================================
# CREATE SUBSCRIPTION
# ==========================================================

@router.post(
    "",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subscription(
    request: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Create a new PENDING subscription for the authenticated company.
    """

    try:
        return service.create_subscription(
            company_id=current_user.company_id,
            customer_id=request.customer_id,
            package_id=request.package_id,
            auto_renew=request.auto_renew,
        )

    except CustomerNotFoundForSubscriptionError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except PackageNotFoundForSubscriptionError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InactiveCustomerError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except InactivePackageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except CrossCompanySubscriptionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ==========================================================
# LIST SUBSCRIPTIONS
# ==========================================================

@router.get(
    "",
    response_model=SubscriptionListResponse,
)
def list_subscriptions(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    status_filter: SubscriptionStatus | None = Query(
        default=None,
        alias="status",
    ),
    customer_id: int | None = Query(
        default=None,
        gt=0,
    ),
    package_id: int | None = Query(
        default=None,
        gt=0,
    ),
    current_user: User = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Return paginated subscriptions belonging to the
    authenticated company.
    """

    items, total = service.list_subscriptions(
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        status=status_filter,
        customer_id=customer_id,
        package_id=package_id,
    )

    return SubscriptionListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


# ==========================================================
# GET SUBSCRIPTION
# ==========================================================

@router.get(
    "/{subscription_id}",
    response_model=SubscriptionResponse,
)
def get_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Get a single subscription belonging to the authenticated company.
    """

    try:
        return service.get_subscription(
            company_id=current_user.company_id,
            subscription_id=subscription_id,
        )

    except SubscriptionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# ACTIVATE SUBSCRIPTION
# ==========================================================

@router.patch(
    "/{subscription_id}/activate",
    response_model=SubscriptionResponse,
)
def activate_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Activate a PENDING or SUSPENDED subscription.
    """

    try:
        return service.activate_subscription(
            company_id=current_user.company_id,
            subscription_id=subscription_id,
        )

    except SubscriptionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InvalidSubscriptionStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# ==========================================================
# SUSPEND SUBSCRIPTION
# ==========================================================

@router.patch(
    "/{subscription_id}/suspend",
    response_model=SubscriptionResponse,
)
def suspend_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Suspend an ACTIVE subscription.
    """

    try:
        return service.suspend_subscription(
            company_id=current_user.company_id,
            subscription_id=subscription_id,
        )

    except SubscriptionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InvalidSubscriptionStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# ==========================================================
# CANCEL SUBSCRIPTION
# ==========================================================

@router.patch(
    "/{subscription_id}/cancel",
    response_model=SubscriptionResponse,
)
def cancel_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Permanently cancel a PENDING, ACTIVE, or SUSPENDED subscription.
    """

    try:
        return service.cancel_subscription(
            company_id=current_user.company_id,
            subscription_id=subscription_id,
        )

    except SubscriptionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InvalidSubscriptionStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )