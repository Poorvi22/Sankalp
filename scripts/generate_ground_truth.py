
from pathlib import Path
import pandas as pd
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"
OUTPUT = ROOT / "data" / "benchmarks"
AUDIT = ROOT / "evaluation" / "results" / "dataset_audit_report.json"

OUTPUT.mkdir(parents=True, exist_ok=True)

# Do not create final ground truth from failed audits.
if not AUDIT.exists():
    raise SystemExit(
        "Dataset audit report missing. "
        "Run python scripts/audit_dataset.py first."
    )

with open(AUDIT, encoding="utf-8") as f:
    audit = json.load(f)

if audit.get("status") != "PASS":
    raise SystemExit(
        "Dataset audit failed. Fix reported issues first."
    )

sales = pd.read_csv(DATA / "sales_orders.csv")
products = pd.read_csv(DATA / "products.csv")
inventory = pd.read_csv(DATA / "inventory.csv")
suppliers = pd.read_csv(DATA / "suppliers.csv")
offers = pd.read_csv(DATA / "supplier_offers.csv")
deliveries = pd.read_csv(DATA / "deliveries.csv")
finance = pd.read_csv(DATA / "finance_transactions.csv")
purchase_orders = pd.read_csv(DATA / "purchase_orders.csv")

ground_truth = []

def add_case(case_id, question, answer, sources, metric):
    ground_truth.append({
        "case_id": case_id,
        "question": question,
        "expected_answer": answer,
        "source_tables": sources,
        "metric": metric
    })

# ---------------------------------------
# CASE 1 — Total recognized revenue
# ---------------------------------------

# Business rule: recognize revenue for delivered orders.
delivered_sales = sales[
    sales["status"] == "Delivered"
].copy()

total_revenue = round(
    float(delivered_sales["revenue"].sum()), 2
)

add_case(
    "GT-001",
    "What is the total recognized sales revenue?",
    {"value": total_revenue, "currency": "INR"},
    ["sales_orders.csv"],
    "total_revenue"
)

# ---------------------------------------
# CASE 2 — Low-stock products
# ---------------------------------------

low_stock = inventory[
    inventory["quantity_available"]
    < inventory["reorder_level"]
]

add_case(
    "GT-002",
    "How many inventory records are below reorder level?",
    {"count": int(len(low_stock))},
    ["inventory.csv"],
    "low_stock_count"
)

# ---------------------------------------
# CASE 3 — Top selling product
# ---------------------------------------

product_sales = (
    delivered_sales.groupby("product_id")["quantity"]
    .sum()
    .sort_values(ascending=False)
)

top_product = (
    str(product_sales.index[0])
    if not product_sales.empty else None
)

add_case(
    "GT-003",
    "Which product has the highest delivered sales quantity?",
    {"product_id": top_product},
    ["sales_orders.csv"],
    "top_selling_product"
)

# ---------------------------------------
# CASE 4 — Cheapest eligible supplier
# ---------------------------------------

product_id = "PRD-0001"
order_quantity = 100

eligible = offers[
    (offers["product_id"] == product_id)
    & (offers["reliability_score"] >= 0.80)
    & (offers["minimum_order_quantity"] <= order_quantity)
].copy()

eligible = eligible.sort_values(
    ["unit_cost", "lead_time_days", "supplier_id"]
)

if eligible.empty:
    supplier_answer = {
        "supplier_id": None,
        "estimated_cost": None
    }
else:
    best = eligible.iloc[0]

    supplier_answer = {
        "supplier_id": str(best["supplier_id"]),
        "estimated_cost": round(
            float(best["unit_cost"]) * order_quantity, 2
        )
    }

add_case(
    "GT-004",
    "Find the cheapest eligible supplier for 100 units of PRD-0001.",
    supplier_answer,
    ["supplier_offers.csv"],
    "supplier_selection"
)

# ---------------------------------------
# CASE 5 — Delayed deliveries
# ---------------------------------------

delayed = deliveries[
    deliveries["delivery_status"] == "Delayed"
]

add_case(
    "GT-005",
    "How many recorded deliveries were delayed?",
    {"count": int(len(delayed))},
    ["deliveries.csv"],
    "delayed_deliveries"
)

# ---------------------------------------
# CASE 6 — Net cash flow
# ---------------------------------------

inflow = finance.loc[
    finance["direction"] == "Inflow", "amount"
].sum()

outflow = finance.loc[
    finance["direction"] == "Outflow", "amount"
].sum()

net_cash_flow = round(
    float(inflow - outflow), 2
)

add_case(
    "GT-006",
    "What is the net cash flow across all recorded transactions?",
    {"value": net_cash_flow, "currency": "INR"},
    ["finance_transactions.csv"],
    "net_cash_flow"
)

# ---------------------------------------
# CASE 7 — Pending approval value
# ---------------------------------------

pending = purchase_orders[
    purchase_orders["status"] == "Pending Approval"
]

pending_value = round(
    float(pending["total_cost"].sum()), 2
)

add_case(
    "GT-007",
    "What is the total value of purchase orders pending approval?",
    {"value": pending_value, "currency": "INR"},
    ["purchase_orders.csv"],
    "pending_approval_value"
)

# ---------------------------------------
# CASE 8 — Revenue comparison
# ---------------------------------------

delivered_sales["order_date"] = pd.to_datetime(
    delivered_sales["order_date"]
)

period_a = delivered_sales[
    delivered_sales["order_date"].between(
        "2026-04-01", "2026-06-30"
    )
]["revenue"].sum()

period_b = delivered_sales[
    delivered_sales["order_date"].between(
        "2026-07-01", "2026-09-30"
    )
]["revenue"].sum()

change_pct = (
    round(float((period_b - period_a) / period_a * 100), 2)
    if period_a != 0 else None
)

add_case(
    "GT-008",
    "Compare recognized revenue in Q3 2026 against Q2 2026.",
    {
        "q2_revenue": round(float(period_a), 2),
        "q3_revenue": round(float(period_b), 2),
        "percentage_change": change_pct
    },
    ["sales_orders.csv"],
    "quarterly_revenue_comparison"
)

# ---------------------------------------
# SAVE
# ---------------------------------------

output_file = OUTPUT / "analytics_ground_truth.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(ground_truth, f, indent=2)

print("\nBIZPILOT AI — ANALYTICAL GROUND TRUTH")
print("=" * 50)
print("Cases generated:", len(ground_truth))
print("Saved to:", output_file)

for case in ground_truth:
    print(case["case_id"], "-", case["metric"])
