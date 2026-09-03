from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.app.models.payment import Payment, PaymentMethod, PaymentStatus
from backend.app.models.subscription import Subscription, SubscriptionStatus


def create_subscription(
    client: TestClient,
    create_customer,
    create_package,
    phone: str,
    email: str,
):
    customer = create_customer(
        phone=phone,
        email=email,
    )

    package = create_package(
        name=f"Payment Package {phone}",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    assert response.status_code == 201

    return response.json(), customer, package


def create_payment(
    client: TestClient,
    create_customer,
    create_package,
    phone: str,
    email: str,
    amount: str = "6.000",
):
    subscription, customer, package = create_subscription(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone=phone,
        email=email,
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "subscription_id": subscription["id"],
            "amount": amount,
            "payment_method": "CASH",
            "provider": "MANUAL",
        },
    )

    assert response.status_code == 201

    return response.json(), subscription, customer, package


def test_create_payment(
    client: TestClient,
    create_customer,
    create_package,
):
    payment, subscription, customer, package = create_payment(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93111111",
        email="payment1@example.com",
    )

    assert payment["company_id"] == 1
    assert payment["customer_id"] == customer.id
    assert payment["subscription_id"] == subscription["id"]
    assert float(payment["amount"]) == 6
    assert payment["currency"] == "OMR"
    assert payment["payment_method"] == "CASH"
    assert payment["provider"] == "MANUAL"
    assert payment["status"] == "PENDING"
    assert payment["transaction_reference"].startswith("OK-PAY-")
    assert payment["provider_reference"] is None
    assert payment["paid_at"] is None
    assert payment["failure_reason"] is None


def test_create_payment_missing_subscription(
    client: TestClient,
):
    response = client.post(
        "/api/v1/payments",
        json={
            "subscription_id": 999999,
            "amount": "6.000",
            "payment_method": "CASH",
            "provider": "MANUAL",
        },
    )

    assert response.status_code == 404


def test_create_payment_rejects_invalid_subscription_status(
    client: TestClient,
    create_customer,
    create_package,
):
    subscription, customer, package = create_subscription(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93111112",
        email="payment2@example.com",
    )

    response = client.patch(
        f"/api/v1/subscriptions/{subscription['id']}/cancel"
    )

    assert response.status_code == 200

    response = client.post(
        "/api/v1/payments",
        json={
            "subscription_id": subscription["id"],
            "amount": "6.000",
            "payment_method": "CASH",
            "provider": "MANUAL",
        },
    )

    assert response.status_code == 409


