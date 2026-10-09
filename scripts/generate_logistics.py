
from pathlib import Path
from datetime import timedelta
import random
import pandas as pd

random.seed(45)

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"

sales = pd.read_csv(DATA / "sales_orders.csv")
purchase_orders = pd.read_csv(DATA / "purchase_orders.csv")
inventory = pd.read_csv(DATA / "inventory.csv")

# --------------------------------------------------
# 1. CUSTOMER DELIVERIES
# --------------------------------------------------

# Shipments can only be created for dispatched orders.
eligible_sales = sales[
    sales["status"].isin(["Delivered", "Shipped"])
].copy()

sample = eligible_sales.sample(
    n=min(2500, len(eligible_sales)),
    random_state=45
)

deliveries = []

for _, order in sample.iterrows():
    order_date = pd.Timestamp(order["order_date"])
    dispatch_date = order_date + timedelta(
        days=random.randint(0, 3)
    )
    promised_date = dispatch_date + timedelta(
        days=random.randint(2, 8)
    )

    if order["status"] == "Delivered":
        actual_date = promised_date + timedelta(
            days=random.randint(-2, 5)
        )
        delivery_status = (
            "Delayed" if actual_date > promised_date
            else "Delivered"
        )
        actual_value = actual_date.date().isoformat()
    else:
        actual_value = ""
        delivery_status = "In Transit"

    deliveries.append({
        "delivery_id": f"DLV-{len(deliveries)+1:05d}",
        "order_id": order["order_id"],
        "product_id": order["product_id"],
        "dispatch_date": dispatch_date.date().isoformat(),
        "promised_date": promised_date.date().isoformat(),
        "actual_delivery_date": actual_value,
        "delivery_status": delivery_status,
        "carrier": random.choice([
            "BlueDart", "Delhivery",
            "SwiftShip", "In-house"
        ]),
        "shipping_cost": round(
            random.uniform(100, 2000), 2
        )
    })

pd.DataFrame(deliveries).to_csv(
    DATA / "deliveries.csv", index=False
)

# --------------------------------------------------
# 2. INVENTORY MOVEMENTS
# --------------------------------------------------

movements = []

# Goods receipts from purchase orders
received_orders = purchase_orders[
    purchase_orders["status"].isin([
        "Received", "Partially Received"
    ])
]

for _, po in received_orders.iterrows():
    qty = int(po["quantity"])

    if po["status"] == "Partially Received":
        qty = max(1, qty // 2)

    movement_date = pd.Timestamp(
        po["expected_delivery_date"]
    )

    movements.append({
        "movement_id": f"MOV-{len(movements)+1:06d}",
        "movement_date": movement_date.date().isoformat(),
        "product_id": po["product_id"],
        "warehouse_id": po["warehouse_id"],
        "movement_type": "Purchase Receipt",
        "quantity_change": qty,
        "reference_id": po["po_id"]
    })

# Sales-related stock issues
warehouse_by_product = inventory.set_index(
    "product_id"
)["warehouse_id"].to_dict()

dispatched_sales = sales[
    sales["status"].isin(["Delivered", "Shipped"])
]

for _, order in dispatched_sales.iterrows():
    warehouse_id = warehouse_by_product.get(
        order["product_id"]
    )

    if warehouse_id is None:
        continue

    movements.append({
        "movement_id": f"MOV-{len(movements)+1:06d}",
        "movement_date": order["order_date"],
        "product_id": order["product_id"],
        "warehouse_id": warehouse_id,
        "movement_type": "Sales Issue",
        "quantity_change": -int(order["quantity"]),
        "reference_id": order["order_id"]
    })

# Optional stock adjustments
for _, item in inventory.sample(
    n=min(200, len(inventory)),
    random_state=45
).iterrows():
    movements.append({
        "movement_id": f"MOV-{len(movements)+1:06d}",
        "movement_date": "2026-09-30",
        "product_id": item["product_id"],
        "warehouse_id": item["warehouse_id"],
        "movement_type": "Stock Adjustment",
        "quantity_change": random.randint(-5, 10),
        "reference_id": f"ADJ-{len(movements)+1:06d}"
    })

movements_df = pd.DataFrame(movements)

movements_df.to_csv(
    DATA / "inventory_movements.csv",
    index=False
)

print("Deliveries generated:", len(deliveries))
print("Inventory movements generated:", len(movements_df))
print("Logistics dataset generation completed!")
