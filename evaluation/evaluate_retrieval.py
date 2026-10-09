
from pathlib import Path
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]

GOLD = ROOT / "data/benchmarks/retrieval_ground_truth.jsonl"
PRED = ROOT / "evaluation/results/retrieval_predictions.jsonl"
REPORT = ROOT / "evaluation/results/retrieval_report.json"

def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

gold = load_jsonl(GOLD)
pred = load_jsonl(PRED)

assert len({x["query_id"] for x in gold}) == len(gold)
assert len({x["query_id"] for x in pred}) == len(pred)

predictions = {x["query_id"]: x for x in pred}

precision = []
recall = []
rr = []

for case in gold:
    relevant = set(case["relevant_ids"])

    retrieved = predictions.get(
        case["query_id"], {}
    ).get("retrieved_ids", [])[:5]

    assert len(retrieved) == len(set(retrieved)), \
        "Duplicate retrieved IDs"

    hits = len(relevant.intersection(retrieved))

    precision.append(hits / 5)
    recall.append(hits / len(relevant))

    rank = next(
        (i for i, item in enumerate(retrieved, 1)
         if item in relevant),
        None
    )

    rr.append(1 / rank if rank else 0)

report = {
    "queries": len(gold),
    "precision_at_5": round(statistics.mean(precision), 4),
    "recall_at_5": round(statistics.mean(recall), 4),
    "mrr_at_5": round(statistics.mean(rr), 4),
    "retrieval_method": "TF-IDF baseline"
}

REPORT.parent.mkdir(parents=True, exist_ok=True)

with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
