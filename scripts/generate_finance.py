
from pathlib import Path
from datetime import timedelta
import random
import pandas as pd

random.seed(46)

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"
CUTOFF = pd.Timestamp("2026-09-30")

sales = pd.read_csv(DATA / "sales_orders.csv")
purchase_orders = pd.read_csv(DATA / "purchase_orders.csv")

transactions = []

def add_transaction(date, kind, direction, amount,
                    reference_id, status, category):
    transactions.append({
        "transaction_id": f"FIN-{len(transactions)+1:06d}",
        "transaction_date": date.date().isoformat(),
        "transaction_type": kind,
        "direction": direction,
        "amount": round(float(amount), 2),
        "reference_id": reference_id,
        "status": status,
        "category": category
    })

# 1. Customer receipts
# Only delivered orders are eligible for cash receipts.
delivered_sales = sales[sales["status"] == "Delivered"]

for _, order in delivered_sales.iterrows():
    if random.random() > 0.75:
        continue

    date = pd.Timestamp(order["order_date"])
    receipt_date = date + timedelta(days=random.randint(0, 20))

    if receipt_date > CUTOFF:
        continue

    add_transaction(
        receipt_date,
        "Customer Receipt",
        "Inflow",
        order["revenue"],
        order["order_id"],
        "Completed",
        "Sales"
    )

# 2. Supplier payments
payable_orders = purchase_orders[
    purchase_orders["status"].isin([
        "Approved", "Ordered",
        "Partially Received", "Received"
    ])
]

for _, po in payable_orders.iterrows():
    created = pd.Timestamp(po["created_date"])
    payment_date = created + timedelta(
        days=random.randint(5, 45)
    )

    if payment_date > CUTOFF:
        continue

    if random.random() > 0.65:
        continue

    add_transaction(
        payment_date,
        "Supplier Payment",
        "Outflow",
        po["total_cost"],
        po["po_id"],
        "Completed",
        "Procurement"
    )

# 3. Operating expenses
months = pd.date_range(
    start="2024-10-01",
    end="2026-09-01",
    freq="MS"
)

expense_categories = {
    "Rent": (30000, 70000),
    "Utilities": (8000, 20000),
    "Salaries": (120000, 250000),
    "Maintenance": (5000, 30000),
    "Software": (3000, 15000),
    "Transport": (10000, 45000)
}

for month in months:
    for category, (low, high) in expense_categories.items():
        expense_date = month + timedelta(
            days=random.randint(0, 20)
        )

        add_transaction(
            expense_date,
            "Operating Expense",
            "Outflow",
            random.uniform(low, high),
            f"EXP-{month.strftime('%Y%m')}-{category}",
            "Completed",
            category
        )

finance = pd.DataFrame(transactions)

finance = finance.sort_values(
    ["transaction_date", "transaction_id"]
).reset_index(drop=True)

finance.to_csv(
    DATA / "finance_transactions.csv",
    index=False
)

print("Finance dataset generated successfully!")
print("Transactions:", len(finance))
print("Inflows:", (finance["direction"] == "Inflow").sum())
print("Outflows:", (finance["direction"] == "Outflow").sum())
print("Date range:",
      finance["transaction_date"].min(),
      "to",
      finance["transaction_date"].max())
