from sqlalchemy.orm import Session

from backend.app.models.company import Company


class CompanyRepository:
    """
    Repository responsible for all Company database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, company_id: int) -> Company | None:
        return (
            self.db.query(Company)
            .filter(Company.id == company_id)
            .first()
        )

    def get_by_email(self, email: str) -> Company | None:
        return (
            self.db.query(Company)
            .filter(Company.email == email)
            .first()
        )

    def get_by_name(self, name: str) -> Company | None:
        return (
            self.db.query(Company)
            .filter(Company.name == name)
            .first()
        )

    def create(self, company: Company) -> Company:
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def update(self, company: Company) -> Company:
        self.db.commit()
        self.db.refresh(company)
        return company

    def delete(self, company: Company) -> None:
        self.db.delete(company)
        self.db.commit()