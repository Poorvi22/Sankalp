import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parent
BUSINESS_DIR = ROOT / "business"
BUSINESS_DIR.mkdir(parents=True, exist_ok=True)

TODAY = date(2026, 10, 9)
START_DATE = date(2024, 10, 1)


def random_date():
    days = (TODAY - START_DATE).days
    return START_DATE + timedelta(days=random.randint(0, days))


# -------------------------------------------------
# 1. PRODUCTS
# -------------------------------------------------

products = []

for i in range(1, 501):
    cost = round(random.uniform(10, 500), 2)

    products.append({
        "product_id": f"PRD-{i:04d}",
        "product_name": f"Product {i:03d}",
        "category": random.choice([
            "Electronics",
            "Office Supplies",
            "Packaging",
            "Safety",
            "Industrial Parts"
        ]),
        "unit_cost": cost,
        "unit_price": round(cost * random.uniform(1.2, 1.8), 2),
        "reorder_point": random.randint(20, 150),
        "target_stock": random.randint(150, 600)
    })

products_df = pd.DataFrame(products)
products_df.to_csv(BUSINESS_DIR / "products.csv", index=False)


# -------------------------------------------------
# 2. SUPPLIERS
# -------------------------------------------------

suppliers = []

for i in range(1, 51):
    suppliers.append({
        "supplier_id": f"SUP-{i:03d}",
        "supplier_name": f"Supplier {i:02d}",
        "region": random.choice([
            "North", "South", "East", "West", "Central"
        ]),
        "lead_time_days": random.randint(2, 28),
        "reliability_score": round(random.uniform(0.70, 0.99), 3),
        "active": random.random() > 0.08
    })

suppliers_df = pd.DataFrame(suppliers)
suppliers_df.to_csv(BUSINESS_DIR / "suppliers.csv", index=False)


# -------------------------------------------------
# 3. INVENTORY
# -------------------------------------------------

inventory = []

for i, product in enumerate(products, start=1):
    quantity = random.randint(0, 700)

    inventory.append({
        "inventory_id": f"INV-{i:05d}",
        "product_id": product["product_id"],
        "warehouse_id": f"WH-{random.randint(1, 5):03d}",
        "on_hand": quantity,
        "reserved": random.randint(0, min(quantity, 50)),
        "reorder_point": product["reorder_point"],
        "updated_at": TODAY.isoformat()
    })

inventory_df = pd.DataFrame(inventory)
inventory_df.to_csv(BUSINESS_DIR / "inventory.csv", index=False)


# -------------------------------------------------
# 4. SALES ORDERS — 10,000 RECORDS
# -------------------------------------------------

sales = []

for i in range(1, 10001):
    product = random.choice(products)

    quantity = random.choice([1, 2, 3, 5, 10, 20, 50])
    price = round(
        product["unit_price"] * random.uniform(0.94, 1.06), 2
    )

    sales.append({
        "order_id": f"SO-{i:06d}",
        "order_date": random_date().isoformat(),
        "product_id": product["product_id"],
        "quantity": quantity,
        "unit_price": price,
        "revenue": round(price * quantity, 2),
        "status": random.choice([
            "Delivered", "Shipped", "Processing", "Cancelled"
        ]),
        "region": random.choice([
            "North", "South", "East", "West", "Central"
        ])
    })

sales_df = pd.DataFrame(sales)
sales_df.to_csv(BUSINESS_DIR / "sales_orders.csv", index=False)


# -------------------------------------------------
# 5. SUPPLIER OFFERS
# -------------------------------------------------

offers = []

for product in products:
    for supplier in random.sample(suppliers, 3):
        offers.append({
            "offer_id": f"OFR-{len(offers) + 1:05d}",
            "product_id": product["product_id"],
            "supplier_id": supplier["supplier_id"],
            "unit_price": round(
                product["unit_cost"] * random.uniform(0.9, 1.2), 2
            ),
            "lead_time_days": supplier["lead_time_days"],
            "minimum_order_qty": random.choice([1, 5, 10, 20, 50])
        })

offers_df = pd.DataFrame(offers)
offers_df.to_csv(BUSINESS_DIR / "supplier_offers.csv", index=False)


# -------------------------------------------------
# 6. PURCHASE ORDERS
# -------------------------------------------------

purchase_orders = []

for i in range(1, 1001):
    product = random.choice(products)
    supplier = random.choice(suppliers)
    quantity = random.choice([10, 20, 50, 100, 200])
    unit_cost = round(product["unit_cost"] * random.uniform(0.9, 1.2), 2)

    purchase_orders.append({
        "po_id": f"PO-{i:05d}",
        "created_date": random_date().isoformat(),
        "product_id": product["product_id"],
        "supplier_id": supplier["supplier_id"],
        "quantity": quantity,
        "unit_cost": unit_cost,
        "total_cost": round(quantity * unit_cost, 2),
        "status": random.choice([
            "Draft", "Pending Approval", "Approved",
            "Ordered", "Received", "Cancelled"
        ])
    })

pd.DataFrame(purchase_orders).to_csv(
    BUSINESS_DIR / "purchase_orders.csv", index=False
)


# -------------------------------------------------
# 7. FINANCIAL TRANSACTIONS
# -------------------------------------------------

finance = []

for i in range(1, 3501):
    transaction_type = random.choice([
        "Customer Receipt",
        "Supplier Payment",
        "Operating Expense",
        "Freight"
    ])

    finance.append({
        "transaction_id": f"FIN-{i:06d}",
        "transaction_date": random_date().isoformat(),
        "transaction_type": transaction_type,
        "amount": round(random.uniform(100, 25000), 2),
        "direction": (
            "Inflow"
            if transaction_type == "Customer Receipt"
            else "Outflow"
        ),
        "status": random.choice([
            "Completed", "Pending", "Overdue"
        ])
    })

pd.DataFrame(finance).to_csv(
    BUSINESS_DIR / "finance_transactions.csv", index=False
)


# -------------------------------------------------
# 8. DELIVERY RECORDS
# -------------------------------------------------

deliveries = []

for i in range(1, 2501):
    dispatch_date = random_date()
    promised_date = dispatch_date + timedelta(
        days=random.randint(2, 12)
    )

    deliveries.append({
        "delivery_id": f"DLV-{i:05d}",
        "dispatch_date": dispatch_date.isoformat(),
        "promised_date": promised_date.isoformat(),
        "carrier": random.choice([
            "Carrier A", "Carrier B", "Carrier C"
        ]),
        "status": random.choice([
            "In Transit", "Delivered", "Delayed", "Exception"
        ]),
        "shipping_cost": round(random.uniform(80, 3000), 2)
    })

pd.DataFrame(deliveries).to_csv(
    BUSINESS_DIR / "deliveries.csv", index=False
)


# -------------------------------------------------
# VALIDATION SUMMARY
# -------------------------------------------------

print("\nDataset generation completed successfully.")
print(f"Products: {len(products_df)}")
print(f"Suppliers: {len(suppliers_df)}")
print(f"Inventory records: {len(inventory_df)}")
print(f"Sales orders: {len(sales_df)}")
print(f"Supplier offers: {len(offers_df)}")
print(f"Purchase orders: {len(purchase_orders)}")
print("Finance transactions: 3500")
print("Delivery records: 2500")

assert products_df["product_id"].is_unique
assert suppliers_df["supplier_id"].is_unique
assert sales_df["order_id"].is_unique

print("Basic validation passed.")