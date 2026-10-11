import json
import statistics
import time
from pathlib import Path

from backend.app.agent.page_router import PageRouter
from backend.app.agent.semantic_retrieval import SemanticMetadataRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[3]

BENCHMARK_PATH = (
    PROJECT_ROOT
    / "data"
    / "benchmarks"
    / "retrieval_queries.json"
)


def load_queries():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def percentile(values, percentile_value):
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


def calculate_metrics(results):
    total = len(results)

    if total == 0:
        return {
            "top1_accuracy": 0.0,
            "recall_at_5": 0.0,
            "mrr": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
        }

    top1_hits = 0
    recall_hits = 0
    reciprocal_ranks = []

    for result in results:
        expected = result["expected"]
        ranked_pages = result["ranked_pages"]

        if ranked_pages and ranked_pages[0] == expected:
            top1_hits += 1

        if expected in ranked_pages[:5]:
            recall_hits += 1

        reciprocal_rank = 0.0

        for rank, page_id in enumerate(ranked_pages, start=1):
            if page_id == expected:
                reciprocal_rank = 1.0 / rank
                break

        reciprocal_ranks.append(reciprocal_rank)

    latencies = [result["latency_ms"] for result in results]

    return {
        "top1_accuracy": top1_hits / total,
        "recall_at_5": recall_hits / total,
        "mrr": statistics.mean(reciprocal_ranks),
        "p50_latency_ms": percentile(latencies, 50),
        "p95_latency_ms": percentile(latencies, 95),
    }


def evaluate_faiss(retriever, queries):
    results = []

    for item in queries:
        start = time.perf_counter()

        response = retriever.retrieve_pages(
            item["query"],
            top_k=5,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000

        results.append({
            "query": item["query"],
            "expected": item["expected_page_id"],
            "ranked_pages": [
                result["page_id"]
                for result in response["results"]
            ],
            "latency_ms": elapsed_ms,
        })

    return results


def evaluate_router(router, queries):
    results = []

    for item in queries:
        start = time.perf_counter()

        response = router.route(item["query"])

        elapsed_ms = (time.perf_counter() - start) * 1000

        # The router selects one page. Do not count the fallback
        # candidate list as the router's final ranked output.
        selected_page = response["page_id"]

        results.append({
            "query": item["query"],
            "expected": item["expected_page_id"],
            "ranked_pages": (
                [selected_page]
                if selected_page is not None
                else []
            ),
            "latency_ms": elapsed_ms,
            "method": response["method"],
        })

    return results


def print_report(name, results):
    metrics = calculate_metrics(results)

    print(f"\n{name}")
    print("=" * len(name))
    print(f"Top-1 Accuracy : {metrics['top1_accuracy']:.2%}")
    print(f"Recall@5       : {metrics['recall_at_5']:.2%}")
    print(f"MRR            : {metrics['mrr']:.4f}")
    print(f"P50 Latency    : {metrics['p50_latency_ms']:.2f} ms")
    print(f"P95 Latency    : {metrics['p95_latency_ms']:.2f} ms")

    return metrics


def print_failures(name, results):
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
        print(f"Expected: {result['expected']}")
        print(f"Retrieved: {result['ranked_pages']}")

        if "method" in result:
            print(f"Routing method: {result['method']}")


def main():
    queries = load_queries()

    print(f"Benchmark queries: {len(queries)}")

    # Create one retriever and share it with the router.
    # This avoids loading the embedding model twice.
    retriever = SemanticMetadataRetriever()
    router = PageRouter(retriever=retriever)

    # Warm up the embedding model before timing.
    retriever.retrieve_pages("warm up retrieval", top_k=5)

    faiss_results = evaluate_faiss(retriever, queries)
    router_results = evaluate_router(router, queries)

    print_report("FAISS-ONLY RETRIEVAL", faiss_results)
    print_report("RULE-BASED + FAISS ROUTER", router_results)

    print_failures("FAISS-ONLY RETRIEVAL", faiss_results)
    print_failures("RULE-BASED + FAISS ROUTER", router_results)

    rule_count = sum(
        result.get("method") == "rule"
        for result in router_results
    )

    print("\nROUTING SUMMARY")
    print("================")
    print(f"Rule-routed queries: {rule_count}")
    print(f"Semantic-routed queries: {len(queries) - rule_count}")

    print(
        "\nNote: Router Recall@5 and MRR are based on its single "
        "selected page, not the fallback candidate list."
    )
    print(
        "Latency excludes model initialization and index construction. "
        "Measurements are single-pass estimates."
    )


if __name__ == "__main__":
    main()