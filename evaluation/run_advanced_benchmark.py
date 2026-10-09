
from pathlib import Path
from collections import Counter
import json
import math
import re
import statistics
import time

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "metadata"
GOLD = ROOT / "data" / "benchmarks" / "advanced_retrieval_ground_truth.jsonl"
OUT = ROOT / "evaluation" / "results" / "advanced"
OUT.mkdir(parents=True, exist_ok=True)

MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def percentile(values, p):
    return float(np.percentile(values, p)) if values else None


# -----------------------------------------
# LOAD METADATA
# -----------------------------------------

app = load_json(META / "application_metadata.json")
registry = load_json(META / "api_registry.json")
cases = load_jsonl(GOLD)

documents = []

for page in app["pages"]:
    documents.append({
        "id": page["page_id"],
        "text": " ".join([
            page["name"],
            page["description"],
            page["route"]
        ])
    })

    for widget in page.get("widgets", []):
        documents.append({
            "id": widget["widget_id"],
            "text": " ".join([
                page["name"],
                widget["type"],
                widget.get("description", "")
            ])
        })

for api in registry["apis"]:
    documents.append({
        "id": api["api_id"],
        "text": " ".join([
            api["api_id"],
            api["description"],
            api["path"]
        ])
    })

if not documents:
    raise SystemExit("No metadata documents found.")

ids = [d["id"] for d in documents]

if len(ids) != len(set(ids)):
    raise ValueError("Duplicate metadata IDs detected.")

known_ids = set(ids)

for case in cases:
    if not set(case["relevant_ids"]).issubset(known_ids):
        raise ValueError(
            f"Unknown ground-truth ID: {case['query_id']}"
        )

# -----------------------------------------
# TF-IDF INDEX
# -----------------------------------------

def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


tokens = [tokenize(d["text"]) for d in documents]

df = Counter()
for terms in tokens:
    df.update(set(terms))

N = len(documents)


def vector(terms):
    counts = Counter(terms)
    result = {}

    for term, tf in counts.items():
        idf = math.log(
            (N + 1) / (df.get(term, 0) + 1)
        ) + 1
        result[term] = tf * idf

    return result


doc_vectors = [vector(t) for t in tokens]


def cosine(a, b):
    common = set(a) & set(b)

    dot = sum(a[t] * b[t] for t in common)

    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))

    return dot / (na * nb) if na and nb else 0.0


def tfidf_search(query, k=10):
    qvec = vector(tokenize(query))

    ranked = sorted(
        range(N),
        key=lambda i: (
            -cosine(qvec, doc_vectors[i]),
            documents[i]["id"]
        )
    )

    return [documents[i]["id"] for i in ranked[:k]]


# -----------------------------------------
# FAISS INDEX
# -----------------------------------------

print("Loading embedding model...")
model = SentenceTransformer(MODEL)

print("Building FAISS index...")

embeddings = model.encode(
    [d["text"] for d in documents],
    normalize_embeddings=True,
    convert_to_numpy=True,
    show_progress_bar=False
).astype("float32")

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)


def faiss_search(query, k=10):
    query_vector = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False
    ).astype("float32")

    _, indices = index.search(
        query_vector,
        min(k, N)
    )

    return [
        documents[int(i)]["id"]
        for i in indices[0]
        if i >= 0
    ]


# -----------------------------------------
# HYBRID SEARCH
# -----------------------------------------

def rrf(rankings, k=60):
    scores = {}

    for ranking in rankings:
        for rank, item in enumerate(ranking, 1):
            scores[item] = (
                scores.get(item, 0)
                + 1 / (k + rank)
            )

    return [
        item
        for item, _ in sorted(
            scores.items(),
            key=lambda x: (-x[1], x[0])
        )
    ]


# Warm up model before latency testing.
faiss_search("Show inventory")

# -----------------------------------------
# RUN BENCHMARK
# -----------------------------------------

results = {
    "tfidf": [],
    "faiss": [],
    "hybrid": []
}

latencies = {
    "tfidf": [],
    "faiss": [],
    "hybrid": []
}

for case in cases:
    query = case["query"]

    start = time.perf_counter()
    tfidf_ranked = tfidf_search(query)
    tfidf_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    faiss_ranked = faiss_search(query)
    faiss_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    hybrid_ranked = rrf([
        tfidf_ranked,
        faiss_ranked
    ])[:10]
    fusion_ms = (time.perf_counter() - start) * 1000

    # Sequential retrieval + fusion time.
    hybrid_ms = tfidf_ms + faiss_ms + fusion_ms

    rankings = {
        "tfidf": (tfidf_ranked, tfidf_ms),
        "faiss": (faiss_ranked, faiss_ms),
        "hybrid": (hybrid_ranked, hybrid_ms)
    }

    for method, (ranked, elapsed) in rankings.items():
        results[method].append({
            "query_id": case["query_id"],
            "retrieved_ids": ranked,
            "retrieval_latency_ms": round(elapsed, 3)
        })

        latencies[method].append(elapsed)


# -----------------------------------------
# CALCULATE METRICS
# -----------------------------------------

def evaluate(predictions):
    prediction_map = {
        r["query_id"]: r
        for r in predictions
    }

    p1 = []
    r3 = []
    mrr = []

    for case in cases:
        relevant = set(case["relevant_ids"])
        retrieved = prediction_map[
            case["query_id"]
        ]["retrieved_ids"]

        p1.append(
            int(bool(retrieved) and retrieved[0] in relevant)
        )

        r3.append(
            len(relevant.intersection(retrieved[:3]))
            / len(relevant)
        )

        rank = next(
            (
                i for i, item in enumerate(retrieved, 1)
                if item in relevant
            ),
            None
        )

        mrr.append(1 / rank if rank else 0)

    return {
        "precision_at_1": round(statistics.mean(p1), 4),
        "recall_at_3": round(statistics.mean(r3), 4),
        "mrr": round(statistics.mean(mrr), 4)
    }


summary = {}

for method in results:
    metrics = evaluate(results[method])

    metrics.update({
        "queries": len(cases),
        "indexed_documents": len(documents),
        "average_latency_ms": round(
            statistics.mean(latencies[method]), 3
        ),
        "p50_latency_ms": round(
            percentile(latencies[method], 50), 3
        ),
        "p95_latency_ms": round(
            percentile(latencies[method], 95), 3
        )
    })

    summary[method] = metrics

    prediction_file = OUT / f"{method}_predictions.jsonl"

    with open(prediction_file, "w", encoding="utf-8") as f:
        for record in results[method]:
            f.write(json.dumps(record) + "\n")

save_json(OUT / "comparison.json", summary)

print("\nBIZPILOT AI — ADVANCED RETRIEVAL BENCHMARK")
print("=" * 70)

print(
    f"{'Method':<12}"
    f"{'P@1':>10}"
    f"{'R@3':>10}"
    f"{'MRR':>10}"
    f"{'p50 ms':>12}"
    f"{'p95 ms':>12}"
)

for method, metrics in summary.items():
    print(
        f"{method:<12}"
        f"{metrics['precision_at_1']:>10.2%}"
        f"{metrics['recall_at_3']:>10.2%}"
        f"{metrics['mrr']:>10.2%}"
        f"{metrics['p50_latency_ms']:>12.3f}"
        f"{metrics['p95_latency_ms']:>12.3f}"
    )

print("\nSaved results to:", OUT)
