
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"


def get_low_stock_products():
    inventory = pd.read_csv(
        DATA / "inventory.csv"
    )

    products = pd.read_csv(
        DATA / "products.csv"
    )

    low_stock = inventory[
        inventory["quantity_available"]
        < inventory["reorder_level"]
    ]

    result = low_stock.merge(
        products[
            ["product_id", "product_name"]
        ],
        on="product_id",
        how="left"
    )

    return result.to_dict(
        orient="records"
    )


def compare_suppliers(product_id, quantity):
    offers = pd.read_csv(
        DATA / "supplier_offers.csv"
    )

    suppliers = pd.read_csv(
        DATA / "suppliers.csv"
    )

    eligible = offers[
        (offers["product_id"] == product_id)
        & (offers["minimum_order_quantity"] <= quantity)
        & (offers["reliability_score"] >= 0.80)
    ].copy()

    eligible["estimated_cost"] = (
        eligible["unit_cost"] * quantity
    ).round(2)

    result = eligible.merge(
        suppliers[
            ["supplier_id", "supplier_name"]
        ],
        on="supplier_id",
        how="left"
    )

    result = result.sort_values(
        ["estimated_cost", "lead_time_days"]
    )

    return result.to_dict(
        orient="records"
    )


if __name__ == "__main__":
    print("\nLOW STOCK PRODUCTS")
    print(get_low_stock_products()[:5])

    print("\nSUPPLIER COMPARISON")
    print(compare_suppliers("PRD-0001", 100))
