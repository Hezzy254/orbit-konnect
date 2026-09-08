from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.exceptions.network_device import (
    DuplicateNetworkDeviceError,
    NetworkDeviceNotFoundError,
)
from backend.app.models.network_device import (
    NetworkDeviceStatus,
    NetworkDeviceType,
    NetworkDeviceVendor,
)
from backend.app.models.user import User
from backend.app.schemas.network_device import (
    NetworkDeviceCreate,
    NetworkDeviceListResponse,
    NetworkDeviceResponse,
    NetworkDeviceUpdate,
)
from backend.app.services.network_device_service import NetworkDeviceService


router = APIRouter(
    prefix="/network-devices",
    tags=["Network Devices"],
)


# ==========================================================
# SERVICE DEPENDENCY
# ==========================================================

def get_network_device_service(
    db: Session = Depends(get_db),
) -> NetworkDeviceService:
    """
    Create the NetworkDeviceService dependency.
    """
    return NetworkDeviceService(db)


# ==========================================================
# CREATE NETWORK DEVICE
# ==========================================================

@router.post(
    "",
    response_model=NetworkDeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_network_device(
    request: NetworkDeviceCreate,
    current_user: User = Depends(get_current_user),
    service: NetworkDeviceService = Depends(get_network_device_service),
):
    """
    Register a new network device for the authenticated company.
    """

    try:
        return service.create_device(
            data=request,
            company_id=current_user.company_id,
        )

    except DuplicateNetworkDeviceError as exc:
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
# LIST NETWORK DEVICES
# ==========================================================

@router.get(
    "",
    response_model=NetworkDeviceListResponse,
)
def list_network_devices(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    vendor: NetworkDeviceVendor | None = Query(default=None),
    device_type: NetworkDeviceType | None = Query(default=None),
    status_filter: NetworkDeviceStatus | None = Query(
        default=None,
        alias="status",
    ),
    is_active: bool | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    service: NetworkDeviceService = Depends(get_network_device_service),
):
    """
    Return paginated network devices belonging to the
    authenticated company.
    """

    return service.list_devices(
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        vendor=vendor,
        device_type=device_type,
        status=status_filter,
        is_active=is_active,
    )


# ==========================================================
# GET NETWORK DEVICE
# ==========================================================

@router.get(
    "/{device_id}",
    response_model=NetworkDeviceResponse,
)
def get_network_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    service: NetworkDeviceService = Depends(get_network_device_service),
):
    """
    Get a single network device belonging to the authenticated company.
    """

    try:
        return service.get_device(
            device_id=device_id,
            company_id=current_user.company_id,
        )

    except NetworkDeviceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# UPDATE NETWORK DEVICE
# ==========================================================

@router.put(
    "/{device_id}",
    response_model=NetworkDeviceResponse,
)
def update_network_device(
    device_id: int,
    request: NetworkDeviceUpdate,
    current_user: User = Depends(get_current_user),
    service: NetworkDeviceService = Depends(get_network_device_service),
):
    """
    Update a network device belonging to the authenticated company.
    """

    try:
        return service.update_device(
            device_id=device_id,
            company_id=current_user.company_id,
            data=request,
        )

    except NetworkDeviceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except DuplicateNetworkDeviceError as exc:
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
# DEACTIVATE NETWORK DEVICE
# ==========================================================

@router.patch(
    "/{device_id}/deactivate",
    response_model=NetworkDeviceResponse,
)
def deactivate_network_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    service: NetworkDeviceService = Depends(get_network_device_service),
):
    """
    Disable a network device without deleting its record.
    """

    try:
        return service.deactivate_device(
            device_id=device_id,
            company_id=current_user.company_id,
        )

    except NetworkDeviceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# ACTIVATE NETWORK DEVICE
# ==========================================================

@router.patch(
    "/{device_id}/activate",
    response_model=NetworkDeviceResponse,
)
def activate_network_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    service: NetworkDeviceService = Depends(get_network_device_service),
):
    """
    Activate a previously deactivated network device.
    """

    try:
        return service.activate_device(
            device_id=device_id,
            company_id=current_user.company_id,
        )

    except NetworkDeviceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
