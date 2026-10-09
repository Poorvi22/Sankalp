
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evaluation/results"

def load(name):
    with open(RESULTS / name, encoding="utf-8") as f:
        return json.load(f)

tfidf = load("tfidf_retrieval_report.json")
faiss = load("faiss_retrieval_report.json")

metrics = [
    "hit_at_1",
    "hit_at_5",
    "precision_at_5",
    "recall_at_5",
    "mrr_at_5"
]

print("\nBIZPILOT AI — RETRIEVAL COMPARISON")
print("-" * 54)
print(f"{'Metric':<22}{'TF-IDF':>14}{'FAISS':>14}")
print("-" * 54)

for metric in metrics:
    print(
        f"{metric:<22}"
        f"{tfidf[metric]:>14.4f}"
        f"{faiss[metric]:>14.4f}"
    )

print("-" * 54)

if faiss["hit_at_1"] > tfidf["hit_at_1"]:
    print("FAISS has better top-1 retrieval accuracy.")
elif faiss["hit_at_1"] < tfidf["hit_at_1"]:
    print("TF-IDF has better top-1 retrieval accuracy.")
else:
    print("Both methods have equal top-1 accuracy.")

print(
    "\nNote: This comparison measures retrieval accuracy, "
    "not end-to-end latency."
)
