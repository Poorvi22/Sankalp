
from pathlib import Path
import argparse
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evaluation" / "results"
GOLD = ROOT / "data" / "benchmarks" / "retrieval_ground_truth.jsonl"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--method",
    choices=["tfidf", "faiss", "hybrid"],
    default="faiss"
)
args = parser.parse_args()

files = {
    "tfidf": "retrieval_predictions.jsonl",
    "faiss": "faiss_predictions.jsonl",
    "hybrid": "hybrid_predictions.jsonl"
}

PRED = RESULTS / files[args.method]
REPORT = RESULTS / f"{args.method}_retrieval_report.json"


def load_jsonl(path):
    if not path.exists():
        raise SystemExit(f"Missing file: {path}")

    with open(path, encoding="utf-8") as f:
        return [
            json.loads(line)
            for line in f
            if line.strip()
        ]


gold = load_jsonl(GOLD)
pred = load_jsonl(PRED)

if not gold:
    raise SystemExit("Ground truth is empty.")

gold_ids = [r["query_id"] for r in gold]
pred_ids = [r["query_id"] for r in pred]

if len(gold_ids) != len(set(gold_ids)):
    raise ValueError("Duplicate ground-truth query IDs")

if len(pred_ids) != len(set(pred_ids)):
    raise ValueError("Duplicate prediction query IDs")

unknown = set(pred_ids) - set(gold_ids)
if unknown:
    raise ValueError(f"Unknown prediction IDs: {unknown}")

pred_map = {r["query_id"]: r for r in pred}

precision_1 = []
recall_3 = []
reciprocal_rank = []
hit_1 = []
hit_5 = []
latencies = []

for case in gold:
    relevant = set(case["relevant_ids"])
    if not relevant:
        raise ValueError("Empty relevant IDs")

    result = pred_map.get(case["query_id"], {})
    retrieved = result.get("retrieved_ids", [])

    if not isinstance(retrieved, list):
        raise ValueError("retrieved_ids must be a list")

    if len(retrieved) != len(set(retrieved)):
        raise ValueError("Duplicate retrieved IDs")

    top1 = retrieved[:1]
    top3 = retrieved[:3]
    top5 = retrieved[:5]

    precision_1.append(
        len(relevant.intersection(top1))
    )

    recall_3.append(
        len(relevant.intersection(top3)) / len(relevant)
    )

    hit_1.append(
        int(bool(top1) and top1[0] in relevant)
    )

    hit_5.append(
        int(any(x in relevant for x in top5))
    )

    rank = next(
        (
            i for i, item in enumerate(retrieved, 1)
            if item in relevant
        ),
        None
    )

    reciprocal_rank.append(
        1 / rank if rank else 0
    )

    latency = result.get("retrieval_latency_ms")
    if (
        isinstance(latency, (int, float))
        and not isinstance(latency, bool)
        and latency >= 0
    ):
        latencies.append(float(latency))


def average(values):
    return round(statistics.mean(values), 4)


def percentile(values, p):
    if not values:
        return None

    ordered = sorted(values)
    position = (len(ordered) - 1) * p / 100
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower

    return round(
        ordered[lower] * (1 - fraction)
        + ordered[upper] * fraction,
        3
    )


report = {
    "project": "BizPilot AI",
    "problem": "5A Context-Aware Application Agent",
    "method": args.method,
    "total_queries": len(gold),
    "predictions_received": len(pred),
    "precision_at_1": average(precision_1),
    "recall_at_3": average(recall_3),
    "mrr": average(reciprocal_rank),
    "hit_at_1": average(hit_1),
    "hit_at_5": average(hit_5),
    "latency_samples": len(latencies),
    "latency_coverage": round(
        len(latencies) / len(gold), 4
    ),
    "average_retrieval_ms": (
        round(statistics.mean(latencies), 3)
        if latencies else None
    ),
    "p50_retrieval_ms": percentile(latencies, 50),
    "p95_retrieval_ms": percentile(latencies, 95)
}

RESULTS.mkdir(parents=True, exist_ok=True)

with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print("\nBIZPILOT AI — RETRIEVAL KPI")
print("=" * 50)
print("Method:", args.method.upper())
print("Queries:", len(gold))
print("Precision@1:", f"{report['precision_at_1']:.2%}")
print("Recall@3:", f"{report['recall_at_3']:.2%}")
print("MRR:", f"{report['mrr']:.2%}")
print("Hit@1:", f"{report['hit_at_1']:.2%}")
print("Hit@5:", f"{report['hit_at_5']:.2%}")
print("P50 latency:", report["p50_retrieval_ms"], "ms")
print("P95 latency:", report["p95_retrieval_ms"], "ms")
print("Saved:", REPORT)
