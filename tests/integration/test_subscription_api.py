from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from backend.app.models.subscription import Subscription, SubscriptionStatus


def test_create_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111111",
        email="subscription1@example.com",
    )

    package = create_package(
        name="Monthly 15Mbps",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
            "auto_renew": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["customer_id"] == customer.id
    assert data["package_id"] == package.id
    assert data["status"] == "PENDING"
    assert data["package_name"] == package.name
    assert data["download_speed_mbps"] == 15
    assert data["upload_speed_mbps"] == 10
    assert data["duration_value"] == 30
    assert data["duration_unit"] == "DAY"
    assert float(data["price"]) == 6
    assert data["auto_renew"] is True
    assert data["start_at"] is None
    assert data["end_at"] is None


def test_create_subscription_missing_customer(
    client: TestClient,
    create_package,
):
    package = create_package(
        name="Missing Customer Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": 999999,
            "package_id": package.id,
        },
    )

    assert response.status_code == 404


def test_create_subscription_missing_package(
    client: TestClient,
    create_customer,
):
    customer = create_customer(
        phone="91111112",
        email="subscription2@example.com",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": 999999,
        },
    )

    assert response.status_code == 404


def test_inactive_customer_cannot_create_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111113",
        email="subscription3@example.com",
        is_active=False,
    )

    package = create_package(
        name="Inactive Customer Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    assert response.status_code == 400


def test_inactive_package_cannot_create_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111114",
        email="subscription4@example.com",
    )

    package = create_package(
        name="Inactive Package",
        is_active=False,
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    assert response.status_code == 400


def test_list_subscriptions(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111115",
        email="subscription5@example.com",
    )

    package = create_package(
        name="List Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    assert response.status_code == 201

    response = client.get("/api/v1/subscriptions")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["customer_id"] == customer.id


def test_filter_subscriptions_by_status(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111116",
        email="subscription6@example.com",
    )

    package = create_package(
        name="Status Filter Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    assert response.status_code == 201

    response = client.get(
        "/api/v1/subscriptions?status=PENDING"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["status"] == "PENDING"


def test_get_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111117",
        email="subscription7@example.com",
    )

    package = create_package(
        name="Get Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    assert response.status_code == 201

    subscription_id = response.json()["id"]

    response = client.get(
        f"/api/v1/subscriptions/{subscription_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == subscription_id


def test_get_missing_subscription(client: TestClient):
    response = client.get(
        "/api/v1/subscriptions/999999"
    )

    assert response.status_code == 404


def test_activate_pending_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111118",
        email="subscription8@example.com",
    )

    package = create_package(
        name="Activation Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    subscription_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/activate"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ACTIVE"
    assert data["start_at"] is not None
    assert data["end_at"] is not None


def test_suspend_active_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111119",
        email="subscription9@example.com",
    )

    package = create_package(
        name="Suspend Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    subscription_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/activate"
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/suspend"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "SUSPENDED"


def test_reactivate_suspended_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111120",
        email="subscription10@example.com",
    )

    package = create_package(
        name="Reactivate Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    subscription_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/activate"
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/suspend"
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/activate"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ACTIVE"


def test_cancel_pending_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111121",
        email="subscription11@example.com",
    )

    package = create_package(
        name="Cancel Pending Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    subscription_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/cancel"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cancel_active_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111122",
        email="subscription12@example.com",
    )

    package = create_package(
        name="Cancel Active Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    subscription_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/activate"
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/cancel"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cannot_activate_cancelled_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111123",
        email="subscription13@example.com",
    )

    package = create_package(
        name="Invalid Activation Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    subscription_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/cancel"
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/activate"
    )

    assert response.status_code == 409


def test_cannot_suspend_pending_subscription(
    client: TestClient,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111124",
        email="subscription14@example.com",
    )

    package = create_package(
        name="Invalid Suspend Package",
    )

    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": customer.id,
            "package_id": package.id,
        },
    )

    subscription_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/subscriptions/{subscription_id}/suspend"
    )

    assert response.status_code == 409


def test_cannot_cancel_expired_subscription(
    client: TestClient,
    db,
    create_customer,
    create_package,
):
    customer = create_customer(
        phone="91111125",
        email="subscription15@example.com",
    )

    package = create_package(
        name="Expired Package",
    )

    now = datetime.now(UTC)

    subscription = Subscription(
        company_id=1,
        customer_id=customer.id,
        package_id=package.id,
        status=SubscriptionStatus.EXPIRED,
        package_name=package.name,
        download_speed_mbps=package.download_speed_mbps,
        upload_speed_mbps=package.upload_speed_mbps,
        duration_value=package.duration_value,
        duration_unit=package.duration_unit,
        price=package.price,
        start_at=now - timedelta(days=31),
        end_at=now - timedelta(days=1),
        auto_renew=False,
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    response = client.patch(
        f"/api/v1/subscriptions/{subscription.id}/cancel"
    )

    assert response.status_code == 409