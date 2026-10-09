
from pathlib import Path
import json
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evaluation" / "results"
GOLD = ROOT / "data/benchmarks/retrieval_ground_truth.jsonl"

TFIDF = RESULTS / "retrieval_predictions.jsonl"
FAISS = RESULTS / "faiss_predictions.jsonl"
OUTPUT = RESULTS / "hybrid_predictions.jsonl"

def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [
            json.loads(line)
            for line in f if line.strip()
        ]

gold = load_jsonl(GOLD)
tfidf = {
    x["query_id"]: x
    for x in load_jsonl(TFIDF)
}
faiss = {
    x["query_id"]: x
    for x in load_jsonl(FAISS)
}

# Reciprocal Rank Fusion
# This combines rankings without requiring
# the two methods to have comparable scores.

RRF_K = 60

def fuse(rankings):
    scores = {}

    for ranking in rankings:
        for rank, item_id in enumerate(ranking, 1):
            scores[item_id] = (
                scores.get(item_id, 0)
                + 1 / (RRF_K + rank)
            )

    return [
        item_id
        for item_id, _ in sorted(
            scores.items(),
            key=lambda item: (-item[1], item[0])
        )
    ]

predictions = []
fusion_latencies = []

for case in gold:
    query_id = case["query_id"]

    if query_id not in tfidf or query_id not in faiss:
        raise ValueError(
            f"Missing retrieval prediction: {query_id}"
        )

    start = time.perf_counter()

    ranked_ids = fuse([
        tfidf[query_id]["retrieved_ids"],
        faiss[query_id]["retrieved_ids"]
    ])

    fusion_ms = (
        time.perf_counter() - start
    ) * 1000

    fusion_latencies.append(fusion_ms)

    predictions.append({
        "query_id": query_id,
        "retrieved_ids": ranked_ids[:5],
        "fusion_latency_ms": round(fusion_ms, 4)
    })

with open(OUTPUT, "w", encoding="utf-8") as f:
    for prediction in predictions:
        f.write(json.dumps(prediction) + "\n")

print("Hybrid predictions saved:", OUTPUT)
print("Queries:", len(predictions))
print(
    "Average fusion latency:",
    round(float(np.mean(fusion_latencies)), 4),
    "ms"
)
