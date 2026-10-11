import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "application_metadata.json"
)


class MetadataRegistry:
    """Registry for application page metadata."""

    def __init__(self):
        self.pages = []
        self.load_metadata()

    def load_metadata(self):
        """Load application metadata from JSON."""

        if not METADATA_PATH.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {METADATA_PATH}"
            )

        with open(METADATA_PATH, "r", encoding="utf-8") as file:
            metadata = json.load(file)

        self.pages = metadata.get("pages", [])

    def get_all_pages(self):
        """Return all registered application pages."""

        return self.pages

    def get_page(self, page_id):
        """Find a page using its unique ID."""

        for page in self.pages:
            if page["page_id"] == page_id:
                return page

        return None

    def search_pages(self, query, limit=5):
        """Rank pages using simple keyword matching."""

        if not query or not query.strip():
            return []

        query_words = set(query.lower().split())
        results = []

        for page in self.pages:
            searchable_text = " ".join([
                page.get("title", ""),
                page.get("description", ""),
                " ".join(page.get("keywords", [])),
                " ".join(page.get("filters", [])),
            ]).lower()

            searchable_words = set(searchable_text.split())

            score = len(query_words & searchable_words)

            if score > 0:
                results.append({
                    "page_id": page["page_id"],
                    "title": page["title"],
                    "route": page["route"],
                    "score": score,
                })

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return results[:limit]