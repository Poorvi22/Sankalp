
from pathlib import Path
from datetime import date, timedelta
import random
import pandas as pd

random.seed(43)

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "synthetic"

products = pd.read_csv(DATA / "products.csv")

# 24 months: October 2024 to September 2026
START = date(2024, 10, 1)
END = date(2026, 9, 30)
DAYS = (END - START).days

regions = ["North", "South", "East", "West", "Central"]
statuses = ["Delivered", "Shipped", "Processing", "Cancelled"]
channels = ["Online", "Retail", "Distributor"]

orders = []

for i in range(1, 10001):
    product = products.iloc[random.randrange(len(products))]

    order_date = START + timedelta(
        days=random.randint(0, DAYS)
    )

    quantity = random.randint(1, 30)

    # Seasonal demand pattern
    seasonal_factor = (
        1.20 if order_date.month in [10, 11, 12]
        else 1.0
    )

    unit_price = round(
        float(product["selling_price"]) * seasonal_factor,
        2
    )

    status = random.choices(
        statuses,
        weights=[75, 10, 10, 5],
        k=1
    )[0]

    orders.append({
        "order_id": f"SO-{i:06d}",
        "order_date": order_date.isoformat(),
        "customer_id": f"CUS-{random.randint(1, 1000):04d}",
        "product_id": product["product_id"],
        "quantity": quantity,
        "unit_price": unit_price,
        "revenue": round(quantity * unit_price, 2),
        "region": random.choice(regions),
        "sales_channel": random.choice(channels),
        "status": status
    })

sales = pd.DataFrame(orders)

sales.to_csv(DATA / "sales_orders.csv", index=False)

print("Sales dataset generated successfully!")
print("Total orders:", len(sales))
print("Date range:", sales["order_date"].min(),
      "to", sales["order_date"].max())
print("Unique products:", sales["product_id"].nunique())
