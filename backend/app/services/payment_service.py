from datetime import UTC, datetime
from decimal import Decimal
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.exceptions.payment import (
    CrossCompanyPaymentError,
    CustomerNotFoundForPaymentError,
    DuplicatePaymentReferenceError,
    InvalidPaymentStatusError,
    PaymentCustomerMismatchError,
    PaymentNotFoundError,
    SubscriptionNotFoundForPaymentError,
)
from backend.app.models.customer import Customer
from backend.app.models.payment import (
    Payment,
    PaymentMethod,
    PaymentStatus,
)
from backend.app.models.subscription import (
    Subscription,
    SubscriptionStatus,
)
from backend.app.repositories.payment_repository import PaymentRepository


class PaymentService:
    """
    Business logic for subscription payments.

    Responsibilities:
    - Validate subscription ownership.
    - Validate customer ownership.
    - Enforce company/tenant isolation.
    - Validate payment data.
    - Create payment transaction records.
    - Generate Orbit Konnect transaction references.
    - Manage payment lifecycle transitions.

    Payment confirmation is intentionally kept separate from
    subscription activation and network provisioning.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = PaymentRepository(db)

    # ------------------------------------------------------------------
    # Time and reference helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _now() -> datetime:
        """
        Return the current UTC time.
        """

        return datetime.now(UTC)

    @staticmethod
    def _generate_transaction_reference() -> str:
        """
        Generate a unique Orbit Konnect transaction reference.

        Example:
            OK-PAY-8F4A1C2D9E
        """

        return f"OK-PAY-{uuid.uuid4().hex[:10].upper()}"

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _get_subscription(
        self,
        company_id: int,
        subscription_id: int,
    ) -> Subscription:
        """
        Retrieve a subscription belonging to the authenticated company.
        """

        subscription = (
            self.db.query(Subscription)
            .filter(
                Subscription.id == subscription_id,
                Subscription.company_id == company_id,
            )
            .first()
        )

        if subscription is None:
            raise SubscriptionNotFoundForPaymentError(
                "Subscription not found."
            )

        return subscription

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
            raise CustomerNotFoundForPaymentError(
                "Customer not found."
            )

        return customer

    @staticmethod
    def _validate_subscription_for_payment(
        subscription: Subscription,
    ) -> None:
        """
        Validate whether a subscription can receive a payment.

        New payment records are allowed for:
            PENDING
            ACTIVE
            SUSPENDED

        New payments are rejected for:
            EXPIRED
            CANCELLED
        """

        allowed_statuses = {
            SubscriptionStatus.PENDING,
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.SUSPENDED,
        }

        if subscription.status not in allowed_statuses:
            raise InvalidPaymentStatusError(
                "Payment cannot be created for a subscription "
                f"in {subscription.status.value} status."
            )

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        """
        Validate payment amount.
        """

        if amount <= Decimal("0"):
            raise ValueError(
                "Payment amount must be greater than zero."
            )

    @staticmethod
    def _validate_currency(currency: str) -> str:
        """
        Validate and normalize ISO-style three-letter currency code.
        """

        normalized = currency.strip().upper()

        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError(
                "Currency must be a valid three-letter currency code."
            )

        return normalized

    @staticmethod
    def _validate_provider(provider: str) -> str:
        """
        Validate and normalize payment provider.
        """

        normalized = provider.strip()

        if not normalized:
            raise ValueError(
                "Payment provider cannot be empty."
            )

        if len(normalized) > 50:
            raise ValueError(
                "Payment provider cannot exceed 50 characters."
            )

        return normalized

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_payment(
        self,
        company_id: int,
        subscription_id: int,
        amount: Decimal,
        payment_method: PaymentMethod,
        provider: str,
        currency: str,
    ) -> Payment:
        """
        Create a new PENDING payment.

        Customer identity is derived from the subscription instead
        of being independently supplied by the API client.

        This prevents a caller from attempting to create a payment
        for Customer A against Customer B's subscription.
        """

        self._validate_amount(amount)

        normalized_currency = self._validate_currency(
            currency
        )

        normalized_provider = self._validate_provider(
            provider
        )

        subscription = self._get_subscription(
            company_id=company_id,
            subscription_id=subscription_id,
        )

        self._validate_subscription_for_payment(
            subscription
        )

        customer = self._get_customer(
            company_id=company_id,
            customer_id=subscription.customer_id,
        )

        # Defensive tenant-isolation check.
        if subscription.company_id != company_id:
            raise CrossCompanyPaymentError(
                "Subscription does not belong to the "
                "authenticated company."
            )

        if customer.company_id != company_id:
            raise CrossCompanyPaymentError(
                "Customer does not belong to the "
                "authenticated company."
            )

        # Defensive relationship consistency check.
        if customer.id != subscription.customer_id:
            raise PaymentCustomerMismatchError(
                "Payment customer does not match the "
                "subscription customer."
            )

        transaction_reference = (
            self._generate_transaction_reference()
        )

        payment = Payment(
            company_id=company_id,
            customer_id=customer.id,
            subscription_id=subscription.id,
            amount=amount,
            currency=normalized_currency,
            payment_method=payment_method,
            provider=normalized_provider,
            status=PaymentStatus.PENDING,
            transaction_reference=transaction_reference,
            provider_reference=None,
            paid_at=None,
            failure_reason=None,
        )

        try:
            return self.repository.create(payment)

        except IntegrityError as exc:
            self.db.rollback()

            raise DuplicatePaymentReferenceError(
                "Payment transaction reference already exists."
            ) from exc

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_payment(
        self,
        company_id: int,
        payment_id: int,
    ) -> Payment:
        """
        Retrieve a payment within the authenticated company.
        """

        payment = self.repository.get_by_id(
            company_id=company_id,
            payment_id=payment_id,
        )

        if payment is None:
            raise PaymentNotFoundError(
                "Payment not found."
            )

        return payment

    def list_payments(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 50,
        status: PaymentStatus | None = None,
        customer_id: int | None = None,
        subscription_id: int | None = None,
    ) -> tuple[list[Payment], int]:
        """
        List payments belonging to the authenticated company.
        """

        items = self.repository.list_by_company(
            company_id=company_id,
            skip=skip,
            limit=limit,
            status=status,
            customer_id=customer_id,
            subscription_id=subscription_id,
        )

        total = self.repository.count_by_company(
            company_id=company_id,
            status=status,
            customer_id=customer_id,
            subscription_id=subscription_id,
        )

        return items, total

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def mark_payment_success(
        self,
        company_id: int,
        payment_id: int,
        provider_reference: str | None = None,
    ) -> Payment:
        """
        Mark a PENDING payment as successful.

        This method does NOT activate the subscription.

        Subscription activation and network provisioning will be
        handled by a separate orchestration layer.
        """

        payment = self.get_payment(
            company_id=company_id,
            payment_id=payment_id,
        )

        if payment.status != PaymentStatus.PENDING:
            raise InvalidPaymentStatusError(
                "Payment cannot be marked SUCCESS from "
                f"{payment.status.value} status."
            )

        normalized_provider_reference = None

        if provider_reference is not None:
            normalized_provider_reference = (
                provider_reference.strip()
            )

            if not normalized_provider_reference:
                raise ValueError(
                    "Provider reference cannot be empty."
                )

            if len(normalized_provider_reference) > 150:
                raise ValueError(
                    "Provider reference cannot exceed "
                    "150 characters."
                )

        payment.status = PaymentStatus.SUCCESS
        payment.paid_at = self._now()
        payment.failure_reason = None

        if normalized_provider_reference is not None:
            payment.provider_reference = (
                normalized_provider_reference
            )

        try:
            return self.repository.update(payment)

        except IntegrityError as exc:
            self.db.rollback()

            raise DuplicatePaymentReferenceError(
                "Provider reference already belongs to "
                "another payment."
            ) from exc

    def mark_payment_failed(
        self,
        company_id: int,
        payment_id: int,
        failure_reason: str,
    ) -> Payment:
        """
        Mark a PENDING payment as failed.
        """

        payment = self.get_payment(
            company_id=company_id,
            payment_id=payment_id,
        )

        if payment.status != PaymentStatus.PENDING:
            raise InvalidPaymentStatusError(
                "Payment cannot be marked FAILED from "
                f"{payment.status.value} status."
            )

        normalized_reason = failure_reason.strip()

        if not normalized_reason:
            raise ValueError(
                "Failure reason cannot be empty."
            )

        if len(normalized_reason) > 255:
            raise ValueError(
                "Failure reason cannot exceed "
                "255 characters."
            )

        payment.status = PaymentStatus.FAILED
        payment.paid_at = None
        payment.failure_reason = normalized_reason

        return self.repository.update(payment)

    def cancel_payment(
        self,
        company_id: int,
        payment_id: int,
    ) -> Payment:
        """
        Cancel a PENDING payment.

        SUCCESS and FAILED payments remain historical records
        and cannot be cancelled through this lifecycle operation.
        """

        payment = self.get_payment(
            company_id=company_id,
            payment_id=payment_id,
        )

        if payment.status != PaymentStatus.PENDING:
            raise InvalidPaymentStatusError(
                "Payment cannot be cancelled from "
                f"{payment.status.value} status."
            )

        payment.status = PaymentStatus.CANCELLED
        payment.paid_at = None

        return self.repository.update(payment)