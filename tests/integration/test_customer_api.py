def test_create_customer_returns_201(client, customer_payload):
    response = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "John Test Customer"
    assert data["phone"] == "91234567"
    assert data["email"] == "john.test@example.com"
    assert data["company_id"] == 1
    assert data["is_active"] is True


def test_create_customer_normalizes_input(client, customer_payload):
    response = client.post(
        "/api/v1/customers",
        json=customer_payload(
            full_name="   John Normalized   ",
            phone="   92345678   ",
            email="   John.Normalized@Example.com   ",
            address="   Muscat   ",
            national_id="   TEST002   ",
        ),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "John Normalized"
    assert data["phone"] == "92345678"
    assert data["email"] == "john.normalized@example.com"
    assert data["address"] == "Muscat"
    assert data["national_id"] == "TEST002"


def test_create_customer_duplicate_phone_returns_409(
    client,
    customer_payload,
):
    first = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/api/v1/customers",
        json=customer_payload(
            full_name="Different Customer",
            email="different@example.com",
        ),
    )

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == (
        "A customer with this phone number already exists."
    )


def test_create_customer_duplicate_email_returns_409(
    client,
    customer_payload,
):
    first = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/api/v1/customers",
        json=customer_payload(
            full_name="Different Customer",
            phone="92345678",
        ),
    )

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == (
        "A customer with this email already exists."
    )


def test_same_phone_and_email_are_allowed_across_companies(
    client,
    current_user,
    customer_payload,
):
    first = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    assert first.status_code == 201

    current_user.company_id = 2

    second = client.post(
        "/api/v1/customers",
        json=customer_payload(
            full_name="Same Contact Different ISP",
        ),
    )

    assert second.status_code == 201
    assert second.json()["company_id"] == 2


def test_list_customers_returns_company_scoped_results(
    client,
    current_user,
    customer_payload,
):
    first = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    assert first.status_code == 201

    current_user.company_id = 2

    second = client.post(
        "/api/v1/customers",
        json=customer_payload(
            full_name="Company Two Customer",
            phone="92345678",
            email="company2@example.com",
        ),
    )
    assert second.status_code == 201

    current_user.company_id = 1

    response = client.get("/api/v1/customers")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["company_id"] == 1


def test_get_customer_returns_customer_for_same_company(
    client,
    customer_payload,
):
    create_response = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    customer_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/customers/{customer_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == customer_id


def test_get_customer_returns_404_for_missing_customer(client):
    response = client.get("/api/v1/customers/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found."


def test_customer_cannot_be_read_across_companies(
    client,
    current_user,
    customer_payload,
):
    current_user.company_id = 2

    create_response = client.post(
        "/api/v1/customers",
        json=customer_payload(
            full_name="Company Two Customer",
            phone="92345678",
            email="company2@example.com",
        ),
    )
    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    current_user.company_id = 1

    response = client.get(
        f"/api/v1/customers/{customer_id}"
    )

    assert response.status_code == 404


def test_update_customer_returns_200(
    client,
    customer_payload,
):
    create_response = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    customer_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/customers/{customer_id}",
        json={
            "full_name": "Updated Customer",
            "address": "Updated Address",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["full_name"] == "Updated Customer"
    assert data["address"] == "Updated Address"
    assert data["phone"] == "91234567"
    assert data["is_active"] is True


def test_update_customer_rejects_is_active(
    client,
    customer_payload,
):
    create_response = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    customer_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/customers/{customer_id}",
        json={
            "full_name": "Status Protection Test",
            "is_active": False,
        },
    )

    assert response.status_code == 422
    assert "is_active" in response.text


def test_update_customer_duplicate_phone_returns_409(
    client,
    customer_payload,
):
    first = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    assert first.status_code == 201

    second = client.post(
        "/api/v1/customers",
        json=customer_payload(
            full_name="Second Customer",
            phone="92345678",
            email="second@example.com",
        ),
    )
    assert second.status_code == 201

    second_id = second.json()["id"]

    response = client.put(
        f"/api/v1/customers/{second_id}",
        json={"phone": "91234567"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "A customer with this phone number already exists."
    )


def test_update_customer_duplicate_email_returns_409(
    client,
    customer_payload,
):
    first = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    assert first.status_code == 201

    second = client.post(
        "/api/v1/customers",
        json=customer_payload(
            full_name="Second Customer",
            phone="92345678",
            email="second@example.com",
        ),
    )
    assert second.status_code == 201

    second_id = second.json()["id"]

    response = client.put(
        f"/api/v1/customers/{second_id}",
        json={"email": "john.test@example.com"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "A customer with this email already exists."
    )


def test_update_customer_can_clear_email(
    client,
    customer_payload,
):
    create_response = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    customer_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/customers/{customer_id}",
        json={"email": None},
    )

    assert response.status_code == 200
    assert response.json()["email"] is None


def test_deactivate_customer_persists(
    client,
    customer_payload,
):
    create_response = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    customer_id = create_response.json()["id"]

    deactivate = client.patch(
        f"/api/v1/customers/{customer_id}/deactivate"
    )

    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False

    get_response = client.get(
        f"/api/v1/customers/{customer_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_activate_customer_persists(
    client,
    customer_payload,
):
    create_response = client.post(
        "/api/v1/customers",
        json=customer_payload(),
    )
    customer_id = create_response.json()["id"]

    client.patch(
        f"/api/v1/customers/{customer_id}/deactivate"
    )

    activate = client.patch(
        f"/api/v1/customers/{customer_id}/activate"
    )

    assert activate.status_code == 200
    assert activate.json()["is_active"] is True

    get_response = client.get(
        f"/api/v1/customers/{customer_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is True


def test_list_customers_pagination(
    client,
    customer_payload,
):
    for index in range(3):
        response = client.post(
            "/api/v1/customers",
            json=customer_payload(
                full_name=f"Pagination Customer {index}",
                phone=f"93{index:06d}",
                email=f"pagination{index}@example.com",
            ),
        )
        assert response.status_code == 201

    response = client.get(
        "/api/v1/customers?skip=1&limit=1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert data["skip"] == 1
    assert data["limit"] == 1
    assert len(data["items"]) == 1
