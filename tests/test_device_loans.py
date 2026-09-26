def create_user(client, email="ana@sena.edu.co"):
    response = client.post(
        "/users",
        json={"name": "Ana Perez", "email": email, "role": "user"},
    )
    assert response.status_code == 201
    return response.json()


def create_device(client, serial_number="LEN-2024-001"):
    response = client.post(
        "/devices",
        json={
            "name": "ThinkPad T14",
            "serial_number": serial_number,
            "device_type": "laptop",
            "brand": "Lenovo",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_loan_lifecycle_and_join_filters(client):
    user = create_user(client)
    device = create_device(client)

    loan_response = client.post(
        "/loans", json={"user_id": user["id"], "device_id": device["id"]}
    )
    assert loan_response.status_code == 201
    loan_id = loan_response.json()["id"]

    unavailable = client.get(f"/devices/{device['id']}").json()
    assert unavailable["is_available"] is False
    assert client.post(
        "/loans", json={"user_id": user["id"], "device_id": device["id"]}
    ).status_code == 409

    details = client.get("/loans/details").json()
    assert details[0]["loan_id"] == loan_id
    assert details[0]["user"]["email"] == "ana@sena.edu.co"
    assert details[0]["device"]["device_type"] == "laptop"
    filtered = client.get(
        "/loans",
        params={"status": "active", "user_email": "ana@sena.edu.co", "device_type": "laptop"},
    )
    assert filtered.status_code == 200
    assert len(filtered.json()) == 1
    assert len(client.get(f"/users/{user['id']}/loans").json()) == 1
    assert len(client.get(f"/devices/{device['id']}/loans").json()) == 1

    returned = client.patch(f"/loans/{loan_id}/return")
    assert returned.status_code == 200
    assert returned.json()["status"] == "returned"
    assert returned.json()["return_date"] is not None
    assert client.get(f"/devices/{device['id']}").json()["is_available"] is True
    assert client.patch(f"/loans/{loan_id}/return").status_code == 409


def test_device_filters_duplicates_and_crud(client):
    device = create_device(client)
    assert client.get("/devices?device_type=laptop&brand=lenovo&is_available=true").json()[0]["id"] == device["id"]
    assert client.get("/devices?search=ThinkPad").json()[0]["id"] == device["id"]
    assert client.post(
        "/devices",
        json={
            "name": "Another laptop",
            "serial_number": device["serial_number"],
            "device_type": "laptop",
        },
    ).status_code == 400

    assert client.patch(f"/devices/{device['id']}", json={"brand": "Dell"}).json()["brand"] == "Dell"
    replacement = {
        "name": "Latitude",
        "serial_number": "DEL-2024-002",
        "device_type": "laptop",
        "brand": "Dell",
        "is_available": True,
    }
    assert client.put(f"/devices/{device['id']}", json=replacement).status_code == 200
    assert client.delete(f"/devices/{device['id']}").status_code == 204
    assert client.get(f"/devices/{device['id']}").status_code == 404


def test_missing_references_invalid_filters_and_history_protection(client):
    user = create_user(client)
    device = create_device(client)
    assert client.post("/loans", json={"user_id": 999, "device_id": device["id"]}).status_code == 404
    assert client.post("/loans", json={"user_id": user["id"], "device_id": 999}).status_code == 404
    assert client.get("/loans?status=unknown").status_code == 422
    assert client.get("/loans?date_from=2030-01-02T00:00:00&date_to=2030-01-01T00:00:00").status_code == 422
    assert client.get("/loans/999").status_code == 404

    loan = client.post("/loans", json={"user_id": user["id"], "device_id": device["id"]}).json()
    assert client.delete(f"/devices/{device['id']}").status_code == 409
    assert client.delete(f"/users/{user['id']}").status_code == 409
    assert client.patch(f"/loans/{loan['id']}/return").status_code == 200
    assert client.get(f"/devices/{device['id']}/loans").json()[0]["status"] == "returned"