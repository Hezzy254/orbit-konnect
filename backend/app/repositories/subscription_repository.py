from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.subscription import Subscription, SubscriptionStatus


class SubscriptionRepository:
    """
    Handles database operations for subscriptions.

    Business rules belong in the service layer.
    This repository is responsible only for database access.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        subscription: Subscription,
    ) -> Subscription:
        """
        Create a new subscription.
        """

        self.db.add(subscription)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise

        self.db.refresh(subscription)

        return subscription

    def get_by_id(
        self,
        company_id: int,
        subscription_id: int,
    ) -> Subscription | None:
        """
        Retrieve a subscription belonging to a specific company.
        """

        return (
            self.db.query(Subscription)
            .filter(
                Subscription.id == subscription_id,
                Subscription.company_id == company_id,
            )
            .first()
        )

    def list_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        status: SubscriptionStatus | None = None,
        customer_id: int | None = None,
        package_id: int | None = None,
    ) -> list[Subscription]:
        """
        Return subscriptions belonging to a company.

        Optional filters allow the API to retrieve subscriptions
        by status, customer, or package.
        """

        query = self.db.query(Subscription).filter(
            Subscription.company_id == company_id,
        )

        if status is not None:
            query = query.filter(
                Subscription.status == status,
            )

        if customer_id is not None:
            query = query.filter(
                Subscription.customer_id == customer_id,
            )

        if package_id is not None:
            query = query.filter(
                Subscription.package_id == package_id,
            )

        return (
            query.order_by(Subscription.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_company(
        self,
        company_id: int,
        status: SubscriptionStatus | None = None,
        customer_id: int | None = None,
        package_id: int | None = None,
    ) -> int:
        """
        Count subscriptions belonging to a company.
        """

        query = self.db.query(Subscription).filter(
            Subscription.company_id == company_id,
        )

        if status is not None:
            query = query.filter(
                Subscription.status == status,
            )

        if customer_id is not None:
            query = query.filter(
                Subscription.customer_id == customer_id,
            )

        if package_id is not None:
            query = query.filter(
                Subscription.package_id == package_id,
            )

        return query.count()

    def update(
        self,
        subscription: Subscription,
    ) -> Subscription:
        """
        Persist changes to an existing subscription.
        """

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise

        self.db.refresh(subscription)

        return subscription