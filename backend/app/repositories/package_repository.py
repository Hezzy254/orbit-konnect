from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.package import Package


class PackageRepository:
    """
    Repository responsible for Package database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================
    # CREATE
    # ==========================================================

    def create(
        self,
        package: Package,
    ) -> Package:
        """
        Create a new package.

        The database remains the final protection against
        duplicate company + package-name combinations.
        """

        try:
            self.db.add(package)
            self.db.commit()
            self.db.refresh(package)

            return package

        except IntegrityError:
            self.db.rollback()
            raise

    # ==========================================================
    # GET BY ID
    # ==========================================================

    def get_by_id(
        self,
        package_id: int,
        company_id: int,
    ) -> Package | None:
        """
        Get a package by ID within a specific company.

        Company scoping prevents one ISP from accessing
        another ISP's packages.
        """

        return (
            self.db.query(Package)
            .filter(
                Package.id == package_id,
                Package.company_id == company_id,
            )
            .first()
        )

    # ==========================================================
    # GET BY NAME
    # ==========================================================

    def get_by_name(
        self,
        name: str,
        company_id: int,
    ) -> Package | None:
        """
        Get a package by name within a specific company.
        """

        return (
            self.db.query(Package)
            .filter(
                Package.name == name,
                Package.company_id == company_id,
            )
            .first()
        )

    # ==========================================================
    # LIST BY COMPANY
    # ==========================================================

    def list_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Package]:
        """
        Return packages belonging to a company.

        Pagination is handled using skip and limit.
        """

        return (
            self.db.query(Package)
            .filter(
                Package.company_id == company_id,
            )
            .order_by(
                Package.id.desc(),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ==========================================================
    # COUNT BY COMPANY
    # ==========================================================

    def count_by_company(
        self,
        company_id: int,
    ) -> int:
        """
        Count packages belonging to a company.
        """

        return (
            self.db.query(Package)
            .filter(
                Package.company_id == company_id,
            )
            .count()
        )

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        package: Package,
    ) -> Package:
        """
        Save changes to an existing package.
        """

        try:
            self.db.commit()
            self.db.refresh(package)

            return package

        except IntegrityError:
            self.db.rollback()
            raise

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(
        self,
        package: Package,
    ) -> None:
        """
        Permanently delete a package.

        Prefer soft deletion through is_active=False
        for normal business operations.
        """

        try:
            self.db.delete(package)
            self.db.commit()

        except IntegrityError:
            self.db.rollback()
            raise