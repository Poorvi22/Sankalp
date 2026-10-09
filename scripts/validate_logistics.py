
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"

sales = pd.read_csv(DATA / "sales_orders.csv")
purchase_orders = pd.read_csv(DATA / "purchase_orders.csv")
products = pd.read_csv(DATA / "products.csv")
warehouses = pd.read_csv(DATA / "warehouses.csv")
deliveries = pd.read_csv(DATA / "deliveries.csv")
movements = pd.read_csv(DATA / "inventory_movements.csv")

# Unique IDs
assert deliveries["delivery_id"].is_unique
assert movements["movement_id"].is_unique

# Referential integrity
assert deliveries["order_id"].isin(
    sales["order_id"]
).all()

assert movements["product_id"].isin(
    products["product_id"]
).all()

assert movements["warehouse_id"].isin(
    warehouses["warehouse_id"]
).all()

# Valid delivery dates
dispatch = pd.to_datetime(deliveries["dispatch_date"])
promised = pd.to_datetime(deliveries["promised_date"])
actual = pd.to_datetime(
    deliveries["actual_delivery_date"], errors="coerce"
)

assert (promised >= dispatch).all()
assert (actual.dropna() >= dispatch[actual.notna()]).all()

# Delivery status consistency
delayed = deliveries["delivery_status"] == "Delayed"
assert (actual[delayed] > promised[delayed]).all()

in_transit = deliveries["delivery_status"] == "In Transit"
assert actual[in_transit].isna().all()

# Purchase receipt references
receipts = movements[
    movements["movement_type"] == "Purchase Receipt"
]

assert receipts["reference_id"].isin(
    purchase_orders["po_id"]
).all()

# Sales issue references
issues = movements[
    movements["movement_type"] == "Sales Issue"
]

assert issues["reference_id"].isin(
    sales["order_id"]
).all()

print("All logistics validations passed!")
print("Deliveries:", len(deliveries))
print("Inventory movements:", len(movements))
