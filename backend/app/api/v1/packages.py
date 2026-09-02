from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.exceptions.package import (
    DuplicatePackageNameError,
    PackageNotFoundError,
)
from backend.app.models.user import User
from backend.app.repositories.package_repository import PackageRepository
from backend.app.schemas.package import (
    PackageCreate,
    PackageListResponse,
    PackageResponse,
    PackageUpdate,
)
from backend.app.services.package_service import PackageService


router = APIRouter(
    prefix="/packages",
    tags=["Packages"],
)


# ==========================================================
# SERVICE DEPENDENCY
# ==========================================================

def get_package_service(
    db: Session = Depends(get_db),
) -> PackageService:
    """
    Create the PackageService dependency.
    """

    repository = PackageRepository(db)

    return PackageService(repository)


# ==========================================================
# CREATE PACKAGE
# ==========================================================

@router.post(
    "",
    response_model=PackageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_package(
    request: PackageCreate,
    current_user: User = Depends(get_current_user),
    service: PackageService = Depends(get_package_service),
):
    """
    Create a new package for the authenticated company.
    """

    try:
        return service.create_package(
            data=request,
            company_id=current_user.company_id,
        )

    except DuplicatePackageNameError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# ==========================================================
# LIST PACKAGES
# ==========================================================

@router.get(
    "",
    response_model=PackageListResponse,
)
def list_packages(
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
    service: PackageService = Depends(get_package_service),
):
    """
    Return paginated packages belonging to the
    authenticated company.
    """

    return service.list_packages(
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
    )


# ==========================================================
# GET PACKAGE
# ==========================================================

@router.get(
    "/{package_id}",
    response_model=PackageResponse,
)
def get_package(
    package_id: int,
    current_user: User = Depends(get_current_user),
    service: PackageService = Depends(get_package_service),
):
    """
    Get a single package belonging to the authenticated company.
    """

    try:
        return service.get_package(
            package_id=package_id,
            company_id=current_user.company_id,
        )

    except PackageNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# UPDATE PACKAGE
# ==========================================================

@router.put(
    "/{package_id}",
    response_model=PackageResponse,
)
def update_package(
    package_id: int,
    request: PackageUpdate,
    current_user: User = Depends(get_current_user),
    service: PackageService = Depends(get_package_service),
):
    """
    Update a package belonging to the authenticated company.
    """

    try:
        return service.update_package(
            package_id=package_id,
            company_id=current_user.company_id,
            data=request,
        )

    except PackageNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except DuplicatePackageNameError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# ==========================================================
# DEACTIVATE PACKAGE
# ==========================================================

@router.patch(
    "/{package_id}/deactivate",
    response_model=PackageResponse,
)
def deactivate_package(
    package_id: int,
    current_user: User = Depends(get_current_user),
    service: PackageService = Depends(get_package_service),
):
    """
    Deactivate a package instead of permanently deleting it.
    """

    try:
        return service.deactivate_package(
            package_id=package_id,
            company_id=current_user.company_id,
        )

    except PackageNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# ACTIVATE PACKAGE
# ==========================================================

@router.patch(
    "/{package_id}/activate",
    response_model=PackageResponse,
)
def activate_package(
    package_id: int,
    current_user: User = Depends(get_current_user),
    service: PackageService = Depends(get_package_service),
):
    """
    Reactivate a previously deactivated package.
    """

    try:
        return service.activate_package(
            package_id=package_id,
            company_id=current_user.company_id,
        )

    except PackageNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )