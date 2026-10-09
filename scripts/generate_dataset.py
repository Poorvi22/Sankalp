
from pathlib import Path
import random
import pandas as pd
from faker import Faker

random.seed(42)
Faker.seed(42)
fake = Faker("en_IN")

OUTPUT = Path(__file__).resolve().parents[1] / "data" / "synthetic"
OUTPUT.mkdir(parents=True, exist_ok=True)

# 1. Products
products = []

categories = [
    "Electronics",
    "Packaging",
    "Industrial Parts",
    "Office Supplies",
    "Safety Equipment"
]

for i in range(1, 501):
    cost = round(random.uniform(100, 5000), 2)

    products.append({
        "product_id": f"PRD-{i:04d}",
        "product_name": f"Product {i}",
        "category": random.choice(categories),
        "unit_cost": cost,
        "selling_price": round(cost * 1.30, 2),
        "reorder_level": random.randint(20, 100)
    })

# 2. Suppliers
suppliers = []

for i in range(1, 51):
    suppliers.append({
        "supplier_id": f"SUP-{i:03d}",
        "supplier_name": fake.company(),
        "lead_time_days": random.randint(2, 25),
        "reliability_score": round(
            random.uniform(0.70, 0.99), 2
        )
    })

# 3. Warehouses
cities = [
    "Bengaluru",
    "Mumbai",
    "Delhi",
    "Hyderabad",
    "Chennai"
]

warehouses = [
    {
        "warehouse_id": f"WH-{i:03d}",
        "warehouse_name": f"{city} Warehouse",
        "city": city
    }
    for i, city in enumerate(cities, 1)
]

# 4. Inventory
inventory = []

for i, product in enumerate(products, 1):
    warehouse = random.choice(warehouses)
    stock = random.randint(0, 300)

    inventory.append({
        "inventory_id": f"INV-{i:05d}",
        "product_id": product["product_id"],
        "warehouse_id": warehouse["warehouse_id"],
        "quantity_available": stock,
        "reorder_level": product["reorder_level"],
        "stock_status": (
            "Low Stock"
            if stock < product["reorder_level"]
            else "Available"
        )
    })

datasets = {
    "products": products,
    "suppliers": suppliers,
    "warehouses": warehouses,
    "inventory": inventory
}

for name, records in datasets.items():
    df = pd.DataFrame(records)
    df.to_csv(OUTPUT / f"{name}.csv", index=False)
    print(f"{name}.csv: {len(df)} records")

print("Dataset generation completed!")
