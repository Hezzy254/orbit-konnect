from sqlalchemy.exc import IntegrityError

from backend.app.exceptions.package import (
    DuplicatePackageNameError,
    PackageNotFoundError,
)
from backend.app.models.package import Package
from backend.app.repositories.package_repository import PackageRepository
from backend.app.schemas.package import PackageCreate, PackageUpdate


PACKAGE_NAME_CONSTRAINT = "uq_package_company_name"


class PackageService:
    """
    Service layer responsible for Package business logic.
    """

    def __init__(self, repository: PackageRepository):
        self.repository = repository

    # ==========================================================
    # NORMALIZATION HELPERS
    # ==========================================================

    @staticmethod
    def _normalize_name(name: str) -> str:
        """
        Normalize a package name.

        At this stage we intentionally only remove surrounding
        whitespace. Case-insensitive package-name policies can
        be introduced later as a deliberate business rule.
        """

        return name.strip()

    @staticmethod
    def _normalize_optional_text(
        value: str | None,
    ) -> str | None:
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
        database-driver diagnostic information.

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

        if constraint_name == PACKAGE_NAME_CONSTRAINT:
            raise DuplicatePackageNameError(
                "A package with this name already exists."
            ) from exc

        # ------------------------------------------------------
        # SQLite development fallback
        # ------------------------------------------------------

        message = str(original_error or exc).lower()

        if (
            PACKAGE_NAME_CONSTRAINT.lower() in message
            or (
                "unique constraint failed" in message
                and "packages.company_id" in message
                and "packages.name" in message
            )
        ):
            raise DuplicatePackageNameError(
                "A package with this name already exists."
            ) from exc

        # ------------------------------------------------------
        # Unknown integrity error
        # ------------------------------------------------------

        raise exc

    # ==========================================================
    # CREATE PACKAGE
    # ==========================================================

    def create_package(
        self,
        data: PackageCreate,
        company_id: int,
    ) -> Package:
        """
        Create a package for the authenticated company.

        Duplicate checks provide fast and user-friendly
        validation.

        Database constraints remain the final protection
        against concurrent duplicate requests.
        """

        name = self._normalize_name(data.name)

        description = self._normalize_optional_text(
            data.description,
        )

        # ------------------------------------------------------
        # Duplicate package-name check
        # ------------------------------------------------------

        existing_package = self.repository.get_by_name(
            name=name,
            company_id=company_id,
        )

        if existing_package is not None:
            raise DuplicatePackageNameError(
                "A package with this name already exists."
            )

        # ------------------------------------------------------
        # Create package
        # ------------------------------------------------------

        package = Package(
            company_id=company_id,
            name=name,
            download_speed_mbps=data.download_speed_mbps,
            upload_speed_mbps=data.upload_speed_mbps,
            duration_value=data.duration_value,
            duration_unit=data.duration_unit,
            price=data.price,
            description=description,
            is_active=True,
        )

        # ------------------------------------------------------
        # Database-level protection
        # ------------------------------------------------------

        try:
            return self.repository.create(package)

        except IntegrityError as exc:
            self._raise_duplicate_from_integrity_error(exc)

    # ==========================================================
    # GET PACKAGE
    # ==========================================================

    def get_package(
        self,
        package_id: int,
        company_id: int,
    ) -> Package:
        """
        Get a package belonging to the authenticated company.
        """

        package = self.repository.get_by_id(
            package_id=package_id,
            company_id=company_id,
        )

        if package is None:
            raise PackageNotFoundError(
                "Package not found."
            )

        return package

    # ==========================================================
    # LIST PACKAGES
    # ==========================================================

    def list_packages(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> dict:
        """
        Return paginated packages for a company.
        """

        packages = self.repository.list_by_company(
            company_id=company_id,
            skip=skip,
            limit=limit,
        )

        total = self.repository.count_by_company(
            company_id=company_id,
        )

        return {
            "items": packages,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    # ==========================================================
    # UPDATE PACKAGE
    # ==========================================================

    def update_package(
        self,
        package_id: int,
        company_id: int,
        data: PackageUpdate,
    ) -> Package:
        """
        Update package information.

        Package activation state is intentionally handled
        separately through activate_package() and
        deactivate_package().
        """

        package = self.get_package(
            package_id=package_id,
            company_id=company_id,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        # ------------------------------------------------------
        # Normalize fields
        # ------------------------------------------------------

        if "name" in update_data:
            update_data["name"] = self._normalize_name(
                update_data["name"],
            )

        if "description" in update_data:
            update_data["description"] = (
                self._normalize_optional_text(
                    update_data["description"],
                )
            )

        # ------------------------------------------------------
        # Duplicate package-name check
        # ------------------------------------------------------

        new_name = update_data.get("name")

        if (
            new_name is not None
            and new_name != package.name
        ):
            existing_package = self.repository.get_by_name(
                name=new_name,
                company_id=company_id,
            )

            if (
                existing_package is not None
                and existing_package.id != package.id
            ):
                raise DuplicatePackageNameError(
                    "A package with this name already exists."
                )

        # ------------------------------------------------------
        # Apply updates
        # ------------------------------------------------------

        for field, value in update_data.items():
            setattr(
                package,
                field,
                value,
            )

        # ------------------------------------------------------
        # Database-level protection
        # ------------------------------------------------------

        try:
            return self.repository.update(package)

        except IntegrityError as exc:
            self._raise_duplicate_from_integrity_error(exc)

    # ==========================================================
    # DEACTIVATE PACKAGE
    # ==========================================================

    def deactivate_package(
        self,
        package_id: int,
        company_id: int,
    ) -> Package:
        """
        Deactivate a package instead of deleting the record.
        """

        package = self.get_package(
            package_id=package_id,
            company_id=company_id,
        )

        package.is_active = False

        return self.repository.update(package)

    # ==========================================================
    # ACTIVATE PACKAGE
    # ==========================================================

    def activate_package(
        self,
        package_id: int,
        company_id: int,
    ) -> Package:
        """
        Reactivate a previously deactivated package.
        """

        package = self.get_package(
            package_id=package_id,
            company_id=company_id,
        )

        package.is_active = True

        return self.repository.update(package)