from sqlalchemy.exc import IntegrityError

from backend.app.exceptions.customer import (
    CustomerNotFoundError,
    DuplicateCustomerEmailError,
    DuplicateCustomerPhoneError,
)
from backend.app.models.customer import Customer
from backend.app.repositories.customer_repository import CustomerRepository
from backend.app.schemas.customer import CustomerCreate, CustomerUpdate


CUSTOMER_PHONE_CONSTRAINT = "uq_customer_company_phone"
CUSTOMER_EMAIL_CONSTRAINT = "uq_customer_company_email"


class CustomerService:
    """
    Service layer responsible for Customer business logic.
    """

    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    # ==========================================================
    # NORMALIZATION HELPERS
    # ==========================================================

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """
        Normalize a phone number at the Customer service boundary.

        At this stage we intentionally only remove surrounding
        whitespace. International phone-number canonicalization
        such as E.164 will be introduced as a separate,
        deliberate policy later.
        """

        return phone.strip()

    @staticmethod
    def _normalize_email(email: str | None) -> str | None:
        """
        Normalize email addresses.

        Email comparison is performed case-insensitively by
        storing the normalized lowercase representation.
        """

        if email is None:
            return None

        normalized = str(email).strip().lower()

        return normalized or None

    @staticmethod
    def _normalize_optional_text(value: str | None) -> str | None:
        """
        Normalize optional text fields.

        Empty strings become None so the database does not
        receive meaningless whitespace-only values.
        """

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    @staticmethod
    def _raise_duplicate_from_integrity_error(
        exc: IntegrityError,
    ) -> None:
        """
        Convert a database uniqueness violation into the
        appropriate domain exception.

        PostgreSQL exposes the violated constraint through
        the database driver's diagnostic information.

        A message-based fallback is retained for SQLite
        development environments.
        """

        original_error = getattr(exc, "orig", None)

        # ------------------------------------------------------
        # PostgreSQL / drivers exposing constraint metadata
        # ------------------------------------------------------

        diagnostic = getattr(
            original_error,
            "diag",
            None,
        )

        constraint_name = getattr(
            diagnostic,
            "constraint_name",
            None,
        )

        if constraint_name == CUSTOMER_PHONE_CONSTRAINT:
            raise DuplicateCustomerPhoneError(
                "A customer with this phone number already exists."
            ) from exc

        if constraint_name == CUSTOMER_EMAIL_CONSTRAINT:
            raise DuplicateCustomerEmailError(
                "A customer with this email already exists."
            ) from exc

        # ------------------------------------------------------
        # SQLite development fallback
        # ------------------------------------------------------

        message = str(original_error or exc).lower()

        if (
            CUSTOMER_PHONE_CONSTRAINT.lower() in message
            or (
                "unique constraint failed" in message
                and "customers.company_id" in message
                and "customers.phone" in message
            )
        ):
            raise DuplicateCustomerPhoneError(
                "A customer with this phone number already exists."
            ) from exc

        if (
            CUSTOMER_EMAIL_CONSTRAINT.lower() in message
            or (
                "unique constraint failed" in message
                and "customers.company_id" in message
                and "customers.email" in message
            )
        ):
            raise DuplicateCustomerEmailError(
                "A customer with this email already exists."
            ) from exc

        # ------------------------------------------------------
        # Unknown integrity error
        # ------------------------------------------------------

        raise exc

    # ==========================================================
    # CREATE CUSTOMER
    # ==========================================================

    def create_customer(
        self,
        data: CustomerCreate,
        company_id: int,
    ) -> Customer:
        """
        Create a customer for the authenticated company.

        Duplicate checks provide fast and user-friendly
        validation.

        Database constraints remain the final protection
        against concurrent duplicate requests.
        """

        phone = self._normalize_phone(
            data.phone,
        )

        email = self._normalize_email(
            data.email,
        )

        address = self._normalize_optional_text(
            data.address,
        )

        national_id = self._normalize_optional_text(
            data.national_id,
        )

        full_name = data.full_name.strip()

        # ------------------------------------------------------
        # Duplicate phone check
        # ------------------------------------------------------

        existing_phone = self.repository.get_by_phone(
            phone=phone,
            company_id=company_id,
        )

        if existing_phone is not None:
            raise DuplicateCustomerPhoneError(
                "A customer with this phone number already exists."
            )

        # ------------------------------------------------------
        # Duplicate email check
        # ------------------------------------------------------

        if email is not None:
            existing_email = self.repository.get_by_email(
                email=email,
                company_id=company_id,
            )

            if existing_email is not None:
                raise DuplicateCustomerEmailError(
                    "A customer with this email already exists."
                )

        # ------------------------------------------------------
        # Create customer
        # ------------------------------------------------------

        customer = Customer(
            company_id=company_id,
            full_name=full_name,
            phone=phone,
            email=email,
            address=address,
            national_id=national_id,
            is_active=True,
        )

        # ------------------------------------------------------
        # Database-level protection
        # ------------------------------------------------------

        try:
            return self.repository.create(customer)

        except IntegrityError as exc:
            self._raise_duplicate_from_integrity_error(exc)

    # ==========================================================
    # GET CUSTOMER
    # ==========================================================

    def get_customer(
        self,
        customer_id: int,
        company_id: int,
    ) -> Customer:
        """
        Get a customer belonging to the authenticated company.
        """

        customer = self.repository.get_by_id(
            customer_id=customer_id,
            company_id=company_id,
        )

        if customer is None:
            raise CustomerNotFoundError(
                "Customer not found."
            )

        return customer

    # ==========================================================
    # LIST CUSTOMERS
    # ==========================================================

    def list_customers(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> dict:
        """
        Return paginated customers for a company.
        """

        customers = self.repository.list_by_company(
            company_id=company_id,
            skip=skip,
            limit=limit,
        )

        total = self.repository.count_by_company(
            company_id=company_id,
        )

        return {
            "items": customers,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    # ==========================================================
    # UPDATE CUSTOMER
    # ==========================================================

    def update_customer(
        self,
        customer_id: int,
        company_id: int,
        data: CustomerUpdate,
    ) -> Customer:
        """
        Update customer profile information.

        Customer activation state is intentionally handled
        separately through activate_customer() and
        deactivate_customer().
        """

        customer = self.get_customer(
            customer_id=customer_id,
            company_id=company_id,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        # ------------------------------------------------------
        # Normalize fields
        # ------------------------------------------------------

        if "full_name" in update_data:
            update_data["full_name"] = (
                update_data["full_name"].strip()
            )

        if "phone" in update_data:
            update_data["phone"] = (
                self._normalize_phone(
                    update_data["phone"],
                )
            )

        if "email" in update_data:
            update_data["email"] = (
                self._normalize_email(
                    update_data["email"],
                )
            )

        if "address" in update_data:
            update_data["address"] = (
                self._normalize_optional_text(
                    update_data["address"],
                )
            )

        if "national_id" in update_data:
            update_data["national_id"] = (
                self._normalize_optional_text(
                    update_data["national_id"],
                )
            )

        # ------------------------------------------------------
        # Duplicate phone check
        # ------------------------------------------------------

        new_phone = update_data.get("phone")

        if (
            new_phone is not None
            and new_phone != customer.phone
        ):
            existing_phone = self.repository.get_by_phone(
                phone=new_phone,
                company_id=company_id,
            )

            if (
                existing_phone is not None
                and existing_phone.id != customer.id
            ):
                raise DuplicateCustomerPhoneError(
                    "A customer with this phone number already exists."
                )

        # ------------------------------------------------------
        # Duplicate email check
        # ------------------------------------------------------

        new_email = update_data.get("email")

        if (
            new_email is not None
            and new_email != customer.email
        ):
            existing_email = self.repository.get_by_email(
                email=new_email,
                company_id=company_id,
            )

            if (
                existing_email is not None
                and existing_email.id != customer.id
            ):
                raise DuplicateCustomerEmailError(
                    "A customer with this email already exists."
                )

        # ------------------------------------------------------
        # Apply updates
        # ------------------------------------------------------

        for field, value in update_data.items():
            setattr(
                customer,
                field,
                value,
            )

        # ------------------------------------------------------
        # Database-level protection
        # ------------------------------------------------------

        try:
            return self.repository.update(customer)

        except IntegrityError as exc:
            self._raise_duplicate_from_integrity_error(exc)

    # ==========================================================
    # DEACTIVATE CUSTOMER
    # ==========================================================

    def deactivate_customer(
        self,
        customer_id: int,
        company_id: int,
    ) -> Customer:
        """
        Deactivate a customer instead of deleting the record.
        """

        customer = self.get_customer(
            customer_id=customer_id,
            company_id=company_id,
        )

        customer.is_active = False

        return self.repository.update(customer)

    # ==========================================================
    # ACTIVATE CUSTOMER
    # ==========================================================

    def activate_customer(
        self,
        customer_id: int,
        company_id: int,
    ) -> Customer:
        """
        Reactivate a previously deactivated customer.
        """

        customer = self.get_customer(
            customer_id=customer_id,
            company_id=company_id,
        )

        customer.is_active = True

        return self.repository.update(customer)