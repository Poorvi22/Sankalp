
import pytest


PASSWORD = "SecureTestPassword123!"


def register(client, username):
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": PASSWORD
        }
    )
    assert response.status_code == 200, response.text
    return response.json()


def login(client, username):
    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": PASSWORD
        }
    )
    assert response.status_code == 200, response.text

    return {
        "Authorization":
            f"Bearer {response.json()['access_token']}"
    }


@pytest.fixture
def role_headers(client):
    owner = register(client, "business_owner")
    manager = register(client, "business_manager")
    warehouse = register(client, "business_warehouse")
    viewer = register(client, "business_viewer")

    owner_headers = login(client, "business_owner")

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
        "Owner": owner_headers,
        "Manager": login(client, "business_manager"),
        "Warehouse": login(client, "business_warehouse"),
        "Viewer": login(client, "business_viewer")
    }


def create_product(client, headers, sku="TEST-001"):
    return client.post(
        "/inventory/products",
        json={
            "sku": sku,
            "name": "Test Product",
            "category": "Electronics",
            "quantity": 10,
            "reorder_level": 20,
            "unit_price": 500
        },
        headers=headers
    )


def create_supplier(client, headers):
    return client.post(
        "/suppliers",
        json={
            "name": "Test Supplier",
            "email": "supplier@example.com",
            "category": "Electronics"
        },
        headers=headers
    )


# -----------------------------------------
# INVENTORY PERMISSIONS
# -----------------------------------------

@pytest.mark.parametrize(
    "role,expected",
    [
        ("Owner", 200),
        ("Warehouse", 200),
        ("Manager", 403),
        ("Viewer", 403)
    ]
)
def test_product_creation_permissions(
    client, role_headers, role, expected
):
    response = create_product(
        client,
        role_headers[role],
        sku=f"TEST-{role}"
    )

    assert response.status_code == expected, response.text


@pytest.mark.parametrize(
    "role,expected",
    [
        ("Owner", 200),
        ("Warehouse", 200),
        ("Manager", 403),
        ("Viewer", 403)
    ]
)
def test_product_update_permissions(
    client, role_headers, role, expected
):
    created = create_product(
        client,
        role_headers["Owner"]
    )
    assert created.status_code == 200

    product_id = created.json()["id"]

    response = client.patch(
        f"/inventory/products/{product_id}",
        json={"quantity": 50},
        headers=role_headers[role]
    )

    assert response.status_code == expected

    check = client.get(
        "/inventory/products",
        headers=role_headers["Owner"]
    )
    assert check.status_code == 200

    product = next(
        p for p in check.json()
        if p["id"] == product_id
    )

    assert product["quantity"] == (
        50 if expected == 200 else 10
    )


def test_negative_inventory_rejected(client, role_headers):
    response = client.post(
        "/inventory/products",
        json={
            "sku": "NEG-001",
            "name": "Invalid Product",
            "quantity": -10
        },
        headers=role_headers["Owner"]
    )

    assert response.status_code == 422


def test_duplicate_sku_rejected(client, role_headers):
    first = create_product(
        client, role_headers["Owner"], "DUP-001"
    )
    second = create_product(
        client, role_headers["Owner"], "DUP-001"
    )

    assert first.status_code == 200
    assert second.status_code == 409


# -----------------------------------------
# PROCUREMENT PERMISSIONS
# -----------------------------------------

@pytest.mark.parametrize(
    "role,expected",
    [
        ("Owner", 200),
        ("Manager", 200),
        ("Warehouse", 403),
        ("Viewer", 403)
    ]
)
def test_supplier_creation_permissions(
    client, role_headers, role, expected
):
    response = create_supplier(
        client, role_headers[role]
    )
    assert response.status_code == expected


@pytest.mark.parametrize(
    "role,expected",
    [
        ("Owner", 200),
        ("Manager", 200),
        ("Warehouse", 403),
        ("Viewer", 403)
    ]
)
def test_purchase_order_creation_permissions(
    client, role_headers, role, expected
):
    supplier = create_supplier(
        client, role_headers["Owner"]
    )
    assert supplier.status_code == 200

    response = client.post(
        "/purchase-orders",
        json={
            "supplier_id": supplier.json()["id"],
            "total_amount": 5000
        },
        headers=role_headers[role]
    )

    assert response.status_code == expected

    if expected == 200:
        assert response.json()["status"] == "Draft"


def test_negative_purchase_amount_rejected(
    client, role_headers
):
    supplier = create_supplier(
        client, role_headers["Owner"]
    )

    response = client.post(
        "/purchase-orders",
        json={
            "supplier_id": supplier.json()["id"],
            "total_amount": -500
        },
        headers=role_headers["Owner"]
    )

    assert response.status_code == 422


def test_invalid_supplier_rejected(client, role_headers):
    response = client.post(
        "/purchase-orders",
        json={
            "supplier_id": 999999,
            "total_amount": 5000
        },
        headers=role_headers["Owner"]
    )

    assert response.status_code == 404


# -----------------------------------------
# APPROVAL WORKFLOW
# -----------------------------------------

@pytest.fixture
def draft_order(client, role_headers):
    supplier = create_supplier(
        client, role_headers["Owner"]
    )
    assert supplier.status_code == 200

    response = client.post(
        "/purchase-orders",
        json={
            "supplier_id": supplier.json()["id"],
            "total_amount": 10000
        },
        headers=role_headers["Manager"]
    )
    assert response.status_code == 200

    return response.json()["id"]


@pytest.mark.parametrize(
    "role,expected",
    [
        ("Owner", 200),
        ("Manager", 200),
        ("Warehouse", 403),
        ("Viewer", 403)
    ]
)
def test_submit_permissions(
    client, role_headers, draft_order, role, expected
):
    response = client.post(
        f"/purchase-orders/{draft_order}/submit",
        headers=role_headers[role]
    )

    assert response.status_code == expected


@pytest.mark.parametrize(
    "role,expected",
    [
        ("Owner", 200),
        ("Manager", 403),
        ("Warehouse", 403),
        ("Viewer", 403)
    ]
)
def test_approval_permissions(
    client, role_headers, draft_order, role, expected
):
    submitted = client.post(
        f"/purchase-orders/{draft_order}/submit",
        headers=role_headers["Manager"]
    )
    assert submitted.status_code == 200

    response = client.post(
        f"/purchase-orders/{draft_order}/approve",
        headers=role_headers[role]
    )

    assert response.status_code == expected


def test_duplicate_submission_rejected(
    client, role_headers, draft_order
):
    url = f"/purchase-orders/{draft_order}/submit"

    first = client.post(
        url, headers=role_headers["Manager"]
    )
    second = client.post(
        url, headers=role_headers["Manager"]
    )

    assert first.status_code == 200
    assert second.status_code == 400


def test_approval_before_submission_rejected(
    client, role_headers, draft_order
):
    response = client.post(
        f"/purchase-orders/{draft_order}/approve",
        headers=role_headers["Owner"]
    )

    assert response.status_code == 400


def test_missing_authentication_rejected(client):
    response = client.post(
        "/inventory/products",
        json={
            "sku": "NOAUTH",
            "name": "Unauthorized Product"
        }
    )

    assert response.status_code in (401, 403)
