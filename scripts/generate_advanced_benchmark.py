
from pathlib import Path
import json
import random

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "metadata"
OUT = ROOT / "data" / "benchmarks"
OUT.mkdir(parents=True, exist_ok=True)

random.seed(52)

with open(META / "application_metadata.json", encoding="utf-8") as f:
    app = json.load(f)

with open(META / "api_registry.json", encoding="utf-8") as f:
    registry = json.load(f)

pages = app["pages"]
apis = registry["apis"]

# Natural-language queries written separately from metadata descriptions.
page_queries = {
    "PAGE_DASHBOARD": [
        "How is the whole company doing?",
        "Give me a quick overview of business health",
        "What needs the owner's attention today?"
    ],
    "PAGE_INVENTORY": [
        "Which items are running out?",
        "Where do I check warehouse stock?",
        "Find products that need replenishment"
    ],
    "PAGE_SUPPLIERS": [
        "Which vendors are dependable?",
        "Where can I compare vendor prices?",
        "Find suppliers with shorter lead times"
    ],
    "PAGE_PROCUREMENT": [
        "Where do I prepare buying requests?",
        "Show purchasing paperwork",
        "I need to order more materials"
    ],
    "PAGE_SALES": [
        "What are customers buying?",
        "Show customer order activity",
        "Which products sold the most?"
    ],
    "PAGE_LOGISTICS": [
        "Which shipments missed their deadline?",
        "Where are my deliveries?",
        "Show transportation delays"
    ],
    "PAGE_FINANCE": [
        "Where is the company's money going?",
        "Show money received and paid",
        "What are our outstanding expenses?"
    ],
    "PAGE_ANALYTICS": [
        "Compare this quarter with last quarter",
        "Find long-term business trends",
        "Analyze our performance over two years"
    ],
    "PAGE_APPROVALS": [
        "What decisions are waiting for authorization?",
        "Where do I approve purchase requests?",
        "Show pending sign-offs"
    ],
    "PAGE_AGENT_ACTIVITY": [
        "What actions did the assistant perform?",
        "Show the chatbot's execution history",
        "Where can I inspect failed agent tasks?"
    ]
}

cases = []

def add_case(query, relevant_ids, category):
    cases.append({
        "query_id": f"ADV-{len(cases)+1:04d}",
        "query": query,
        "relevant_ids": relevant_ids,
        "category": category
    })

valid_page_ids = {p["page_id"] for p in pages}

# 1. Page retrieval cases
for page_id, queries in page_queries.items():
    if page_id not in valid_page_ids:
        continue

    for query in queries:
        add_case(query, [page_id], "page")

# 2. Widget retrieval cases
for page in pages:
    for widget in page.get("widgets", []):
        widget_type = widget.get("type", "component")

        add_case(
            f"Find the {widget_type.replace('_', ' ')} "
            f"for {page['name'].lower()}",
            [widget["widget_id"]],
            "widget"
        )

# 3. API retrieval cases
for api in apis:
    add_case(
        f"Which service should handle: "
        f"{api['description'].lower()}?",
        [api["api_id"]],
        "api"
    )

# 4. Filter retrieval cases
for page in pages:
    for item in page.get("filters", []):
        filter_id = item["filter_id"]

        add_case(
            f"Where can I filter {page['name'].lower()} "
            f"by {filter_id.replace('_', ' ')}?",
            [page["page_id"]],
            "filter"
        )

# 5. Additional paraphrases, if needed
base_cases = list(cases)

while len(cases) < 100:
    original = random.choice(base_cases)

    add_case(
        "Please help me with this: " + original["query"],
        original["relevant_ids"],
        original["category"]
    )

# Save exactly 100 cases
cases = cases[:100]

output = OUT / "advanced_retrieval_ground_truth.jsonl"

with open(output, "w", encoding="utf-8") as f:
    for case in cases:
        f.write(json.dumps(case) + "\n")

print("Advanced benchmark generated:", len(cases))
print("Saved to:", output)
