from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.network_device import (
    NetworkDevice,
    NetworkDeviceStatus,
    NetworkDeviceType,
    NetworkDeviceVendor,
)


class NetworkDeviceRepository:
    """
    Handles database operations for network devices.

    Business rules belong in the service layer.
    This repository is responsible only for database access.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        device: NetworkDevice,
    ) -> NetworkDevice:
        """
        Create a new network device.
        """

        self.db.add(device)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise

        self.db.refresh(device)

        return device

    def get_by_id(
        self,
        company_id: int,
        device_id: int,
    ) -> NetworkDevice | None:
        """
        Retrieve a network device belonging to a specific company.
        """

        return (
            self.db.query(NetworkDevice)
            .filter(
                NetworkDevice.id == device_id,
                NetworkDevice.company_id == company_id,
            )
            .first()
        )

    def list_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        vendor: NetworkDeviceVendor | None = None,
        device_type: NetworkDeviceType | None = None,
        status: NetworkDeviceStatus | None = None,
        is_active: bool | None = None,
    ) -> list[NetworkDevice]:
        """
        Return network devices belonging to a company.

        Optional filters allow filtering by vendor,
        device type, status, and active state.
        """

        query = self.db.query(NetworkDevice).filter(
            NetworkDevice.company_id == company_id,
        )

        if vendor is not None:
            query = query.filter(
                NetworkDevice.vendor == vendor,
            )

        if device_type is not None:
            query = query.filter(
                NetworkDevice.device_type == device_type,
            )

        if status is not None:
            query = query.filter(
                NetworkDevice.status == status,
            )

        if is_active is not None:
            query = query.filter(
                NetworkDevice.is_active == is_active,
            )

        return (
            query.order_by(NetworkDevice.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_company(
        self,
        company_id: int,
        vendor: NetworkDeviceVendor | None = None,
        device_type: NetworkDeviceType | None = None,
        status: NetworkDeviceStatus | None = None,
        is_active: bool | None = None,
    ) -> int:
        """
        Count network devices belonging to a company.
        """

        query = self.db.query(NetworkDevice).filter(
            NetworkDevice.company_id == company_id,
        )

        if vendor is not None:
            query = query.filter(
                NetworkDevice.vendor == vendor,
            )

        if device_type is not None:
            query = query.filter(
                NetworkDevice.device_type == device_type,
            )

        if status is not None:
            query = query.filter(
                NetworkDevice.status == status,
            )

        if is_active is not None:
            query = query.filter(
                NetworkDevice.is_active == is_active,
            )

        return query.count()

    def update(
        self,
        device: NetworkDevice,
    ) -> NetworkDevice:
        """
        Persist changes to an existing network device.
        """

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise

        self.db.refresh(device)

        return device