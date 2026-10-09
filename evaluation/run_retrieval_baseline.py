
from pathlib import Path
from collections import Counter
import json
import re
import math

ROOT = Path(__file__).resolve().parents[1]

META = ROOT / "data/metadata"
GOLD = ROOT / "data/benchmarks/retrieval_ground_truth.jsonl"
OUTPUT = ROOT / "evaluation/results/retrieval_predictions.jsonl"

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())

app = load_json(META / "application_metadata.json")
registry = load_json(META / "api_registry.json")

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

# Simple TF-IDF document vectors
doc_tokens = [tokenize(d["text"]) for d in documents]
df = Counter()

for tokens in doc_tokens:
    df.update(set(tokens))

N = len(documents)

def vector(tokens):
    counts = Counter(tokens)
    result = {}

    for term, tf in counts.items():
        idf = math.log((N + 1) / (df.get(term, 0) + 1)) + 1
        result[term] = tf * idf

    return result

vectors = [vector(tokens) for tokens in doc_tokens]

def cosine(a, b):
    common = set(a) & set(b)
    dot = sum(a[t] * b[t] for t in common)
    norm_a = math.sqrt(sum(v*v for v in a.values()))
    norm_b = math.sqrt(sum(v*v for v in b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0

    return dot / (norm_a * norm_b)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(GOLD, encoding="utf-8") as f:
    cases = [json.loads(line) for line in f if line.strip()]

with open(OUTPUT, "w", encoding="utf-8") as f:
    for case in cases:
        qvec = vector(tokenize(case["query"]))

        ranked = sorted(
            zip(documents, vectors),
            key=lambda item: cosine(qvec, item[1]),
            reverse=True
        )

        prediction = {
            "query_id": case["query_id"],
            "retrieved_ids": [
                doc["id"] for doc, _ in ranked[:5]
            ]
        }

        f.write(json.dumps(prediction) + "\n")

print("Retrieval predictions generated:", len(cases))
print("Saved to:", OUTPUT)
