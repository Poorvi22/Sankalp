
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"

finance = pd.read_csv(DATA / "finance_transactions.csv")
sales = pd.read_csv(DATA / "sales_orders.csv")
purchase_orders = pd.read_csv(DATA / "purchase_orders.csv")

assert finance["transaction_id"].is_unique
assert finance["transaction_id"].notna().all()
assert (finance["amount"] > 0).all()

assert finance["direction"].isin(
    ["Inflow", "Outflow"]
).all()

dates = pd.to_datetime(finance["transaction_date"])

assert dates.between(
    "2024-10-01", "2026-09-30"
).all()

receipts = finance[
    finance["transaction_type"] == "Customer Receipt"
]

payments = finance[
    finance["transaction_type"] == "Supplier Payment"
]

assert receipts["reference_id"].isin(
    sales["order_id"]
).all()

assert payments["reference_id"].isin(
    purchase_orders["po_id"]
).all()

# Receipts must reference delivered orders.
delivered_ids = set(
    sales.loc[
        sales["status"] == "Delivered", "order_id"
    ]
)

assert receipts["reference_id"].isin(delivered_ids).all()

# Supplier payments must reference eligible orders.
eligible_po_ids = set(
    purchase_orders.loc[
        purchase_orders["status"].isin([
            "Approved", "Ordered",
            "Partially Received", "Received"
        ]),
        "po_id"
    ]
)

assert payments["reference_id"].isin(
    eligible_po_ids
).all()

print("Finance validation passed!")
print("Total transactions:", len(finance))
print("Customer receipts:", len(receipts))
print("Supplier payments:", len(payments))
