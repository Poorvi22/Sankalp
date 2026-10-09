
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evaluation" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

retrieval_file = RESULTS / "faiss_retrieval_report.json"

retrieval = None

if retrieval_file.exists():
    with open(retrieval_file, encoding="utf-8") as f:
        retrieval = json.load(f)

retrieval_score = (
    retrieval.get("recall_at_3")
    if retrieval else None
)

retrieval_status = (
    "NOT TESTED"
    if retrieval_score is None
    else "PASS"
    if retrieval_score >= 0.95
    else "FAIL"
)

kpis = [
    {
        "id": 1,
        "name": "Intent Accuracy",
        "target": ">=95%",
        "actual": None,
        "status": "NOT TESTED"
    },
    {
        "id": 2,
        "name": "UI Accuracy",
        "target": ">=95%",
        "actual": None,
        "status": "NOT TESTED"
    },
    {
        "id": 3,
        "name": "Task Success",
        "target": ">=90%",
        "actual": None,
        "status": "NOT TESTED"
    },
    {
        "id": 4,
        "name": "Analytical Accuracy",
        "target": "<=1% error",
        "actual": None,
        "status": "NOT TESTED"
    },
    {
        "id": 5,
        "name": "Explanation Faithfulness",
        "target": ">=95%",
        "actual": None,
        "status": "NOT TESTED"
    },
    {
        "id": 6,
        "name": "Retrieval Quality",
        "target": "Recall@3 >=95%",
        "actual": retrieval_score,
        "status": retrieval_status,
        "sample_size": (
            retrieval.get("total_queries")
            if retrieval else 0
        ),
        "evidence": (
            str(retrieval_file.relative_to(ROOT))
            if retrieval else None
        )
    },
    {
        "id": 7,
        "name": "Safety and Reliability",
        "target": "Zero unauthorized actions",
        "actual": None,
        "status": "NOT TESTED"
    },
    {
        "id": 8,
        "name": "Performance and UX",
        "target": "Measured p50/p95 and usefulness",
        "actual": None,
        "status": "NOT TESTED"
    }
]

summary = {
    "project": "BizPilot AI",
    "problem": "5A Context-Aware Application Agent",
    "kpis": kpis
}

output = RESULTS / "kpi_summary.json"

with open(output, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("\nBIZPILOT AI — KPI SUMMARY")
print("=" * 65)

for kpi in kpis:
    print(
        f"KPI {kpi['id']}: "
        f"{kpi['name']:<28}"
        f"{kpi['status']}"
    )

print("\nSaved to:", output)
