
from pathlib import Path
import json
import time

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]

META = ROOT / "data" / "metadata"
GOLD = ROOT / "data" / "benchmarks/retrieval_ground_truth.jsonl"
RESULTS = ROOT / "evaluation" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [
            json.loads(line)
            for line in f if line.strip()
        ]

app = load_json(META / "application_metadata.json")
registry = load_json(META / "api_registry.json")
queries = load_jsonl(GOLD)

# Build searchable metadata documents.
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

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

texts = [doc["text"] for doc in documents]

# Build the index once.
build_start = time.perf_counter()

embeddings = model.encode(
    texts,
    normalize_embeddings=True,
    convert_to_numpy=True
).astype("float32")

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

build_ms = (time.perf_counter() - build_start) * 1000

print("Indexed documents:", index.ntotal)
print("Index build time (ms):", round(build_ms, 2))

# Encode queries in one batch for efficient evaluation.
query_texts = [case["query"] for case in queries]

query_vectors = model.encode(
    query_texts,
    normalize_embeddings=True,
    convert_to_numpy=True
).astype("float32")

predictions = []
search_latencies = []

for case, vector in zip(queries, query_vectors):
    start = time.perf_counter()

    scores, indices = index.search(
        vector.reshape(1, -1),
        min(5, len(documents))
    )

    elapsed_ms = (time.perf_counter() - start) * 1000
    search_latencies.append(elapsed_ms)

    retrieved_ids = [
        documents[int(i)]["id"]
        for i in indices[0]
        if i >= 0
    ]

    predictions.append({
        "query_id": case["query_id"],
        "retrieved_ids": retrieved_ids
    })

output = RESULTS / "faiss_predictions.jsonl"

with open(output, "w", encoding="utf-8") as f:
    for item in predictions:
        f.write(json.dumps(item) + "\n")

with open(
    RESULTS / "faiss_timing.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump({
        "model": MODEL_NAME,
        "indexed_documents": len(documents),
        "index_build_ms": round(build_ms, 2),
        "average_faiss_search_ms": round(
            float(np.mean(search_latencies)), 4
        ),
        "note": (
            "Search time excludes query embedding, "
            "model loading and index building."
        )
    }, f, indent=2)

print("FAISS predictions saved:", output)
print("Average FAISS search time (ms):",
      round(float(np.mean(search_latencies)), 4))
