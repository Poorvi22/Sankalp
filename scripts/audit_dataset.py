
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"
RESULTS = ROOT / "evaluation" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

files = {
    "products": "products.csv",
    "suppliers": "suppliers.csv",
    "warehouses": "warehouses.csv",
    "inventory": "inventory.csv",
    "sales": "sales_orders.csv",
    "offers": "supplier_offers.csv",
    "purchase_orders": "purchase_orders.csv",
    "deliveries": "deliveries.csv",
    "movements": "inventory_movements.csv",
    "finance": "finance_transactions.csv"
}

tables = {}
issues = []

def check(condition, message):
    if not bool(condition):
        issues.append(message)

# 1. Load datasets
for name, filename in files.items():
    path = DATA / filename

    if not path.exists():
        issues.append(f"Missing dataset: {filename}")
        continue

    tables[name] = pd.read_csv(path)

# 2. Check unique IDs
primary_keys = {
    "products": "product_id",
    "suppliers": "supplier_id",
    "warehouses": "warehouse_id",
    "inventory": "inventory_id",
    "sales": "order_id",
    "offers": "offer_id",
    "purchase_orders": "po_id",
    "deliveries": "delivery_id",
    "movements": "movement_id",
    "finance": "transaction_id"
}

for table_name, key in primary_keys.items():
    if table_name not in tables:
        continue

    df = tables[table_name]

    if key not in df.columns:
        issues.append(f"{table_name}: missing {key}")
        continue

    check(
        df[key].notna().all(),
        f"{table_name}: null primary keys"
    )

    check(
        df[key].is_unique,
        f"{table_name}: duplicate primary keys"
    )

# 3. Check foreign-key relationships
relationships = [
    ("inventory", "product_id", "products", "product_id"),
    ("inventory", "warehouse_id", "warehouses", "warehouse_id"),
    ("sales", "product_id", "products", "product_id"),
    ("offers", "product_id", "products", "product_id"),
    ("offers", "supplier_id", "suppliers", "supplier_id"),
    ("purchase_orders", "product_id", "products", "product_id"),
    ("purchase_orders", "supplier_id", "suppliers", "supplier_id"),
    ("purchase_orders", "warehouse_id", "warehouses", "warehouse_id"),
    ("deliveries", "order_id", "sales", "order_id"),
    ("movements", "product_id", "products", "product_id"),
    ("movements", "warehouse_id", "warehouses", "warehouse_id")
]

for child, child_key, parent, parent_key in relationships:
    if child not in tables or parent not in tables:
        continue

    c = tables[child]
    p = tables[parent]

    if child_key not in c or parent_key not in p:
        issues.append(
            f"Missing relationship column: "
            f"{child}.{child_key} -> {parent}.{parent_key}"
        )
        continue

    check(
        c[child_key].notna().all(),
        f"{child}: null foreign keys in {child_key}"
    )

    check(
        c[child_key].isin(p[parent_key]).all(),
        f"Broken FK: {child}.{child_key} -> "
        f"{parent}.{parent_key}"
    )

# 4. Check sales calculations
if "sales" in tables:
    sales = tables["sales"]

    expected = (
        sales["quantity"] * sales["unit_price"]
    )

    check(
        ((sales["revenue"] - expected).abs() < 0.01).all(),
        "Sales revenue calculation mismatch"
    )

    check(
        (sales["quantity"] > 0).all(),
        "Sales contains invalid quantities"
    )

# 5. Check purchase-order calculations
if "purchase_orders" in tables:
    po = tables["purchase_orders"]

    expected = po["quantity"] * po["unit_cost"]

    check(
        ((po["total_cost"] - expected).abs() < 0.01).all(),
        "Purchase order total calculation mismatch"
    )

    created = pd.to_datetime(po["created_date"])
    expected_delivery = pd.to_datetime(
        po["expected_delivery_date"]
    )

    check(
        (expected_delivery >= created).all(),
        "Purchase order delivery before creation"
    )

# 6. Check logistics chronology
if "deliveries" in tables:
    deliveries = tables["deliveries"]

    dispatch = pd.to_datetime(
        deliveries["dispatch_date"]
    )
    promised = pd.to_datetime(
        deliveries["promised_date"]
    )
    actual = pd.to_datetime(
        deliveries["actual_delivery_date"],
        errors="coerce"
    )

    check(
        (promised >= dispatch).all(),
        "Delivery promised before dispatch"
    )

    valid_actual = actual.notna()

    check(
        (
            actual[valid_actual]
            >= dispatch[valid_actual]
        ).all(),
        "Delivery completed before dispatch"
    )

# 7. Check finance references
if "finance" in tables:
    finance = tables["finance"]

    check(
        (finance["amount"] > 0).all(),
        "Finance contains non-positive amounts"
    )

    if "sales" in tables:
        receipts = finance[
            finance["transaction_type"] == "Customer Receipt"
        ]

        check(
            receipts["reference_id"].isin(
                tables["sales"]["order_id"]
            ).all(),
            "Customer receipt references invalid sales orders"
        )

    if "purchase_orders" in tables:
        payments = finance[
            finance["transaction_type"] == "Supplier Payment"
        ]

        check(
            payments["reference_id"].isin(
                tables["purchase_orders"]["po_id"]
            ).all(),
            "Supplier payments reference invalid purchase orders"
        )

# 8. Generate audit report
report = {
    "project": "BizPilot AI",
    "audit": "Enterprise Dataset Consistency",
    "datasets_found": len(tables),
    "datasets_expected": len(files),
    "record_counts": {
        name: len(df)
        for name, df in tables.items()
    },
    "issues_found": len(issues),
    "issues": issues,
    "status": "PASS" if not issues else "FAIL"
}

output = RESULTS / "dataset_audit_report.json"

with open(output, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print("\nBIZPILOT AI — DATASET AUDIT")
print("=" * 50)
print("Datasets:", len(tables), "/", len(files))
print("Issues found:", len(issues))
print("Status:", report["status"])

for issue in issues:
    print(" -", issue)

print("\nReport saved:", output)

if issues:
    raise SystemExit(1)
