from backend.app.agent.metadata_registry import MetadataRegistry


class MetadataRetrieval:

    def __init__(self):
        self.registry = MetadataRegistry()

    def retrieve(self, query, limit=5):
        """
        Retrieve relevant application pages for a user query.
        """

        query = query.lower().strip()

        if not query:
            return []

        results = self.registry.search_pages(
            query=query,
            limit=limit
        )

        return results