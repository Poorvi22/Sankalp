
from pathlib import Path
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "metadata"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class MetadataRetriever:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

        with open(
            META / "application_metadata.json",
            encoding="utf-8"
        ) as f:
            self.app = json.load(f)

        with open(
            META / "api_registry.json",
            encoding="utf-8"
        ) as f:
            self.registry = json.load(f)

        self.documents = []

        for page in self.app["pages"]:
            self.documents.append({
                "id": page["page_id"],
                "type": "page",
                "text": " ".join([
                    page["name"],
                    page["description"],
                    page["route"]
                ]),
                "metadata": page
            })

            for widget in page.get("widgets", []):
                self.documents.append({
                    "id": widget["widget_id"],
                    "type": "widget",
                    "text": " ".join([
                        page["name"],
                        widget["type"],
                        widget.get("description", "")
                    ]),
                    "metadata": widget,
                    "page_id": page["page_id"]
                })

        for api in self.registry["apis"]:
            self.documents.append({
                "id": api["api_id"],
                "type": "api",
                "text": " ".join([
                    api["api_id"],
                    api["description"],
                    api["path"]
                ]),
                "metadata": api
            })

        texts = [d["text"] for d in self.documents]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")

        self.index = faiss.IndexFlatIP(
            embeddings.shape[1]
        )

        self.index.add(embeddings)

    def search(
        self,
        query: str,
        top_k: int = 5,
        allowed_ids=None
    ):
        vector = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")

        # Retrieve a broader candidate set before
        # applying permission-aware filtering.
        k = len(self.documents)

        scores, indices = self.index.search(
            vector, k
        )

        allowed = (
            set(allowed_ids)
            if allowed_ids is not None
            else None
        )

        results = []

        for score, index in zip(
            scores[0], indices[0]
        ):
            if index < 0:
                continue

            doc = self.documents[int(index)]

            if (
                allowed is not None
                and doc["id"] not in allowed
            ):
                continue

            results.append({
                "id": doc["id"],
                "type": doc["type"],
                "score": float(score),
                "page_id": doc.get("page_id"),
                "metadata": doc["metadata"]
            })

            if len(results) >= top_k:
                break

        return results


if __name__ == "__main__":
    retriever = MetadataRetriever()

    query = "Find products with low stock"

    results = retriever.search(query)

    print("\nQuery:", query)

    for result in results:
        print(
            result["id"],
            result["type"],
            round(result["score"], 4)
        )
