import csv
from pathlib import Path
from collections import defaultdict


# Locate the project root regardless of the terminal's current directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUSINESS_DATA_DIR = PROJECT_ROOT / "data" / "business"


def load_csv(filename):
    """Load a business CSV file and return its records."""

    file_path = BUSINESS_DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Business dataset not found: {filename}"
        )

    with file_path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        return list(csv.DictReader(file))


def analyze_sales():
    """
    Calculate sales metrics using the existing business datasets.

    Cancelled orders are excluded from recognized sales.
    Returned figures describe the CSV dataset, not necessarily
    a company's live operational records.
    """

    orders = load_csv("sales_orders.csv")
    products = load_csv("products.csv")

    product_names = {
        product["product_id"]: product["product_name"]
        for product in products
    }

    valid_statuses = {
        "delivered",
        "shipped",
        "completed",
    }

    recognized_orders = [
        order
        for order in orders
        if order.get("status", "").strip().lower()
        in valid_statuses
    ]

    total_revenue = sum(
        float(order["revenue"])
        for order in recognized_orders
    )

    total_orders = len(orders)
    recognized_count = len(recognized_orders)

    cancelled_count = sum(
        1
        for order in orders
        if order.get("status", "").strip().lower()
        == "cancelled"
    )

    revenue_by_region = defaultdict(float)
    revenue_by_product = defaultdict(float)

    for order in recognized_orders:
        revenue = float(order["revenue"])

        region = order.get("region", "Unknown")
        product_id = order.get("product_id", "Unknown")

        revenue_by_region[region] += revenue
        revenue_by_product[product_id] += revenue

    top_products = sorted(
        [
            {
                "product_id": product_id,
                "product_name": product_names.get(
                    product_id,
                    product_id,
                ),
                "revenue": round(revenue, 2),
            }
            for product_id, revenue
            in revenue_by_product.items()
        ],
        key=lambda item: item["revenue"],
        reverse=True,
    )[:10]

    regional_performance = sorted(
        [
            {
                "region": region,
                "revenue": round(revenue, 2),
            }
            for region, revenue in revenue_by_region.items()
        ],
        key=lambda item: item["revenue"],
        reverse=True,
    )

    return {
        "data_source": "demo_csv",
        "dataset": "sales_orders.csv",
        "total_orders": total_orders,
        "recognized_orders": recognized_count,
        "cancelled_orders": cancelled_count,
        "recognized_revenue": round(total_revenue, 2),
        "average_recognized_order_value": round(
            total_revenue / recognized_count,
            2,
        ) if recognized_count else 0,
        "top_products": top_products,
        "regional_performance": regional_performance,
    }
def analyze_inventory():
    """Calculate inventory levels and identify products needing restocking."""

    inventory = load_csv("inventory.csv")
    products = load_csv("products.csv")

    product_details = {
        product["product_id"]: product
        for product in products
    }

    total_on_hand = 0
    total_reserved = 0
    total_available = 0
    low_stock_items = []
    inventory_summary = []

    for item in inventory:
        product_id = item["product_id"]

        on_hand = int(item["on_hand"])
        reserved = int(item["reserved"])
        reorder_point = int(item["reorder_point"])

        available = max(0, on_hand - reserved)

        total_on_hand += on_hand
        total_reserved += reserved
        total_available += available

        product = product_details.get(product_id, {})

        target_stock = int(product.get("target_stock", 0))

        # Compare available stock against the inventory reorder point.
        needs_restock = available <= reorder_point

        # Calculate how many units are required to reach the target.
        restock_quantity = max(0, target_stock - available)

        record = {
            "product_id": product_id,
            "product_name": product.get(
                "product_name",
                product_id,
            ),
            "warehouse_id": item["warehouse_id"],
            "on_hand": on_hand,
            "reserved": reserved,
            "available": available,
            "reorder_point": reorder_point,
            "target_stock": target_stock,
            "needs_restock": needs_restock,
            "suggested_restock_quantity": restock_quantity,
        }

        inventory_summary.append(record)

        if needs_restock:
            low_stock_items.append(record)

    low_stock_items.sort(
        key=lambda item: item["available"]
    )

    return {
        "data_source": "demo_csv",
        "dataset": "inventory.csv",
        "total_inventory_records": len(inventory),
        "total_on_hand": total_on_hand,
        "total_reserved": total_reserved,
        "total_available": total_available,
        "low_stock_count": len(low_stock_items),
        "low_stock_items": low_stock_items,
        "inventory_records": inventory_summary,
    }