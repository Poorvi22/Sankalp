
from pathlib import Path
import json
import time

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------------------------
# 1. FILE PATHS
# -----------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

META = ROOT / "data" / "metadata"

GOLD = (
    ROOT / "data" / "benchmarks" /
    "retrieval_ground_truth.jsonl"
)

RESULTS = ROOT / "evaluation" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# -----------------------------------------------
# 2. LOAD JSON FILES
# -----------------------------------------------

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [
            json.loads(line)
            for line in f
            if line.strip()
        ]


app = load_json(
    META / "application_metadata.json"
)

registry = load_json(
    META / "api_registry.json"
)

queries = load_jsonl(GOLD)

# -----------------------------------------------
# 3. BUILD SEARCHABLE DOCUMENTS
# -----------------------------------------------

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
    raise ValueError("No metadata documents found.")

print("Total metadata documents:", len(documents))

# -----------------------------------------------
# 4. LOAD EMBEDDING MODEL
# -----------------------------------------------

print("\nLoading embedding model...")

model_start = time.perf_counter()

model = SentenceTransformer(MODEL_NAME)

model_load_ms = (
    time.perf_counter() - model_start
) * 1000

print(
    "Model loaded in:",
    round(model_load_ms, 2),
    "ms"
)

# -----------------------------------------------
# 5. BUILD FAISS INDEX
# -----------------------------------------------

print("\nGenerating metadata embeddings...")

texts = [doc["text"] for doc in documents]

build_start = time.perf_counter()

embeddings = model.encode(
    texts,
    normalize_embeddings=True,
    convert_to_numpy=True,
    show_progress_bar=False
).astype("float32")

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

index_build_ms = (
    time.perf_counter() - build_start
) * 1000

print("Indexed documents:", index.ntotal)
print(
    "Embedding + index build time:",
    round(index_build_ms, 2),
    "ms"
)

# -----------------------------------------------
# 6. WARM UP MODEL
# -----------------------------------------------

print("\nWarming up retrieval model...")

warmup_vector = model.encode(
    ["Find inventory products"],
    normalize_embeddings=True,
    convert_to_numpy=True,
    show_progress_bar=False
).astype("float32")

index.search(
    warmup_vector,
    min(5, len(documents))
)

# -----------------------------------------------
# 7. RUN SEMANTIC RETRIEVAL
# -----------------------------------------------

print("\nRunning FAISS semantic retrieval...")

predictions = []

retrieval_latencies = []
embedding_latencies = []
search_latencies = []

for case in queries:

    query = case["query"]

    total_start = time.perf_counter()

    # Generate query embedding
    embedding_start = time.perf_counter()

    query_vector = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False
    ).astype("float32")

    embedding_ms = (
        time.perf_counter() - embedding_start
    ) * 1000

    # Search FAISS index
    search_start = time.perf_counter()

    scores, indices = index.search(
        query_vector,
        min(5, len(documents))
    )

    search_ms = (
        time.perf_counter() - search_start
    ) * 1000

    # Convert indices to metadata IDs
    retrieved_ids = [
        documents[int(i)]["id"]
        for i in indices[0]
        if i >= 0
    ]

    # Total retrieval time
    total_ms = (
        time.perf_counter() - total_start
    ) * 1000

    retrieval_latencies.append(total_ms)
    embedding_latencies.append(embedding_ms)
    search_latencies.append(search_ms)

    predictions.append({
        "query_id": case["query_id"],
        "query": query,
        "retrieved_ids": retrieved_ids,
        "retrieval_latency_ms": round(total_ms, 3),
        "embedding_latency_ms": round(embedding_ms, 3),
        "faiss_search_latency_ms": round(search_ms, 3)
    })

# -----------------------------------------------
# 8. SAVE PREDICTIONS
# -----------------------------------------------

output = RESULTS / "faiss_predictions.jsonl"

with open(output, "w", encoding="utf-8") as f:
    for prediction in predictions:
        f.write(
            json.dumps(prediction) + "\n"
        )

print("\nFAISS predictions saved:", output)

# -----------------------------------------------
# 9. CALCULATE LATENCY KPIs
# -----------------------------------------------

def calculate_percentile(values, percentile):
    return round(
        float(np.percentile(values, percentile)),
        3
    )


timing_report = {
    "retrieval_method": "FAISS",
    "embedding_model": MODEL_NAME,
    "total_queries": len(queries),
    "indexed_documents": len(documents),

    "model_load_ms": round(
        model_load_ms, 3
    ),

    "index_build_ms": round(
        index_build_ms, 3
    ),

    "average_retrieval_ms": round(
        float(np.mean(retrieval_latencies)), 3
    ),

    "p50_retrieval_ms": calculate_percentile(
        retrieval_latencies, 50
    ),

    "p95_retrieval_ms": calculate_percentile(
        retrieval_latencies, 95
    ),

    "average_embedding_ms": round(
        float(np.mean(embedding_latencies)), 3
    ),

    "average_faiss_search_ms": round(
        float(np.mean(search_latencies)), 3
    ),

    "latency_scope": (
        "Warm-model query embedding + "
        "FAISS search + result mapping. "
        "Excludes model loading and index construction."
    )
}

# -----------------------------------------------
# 10. SAVE LATENCY REPORT
# -----------------------------------------------

timing_output = RESULTS / "faiss_timing.json"

with open(
    timing_output,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        timing_report,
        f,
        indent=2
    )

# -----------------------------------------------
# 11. DISPLAY RESULTS
# -----------------------------------------------

print("\n" + "=" * 55)
print("BIZPILOT AI — FAISS RETRIEVAL PERFORMANCE")
print("=" * 55)

print("Queries:", len(queries))
print("Indexed documents:", len(documents))

print(
    "Average retrieval latency:",
    timing_report["average_retrieval_ms"],
    "ms"
)

print(
    "P50 retrieval latency:",
    timing_report["p50_retrieval_ms"],
    "ms"
)

print(
    "P95 retrieval latency:",
    timing_report["p95_retrieval_ms"],
    "ms"
)

print(
    "Average embedding latency:",
    timing_report["average_embedding_ms"],
    "ms"
)

print(
    "Average FAISS search latency:",
    timing_report["average_faiss_search_ms"],
    "ms"
)

print("\nTiming report saved:", timing_output)
print("=" * 55)
