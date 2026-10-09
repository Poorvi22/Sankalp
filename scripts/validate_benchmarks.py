
from pathlib import Path
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

benchmark_file = (
    ROOT / "data" / "benchmarks" /
    "intent_benchmark.jsonl"
)

metadata_file = (
    ROOT / "data" / "metadata" /
    "application_metadata.json"
)

with open(metadata_file, encoding="utf-8") as f:
    metadata = json.load(f)

valid_pages = {
    page["page_id"]
    for page in metadata["pages"]
}

with open(benchmark_file, encoding="utf-8") as f:
    records = [
        json.loads(line)
        for line in f if line.strip()
    ]

assert len(records) == 300

ids = [r["test_id"] for r in records]
assert len(ids) == len(set(ids))

for record in records:
    assert record["target_page_id"] in valid_pages
    assert record["utterance"].strip()
    assert isinstance(record["expected_actions"], list)
    assert isinstance(record["expected_ui_state"], dict)

# Detect evaluation leakage:
# Identical requests must not appear across splits.
utterance_splits = {}

for record in records:
    text = " ".join(
        record["utterance"].lower().split()
    )

    utterance_splits.setdefault(text, set()).add(
        record["split"]
    )

leakage = {
    text: splits
    for text, splits in utterance_splits.items()
    if len(splits) > 1
}

print("Total records:", len(records))
print("Unique utterances:", len(utterance_splits))
print("Intent distribution:", dict(Counter(
    r["intent"] for r in records
)))
print("Cross-split duplicate requests:", len(leakage))

if leakage:
    print(
        "WARNING: Benchmark has train/test leakage. "
        "Use only for development smoke tests."
    )
else:
    print("No exact duplicate leakage detected.")

print("Structural validation passed!")
