from backend.app.models.company import Company
from backend.app.repositories.company_repository import CompanyRepository
from backend.app.schemas.company import CompanyUpdateRequest


class CompanyService:
    """
    Business logic for company management.
    """

    def __init__(self, repository: CompanyRepository):
        self.repository = repository

    def get_company(self, company_id: int) -> Company | None:
        """
        Return a company by its ID.
        """
        return self.repository.get_by_id(company_id)

    def update_company(
        self,
        company: Company,
        request: CompanyUpdateRequest,
    ) -> Company:
        """
        Update a company's profile.
        """

        company.name = request.name
        company.phone = request.phone
        company.address = request.address
        company.country = request.country
        company.currency = request.currency
        company.timezone = request.timezone

        return self.repository.update(company)