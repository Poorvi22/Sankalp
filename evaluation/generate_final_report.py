
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evaluation" / "results"
ADVANCED = RESULTS / "advanced" / "comparison.json"
AUDIT = RESULTS / "dataset_audit_report.json"

OUTPUT = ROOT / "docs" / "results"
OUTPUT.mkdir(parents=True, exist_ok=True)


def load_json(path):
    if not path.exists():
        return None

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def git_value(*args):
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


retrieval = load_json(ADVANCED)
audit = load_json(AUDIT)

# A successful audit is not proof that the
# actual agent has completed its workflows.
kpis = [
    ("Intent Accuracy", ">=95%", None, "NOT TESTED"),
    ("UI Accuracy", ">=95%", None, "NOT TESTED"),
    ("Task Success", ">=90%", None, "NOT TESTED"),
    ("Analytical Accuracy", "<=1% error", None, "NOT TESTED"),
    ("Explanation Faithfulness", ">=95%", None, "NOT TESTED"),
    ("Retrieval Quality", "Recall@3 >=95%", None, "NOT TESTED"),
    ("Safety and Reliability", "Zero unauthorized actions", None, "NOT TESTED"),
    ("Performance and UX", "Measure p50/p95", None, "NOT TESTED")
]

if retrieval and "faiss" in retrieval:
    score = retrieval["faiss"].get("recall_at_3")

    if score is not None:
        kpis[5] = (
            "Retrieval Quality",
            "Recall@3 >=95%",
            f"{score:.2%}",
            "PARTIAL"
        )

lines = [
    "# BizPilot AI — KPI Evidence Report",
    "",
    f"Generated: {datetime.now(timezone.utc).isoformat()}",
    f"Git branch: {git_value('branch', '--show-current')}",
    f"Git commit: {git_value('rev-parse', 'HEAD')}",
    "",
    "## KPI Summary",
    "",
    "| KPI | Target | Actual | Status |",
    "|---|---|---|---|"
]

for name, target, actual, status in kpis:
    lines.append(
        f"| {name} | {target} | {actual or 'Not measured'} | {status} |"
    )

lines += [
    "",
    "## Retrieval Evaluation",
    "",
    "Results below are from the offline metadata benchmark.",
    "They do not establish end-to-end agent task success.",
    ""
]

if retrieval:
    lines += [
        "| Method | P@1 | Recall@3 | MRR | p50 ms | p95 ms |",
        "|---|---:|---:|---:|---:|---:|"
    ]

    for method, values in retrieval.items():
        lines.append(
            f"| {method} "
            f"| {values['precision_at_1']:.2%} "
            f"| {values['recall_at_3']:.2%} "
            f"| {values['mrr']:.2%} "
            f"| {values['p50_latency_ms']:.3f} "
            f"| {values['p95_latency_ms']:.3f} |"
        )
else:
    lines.append("Advanced retrieval benchmark not available.")

lines += [
    "",
    "## Dataset Audit",
    ""
]

if audit:
    lines.append(
        f"Status: {audit.get('status', 'UNKNOWN')}"
    )
    lines.append(
        f"Issues found: {audit.get('issues_found', 'unknown')}"
    )

    for issue in audit.get("issues", []):
        lines.append(f"- {issue}")
else:
    lines.append("Dataset audit report not available.")

lines += [
    "",
    "## Evidence",
    "",
    "- `evaluation/results/advanced/comparison.json`",
    "- `evaluation/results/dataset_audit_report.json`",
    "- `data/benchmarks/advanced_retrieval_ground_truth.jsonl`",
    "",
    "## Limitations",
    "",
    "- Retrieval results are from an offline metadata benchmark.",
    "- The advanced benchmark may contain generated or template-derived queries.",
    "- End-to-end agent actions and UI state are not yet verified here.",
    "- Retrieval latency excludes model loading and index construction.",
    "- Agent response latency must be measured separately.",
    "",
    "## Next Actions",
    "",
    "1. Validate the dataset audit and resolve any issues.",
    "2. Review the advanced benchmark labels independently.",
    "3. Connect the agent to the application and backend APIs.",
    "4. Run authenticated end-to-end task tests.",
    "5. Measure all eight KPIs on the deployed application."
]

report = OUTPUT / "KPI_EVIDENCE_REPORT.md"
report.write_text("\n".join(lines), encoding="utf-8")

print("Final evidence report generated:")
print(report)
