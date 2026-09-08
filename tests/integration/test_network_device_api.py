from fastapi.testclient import TestClient


def network_device_payload(**overrides):
    payload = {
        "name": "Main MikroTik",
        "vendor": "MIKROTIK",
        "model": "hAP ac2",
        "device_type": "ROUTER",
        "ip_address": "192.168.88.1",
        "api_port": 8728,
        "connection_type": "API",
        "username": "admin",
        "password": "test-router-password",
        "verify_tls": True,
        "location": "Main Site",
    }

    payload.update(overrides)

    return payload


def create_network_device(
    client: TestClient,
    **overrides,
):
    response = client.post(
        "/api/v1/network-devices",
        json=network_device_payload(**overrides),
    )

    assert response.status_code == 201

    return response.json()


def test_create_network_device(client: TestClient):
    device = create_network_device(client)

    assert device["company_id"] == 1
    assert device["name"] == "Main MikroTik"
    assert device["vendor"] == "MIKROTIK"
    assert device["model"] == "hAP ac2"
    assert device["device_type"] == "ROUTER"
    assert device["ip_address"] == "192.168.88.1"
    assert device["api_port"] == 8728
    assert device["connection_type"] == "API"
    assert device["username"] == "admin"
    assert device["verify_tls"] is True
    assert device["is_active"] is True
    assert device["status"] == "UNKNOWN"
    assert device["last_seen"] is None

    assert "password" not in device
    assert "encrypted_password" not in device


def test_list_network_devices(client: TestClient):
    device = create_network_device(client)

    response = client.get(
        "/api/v1/network-devices"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == device["id"]


def test_filter_network_devices_by_vendor(client: TestClient):
    create_network_device(client)

    create_network_device(
        client,
        name="TP-Link CPE",
        vendor="TP_LINK",
        model="CPE210",
        device_type="CPE",
        ip_address="192.168.88.2",
    )

    response = client.get(
        "/api/v1/network-devices?vendor=MIKROTIK"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["vendor"] == "MIKROTIK"


def test_filter_network_devices_by_device_type(client: TestClient):
    create_network_device(client)

    create_network_device(
        client,
        name="Outdoor CPE",
        vendor="TP_LINK",
        model="CPE210",
        device_type="CPE",
        ip_address="192.168.88.3",
    )

    response = client.get(
        "/api/v1/network-devices?device_type=CPE"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["device_type"] == "CPE"


def test_get_network_device(client: TestClient):
    device = create_network_device(client)

    response = client.get(
        f"/api/v1/network-devices/{device['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == device["id"]


def test_get_missing_network_device(client: TestClient):
    response = client.get(
        "/api/v1/network-devices/999999"
    )

    assert response.status_code == 404


def test_update_network_device(client: TestClient):
    device = create_network_device(client)

    response = client.put(
        f"/api/v1/network-devices/{device['id']}",
        json={
            "name": "Updated MikroTik",
            "location": "Building A",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated MikroTik"
    assert data["location"] == "Building A"


def test_deactivate_network_device(client: TestClient):
    device = create_network_device(client)

    response = client.patch(
        f"/api/v1/network-devices/{device['id']}/deactivate"
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_activate_network_device(client: TestClient):
    device = create_network_device(client)

    response = client.patch(
        f"/api/v1/network-devices/{device['id']}/deactivate"
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/network-devices/{device['id']}/activate"
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_company_isolation_for_network_devices(
    client: TestClient,
    db,
):
    from backend.app.models.network_device import (
        NetworkDevice,
        NetworkDeviceConnectionType,
        NetworkDeviceType,
        NetworkDeviceVendor,
    )

    device = NetworkDevice(
        company_id=2,
        name="Company 2 Router",
        vendor=NetworkDeviceVendor.MIKROTIK,
        model="hAP ac2",
        device_type=NetworkDeviceType.ROUTER,
        ip_address="192.168.99.1",
        api_port=8728,
        connection_type=NetworkDeviceConnectionType.API,
        username="admin",
        encrypted_password="encrypted-test-password",
        verify_tls=True,
        is_active=True,
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    response = client.get(
        f"/api/v1/network-devices/{device.id}"
    )

    assert response.status_code == 404


def test_create_network_device_rejects_extra_fields(
    client: TestClient,
):
    payload = network_device_payload(
        company_id=999,
        encrypted_password="fake",
        status="ONLINE",
    )

    response = client.post(
        "/api/v1/network-devices",
        json=payload,
    )

    assert response.status_code == 422


def test_create_network_device_rejects_invalid_port(
    client: TestClient,
):
    response = client.post(
        "/api/v1/network-devices",
        json=network_device_payload(
            api_port=70000,
        ),
    )

    assert response.status_code == 422


def test_create_network_device_requires_password(
    client: TestClient,
):
    payload = network_device_payload()
    del payload["password"]

    response = client.post(
        "/api/v1/network-devices",
        json=payload,
    )

    assert response.status_code == 422


def test_create_network_device_rejects_invalid_vendor(
    client: TestClient,
):
    response = client.post(
        "/api/v1/network-devices",
        json=network_device_payload(
            vendor="CISCO",
        ),
    )

    assert response.status_code == 422


def test_create_network_device_rejects_invalid_connection_type(
    client: TestClient,
):
    response = client.post(
        "/api/v1/network-devices",
        json=network_device_payload(
            connection_type="TELNET",
        ),
    )

    assert response.status_code == 422