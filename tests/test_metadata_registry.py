from backend.app.agent.metadata_registry import MetadataRegistry
from backend.app.agent.metadata_retrieval import MetadataRetrieval


def test_all_pages_loaded():
    registry = MetadataRegistry()

    assert len(registry.get_all_pages()) == 8


def test_find_inventory_page():
    registry = MetadataRegistry()

    page = registry.get_page("PAGE_INVENTORY")

    assert page is not None
    assert page["route"] == "/inventory"


def test_search_suppliers():
    registry = MetadataRegistry()

    results = registry.search_pages("compare supplier prices")

    assert len(results) > 0
    assert results[0]["page_id"] == "PAGE_SUPPLIERS"


def test_retrieval_returns_results():
    retriever = MetadataRetrieval()

    results = retriever.retrieve("show inventory stock")

    assert len(results) > 0


def test_empty_query():
    retriever = MetadataRetrieval()

    assert retriever.retrieve("") == []