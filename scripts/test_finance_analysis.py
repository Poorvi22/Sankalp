
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"

finance = pd.read_csv(DATA / "finance_transactions.csv")
finance["transaction_date"] = pd.to_datetime(
    finance["transaction_date"]
)

finance["month"] = finance[
    "transaction_date"
].dt.to_period("M")

finance["signed_amount"] = finance.apply(
    lambda row: row["amount"]
    if row["direction"] == "Inflow"
    else -row["amount"],
    axis=1
)

monthly = finance.groupby("month").agg(
    cash_inflow=(
        "signed_amount",
        lambda x: x[x > 0].sum()
    ),
    cash_outflow=(
        "signed_amount",
        lambda x: -x[x < 0].sum()
    ),
    net_cash_flow=("signed_amount", "sum")
).reset_index()

print("\nMonthly cash flow:")
print(monthly.to_string(index=False))

total_inflow = finance.loc[
    finance["direction"] == "Inflow", "amount"
].sum()

total_outflow = finance.loc[
    finance["direction"] == "Outflow", "amount"
].sum()

print("\nTotal cash inflow: ₹", round(total_inflow, 2))
print("Total cash outflow: ₹", round(total_outflow, 2))
print("Net cash flow: ₹", round(
    total_inflow - total_outflow, 2
))
