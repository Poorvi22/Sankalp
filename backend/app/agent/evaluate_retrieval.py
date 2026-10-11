import json
import statistics
import time
from pathlib import Path

from backend.app.agent.metadata_registry import MetadataRegistry
from backend.app.agent.semantic_retrieval import SemanticMetadataRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[3]

BENCHMARK_PATH = (
    PROJECT_ROOT
    / "data"
    / "benchmarks"
    / "retrieval_queries.json"
)


def load_queries():
    """Load labelled retrieval benchmark queries."""

    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Benchmark file not found: {BENCHMARK_PATH}"
        )

    with open(BENCHMARK_PATH, "r", encoding="utf-8") as file:
        queries = json.load(file)

    if not queries:
        raise ValueError("The benchmark contains no queries.")

    return queries


def percentile(values, percentile_value):
    """Calculate a linearly interpolated percentile."""

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * percentile_value / 100
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower

    return (
        ordered[lower] * (1 - fraction)
        + ordered[upper] * fraction
    )


def evaluate_keyword(registry, queries):
    """Evaluate the keyword-based page retrieval system."""

    results = []

    for item in queries:
        query = item["query"]
        expected = item["expected_page_id"]

        start = time.perf_counter()
        matches = registry.search_pages(query, limit=5)
        latency_ms = (time.perf_counter() - start) * 1000

        ranked_pages = [
            match["page_id"]
            for match in matches
        ]

        results.append({
            "query": query,
            "expected": expected,
            "ranked_pages": ranked_pages,
            "latency_ms": latency_ms,
        })

    return results


def evaluate_faiss(retriever, queries):
    """Evaluate FAISS semantic page retrieval."""

    results = []

    for item in queries:
        query = item["query"]
        expected = item["expected_page_id"]

        start = time.perf_counter()
        response = retriever.retrieve_pages(query, top_k=5)
        latency_ms = (time.perf_counter() - start) * 1000

        ranked_pages = [
            result["page_id"]
            for result in response["results"]
        ]

        results.append({
            "query": query,
            "expected": expected,
            "ranked_pages": ranked_pages,
            "latency_ms": latency_ms,
        })

    return results


def calculate_metrics(results):
    """Calculate ranking quality and retrieval latency."""

    if not results:
        return {
            "top1_accuracy": 0.0,
            "recall_at_5": 0.0,
            "mrr": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
        }

    top1_hits = 0
    recall_at_5_hits = 0
    reciprocal_ranks = []

    for result in results:
        expected = result["expected"]
        ranked_pages = result["ranked_pages"]

        if ranked_pages and ranked_pages[0] == expected:
            top1_hits += 1

        if expected in ranked_pages[:5]:
            recall_at_5_hits += 1

        reciprocal_rank = 0.0

        for rank, page_id in enumerate(ranked_pages, start=1):
            if page_id == expected:
                reciprocal_rank = 1.0 / rank
                break

        reciprocal_ranks.append(reciprocal_rank)

    latencies = [
        result["latency_ms"]
        for result in results
    ]

    return {
        "top1_accuracy": top1_hits / len(results),
        "recall_at_5": recall_at_5_hits / len(results),
        "mrr": statistics.mean(reciprocal_ranks),
        "p50_latency_ms": percentile(latencies, 50),
        "p95_latency_ms": percentile(latencies, 95),
    }


def print_report(name, metrics):
    """Print benchmark metrics."""

    print(f"\n{name}")
    print("=" * len(name))

    print(
        f"Top-1 Accuracy : "
        f"{metrics['top1_accuracy']:.2%}"
    )
    print(
        f"Recall@5       : "
        f"{metrics['recall_at_5']:.2%}"
    )
    print(
        f"MRR            : "
        f"{metrics['mrr']:.4f}"
    )
    print(
        f"P50 Latency    : "
        f"{metrics['p50_latency_ms']:.2f} ms"
    )
    print(
        f"P95 Latency    : "
        f"{metrics['p95_latency_ms']:.2f} ms"
    )


def print_failures(name, results):
    """Show queries where the correct page was not ranked first."""

    failures = [
        result
        for result in results
        if (
            not result["ranked_pages"]
            or result["ranked_pages"][0] != result["expected"]
        )
    ]

    print(f"\n{name} — Top-1 failures: {len(failures)}")

    for result in failures:
        print(f"\nQuery: {result['query']}")
        print(f"Expected page: {result['expected']}")
        print(f"Retrieved pages: {result['ranked_pages']}")


def main():
    queries = load_queries()

    print(f"Benchmark queries: {len(queries)}")

    # Initialize the retrieval systems outside the measurement loop.
    registry = MetadataRegistry()
    retriever = SemanticMetadataRetriever()

    # Warm up FAISS and the embedding model.
    retriever.retrieve_pages(
        "warm up retrieval",
        top_k=5,
    )

    # Run both methods against exactly the same queries.
    keyword_results = evaluate_keyword(registry, queries)
    faiss_results = evaluate_faiss(retriever, queries)

    # Calculate metrics.
    keyword_metrics = calculate_metrics(keyword_results)
    faiss_metrics = calculate_metrics(faiss_results)

    # Print reports.
    print_report("KEYWORD SEARCH", keyword_metrics)
    print_report("FAISS SEMANTIC SEARCH", faiss_metrics)

    # Identify incorrect first-page predictions.
    print_failures("KEYWORD SEARCH", keyword_results)
    print_failures("FAISS SEMANTIC SEARCH", faiss_results)

    print("\nEvaluation complete.")
    print(
        "Latency excludes model initialization and index construction."
    )
    print(
        "Latency is measured per query in a single pass; "
        "repeat measurements are needed for a more robust benchmark."
    )


if __name__ == "__main__":
    main()