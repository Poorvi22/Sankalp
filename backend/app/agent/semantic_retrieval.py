import json
import time
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[3]

METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "application_metadata.json"
)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class SemanticMetadataRetriever:
    """Semantic retrieval for application pages and their components."""

    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

        self.pages = []
        self.components = []

        self.page_index = None
        self.component_index = None

        self.load_metadata()
        self.build_indexes()

    @property
    def index(self):
      """Backward-compatible alias for the page-level FAISS index."""
      return self.page_index
    

    def load_metadata(self):
        """Load pages, widgets, and filters from application metadata."""

        with open(METADATA_PATH, "r", encoding="utf-8") as file:
            metadata = json.load(file)

        for page in metadata.get("pages", []):
            page_id = page["page_id"]

            page_text = " ".join([
                page.get("title", ""),
                page.get("description", ""),
                " ".join(page.get("keywords", [])),
                " ".join(page.get("filters", [])),
            ])

            self.pages.append({
                "id": page_id,
                "type": "page",
                "page_id": page_id,
                "title": page["title"],
                "route": page["route"],
                "text": page_text,
            })

            # Store widgets separately.
            for widget in page.get("widgets", []):
                widget_text = " ".join([
                    widget.get("widget_id", ""),
                    widget.get("type", ""),
                    widget.get("description", ""),
                    page["title"],
                    page.get("description", ""),
                ])

                self.components.append({
                    "id": widget["widget_id"],
                    "type": "widget",
                    "page_id": page_id,
                    "title": widget["widget_id"],
                    "route": page["route"],
                    "text": widget_text,
                })

            # Store filters separately.
            for filter_name in page.get("filters", []):
                self.components.append({
                    "id": f"{page_id}:{filter_name}",
                    "type": "filter",
                    "page_id": page_id,
                    "title": filter_name,
                    "route": page["route"],
                    "text": (
                        f"{page['title']} "
                        f"filter {filter_name} "
                        f"{page.get('description', '')}"
                    ),
                })

    def _build_index(self, documents):
        """Build a FAISS index using cosine similarity."""

        if not documents:
            return None

        texts = [document["text"] for document in documents]

        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype("float32")

        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)

        return index

    def build_indexes(self):
        """Build independent indexes for pages and components."""

        self.page_index = self._build_index(self.pages)
        self.component_index = self._build_index(self.components)

    def _retrieve(self, query, documents, index, top_k):
        """Retrieve matching documents from one index."""

        query = query.strip()

        if not query or index is None:
            return {
                "query": query,
                "results": [],
                "latency_ms": 0.0,
            }

        started = time.perf_counter()

        query_vector = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype("float32")

        k = min(max(1, top_k), len(documents))

        scores, indices = index.search(query_vector, k)

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue

            document = documents[int(idx)]

            results.append({
                "id": document["id"],
                "type": document["type"],
                "page_id": document["page_id"],
                "title": document["title"],
                "route": document["route"],
                "similarity": round(float(score), 4),
                "text": document["text"],
            })

        elapsed_ms = (time.perf_counter() - started) * 1000

        return {
            "query": query,
            "results": results,
            "latency_ms": round(elapsed_ms, 2),
        }

    def retrieve_pages(self, query, top_k=5):
        """Retrieve the most relevant application pages."""

        return self._retrieve(
            query=query,
            documents=self.pages,
            index=self.page_index,
            top_k=top_k,
        )

    def retrieve_components(self, query, page_id=None, top_k=5):
        """Retrieve widgets and filters, optionally within one page."""

        if page_id is None:
            documents = self.components
        else:
            documents = [
                component
                for component in self.components
                if component["page_id"] == page_id
            ]

        # Build a temporary index when searching within a specific page.
        if page_id is not None:
            index = self._build_index(documents)
        else:
            index = self.component_index

        return self._retrieve(
            query=query,
            documents=documents,
            index=index,
            top_k=top_k,
        )

    def retrieve(self, query, top_k=5):
     """Maintain compatibility with the previous retrieval interface."""

     if not query or not query.strip():
        return []

     return self.retrieve_pages(query, top_k=top_k)


if __name__ == "__main__":
    retriever = SemanticMetadataRetriever()

    test_queries = [
        "Which products need replenishment?",
        "Compare vendor prices and delivery times",
        "Show me delayed shipments",
        "Analyze cash inflows and expenses",
    ]

    for query in test_queries:
        response = retriever.retrieve_pages(query, top_k=3)

        print(f"\nQuery: {query}")
        print(f"Retrieval latency: {response['latency_ms']} ms")

        for result in response["results"]:
            print(
                f"  {result['title']} | "
                f"{result['page_id']} | "
                f"score={result['similarity']}"
            )

    print("\nComponent retrieval example:")

    response = retriever.retrieve_components(
        "Find delayed deliveries and shipments",
        page_id="PAGE_LOGISTICS",
        top_k=5,
    )

    for result in response["results"]:
        print(
            f"  {result['type']} | "
            f"{result['title']} | "
            f"score={result['similarity']}"
        )