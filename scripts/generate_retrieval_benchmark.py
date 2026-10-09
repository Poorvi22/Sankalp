
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
METADATA = ROOT / "data/metadata"
OUTPUT = ROOT / "data/benchmarks"
OUTPUT.mkdir(parents=True, exist_ok=True)

with open(METADATA / "application_metadata.json", encoding="utf-8") as f:
    app = json.load(f)

with open(METADATA / "api_registry.json", encoding="utf-8") as f:
    registry = json.load(f)

queries = {
    "PAGE_DASHBOARD": [
        "Where can I see overall business performance?",
        "Show the executive overview"
    ],
    "PAGE_INVENTORY": [
        "Where are the warehouse stock levels?",
        "Find the inventory management screen"
    ],
    "PAGE_SUPPLIERS": [
        "Where can I compare vendors?",
        "Show supplier reliability information"
    ],
    "PAGE_PROCUREMENT": [
        "Where do I manage purchase orders?",
        "Open procurement management"
    ],
    "PAGE_SALES": [
        "Where can I see customer sales orders?",
        "Find the sales performance page"
    ],
    "PAGE_LOGISTICS": [
        "Where are shipment delays tracked?",
        "Show the delivery management page"
    ],
    "PAGE_FINANCE": [
        "Where can I review cash flow?",
        "Find supplier payment information"
    ],
    "PAGE_ANALYTICS": [
        "Where can I compare monthly trends?",
        "Find historical business reports"
    ],
    "PAGE_APPROVALS": [
        "Where do I approve pending requests?",
        "Find purchase order approvals"
    ],
    "PAGE_AGENT_ACTIVITY": [
        "Where can I inspect agent execution logs?",
        "Show the agent performance history"
    ]
}

valid_pages = {p["page_id"] for p in app["pages"]}
records = []

for page_id, utterances in queries.items():
    assert page_id in valid_pages, f"Missing page: {page_id}"

    for utterance in utterances:
        records.append({
            "query_id": f"RET-{len(records)+1:03d}",
            "query": utterance,
            "relevant_ids": [page_id],
            "category": "page_retrieval"
        })

# API retrieval queries
for api in registry["apis"]:
    records.append({
        "query_id": f"RET-{len(records)+1:03d}",
        "query": api["description"],
        "relevant_ids": [api["api_id"]],
        "category": "api_retrieval"
    })

path = OUTPUT / "retrieval_ground_truth.jsonl"

with open(path, "w", encoding="utf-8") as f:
    for record in records:
        f.write(json.dumps(record) + "\n")

print("Retrieval benchmark generated:", len(records))
print("Saved to:", path)
