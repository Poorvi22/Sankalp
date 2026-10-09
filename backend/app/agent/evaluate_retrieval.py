import json
import time
from pathlib import Path

from backend.app.agent.semantic_retrieval import (
    SemanticMetadataRetriever
)


ROOT = Path(__file__).resolve().parents[3]

BENCHMARK_PATH = (
    ROOT / "data" / "benchmarks" / "retrieval_queries.json"
)


def evaluate():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as file:
        queries = json.load(file)

    retriever = SemanticMetadataRetriever()

    correct_top1 = 0
    correct_top5 = 0
    reciprocal_ranks = []
    latencies = []

    for item in queries:
        start = time.perf_counter()

        response = retriever.retrieve(
            item["query"],
            top_k=5
        )

        latencies.append(
            (time.perf_counter() - start) * 1000
        )

        results = response["results"]

        # Collapse page/widget/filter matches into ranked pages.
        ranked_pages = []

        for result in results:
            page_id = result["page_id"]

            if page_id not in ranked_pages:
                ranked_pages.append(page_id)

        expected = item["expected_page_id"]

        if ranked_pages and ranked_pages[0] == expected:
            correct_top1 += 1

        if expected in ranked_pages[:5]:
            correct_top5 += 1

        if expected in ranked_pages:
            rank = ranked_pages.index(expected) + 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0.0)

        print(
            f"Query: {item['query']}\n"
            f"Expected: {expected}\n"
            f"Retrieved: {ranked_pages}\n"
        )

    total = len(queries)

    if total == 0:
        print("No benchmark queries found.")
        return

    print("\n========== RETRIEVAL KPI RESULTS ==========")
    print(f"Queries evaluated: {total}")
    print(f"Top-1 destination accuracy: {correct_top1 / total:.2%}")
    print(f"Page Recall@5: {correct_top5 / total:.2%}")
    print(f"MRR: {sum(reciprocal_ranks) / total:.4f}")

    sorted_latencies = sorted(latencies)

    p50_index = int(0.50 * (total - 1))
    p95_index = int(0.95 * (total - 1))

    print(f"End-to-end retrieval p50: {sorted_latencies[p50_index]:.2f} ms")
    print(f"End-to-end retrieval p95: {sorted_latencies[p95_index]:.2f} ms")


if __name__ == "__main__":
    evaluate()