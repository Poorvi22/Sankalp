import pytest

from backend.app.agent.semantic_retrieval import (
    SemanticMetadataRetriever
)


@pytest.fixture(scope="module")
def retriever():
    return SemanticMetadataRetriever()


def test_index_contains_documents(retriever):
    assert retriever.index.ntotal > 0


def test_inventory_query_returns_results(retriever):
    response = retriever.retrieve(
        "Which products need replenishment?",
        top_k=3
    )

    assert len(response["results"]) == 3


def test_supplier_query_returns_results(retriever):
    response = retriever.retrieve(
        "Compare vendor prices and delivery times",
        top_k=5
    )

    assert len(response["results"]) == 5


def test_empty_query_returns_no_results(retriever):
    assert retriever.retrieve("   ") == []