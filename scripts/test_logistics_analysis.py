
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"

deliveries = pd.read_csv(DATA / "deliveries.csv")

delayed = deliveries[
    deliveries["delivery_status"] == "Delayed"
].copy()

delayed["promised_date"] = pd.to_datetime(
    delayed["promised_date"]
)

delayed["actual_delivery_date"] = pd.to_datetime(
    delayed["actual_delivery_date"]
)

delayed["delay_days"] = (
    delayed["actual_delivery_date"] -
    delayed["promised_date"]
).dt.days

print("Total deliveries:", len(deliveries))
print("Delayed deliveries:", len(delayed))

if not delayed.empty:
    print("Average delay days:", round(
        delayed["delay_days"].mean(), 2
    ))

    print("Shipping cost for delayed deliveries: ₹", round(
        delayed["shipping_cost"].sum(), 2
    ))

    print("\nTop delayed deliveries:")
    print(
        delayed.sort_values(
            "delay_days", ascending=False
        )[[
            "delivery_id",
            "order_id",
            "delay_days",
            "shipping_cost"
        ]].head(10).to_string(index=False)
    )
