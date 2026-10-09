
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evaluation" / "results"

methods = ["tfidf", "faiss", "hybrid"]
reports = {}

for method in methods:
    path = RESULTS / f"{method}_retrieval_report.json"

    if not path.exists():
        raise SystemExit(
            f"Missing report: {path}\n"
            f"Run evaluation for {method} first."
        )

    with open(path, encoding="utf-8") as f:
        reports[method] = json.load(f)

metrics = [
    "hit_at_1",
    "hit_at_5",
    "precision_at_5",
    "recall_at_5",
    "mrr_at_5"
]

print("\nBIZPILOT AI — RETRIEVAL COMPARISON")
print("=" * 68)
print(
    f"{'Metric':<22}"
    f"{'TF-IDF':>14}"
    f"{'FAISS':>14}"
    f"{'Hybrid':>14}"
)
print("-" * 68)

for metric in metrics:
    values = [
        reports[m][metric] * 100
        for m in methods
    ]

    print(
        f"{metric:<22}"
        + "".join(f"{v:>13.2f}%" for v in values)
    )

print("-" * 68)

print("\nLATENCY COMPARISON")
print("-" * 68)

latency_metrics = [
    "average_retrieval_ms",
    "p50_retrieval_ms",
    "p95_retrieval_ms"
]

for metric in latency_metrics:
    values = []

    for method in methods:
        value = reports[method].get(metric)
        values.append(
            f"{value:.3f} ms"
            if value is not None
            else "N/A"
        )

    print(
        f"{metric:<22}"
        + "".join(f"{v:>14}" for v in values)
    )

print("-" * 68)

best = max(
    methods,
    key=lambda m: (
        reports[m]["hit_at_1"],
        reports[m]["mrr_at_5"],
        reports[m]["recall_at_5"]
    )
)

print(f"\nBest method by accuracy: {best.upper()}")

comparison = {
    "project": "BizPilot AI",
    "benchmark_queries": reports["faiss"]["total_queries"],
    "methods": reports,
    "best_method_by_accuracy": best,
    "note": (
        "Accuracy results are from a small benchmark. "
        "Latency coverage differs between methods."
    )
}

output = RESULTS / "retrieval_comparison.json"

with open(output, "w", encoding="utf-8") as f:
    json.dump(comparison, f, indent=2)

print("Comparison saved to:", output)
