
from pathlib import Path
import argparse
import json
import statistics

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

RESULTS = ROOT / "evaluation" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

GOLD = (
    ROOT / "data" / "benchmarks" /
    "retrieval_ground_truth.jsonl"
)

# --------------------------------------------------
# 2. COMMAND-LINE ARGUMENTS
# --------------------------------------------------

parser = argparse.ArgumentParser(
    description="BizPilot AI Retrieval KPI Evaluator"
)

parser.add_argument(
    "--method",
    choices=["tfidf", "faiss", "hybrid"],
    default="tfidf",
    help="Retrieval method to evaluate"
)

args = parser.parse_args()

# --------------------------------------------------
# 3. SELECT PREDICTION FILE
# --------------------------------------------------

prediction_files = {
    "tfidf": "retrieval_predictions.jsonl",
    "faiss": "faiss_predictions.jsonl",
    "hybrid": "hybrid_predictions.jsonl"
}

PRED = RESULTS / prediction_files[args.method]

REPORT = RESULTS / (
    f"{args.method}_retrieval_report.json"
)

# --------------------------------------------------
# 4. LOAD JSONL
# --------------------------------------------------

def load_jsonl(path):
    if not path.exists():
        raise SystemExit(
            f"\nERROR: File not found: {path}\n"
            "Generate predictions before evaluation."
        )

    records = []

    with open(path, encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            if not line.strip():
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at {path}, "
                    f"line {line_number}"
                ) from exc

    return records


gold = load_jsonl(GOLD)
pred = load_jsonl(PRED)

if not gold:
    raise SystemExit("ERROR: Benchmark is empty.")

# --------------------------------------------------
# 5. VALIDATE IDS
# --------------------------------------------------

gold_ids = [r["query_id"] for r in gold]
pred_ids = [r["query_id"] for r in pred]

assert len(gold_ids) == len(set(gold_ids)), (
    "Duplicate query IDs in ground truth"
)

assert len(pred_ids) == len(set(pred_ids)), (
    "Duplicate query IDs in predictions"
)

predictions = {
    r["query_id"]: r
    for r in pred
}

unknown_ids = set(pred_ids) - set(gold_ids)

if unknown_ids:
    raise ValueError(
        f"Unknown prediction IDs: {sorted(unknown_ids)}"
    )

# --------------------------------------------------
# 6. INITIALIZE KPI STORAGE
# --------------------------------------------------

precision_scores = []
recall_scores = []
reciprocal_ranks = []

hit_at_1 = []
hit_at_5 = []

latencies = []

missing_predictions = 0

# --------------------------------------------------
# 7. EVALUATE EVERY QUERY
# --------------------------------------------------

for case in gold:

    query_id = case["query_id"]
    relevant = set(case["relevant_ids"])

    if not relevant:
        raise ValueError(
            f"No relevant IDs for {query_id}"
        )

    prediction = predictions.get(query_id)

    if prediction is None:
        missing_predictions += 1
        retrieved = []
    else:
        retrieved = prediction.get(
            "retrieved_ids", []
        )[:5]

        latency = prediction.get(
            "retrieval_latency_ms"
        )

        if (
            isinstance(latency, (int, float))
            and not isinstance(latency, bool)
            and latency >= 0
        ):
            latencies.append(float(latency))

    if not isinstance(retrieved, list):
        raise ValueError(
            f"Invalid retrieved_ids for {query_id}"
        )

    if len(retrieved) != len(set(retrieved)):
        raise ValueError(
            f"Duplicate retrieved IDs for {query_id}"
        )

    # Precision@5
    hits = len(
        relevant.intersection(retrieved)
    )

    precision_scores.append(
        hits / 5
    )

    # Recall@5
    recall_scores.append(
        hits / len(relevant)
    )

    # Hit@1
    hit_at_1.append(
        int(
            bool(retrieved)
            and retrieved[0] in relevant
        )
    )

    # Hit@5
    hit_at_5.append(
        int(
            any(
                item in relevant
                for item in retrieved
            )
        )
    )

    # Reciprocal Rank
    rank = next(
        (
            i
            for i, item in enumerate(retrieved, 1)
            if item in relevant
        ),
        None
    )

    reciprocal_ranks.append(
        1 / rank if rank else 0
    )

# --------------------------------------------------
# 8. CALCULATE PERCENTILES
# --------------------------------------------------

def percentile(values, p):
    if not values:
        return None

    values = sorted(values)

    position = (
        (len(values) - 1) * p / 100
    )

    lower = int(position)
    upper = min(
        lower + 1,
        len(values) - 1
    )

    fraction = position - lower

    result = (
        values[lower] * (1 - fraction)
        + values[upper] * fraction
    )

    return round(result, 3)


# --------------------------------------------------
# 9. GENERATE KPI REPORT
# --------------------------------------------------

report = {
    "project": "BizPilot AI",
    "problem": "5A Context-Aware Application Agent",
    "retrieval_method": args.method,

    "total_queries": len(gold),
    "predictions_received": len(pred),
    "missing_predictions": missing_predictions,

    "hit_at_1": round(
        statistics.mean(hit_at_1), 4
    ),

    "hit_at_5": round(
        statistics.mean(hit_at_5), 4
    ),

    "precision_at_5": round(
        statistics.mean(precision_scores), 4
    ),

    "recall_at_5": round(
        statistics.mean(recall_scores), 4
    ),

    "mrr_at_5": round(
        statistics.mean(reciprocal_ranks), 4
    ),

    "latency_samples": len(latencies),

    "latency_coverage": round(
        len(latencies) / len(gold), 4
    ),

    "average_retrieval_ms": (
        round(statistics.mean(latencies), 3)
        if latencies else None
    ),

    "p50_retrieval_ms": percentile(
        latencies, 50
    ),

    "p95_retrieval_ms": percentile(
        latencies, 95
    )
}

# --------------------------------------------------
# 10. SAVE REPORT
# --------------------------------------------------

with open(
    REPORT,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        report,
        f,
        indent=2
    )

# --------------------------------------------------
# 11. DISPLAY RESULTS
# --------------------------------------------------

print("\n" + "=" * 55)
print("BIZPILOT AI — RETRIEVAL KPI EVALUATION")
print("=" * 55)

print("Method:", args.method.upper())
print("Total queries:", len(gold))
print("Missing predictions:", missing_predictions)

print("\nACCURACY METRICS")
print("-" * 55)

for metric in [
    "hit_at_1",
    "hit_at_5",
    "precision_at_5",
    "recall_at_5",
    "mrr_at_5"
]:
    print(
        f"{metric:<25}"
        f"{report[metric] * 100:.2f}%"
    )

print("\nLATENCY METRICS")
print("-" * 55)

if latencies:
    print(
        "Average retrieval:",
        report["average_retrieval_ms"],
        "ms"
    )

    print(
        "P50 retrieval:",
        report["p50_retrieval_ms"],
        "ms"
    )

    print(
        "P95 retrieval:",
        report["p95_retrieval_ms"],
        "ms"
    )
else:
    print(
        "No per-query latency measurements available."
    )

print("\nReport saved:", REPORT)
print("=" * 55)
