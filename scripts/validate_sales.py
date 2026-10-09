
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"

sales = pd.read_csv(DATA / "sales_orders.csv")
products = pd.read_csv(DATA / "products.csv")

assert len(sales) == 10000
assert sales["order_id"].is_unique
assert sales["product_id"].isin(products["product_id"]).all()
assert (sales["quantity"] > 0).all()
assert (sales["unit_price"] > 0).all()

expected = sales["quantity"] * sales["unit_price"]

assert ((sales["revenue"] - expected).abs() < 0.01).all()

dates = pd.to_datetime(sales["order_date"])

assert dates.between(
    "2024-10-01", "2026-09-30"
).all()

# Cancelled orders should not count as realized sales.
realized = sales[
    sales["status"].isin(["Delivered", "Shipped"])
]

print("Validation passed!")
print("Total orders:", len(sales))
print("Gross order value:", round(sales["revenue"].sum(), 2))
print("Fulfilled/shipped order value:",
      round(realized["revenue"].sum(), 2))
print("Unique products:", sales["product_id"].nunique())
