from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.customer import Customer


class CustomerRepository:
    """
    Repository responsible for Customer database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================
    # CREATE
    # ==========================================================

    def create(
        self,
        customer: Customer,
    ) -> Customer:
        """
        Create a new customer.

        The database remains the final protection against
        duplicate company + phone/email combinations.
        """

        try:
            self.db.add(customer)
            self.db.commit()
            self.db.refresh(customer)

            return customer

        except IntegrityError:
            self.db.rollback()
            raise

    # ==========================================================
    # GET BY ID
    # ==========================================================

    def get_by_id(
        self,
        customer_id: int,
        company_id: int,
    ) -> Customer | None:
        """
        Get a customer by ID within a specific company.

        Company scoping prevents one ISP from accessing
        another ISP's customers.
        """

        return (
            self.db.query(Customer)
            .filter(
                Customer.id == customer_id,
                Customer.company_id == company_id,
            )
            .first()
        )

    # ==========================================================
    # GET BY PHONE
    # ==========================================================

    def get_by_phone(
        self,
        phone: str,
        company_id: int,
    ) -> Customer | None:
        """
        Get a customer by phone number within a company.
        """

        return (
            self.db.query(Customer)
            .filter(
                Customer.phone == phone,
                Customer.company_id == company_id,
            )
            .first()
        )

    # ==========================================================
    # GET BY EMAIL
    # ==========================================================

    def get_by_email(
        self,
        email: str,
        company_id: int,
    ) -> Customer | None:
        """
        Get a customer by email within a company.
        """

        return (
            self.db.query(Customer)
            .filter(
                Customer.email == email,
                Customer.company_id == company_id,
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
    ) -> list[Customer]:
        """
        Return customers belonging to a company.

        Pagination is handled using skip and limit.
        """

        return (
            self.db.query(Customer)
            .filter(
                Customer.company_id == company_id,
            )
            .order_by(
                Customer.id.desc(),
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
        Count customers belonging to a company.
        """

        return (
            self.db.query(Customer)
            .filter(
                Customer.company_id == company_id,
            )
            .count()
        )

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        customer: Customer,
    ) -> Customer:
        """
        Save changes to an existing customer.
        """

        try:
            self.db.commit()
            self.db.refresh(customer)

            return customer

        except IntegrityError:
            self.db.rollback()
            raise

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(
        self,
        customer: Customer,
    ) -> None:
        """
        Permanently delete a customer.

        Prefer soft deletion through is_active=False
        for normal business operations.
        """

        try:
            self.db.delete(customer)
            self.db.commit()

        except IntegrityError:
            self.db.rollback()
            raise