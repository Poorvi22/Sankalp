
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"

offers = pd.read_csv(DATA / "supplier_offers.csv")
suppliers = pd.read_csv(DATA / "suppliers.csv")

product_id = "PRD-0001"
quantity = 100

options = offers[
    offers["product_id"] == product_id
].merge(
    suppliers[["supplier_id", "supplier_name"]],
    on="supplier_id"
)

eligible = options[
    (options["reliability_score"] >= 0.80) &
    (options["minimum_order_quantity"] <= quantity)
].copy()

eligible["estimated_cost"] = (
    eligible["unit_cost"] * quantity
).round(2)

eligible = eligible.sort_values(
    ["estimated_cost", "lead_time_days"]
)

if eligible.empty:
    print("No eligible suppliers found.")
else:
    print(eligible[[
        "supplier_name",
        "unit_cost",
        "lead_time_days",
        "reliability_score",
        "estimated_cost"
    ]].to_string(index=False))

    best = eligible.iloc[0]

    print("\nRecommended supplier:", best["supplier_name"])
    print("Estimated cost: ₹", best["estimated_cost"])
