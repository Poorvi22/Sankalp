
from pathlib import Path
from datetime import date, timedelta
import random
import pandas as pd

random.seed(44)

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"

products = pd.read_csv(DATA / "products.csv")
suppliers = pd.read_csv(DATA / "suppliers.csv")
warehouses = pd.read_csv(DATA / "warehouses.csv")

# 1. Supplier-product relationships
offers = []

for _, product in products.iterrows():
    selected = suppliers.sample(
        n=3,
        random_state=int(product["product_id"].split("-")[1])
    )

    for _, supplier in selected.iterrows():
        offers.append({
            "offer_id": f"OFR-{len(offers)+1:05d}",
            "product_id": product["product_id"],
            "supplier_id": supplier["supplier_id"],
            "unit_cost": round(
                float(product["unit_cost"]) *
                random.uniform(0.85, 1.15), 2
            ),
            "lead_time_days": int(supplier["lead_time_days"]),
            "minimum_order_quantity": random.choice([5, 10, 20, 50]),
            "reliability_score": float(supplier["reliability_score"])
        })

offers_df = pd.DataFrame(offers)
offers_df.to_csv(DATA / "supplier_offers.csv", index=False)

# 2. Historical purchase orders
orders = []

START = date(2024, 10, 1)
END = date(2026, 9, 30)
DAYS = (END - START).days

statuses = [
    "Draft",
    "Pending Approval",
    "Approved",
    "Ordered",
    "Partially Received",
    "Received",
    "Cancelled"
]

for i in range(1, 1001):
    offer = offers_df.iloc[random.randrange(len(offers_df))]
    warehouse = warehouses.iloc[random.randrange(len(warehouses))]

    created = START + timedelta(days=random.randint(0, DAYS))
    quantity = random.choice([10, 20, 50, 100, 200])

    unit_cost = float(offer["unit_cost"])
    lead_time = int(offer["lead_time_days"])

    orders.append({
        "po_id": f"PO-{i:05d}",
        "created_date": created.isoformat(),
        "product_id": offer["product_id"],
        "supplier_id": offer["supplier_id"],
        "warehouse_id": warehouse["warehouse_id"],
        "quantity": quantity,
        "unit_cost": unit_cost,
        "total_cost": round(quantity * unit_cost, 2),
        "expected_delivery_date": (
            created + timedelta(days=lead_time)
        ).isoformat(),
        "status": random.choice(statuses),
        "requested_by": f"USR-{random.randint(1, 20):03d}"
    })

po_df = pd.DataFrame(orders)
po_df.to_csv(DATA / "purchase_orders.csv", index=False)

print("Supplier offers:", len(offers_df))
print("Purchase orders:", len(po_df))
print("Procurement dataset generated successfully!")
