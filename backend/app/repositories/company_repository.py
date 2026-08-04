from sqlalchemy.orm import Session

from backend.app.models.company import Company


class CompanyRepository:
    """
    Repository responsible for all Company database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, company: Company) -> Company:
        """
        Create a new company.
        """
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def get_by_id(self, company_id: int) -> Company | None:
        """
        Get company by ID.
        """
        return (
            self.db.query(Company)
            .filter(Company.id == company_id)
            .first()
        )

    def get_by_email(self, email: str) -> Company | None:
        """
        Get company by email.
        """
        return (
            self.db.query(Company)
            .filter(Company.email == email)
            .first()
        )

    def update(self, company: Company) -> Company:
        """
        Save changes to an existing company.
        """
        self.db.commit()
        self.db.refresh(company)
        return company

    def delete(self, company: Company) -> None:
        """
        Delete a company.
        """
        self.db.delete(company)
        self.db.commit()