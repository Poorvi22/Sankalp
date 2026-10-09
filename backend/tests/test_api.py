
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_protected_route_without_token():
    response = client.get("/auth/me")

    assert response.status_code in (401, 403)


def test_owner_route_without_token():
    response = client.get("/admin/users")

    assert response.status_code in (401, 403)


def test_invalid_login():
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent_test_user",
            "password": "InvalidPassword123!"
        }
    )

    assert response.status_code == 401
