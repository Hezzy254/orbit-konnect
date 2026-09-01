import pytest
from pydantic import ValidationError

from backend.app.schemas.customer import CustomerCreate, CustomerUpdate


def test_customer_create_strips_surrounding_whitespace():
    customer = CustomerCreate(
        full_name="   John Test   ",
        phone="   91234567   ",
        email="   John.Test@Example.com   ",
        address="   Muscat   ",
        national_id="   TEST001   ",
    )

    assert customer.full_name == "John Test"
    assert customer.phone == "91234567"
    assert str(customer.email) == "John.Test@example.com"
    assert customer.address == "Muscat"
    assert customer.national_id == "TEST001"


def test_customer_create_rejects_whitespace_only_name():
    with pytest.raises(ValidationError):
        CustomerCreate(
            full_name="   ",
            phone="91234567",
            email="valid@example.com",
        )


def test_customer_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        CustomerCreate(
            full_name="John Test",
            phone="91234567",
            email="not-an-email",
        )


def test_customer_update_rejects_is_active():
    with pytest.raises(ValidationError) as exc_info:
        CustomerUpdate(
            full_name="John Updated",
            is_active=False,
        )

    assert "is_active" in str(exc_info.value)
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_customer_update_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        CustomerUpdate(
            full_name="John Updated",
            subscription_id=123,
        )


def test_customer_update_allows_partial_profile_updates():
    customer = CustomerUpdate(
        full_name="   John Updated   ",
        address="   Muscat   ",
    )

    assert customer.full_name == "John Updated"
    assert customer.address == "Muscat"
    assert customer.phone is None
    assert customer.email is None
