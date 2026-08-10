from sqlalchemy.exc import IntegrityError

from backend.app.exceptions.customer import (
    DuplicateCustomerEmailError,
    DuplicateCustomerPhoneError,
    CustomerNotFoundError,
)
from backend.app.models.customer import Customer
from backend.app.repositories.customer_repository import CustomerRepository
from backend.app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """
    Service layer responsible for Customer business logic.
    """

    def __init__(self, repository: CustomerRepository):
        self.repository = repository

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

        Duplicate checks are performed before insertion.
        Database constraints provide the final protection
        against concurrent duplicate requests.
        """

        # ------------------------------------------------------
        # Normalize phone
        # ------------------------------------------------------

        phone = data.phone.strip()

        # ------------------------------------------------------
        # Check duplicate phone
        # ------------------------------------------------------

        existing_phone = self.repository.get_by_phone(
            phone=phone,
            company_id=company_id,
        )

        if existing_phone:
            raise DuplicateCustomerPhoneError(
                "A customer with this phone number already exists."
            )

        # ------------------------------------------------------
        # Normalize email
        # ------------------------------------------------------

        email = None

        if data.email is not None:
            email = str(data.email).strip().lower()

            # --------------------------------------------------
            # Check duplicate email
            # --------------------------------------------------

            existing_email = self.repository.get_by_email(
                email=email,
                company_id=company_id,
            )

            if existing_email:
                raise DuplicateCustomerEmailError(
                    "A customer with this email already exists."
                )

        # ------------------------------------------------------
        # Create customer object
        # ------------------------------------------------------

        customer = Customer(
            company_id=company_id,
            full_name=data.full_name.strip(),
            phone=phone,
            email=email,
            address=(
                data.address.strip()
                if data.address
                else None
            ),
            national_id=(
                data.national_id.strip()
                if data.national_id
                else None
            ),
            is_active=True,
        )

        # ------------------------------------------------------
        # Database-level protection
        # ------------------------------------------------------

        try:
            return self.repository.create(customer)

        except IntegrityError as exc:
            message = str(exc).lower()

            if (
                "phone" in message
                and "company_id" in message
            ):
                raise DuplicateCustomerPhoneError(
                    "A customer with this phone number already exists."
                ) from exc

            if (
                "email" in message
                and "company_id" in message
            ):
                raise DuplicateCustomerEmailError(
                    "A customer with this email already exists."
                ) from exc

            raise

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
        Update a customer belonging to the authenticated company.
        """

        customer = self.get_customer(
            customer_id=customer_id,
            company_id=company_id,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        # ------------------------------------------------------
        # Normalize full name
        # ------------------------------------------------------

        if "full_name" in update_data:
            update_data["full_name"] = (
                update_data["full_name"].strip()
            )

        # ------------------------------------------------------
        # Normalize phone
        # ------------------------------------------------------

        if "phone" in update_data:
            update_data["phone"] = (
                update_data["phone"].strip()
            )

        # ------------------------------------------------------
        # Normalize email
        # ------------------------------------------------------

        if "email" in update_data:
            if update_data["email"] is not None:
                update_data["email"] = (
                    str(update_data["email"])
                    .strip()
                    .lower()
                )

        # ------------------------------------------------------
        # Normalize address
        # ------------------------------------------------------

        if "address" in update_data:
            if update_data["address"] is not None:
                update_data["address"] = (
                    update_data["address"].strip()
                )

        # ------------------------------------------------------
        # Normalize national ID
        # ------------------------------------------------------

        if "national_id" in update_data:
            if update_data["national_id"] is not None:
                update_data["national_id"] = (
                    update_data["national_id"].strip()
                )

        # ------------------------------------------------------
        # Check duplicate phone
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
        # Check duplicate email
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
            setattr(customer, field, value)

        # ------------------------------------------------------
        # Database-level protection
        # ------------------------------------------------------

        try:
            return self.repository.update(customer)

        except IntegrityError as exc:
            message = str(exc).lower()

            if (
                "phone" in message
                and "company_id" in message
            ):
                raise DuplicateCustomerPhoneError(
                    "A customer with this phone number already exists."
                ) from exc

            if (
                "email" in message
                and "company_id" in message
            ):
                raise DuplicateCustomerEmailError(
                    "A customer with this email already exists."
                ) from exc

            raise

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