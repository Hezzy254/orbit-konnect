from calendar import monthrange
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from backend.app.exceptions.subscription import (
    CrossCompanySubscriptionError,
    CustomerNotFoundForSubscriptionError,
    InactiveCustomerError,
    InactivePackageError,
    InvalidSubscriptionStatusError,
    PackageNotFoundForSubscriptionError,
    SubscriptionNotFoundError,
)
from backend.app.models.customer import Customer
from backend.app.models.package import Package
from backend.app.models.subscription import (
    Subscription,
    SubscriptionStatus,
)
from backend.app.repositories.subscription_repository import (
    SubscriptionRepository,
)


class SubscriptionService:
    """
    Business logic for customer subscriptions.

    Responsibilities:
    - Validate customer/package ownership and activity.
    - Create subscriptions from active packages.
    - Snapshot package commercial/network terms.
    - Manage subscription lifecycle transitions.
    - Calculate subscription expiry dates.
    - Enforce company/tenant isolation.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = SubscriptionRepository(db)

    # ------------------------------------------------------------------
    # Time helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _now() -> datetime:
        """
        Return the current UTC time.

        Application-level timestamps are always generated in UTC.
        """
        return datetime.now(UTC)

    @staticmethod
    def _normalize_utc(value: datetime) -> datetime:
        """
        Normalize a datetime to UTC-aware form.

        SQLite may return SQLAlchemy DateTime values without timezone
        information even when the application originally stored UTC.

        Naive values are therefore interpreted as UTC.
        Timezone-aware values are converted to UTC.
        """
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)

        return value.astimezone(UTC)

    @staticmethod
    def _add_months(
        start_at: datetime,
        months: int,
    ) -> datetime:
        """
        Add calendar months while preserving the closest valid day.

        Example:
            January 31 + 1 month
            -> February 28/29

        This is preferable to treating a month as a fixed number
        of days because ISP packages may use calendar-month semantics.
        """
        total_months = (
            start_at.year * 12
            + (start_at.month - 1)
            + months
        )

        target_year = total_months // 12
        target_month = total_months % 12 + 1

        last_day = monthrange(
            target_year,
            target_month,
        )[1]

        target_day = min(
            start_at.day,
            last_day,
        )

        return start_at.replace(
            year=target_year,
            month=target_month,
            day=target_day,
        )

    @classmethod
    def _calculate_end_at(
        cls,
        start_at: datetime,
        duration_value: int,
        duration_unit: str,
    ) -> datetime:
        """
        Calculate subscription expiry from its snapshot duration.

        Supported units:
            MINUTE
            HOUR
            DAY
            WEEK
            MONTH
        """

        if duration_unit == "MINUTE":
            return start_at + timedelta(
                minutes=duration_value
            )

        if duration_unit == "HOUR":
            return start_at + timedelta(
                hours=duration_value
            )

        if duration_unit == "DAY":
            return start_at + timedelta(
                days=duration_value
            )

        if duration_unit == "WEEK":
            return start_at + timedelta(
                weeks=duration_value
            )

        if duration_unit == "MONTH":
            return cls._add_months(
                start_at=start_at,
                months=duration_value,
            )

        raise ValueError(
            f"Unsupported subscription duration unit: "
            f"{duration_unit}"
        )

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _get_customer(
        self,
        company_id: int,
        customer_id: int,
    ) -> Customer:
        """
        Retrieve a customer belonging to the authenticated company.
        """

        customer = (
            self.db.query(Customer)
            .filter(
                Customer.id == customer_id,
                Customer.company_id == company_id,
            )
            .first()
        )

        if customer is None:
            raise CustomerNotFoundForSubscriptionError(
                "Customer not found."
            )

        if not customer.is_active:
            raise InactiveCustomerError(
                "Cannot create a subscription for an inactive customer."
            )

        return customer

    def _get_package(
        self,
        company_id: int,
        package_id: int,
    ) -> Package:
        """
        Retrieve a package belonging to the authenticated company.
        """

        package = (
            self.db.query(Package)
            .filter(
                Package.id == package_id,
                Package.company_id == company_id,
            )
            .first()
        )

        if package is None:
            raise PackageNotFoundForSubscriptionError(
                "Package not found."
            )

        if not package.is_active:
            raise InactivePackageError(
                "Cannot create a subscription using an inactive package."
            )

        return package

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_subscription(
        self,
        company_id: int,
        customer_id: int,
        package_id: int,
        auto_renew: bool = False,
    ) -> Subscription:
        """
        Create a new PENDING subscription.

        The package's commercial and network terms are copied into
        the subscription as a historical snapshot.

        Activation is intentionally separate from creation.
        """

        customer = self._get_customer(
            company_id=company_id,
            customer_id=customer_id,
        )

        package = self._get_package(
            company_id=company_id,
            package_id=package_id,
        )

        # Defensive tenant consistency check.
        if (
            customer.company_id != company_id
            or package.company_id != company_id
        ):
            raise CrossCompanySubscriptionError(
                "Customer and package must belong to the authenticated company."
            )

        subscription = Subscription(
            company_id=company_id,
            customer_id=customer.id,
            package_id=package.id,
            status=SubscriptionStatus.PENDING,
            package_name=package.name,
            download_speed_mbps=package.download_speed_mbps,
            upload_speed_mbps=package.upload_speed_mbps,
            duration_value=package.duration_value,
            duration_unit=package.duration_unit,
            price=package.price,
            auto_renew=auto_renew,
            start_at=None,
            end_at=None,
        )

        return self.repository.create(subscription)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_subscription(
        self,
        company_id: int,
        subscription_id: int,
    ) -> Subscription:
        """
        Retrieve a subscription within the authenticated company.
        """

        subscription = self.repository.get_by_id(
            company_id=company_id,
            subscription_id=subscription_id,
        )

        if subscription is None:
            raise SubscriptionNotFoundError(
                "Subscription not found."
            )

        return subscription

    def list_subscriptions(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 50,
        status: SubscriptionStatus | None = None,
        customer_id: int | None = None,
        package_id: int | None = None,
    ) -> tuple[list[Subscription], int]:
        """
        List subscriptions belonging to the authenticated company.
        """

        items = self.repository.list_by_company(
            company_id=company_id,
            skip=skip,
            limit=limit,
            status=status,
            customer_id=customer_id,
            package_id=package_id,
        )

        total = self.repository.count_by_company(
            company_id=company_id,
            status=status,
            customer_id=customer_id,
            package_id=package_id,
        )

        return items, total

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def activate_subscription(
        self,
        company_id: int,
        subscription_id: int,
    ) -> Subscription:
        """
        Activate a PENDING or SUSPENDED subscription.

        PENDING:
            start_at and end_at are calculated from the snapshot.

        SUSPENDED:
            Existing service dates are preserved.

        A suspended subscription whose original end date has passed
        cannot be reactivated.
        """

        subscription = self.get_subscription(
            company_id=company_id,
            subscription_id=subscription_id,
        )

        now = self._now()

        if subscription.status == SubscriptionStatus.PENDING:
            subscription.start_at = now

            subscription.end_at = self._calculate_end_at(
                start_at=now,
                duration_value=subscription.duration_value,
                duration_unit=subscription.duration_unit.value,
            )

            subscription.status = SubscriptionStatus.ACTIVE

        elif subscription.status == SubscriptionStatus.SUSPENDED:
            if subscription.end_at is not None:
                end_at = self._normalize_utc(
                    subscription.end_at
                )

                if end_at <= now:
                    subscription.status = SubscriptionStatus.EXPIRED

                    self.repository.update(subscription)

                    raise InvalidSubscriptionStatusError(
                        "Subscription has already expired "
                        "and cannot be activated."
                    )

            subscription.status = SubscriptionStatus.ACTIVE

        else:
            raise InvalidSubscriptionStatusError(
                f"Subscription cannot be activated from "
                f"{subscription.status.value} status."
            )

        return self.repository.update(subscription)

    def suspend_subscription(
        self,
        company_id: int,
        subscription_id: int,
    ) -> Subscription:
        """
        Suspend an ACTIVE subscription.
        """

        subscription = self.get_subscription(
            company_id=company_id,
            subscription_id=subscription_id,
        )

        if subscription.status != SubscriptionStatus.ACTIVE:
            raise InvalidSubscriptionStatusError(
                f"Subscription cannot be suspended from "
                f"{subscription.status.value} status."
            )

        subscription.status = SubscriptionStatus.SUSPENDED

        return self.repository.update(subscription)

    def cancel_subscription(
        self,
        company_id: int,
        subscription_id: int,
    ) -> Subscription:
        """
        Cancel a PENDING, ACTIVE, or SUSPENDED subscription.

        EXPIRED and CANCELLED subscriptions cannot be cancelled again.
        """

        subscription = self.get_subscription(
            company_id=company_id,
            subscription_id=subscription_id,
        )

        allowed_statuses = {
            SubscriptionStatus.PENDING,
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.SUSPENDED,
        }

        if subscription.status not in allowed_statuses:
            raise InvalidSubscriptionStatusError(
                f"Subscription cannot be cancelled from "
                f"{subscription.status.value} status."
            )

        subscription.status = SubscriptionStatus.CANCELLED

        return self.repository.update(subscription)