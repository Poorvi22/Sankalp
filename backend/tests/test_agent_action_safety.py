
import uuid
import pytest

PASSWORD = "SecureTestPassword123!"


def setup_users(client):
    suffix = uuid.uuid4().hex[:8]

    owner_name = f"owner_{suffix}"
    manager_name = f"manager_{suffix}"

    def register(username):
        response = client.post(
            "/auth/register",
            json={
                "username": username,
                "password": PASSWORD
            }
        )
        assert response.status_code == 200, response.text
        return response.json()

    owner = register(owner_name)
    manager = register(manager_name)

    def login(username):
        response = client.post(
            "/auth/login",
            json={
                "username": username,
                "password": PASSWORD
            }
        )
        assert response.status_code == 200
        return {
            "Authorization":
                f"Bearer {response.json()['access_token']}"
        }

    owner_headers = login(owner_name)

    role_response = client.patch(
        f"/admin/users/{manager['id']}/role",
        json={"role": "Manager"},
        headers=owner_headers
    )
    assert role_response.status_code == 200

    return owner_headers, login(manager_name)


def create_draft(client, headers):
    supplier = client.post(
        "/suppliers",
        json={"name": "Safety Test Supplier"},
        headers=headers
    )
    assert supplier.status_code == 200, supplier.text

    order = client.post(
        "/purchase-orders",
        json={
            "supplier_id": supplier.json()["id"],
            "total_amount": 10000
        },
        headers=headers
    )
    assert order.status_code == 200, order.text

    return order.json()["id"]


# Expected failure:
# Current API submits without a confirmation token.
@pytest.mark.xfail(
    strict=True,
    reason="Server-side confirmation not implemented"
)
def test_submit_requires_confirmation(client):
    _, manager = setup_users(client)
    order_id = create_draft(client, manager)

    response = client.post(
        f"/purchase-orders/{order_id}/submit",
        headers=manager
    )

    assert response.status_code in (400, 403, 409)


# Expected failure:
# Current API does not enforce idempotency keys.
@pytest.mark.xfail(
    strict=True,
    reason="Idempotent draft creation not implemented"
)
def test_duplicate_creation_is_prevented(client):
    _, manager = setup_users(client)

    supplier = client.post(
        "/suppliers",
        json={"name": "Idempotency Supplier"},
        headers=manager
    )
    assert supplier.status_code == 200

    url = "/purchase-orders"
    payload = {
        "supplier_id": supplier.json()["id"],
        "total_amount": 5000
    }
    headers = {
        **manager,
        "Idempotency-Key": "safety-test-request-001"
    }

    first = client.post(
        url, json=payload, headers=headers
    )
    second = client.post(
        url, json=payload, headers=headers
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.json()["id"] == second.json()["id"]


# Existing protection:
# The same order cannot be submitted twice.
def test_same_order_cannot_be_submitted_twice(client):
    _, manager = setup_users(client)
    order_id = create_draft(client, manager)

    url = f"/purchase-orders/{order_id}/submit"

    first = client.post(url, headers=manager)
    second = client.post(url, headers=manager)

    assert first.status_code == 200
    assert second.status_code == 400


# Existing protection:
# Approval cannot happen before submission.
def test_approval_requires_submitted_state(client):
    owner, manager = setup_users(client)
    order_id = create_draft(client, manager)

    response = client.post(
        f"/purchase-orders/{order_id}/approve",
        headers=owner
    )

    assert response.status_code == 400
