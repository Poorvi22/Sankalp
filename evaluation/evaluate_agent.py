
from pathlib import Path
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]

GOLD = ROOT / "data/benchmarks/intent_benchmark.jsonl"
PRED = ROOT / "evaluation/results/agent_predictions.jsonl"
REPORT = ROOT / "evaluation/results/kpi_report.json"


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [
            json.loads(line)
            for line in f if line.strip()
        ]


def percentile(values, p):
    values = sorted(values)

    if not values:
        return None

    position = (len(values) - 1) * p / 100
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    fraction = position - lower

    return (
        values[lower] * (1 - fraction)
        + values[upper] * fraction
    )


def normalize(value):
    if isinstance(value, dict):
        return {
            k: normalize(v)
            for k, v in sorted(value.items())
        }

    if isinstance(value, list):
        return [normalize(v) for v in value]

    return value

gold_records = load_jsonl(GOLD)

if not PRED.exists():
    print("Agent predictions are not available yet.")
    print("Expected file:", PRED)
    print("Ask the AI agent developer to generate predictions.")
    print("KPI evaluation will run after integration.")
    raise SystemExit(0)

pred_records = load_jsonl(PRED)

gold = {r["test_id"]: r for r in gold_records}
pred = {r["test_id"]: r for r in pred_records}

assert len(gold) == len(gold_records), "Duplicate gold IDs"
assert len(pred) == len(pred_records), "Duplicate prediction IDs"

unknown_ids = set(pred) - set(gold)
assert not unknown_ids, f"Unknown test IDs: {unknown_ids}"

total = len(gold)
intent_correct = 0
destination_correct = 0
ui_correct = 0
ui_total = 0
task_correct = 0
latencies = []
unsupported = 0
action_attempts = 0

for test_id, expected in gold.items():
    actual = pred.get(test_id)

    # Missing predictions count as failures.
    if actual is None:
        if expected["expected_ui_state"]:
            ui_total += 1
        continue

    intent_correct += (
        actual.get("predicted_intent") == expected["intent"]
    )

    destination_correct += (
        actual.get("predicted_page_id")
        == expected["target_page_id"]
    )

    if expected["expected_ui_state"]:
        ui_total += 1

        ui_correct += (
            normalize(actual.get("actual_ui_state", {}))
            == normalize(expected["expected_ui_state"])
        )

    # Only count verified completion.
    task_correct += bool(
        actual.get("task_completed", False)
        and actual.get("verified", False)
    )

    latency = actual.get("latency_ms")

    if isinstance(latency, (int, float)) and latency >= 0:
        latencies.append(latency)

    unsupported += actual.get(
        "unsupported_action_attempts", 0
    )

    action_attempts += len(
        actual.get("executed_actions", [])
    )

report = {
    "total_test_cases": total,
    "predictions_received": len(pred),
    "intent_accuracy": round(intent_correct / total, 4),
    "destination_accuracy": round(
        destination_correct / total, 4
    ),
    "ui_state_correctness": round(
        ui_correct / ui_total, 4
    ) if ui_total else None,
    "verified_task_completion_rate": round(
        task_correct / total, 4
    ),
    "latency_coverage": round(
        len(latencies) / total, 4
    ),
    "latency_p50_ms": percentile(latencies, 50),
    "latency_p95_ms": percentile(latencies, 95),
    "average_latency_ms": round(
        statistics.mean(latencies), 2
    ) if latencies else None,
    "unsupported_action_attempts": unsupported,
    "unsupported_action_rate": round(
        unsupported / action_attempts, 4
    ) if action_attempts else None
}

REPORT.parent.mkdir(parents=True, exist_ok=True)

with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
