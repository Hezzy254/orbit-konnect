from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.payment import Payment, PaymentStatus


class PaymentRepository:
    """
    Handles database operations for payments.

    Business rules belong in the service layer.
    This repository is responsible only for database access.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        payment: Payment,
    ) -> Payment:
        """
        Create a new payment.
        """

        self.db.add(payment)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise

        self.db.refresh(payment)

        return payment

    def get_by_id(
        self,
        company_id: int,
        payment_id: int,
    ) -> Payment | None:
        """
        Retrieve a payment belonging to a specific company.
        """

        return (
            self.db.query(Payment)
            .filter(
                Payment.id == payment_id,
                Payment.company_id == company_id,
            )
            .first()
        )

    def list_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        status: PaymentStatus | None = None,
        customer_id: int | None = None,
        subscription_id: int | None = None,
    ) -> list[Payment]:
        """
        Return payments belonging to a company.

        Optional filters allow the API to retrieve payments
        by status, customer, or subscription.
        """

        query = self.db.query(Payment).filter(
            Payment.company_id == company_id,
        )

        if status is not None:
            query = query.filter(
                Payment.status == status,
            )

        if customer_id is not None:
            query = query.filter(
                Payment.customer_id == customer_id,
            )

        if subscription_id is not None:
            query = query.filter(
                Payment.subscription_id == subscription_id,
            )

        return (
            query.order_by(Payment.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_company(
        self,
        company_id: int,
        status: PaymentStatus | None = None,
        customer_id: int | None = None,
        subscription_id: int | None = None,
    ) -> int:
        """
        Count payments belonging to a company.
        """

        query = self.db.query(Payment).filter(
            Payment.company_id == company_id,
        )

        if status is not None:
            query = query.filter(
                Payment.status == status,
            )

        if customer_id is not None:
            query = query.filter(
                Payment.customer_id == customer_id,
            )

        if subscription_id is not None:
            query = query.filter(
                Payment.subscription_id == subscription_id,
            )

        return query.count()

    def update(
        self,
        payment: Payment,
    ) -> Payment:
        """
        Persist changes to an existing payment.
        """

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise

        self.db.refresh(payment)

        return payment
    