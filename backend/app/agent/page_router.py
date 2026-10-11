from backend.app.agent.semantic_retrieval import SemanticMetadataRetriever


class PageRouter:
    """
    Routes natural-language requests to application pages.

    Uses FAISS semantic retrieval as the default and applies
    conservative business-intent rules for specific requests.
    """

    def __init__(self, retriever=None):
        self.retriever = (
            retriever
            if retriever is not None
            else SemanticMetadataRetriever()
        )

        # Explicit rules for intents that are easy to confuse.
        # Each rule maps distinctive phrases to an existing page ID.
        self.routing_rules = {
            "PAGE_FINANCE": [
                "business expenses",
                "outstanding expenses",
                "recent expenses",
                "cash inflow",
                "cash outflow",
                "cash flow",
                "money received",
                "money spent",
                "income and expenditure",
                "financial transactions",
                "supplier payments",
            ],
            "PAGE_ANALYTICS": [
                "compare business performance",
                "compare periods",
                "historical trends",
                "trend analysis",
                "business performance report",
                "analytical report",
                "compare key indicators",
                "cross-period comparison",
            ],
            "PAGE_DASHBOARD": [
                "business overview",
                "executive summary",
                "business at a glance",
                "overall business health",
                "company snapshot",
                "what is happening across the business",
            ],
            "PAGE_INVENTORY": [
                "low stock",
                "low-stock",
                "stockout",
                "stock out",
                "replenishment",
                "reorder threshold",
                "inventory shortage",
                "warehouse stock",
                "quantity on hand",
            ],
            "PAGE_SUPPLIERS": [
                "supplier directory",
                "vendor directory",
                "supplier comparison",
                "vendor comparison",
                "supplier lead time",
                "fastest suppliers",
                "supplier reliability",
                "supplier quotations",
            ],
            "PAGE_PROCUREMENT": [
                "purchase order",
                "purchase orders",
                "procurement request",
                "purchase approval",
                "orders awaiting approval",
                "purchase order status",
            ],
            "PAGE_SALES": [
                "customer orders",
                "sales orders",
                "units sold",
                "best-selling products",
                "best selling products",
                "top-selling products",
                "top selling products",
                "sales trends",
            ],
            "PAGE_LOGISTICS": [
                "shipment tracking",
                "delayed shipments",
                "late deliveries",
                "overdue deliveries",
                "missed delivery date",
                "shipments in transit",
                "undelivered shipments",
            ],
        }

    def _rule_match(self, query):
        """
        Return a page ID only when a distinctive phrase matches.

        More specific phrases should be used in rules to reduce
        accidental routing based on generic words.
        """

        normalized_query = " ".join(query.lower().split())

        matches = []

        for page_id, phrases in self.routing_rules.items():
            for phrase in phrases:
                if phrase in normalized_query:
                    matches.append((len(phrase), page_id, phrase))

        if not matches:
            return None

        # Prefer the longest matching phrase.
        matches.sort(reverse=True)

        longest_length = matches[0][0]

        # If equally specific phrases point to different pages,
        # defer to semantic retrieval rather than guessing.
        best_matches = [
            match
            for match in matches
            if match[0] == longest_length
        ]

        best_page_ids = {
            match[1]
            for match in best_matches
        }

        if len(best_page_ids) != 1:
            return None

        return best_matches[0][1]

    def route(self, query, top_k=5):
        """
        Resolve a query to a page using explicit rules and FAISS.

        Returns the selected page, ranked candidates, and route source.
        """

        if not query or not query.strip():
            return {
                "query": query or "",
                "page_id": None,
                "route": None,
                "method": "empty_query",
                "candidates": [],
            }

        query = query.strip()

        # First try distinctive business-intent phrases.
        matched_page_id = self._rule_match(query)

        if matched_page_id is not None:
            page = self.retriever.get_page_metadata(
                matched_page_id
            ) if hasattr(self.retriever, "get_page_metadata") else None

            if page is not None:
                return {
                    "query": query,
                    "page_id": page["page_id"],
                    "route": page["route"],
                    "title": page["title"],
                    "method": "rule",
                    "candidates": [],
                }

            # Resolve the page from the retriever's loaded page records.
            for candidate in getattr(self.retriever, "pages", []):
                if candidate["page_id"] == matched_page_id:
                    return {
                        "query": query,
                        "page_id": candidate["page_id"],
                        "route": candidate["route"],
                        "title": candidate["title"],
                        "method": "rule",
                        "candidates": [],
                    }

        # Otherwise, use FAISS to rank application pages.
        response = self.retriever.retrieve_pages(
            query,
            top_k=top_k,
        )

        candidates = response.get("results", [])

        if not candidates:
            return {
                "query": query,
                "page_id": None,
                "route": None,
                "method": "semantic",
                "candidates": [],
            }

        best = candidates[0]

        return {
            "query": query,
            "page_id": best["page_id"],
            "route": best["route"],
            "title": best["title"],
            "method": "semantic",
            "candidates": candidates,
        }