from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.models.user import User
from backend.app.repositories.company_repository import CompanyRepository
from backend.app.schemas.company import (
    CompanyResponse,
    CompanyUpdateRequest,
)
from backend.app.services.company_service import CompanyService

router = APIRouter(
    prefix="/company",
    tags=["Company"],
)


@router.get(
    "/me",
    response_model=CompanyResponse,
)
def get_company(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the authenticated user's company.
    """

    repository = CompanyRepository(db)
    service = CompanyService(repository)

    company = service.get_company(current_user.company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    return CompanyResponse.model_validate(company)


@router.put(
    "/me",
    response_model=CompanyResponse,
)
def update_company(
    request: CompanyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the authenticated user's company.
    """

    repository = CompanyRepository(db)
    service = CompanyService(repository)

    company = service.get_company(current_user.company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    company = service.update_company(
        company=company,
        request=request,
    )

    return CompanyResponse.model_validate(company)