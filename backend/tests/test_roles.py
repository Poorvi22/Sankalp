
import pytest


def register(client, username):
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": "SecureTestPassword123!"
        }
    )

    assert response.status_code == 200, response.text
    return response.json()


def login(client, username):
    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "SecureTestPassword123!"
        }
    )

    assert response.status_code == 200, response.text

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.fixture
def users(client):
    owner = register(client, "test_owner")
    manager = register(client, "test_manager")
    warehouse = register(client, "test_warehouse")
    viewer = register(client, "test_viewer")

    owner_headers = login(client, "test_owner")

    for user, role in [
        (manager, "Manager"),
        (warehouse, "Warehouse")
    ]:
        response = client.patch(
            f"/admin/users/{user['id']}/role",
            json={"role": role},
            headers=owner_headers
        )
        assert response.status_code == 200, response.text

    return {
        "owner": owner,
        "manager": manager,
        "warehouse": warehouse,
        "viewer": viewer,
        "headers": {
            "Owner": owner_headers,
            "Manager": login(client, "test_manager"),
            "Warehouse": login(client, "test_warehouse"),
            "Viewer": login(client, "test_viewer")
        }
    }


def test_first_user_is_owner(client):
    user = register(client, "first_owner")

    assert user["role"] == "Owner"


def test_second_user_is_viewer(client):
    register(client, "first_owner")
    second = register(client, "second_user")

    assert second["role"] == "Viewer"


def test_owner_can_list_users(client, users):
    response = client.get(
        "/admin/users",
        headers=users["headers"]["Owner"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 4


@pytest.mark.parametrize(
    "role",
    ["Manager", "Warehouse", "Viewer"]
)
def test_non_owner_cannot_list_users(client, users, role):
    response = client.get(
        "/admin/users",
        headers=users["headers"][role]
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "role",
    ["Manager", "Warehouse", "Viewer"]
)
def test_non_owner_cannot_change_roles(client, users, role):
    response = client.patch(
        f"/admin/users/{users['viewer']['id']}/role",
        json={"role": "Manager"},
        headers=users["headers"][role]
    )

    assert response.status_code == 403

    # Verify no unauthorized change occurred.
    response = client.get(
        "/admin/users",
        headers=users["headers"]["Owner"]
    )

    viewer = next(
        u for u in response.json()
        if u["id"] == users["viewer"]["id"]
    )

    assert viewer["role"] == "Viewer"


def test_owner_can_change_role(client, users):
    response = client.patch(
        f"/admin/users/{users['viewer']['id']}/role",
        json={"role": "Manager"},
        headers=users["headers"]["Owner"]
    )

    assert response.status_code == 200
    assert response.json()["role"] == "Manager"


def test_owner_cannot_remove_own_role(client, users):
    response = client.patch(
        f"/admin/users/{users['owner']['id']}/role",
        json={"role": "Viewer"},
        headers=users["headers"]["Owner"]
    )

    assert response.status_code == 400


def test_invalid_role_rejected(client, users):
    response = client.patch(
        f"/admin/users/{users['viewer']['id']}/role",
        json={"role": "SuperAdmin"},
        headers=users["headers"]["Owner"]
    )

    assert response.status_code == 422


def test_missing_token_rejected(client):
    response = client.get("/admin/users")

    assert response.status_code in (401, 403)


def test_invalid_token_rejected(client):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401
