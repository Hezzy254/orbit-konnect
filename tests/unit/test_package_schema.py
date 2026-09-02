import pytest
from decimal import Decimal
from pydantic import ValidationError

from backend.app.schemas.package import PackageCreate, PackageUpdate


def test_package_create_strips_surrounding_whitespace():
    package = PackageCreate(
        name="   Monthly   ",
        download_speed_mbps=15,
        upload_speed_mbps=10,
        duration_value=30,
        duration_unit="MONTH",
        price="6.000",
        description="   Monthly package   ",
    )

    assert package.name == "Monthly"
    assert package.description == "Monthly package"


def test_package_create_rejects_zero_download_speed():
    with pytest.raises(ValidationError):
        PackageCreate(
            name="Monthly",
            download_speed_mbps=0,
            upload_speed_mbps=10,
            duration_value=30,
            duration_unit="MONTH",
            price="6.000",
        )


def test_package_create_rejects_negative_upload_speed():
    with pytest.raises(ValidationError):
        PackageCreate(
            name="Monthly",
            download_speed_mbps=15,
            upload_speed_mbps=-1,
            duration_value=30,
            duration_unit="MONTH",
            price="6.000",
        )


def test_package_create_rejects_zero_duration():
    with pytest.raises(ValidationError):
        PackageCreate(
            name="Monthly",
            download_speed_mbps=15,
            upload_speed_mbps=10,
            duration_value=0,
            duration_unit="MONTH",
            price="6.000",
        )


def test_package_create_rejects_negative_price():
    with pytest.raises(ValidationError):
        PackageCreate(
            name="Monthly",
            download_speed_mbps=15,
            upload_speed_mbps=10,
            duration_value=30,
            duration_unit="MONTH",
            price="-1.000",
        )


def test_package_create_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        PackageCreate(
            name="Monthly",
            download_speed_mbps=15,
            upload_speed_mbps=10,
            duration_value=30,
            duration_unit="MONTH",
            price="6.000",
            unknown_field="not allowed",
        )


def test_package_update_allows_partial_updates():
    package = PackageUpdate(
        price="7.000",
    )

    assert package.price == Decimal("7.000")
    assert package.name is None
    assert package.download_speed_mbps is None


def test_package_update_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        PackageUpdate(
            name="Updated Monthly",
            unknown_field="not allowed",
        )