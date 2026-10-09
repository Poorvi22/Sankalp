
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"

sales = pd.read_csv(DATA / "sales_orders.csv")

# Only delivered orders count as recognized revenue.
sales = sales[sales["status"] == "Delivered"].copy()

sales["order_date"] = pd.to_datetime(sales["order_date"])
sales["month"] = sales["order_date"].dt.to_period("M")

monthly = (
    sales.groupby("month")["revenue"]
    .sum()
    .reset_index()
)

print("\nMonthly recognized revenue:")
print(monthly.to_string(index=False))

if len(monthly) >= 2:
    previous = monthly.iloc[-2]["revenue"]
    current = monthly.iloc[-1]["revenue"]

    if previous != 0:
        change = ((current - previous) / previous) * 100
        print(f"\nLatest month-over-month change: {change:.2f}%")
    else:
        print("\nPrevious month revenue is zero.")
