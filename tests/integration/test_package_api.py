def package_payload(**overrides):
    payload = {
        "name": "Monthly",
        "download_speed_mbps": 15,
        "upload_speed_mbps": 15,
        "duration_value": 30,
        "duration_unit": "MONTH",
        "price": "6.000",
        "description": "30-day internet package",
    }

    payload.update(overrides)

    return payload


def test_create_package_returns_201(client):
    response = client.post(
        "/api/v1/packages",
        json=package_payload(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Monthly"
    assert data["download_speed_mbps"] == 15
    assert data["upload_speed_mbps"] == 15
    assert data["duration_value"] == 30
    assert data["duration_unit"] == "MONTH"
    assert data["price"] == "6.000"
    assert data["company_id"] == 1
    assert data["is_active"] is True


def test_create_package_duplicate_name_returns_409(client):
    first = client.post(
        "/api/v1/packages",
        json=package_payload(),
    )

    assert first.status_code == 201

    duplicate = client.post(
        "/api/v1/packages",
        json=package_payload(
            description="Different description",
        ),
    )

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == (
        "A package with this name already exists."
    )


def test_list_packages_returns_company_scoped_results(
    client,
    current_user,
):
    first = client.post(
        "/api/v1/packages",
        json=package_payload(),
    )

    assert first.status_code == 201

    current_user.company_id = 2

    second = client.post(
        "/api/v1/packages",
        json=package_payload(
            name="Company Two Package",
        ),
    )

    assert second.status_code == 201

    current_user.company_id = 1

    response = client.get("/api/v1/packages")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["company_id"] == 1
    assert data["items"][0]["name"] == "Monthly"


def test_get_package_returns_package_for_same_company(client):
    create_response = client.post(
        "/api/v1/packages",
        json=package_payload(),
    )

    assert create_response.status_code == 201

    package_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/packages/{package_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == package_id


def test_get_package_returns_404_for_missing_package(client):
    response = client.get("/api/v1/packages/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Package not found."


def test_package_cannot_be_read_across_companies(
    client,
    current_user,
):
    current_user.company_id = 2

    create_response = client.post(
        "/api/v1/packages",
        json=package_payload(
            name="Company Two Package",
        ),
    )

    assert create_response.status_code == 201

    package_id = create_response.json()["id"]

    current_user.company_id = 1

    response = client.get(
        f"/api/v1/packages/{package_id}"
    )

    assert response.status_code == 404


def test_update_package_returns_200(client):
    create_response = client.post(
        "/api/v1/packages",
        json=package_payload(),
    )

    assert create_response.status_code == 201

    package_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/packages/{package_id}",
        json={
            "name": "Monthly",
            "download_speed_mbps": 20,
            "upload_speed_mbps": 10,
            "duration_value": 30,
            "duration_unit": "MONTH",
            "price": "7.000",
            "description": "Updated package",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Monthly"
    assert data["download_speed_mbps"] == 20
    assert data["upload_speed_mbps"] == 10
    assert data["price"] == "7.000"
    assert data["is_active"] is True


def test_update_package_duplicate_name_returns_409(client):
    first = client.post(
        "/api/v1/packages",
        json=package_payload(),
    )

    assert first.status_code == 201

    second = client.post(
        "/api/v1/packages",
        json=package_payload(
            name="Weekly",
            duration_value=7,
            duration_unit="DAY",
            price="3.000",
        ),
    )

    assert second.status_code == 201

    package_id = second.json()["id"]

    response = client.put(
        f"/api/v1/packages/{package_id}",
        json={
            "name": "Monthly",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "A package with this name already exists."
    )


def test_deactivate_package_persists(client):
    create_response = client.post(
        "/api/v1/packages",
        json=package_payload(),
    )

    assert create_response.status_code == 201

    package_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/packages/{package_id}/deactivate"
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    get_response = client.get(
        f"/api/v1/packages/{package_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_activate_package_persists(client):
    create_response = client.post(
        "/api/v1/packages",
        json=package_payload(),
    )

    assert create_response.status_code == 201

    package_id = create_response.json()["id"]

    deactivate = client.patch(
        f"/api/v1/packages/{package_id}/deactivate"
    )

    assert deactivate.status_code == 200

    response = client.patch(
        f"/api/v1/packages/{package_id}/activate"
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True

    get_response = client.get(
        f"/api/v1/packages/{package_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is True


def test_list_packages_pagination(client):
    for index in range(3):
        response = client.post(
            "/api/v1/packages",
            json=package_payload(
                name=f"Package {index}",
            ),
        )

        assert response.status_code == 201

    response = client.get(
        "/api/v1/packages?skip=1&limit=1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert data["skip"] == 1
    assert data["limit"] == 1
    assert len(data["items"]) == 1