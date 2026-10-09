
from pathlib import Path
import json
import random

random.seed(47)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "benchmarks"
OUTPUT.mkdir(parents=True, exist_ok=True)

# Each scenario includes its expected outcome.
scenarios = [
    {
        "intent": "navigate",
        "page_id": "PAGE_INVENTORY",
        "utterances": [
            "Open inventory",
            "Show the stock page",
            "Take me to warehouse inventory",
            "Where can I see product stock?",
            "Navigate to inventory management"
        ],
        "ui_state": {},
        "actions": ["navigate"]
    },
    {
        "intent": "filter",
        "page_id": "PAGE_INVENTORY",
        "utterances": [
            "Show low-stock products",
            "Find products below reorder level",
            "Which items need restocking?",
            "Filter inventory by low stock",
            "Display products running low"
        ],
        "ui_state": {
            "stock_status": "low_stock"
        },
        "actions": ["navigate", "apply_filter"]
    },
    {
        "intent": "filter",
        "page_id": "PAGE_SALES",
        "utterances": [
            "Show delivered orders",
            "Filter sales by delivered status",
            "Display completed customer orders",
            "Find all delivered sales",
            "Open fulfilled orders"
        ],
        "ui_state": {
            "status": "Delivered"
        },
        "actions": ["navigate", "apply_filter"]
    },
    {
        "intent": "analysis",
        "page_id": "PAGE_ANALYTICS",
        "utterances": [
            "Compare this quarter's revenue with last quarter",
            "How did revenue change quarter over quarter?",
            "Show quarterly revenue comparison",
            "Analyze revenue growth between quarters",
            "Compare current and previous quarter sales"
        ],
        "ui_state": {},
        "actions": [
            "navigate", "query_data", "compare_periods"
        ]
    },
    {
        "intent": "analysis",
        "page_id": "PAGE_SUPPLIERS",
        "utterances": [
            "Find the cheapest reliable supplier",
            "Compare suppliers by price and delivery time",
            "Which supplier has the best reliability?",
            "Rank suppliers by cost and lead time",
            "Show the best supplier options"
        ],
        "ui_state": {},
        "actions": [
            "navigate", "query_data", "rank_suppliers"
        ]
    },
    {
        "intent": "create_draft",
        "page_id": "PAGE_PROCUREMENT",
        "utterances": [
            "Prepare a purchase order draft",
            "Create a draft PO for low-stock products",
            "Fill a new purchase order form",
            "Prepare replenishment purchase orders",
            "Generate purchase order drafts"
        ],
        "ui_state": {},
        "actions": [
            "navigate", "query_data",
            "populate_form", "preview_draft"
        ]
    },
    {
        "intent": "analysis",
        "page_id": "PAGE_LOGISTICS",
        "utterances": [
            "Show delayed deliveries",
            "Which shipments are late?",
            "Find overdue customer deliveries",
            "Analyze delayed shipments",
            "Show delivery performance problems"
        ],
        "ui_state": {
            "delivery_status": "Delayed"
        },
        "actions": [
            "navigate", "apply_filter", "query_data"
        ]
    },
    {
        "intent": "analysis",
        "page_id": "PAGE_FINANCE",
        "utterances": [
            "Show monthly cash flow",
            "Compare cash inflows and outflows",
            "Analyze business cash movement",
            "Open cash flow report",
            "Summarize monthly payments and receipts"
        ],
        "ui_state": {},
        "actions": [
            "navigate", "query_data", "summarize"
        ]
    },
    {
        "intent": "explain_page",
        "page_id": "PAGE_DASHBOARD",
        "utterances": [
            "What does this dashboard show?",
            "Explain the current page",
            "Describe these business KPIs",
            "What information is on this page?",
            "Help me understand this dashboard"
        ],
        "ui_state": {},
        "actions": ["explain_current_page"]
    },
    {
        "intent": "multi_step",
        "page_id": "PAGE_ANALYTICS",
        "utterances": [
            "Analyze stockout risk and prepare purchase orders",
            "Find products running low and compare suppliers",
            "Review inventory risks and create replenishment drafts",
            "Estimate stock shortages and purchasing costs",
            "Plan stock replenishment based on sales demand"
        ],
        "ui_state": {},
        "actions": [
            "query_sales",
            "query_inventory",
            "estimate_demand",
            "compare_suppliers",
            "populate_form",
            "preview_draft"
        ]
    }
]

records = []

# Generate 300 benchmark requests.
for i in range(300):
    scenario = scenarios[i % len(scenarios)]

    # Template-based paraphrases.
    utterance = random.choice(scenario["utterances"])

    records.append({
        "test_id": f"TEST-{i+1:04d}",
        "utterance": utterance,
        "intent": scenario["intent"],
        "target_page_id": scenario["page_id"],
        "expected_ui_state": scenario["ui_state"],
        "expected_actions": scenario["actions"],
        "split": (
            "test" if i % 5 == 0
            else "validation" if i % 5 == 1
            else "train"
        )
    })

with open(
    OUTPUT / "intent_benchmark.jsonl",
    "w",
    encoding="utf-8"
) as file:
    for record in records:
        file.write(json.dumps(record) + "\n")

print("Benchmark generated!")
print("Total requests:", len(records))
print("Scenarios:", len(scenarios))