def test_list_payments(
    client: TestClient,
    create_customer,
    create_package,
):
    payment, subscription, customer, package = create_payment(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93111113",
        email="payment3@example.com",
    )

    response = client.get(
        "/api/v1/payments"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == payment["id"]


def test_filter_payments_by_status(
    client: TestClient,
    create_customer,
    create_package,
):
    payment, subscription, customer, package = create_payment(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93111114",
        email="payment4@example.com",
    )

    response = client.get(
        "/api/v1/payments?status=PENDING"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["id"] == payment["id"]
    assert data["items"][0]["status"] == "PENDING"


def test_filter_payments_by_customer(
    client: TestClient,
    create_customer,
    create_package,
):
    payment, subscription, customer, package = create_payment(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93111115",
        email="payment5@example.com",
    )

    response = client.get(
        f"/api/v1/payments?customer_id={customer.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["id"] == payment["id"]
    assert data["items"][0]["customer_id"] == customer.id


def test_filter_payments_by_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    payment, subscription, customer, package = create_payment(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93111116",
        email="payment6@example.com",
    )

    response = client.get(
        f"/api/v1/payments?subscription_id={subscription['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["id"] == payment["id"]
    assert data["items"][0]["subscription_id"] == subscription["id"]


def test_get_payment(
    client: TestClient,
    create_customer,
    create_package,
):
    payment, subscription, customer, package = create_payment(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93111117",
        email="payment7@example.com",
    )

    response = client.get(
        f"/api/v1/payments/{payment['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == payment["id"]


def test_get_missing_payment(
    client: TestClient,
):
    response = client.get(
        "/api/v1/payments/999999"
    )

    assert response.status_code == 404


def test_mark_payment_success(
    client: TestClient,
    create_customer,
    create_package,
):
    payment, subscription, customer, package = create_payment(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93111118",
        email="payment8@example.com",
    )

    response = client.patch(
        f"/api/v1/payments/{payment['id']}/success"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "SUCCESS"
    assert data["paid_at"] is not None
    assert data["failure_reason"] is None


def test_mark_payment_failed(
    client: TestClient,
    create_customer,
    create_package,
):
    payment, subscription, customer, package = create_payment(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93111119",
        email="payment9@example.com",
    )

    response = client.patch(
        f"/api/v1/payments/{payment['id']}/failed",
        params={
            "failure_reason": "Customer payment rejected",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "FAILED"
    assert data["paid_at"] is None
    assert data["failure_reason"] == "Customer payment rejected"


def test_cancel_payment(
    client: TestClient,
    create_customer,
    create_package,
):
    payment, subscription, customer, package = create_payment(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93111120",
        email="payment10@example.com",
    )

    response = client.patch(
        f"/api/v1/payments/{payment['id']}/cancel"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "CANCELLED"
    assert data["paid_at"] is None


def test_cannot_cancel_successful_payment(
    client: TestClient,
    create_customer,
    create_package,
):
    payment, subscription, customer, package = create_payment(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93111121",
        email="payment11@example.com",
    )

    response = client.patch(
        f"/api/v1/payments/{payment['id']}/success"
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/payments/{payment['id']}/cancel"
    )

    assert response.status_code == 409


def test_cannot_fail_successful_payment(
    client: TestClient,
    create_customer,
    create_package,
):
    payment, subscription, customer, package = create_payment(
        client=client,
        create_package=create_package,
        create_customer=create_customer,
        phone="93111122",
        email="payment12@example.com",
    )

    response = client.patch(
        f"/api/v1/payments/{payment['id']}/success"
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/payments/{payment['id']}/failed",
        params={
            "failure_reason": "Late failure attempt",
        },
    )

    assert response.status_code == 409


def test_company_cannot_access_another_company_payment(
    client: TestClient,
    db,
    create_customer,
    create_package,
):
    customer = create_customer(
        company_id=2,
        phone="93222222",
        email="company2@example.com",
    )

    package = create_package(
        company_id=2,
        name="Company 2 Package",
    )

    now = datetime.now(UTC)

    subscription = Subscription(
        company_id=2,
        customer_id=customer.id,
        package_id=package.id,
        status=SubscriptionStatus.ACTIVE,
        package_name=package.name,
        download_speed_mbps=package.download_speed_mbps,
        upload_speed_mbps=package.upload_speed_mbps,
        duration_value=package.duration_value,
        duration_unit=package.duration_unit,
        price=package.price,
        start_at=now,
        end_at=now,
        auto_renew=False,
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    payment = Payment(
        company_id=2,
        customer_id=customer.id,
        subscription_id=subscription.id,
        amount=Decimal("6.000"),
        currency="OMR",
        payment_method=PaymentMethod.CASH,
        provider="MANUAL",
        status=PaymentStatus.PENDING,
        transaction_reference="OK-PAY-COMPANY2",
        provider_reference=None,
        paid_at=None,
        failure_reason=None,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    response = client.get(
        f"/api/v1/payments/{payment.id}"
    )

    assert response.status_code == 404


def test_create_payment_rejects_backend_controlled_fields(
    client: TestClient,
    create_customer,
    create_package,
):
    subscription, customer, package = create_subscription(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93222223",
        email="payment13@example.com",
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "subscription_id": subscription["id"],
            "amount": "6.000",
            "payment_method": "CASH",
            "provider": "MANUAL",
            "company_id": 999,
            "customer_id": 999,
            "currency": "USD",
            "status": "SUCCESS",
            "transaction_reference": "FAKE-REFERENCE",
        },
    )

    assert response.status_code == 422


def test_create_payment_rejects_zero_amount(
    client: TestClient,
    create_customer,
    create_package,
):
    subscription, customer, package = create_subscription(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93222224",
        email="payment14@example.com",
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "subscription_id": subscription["id"],
            "amount": "0",
            "payment_method": "CASH",
            "provider": "MANUAL",
        },
    )

    assert response.status_code == 422


def test_create_payment_rejects_negative_amount(
    client: TestClient,
    create_customer,
    create_package,
):
    subscription, customer, package = create_subscription(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93222225",
        email="payment15@example.com",
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "subscription_id": subscription["id"],
            "amount": "-1.000",
            "payment_method": "CASH",
            "provider": "MANUAL",
        },
    )

    assert response.status_code == 422


def test_create_payment_rejects_invalid_payment_method(
    client: TestClient,
    create_customer,
    create_package,
):
    subscription, customer, package = create_subscription(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93222226",
        email="payment16@example.com",
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "subscription_id": subscription["id"],
            "amount": "6.000",
            "payment_method": "BITCOIN",
            "provider": "MANUAL",
        },
    )

    assert response.status_code == 422


def test_create_payment_requires_provider(
    client: TestClient,
    create_customer,
    create_package,
):
    subscription, customer, package = create_subscription(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93222227",
        email="payment17@example.com",
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "subscription_id": subscription["id"],
            "amount": "6.000",
            "payment_method": "CASH",
        },
    )

    assert response.status_code == 422


def test_create_payment_rejects_provider_over_50_characters(
    client: TestClient,
    create_customer,
    create_package,
):
    subscription, customer, package = create_subscription(
        client=client,
        create_customer=create_customer,
        create_package=create_package,
        phone="93222228",
        email="payment18@example.com",
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "subscription_id": subscription["id"],
            "amount": "6.000",
            "payment_method": "CASH",
            "provider": "A" * 51,
        },
    )

    assert response.status_code == 422


def test_create_payment_requires_subscription_id(
    client: TestClient,
):
    response = client.post(
        "/api/v1/payments",
        json={
            "amount": "6.000",
            "payment_method": "CASH",
            "provider": "MANUAL",
        },
    )

    assert response.status_code == 422


def test_create_payment_requires_amount(
    client: TestClient,
):
    response = client.post(
        "/api/v1/payments",
        json={
            "subscription_id": 1,
            "payment_method": "CASH",
            "provider": "MANUAL",
        },
    )

    assert response.status_code == 422


def test_create_payment_requires_payment_method(
    client: TestClient,
):
    response = client.post(
        "/api/v1/payments",
        json={
            "subscription_id": 1,
            "amount": "6.000",
            "provider": "MANUAL",
        },
    )

    assert response.status_code == 422