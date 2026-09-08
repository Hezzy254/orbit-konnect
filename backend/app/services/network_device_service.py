from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.exceptions.network_device import (
    DuplicateNetworkDeviceError,
    NetworkDeviceNotFoundError,
)
from backend.app.models.network_device import NetworkDevice
from backend.app.repositories.network_device_repository import (
    NetworkDeviceRepository,
)
from backend.app.schemas.network_device import (
    NetworkDeviceCreate,
    NetworkDeviceUpdate,
)
from backend.app.utils.encryption import credential_encryption


class NetworkDeviceService:
    """
    Business logic for network devices.

    Responsibilities:
    - Enforce company/tenant isolation.
    - Validate network device data.
    - Encrypt network credentials before storage.
    - Manage device lifecycle.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = NetworkDeviceRepository(db)

    # ==========================================================
    # NORMALIZATION HELPERS
    # ==========================================================

    @staticmethod
    def _normalize_text(value: str) -> str:
        return value.strip()

    @staticmethod
    def _normalize_optional_text(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    # ==========================================================
    # CREATE DEVICE
    # ==========================================================

    def create_device(
        self,
        data: NetworkDeviceCreate,
        company_id: int,
    ) -> NetworkDevice:
        """
        Create a network device for the authenticated company.

        The supplied password is encrypted before being stored.
        """

        name = self._normalize_text(data.name)

        if not name:
            raise ValueError(
                "Network device name cannot be empty."
            )

        device = NetworkDevice(
            company_id=company_id,
            name=name,
            vendor=data.vendor,
            model=self._normalize_optional_text(data.model),
            device_type=data.device_type,
            ip_address=self._normalize_text(data.ip_address),
            api_port=data.api_port,
            connection_type=data.connection_type,
            username=self._normalize_text(data.username),
            encrypted_password=credential_encryption.encrypt(
                data.password
            ),
            verify_tls=data.verify_tls,
            is_active=True,
        )

        try:
            return self.repository.create(device)

        except IntegrityError as exc:
            raise DuplicateNetworkDeviceError(
                "A network device with this information already exists."
            ) from exc

    # ==========================================================
    # GET DEVICE
    # ==========================================================

    def get_device(
        self,
        device_id: int,
        company_id: int,
    ) -> NetworkDevice:
        """
        Retrieve a network device belonging to the company.
        """

        device = self.repository.get_by_id(
            company_id=company_id,
            device_id=device_id,
        )

        if device is None:
            raise NetworkDeviceNotFoundError(
                "Network device not found."
            )

        return device

    # ==========================================================
    # LIST DEVICES
    # ==========================================================

    def list_devices(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 50,
        vendor=None,
        device_type=None,
        status=None,
        is_active: bool | None = None,
    ) -> dict:
        """
        Return paginated network devices for a company.
        """

        devices = self.repository.list_by_company(
            company_id=company_id,
            skip=skip,
            limit=limit,
            vendor=vendor,
            device_type=device_type,
            status=status,
            is_active=is_active,
        )

        total = self.repository.count_by_company(
            company_id=company_id,
            vendor=vendor,
            device_type=device_type,
            status=status,
            is_active=is_active,
        )

        return {
            "items": devices,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    # ==========================================================
    # UPDATE DEVICE
    # ==========================================================

    def update_device(
        self,
        device_id: int,
        company_id: int,
        data: NetworkDeviceUpdate,
    ) -> NetworkDevice:
        """
        Update network device configuration.

        Credentials are intentionally excluded. Credential
        rotation will be handled through a dedicated operation.
        """

        device = self.get_device(
            device_id=device_id,
            company_id=company_id,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        if "name" in update_data:
            update_data["name"] = self._normalize_text(
                update_data["name"]
            )

        if "model" in update_data:
            update_data["model"] = (
                self._normalize_optional_text(
                    update_data["model"]
                )
            )

        if "ip_address" in update_data:
            update_data["ip_address"] = self._normalize_text(
                update_data["ip_address"]
            )

        if "username" in update_data:
            update_data["username"] = self._normalize_text(
                update_data["username"]
            )

        if "location" in update_data:
            update_data["location"] = (
                self._normalize_optional_text(
                    update_data["location"]
                )
            )

        for field, value in update_data.items():
            setattr(
                device,
                field,
                value,
            )

        try:
            return self.repository.update(device)

        except IntegrityError as exc:
            raise DuplicateNetworkDeviceError(
                "Network device update violates a database constraint."
            ) from exc

    # ==========================================================
    # DEACTIVATE DEVICE
    # ==========================================================

    def deactivate_device(
        self,
        device_id: int,
        company_id: int,
    ) -> NetworkDevice:
        """
        Disable a network device without deleting it.
        """

        device = self.get_device(
            device_id=device_id,
            company_id=company_id,
        )

        device.is_active = False

        return self.repository.update(device)

    # ==========================================================
    # ACTIVATE DEVICE
    # ==========================================================

    def activate_device(
        self,
        device_id: int,
        company_id: int,
    ) -> NetworkDevice:
        """
        Re-enable a previously disabled network device.
        """

        device = self.get_device(
            device_id=device_id,
            company_id=company_id,
        )

        device.is_active = True

        return self.repository.update(device)