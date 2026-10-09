
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integration.retrieval_service import MetadataRetriever
from integration.business_service import (
    get_low_stock_products,
    compare_suppliers
)


def test_metadata_retrieval():
    retriever = MetadataRetriever()

    results = retriever.search(
        "Find products with low stock",
        top_k=5
    )

    assert len(results) > 0

    ids = [result["id"] for result in results]

    assert "PAGE_INVENTORY" in ids, (
        "Inventory page was not retrieved"
    )


def test_low_stock_query():
    records = get_low_stock_products()

    assert isinstance(records, list)

    for record in records:
        assert (
            record["quantity_available"]
            < record["reorder_level"]
        )


def test_supplier_comparison():
    results = compare_suppliers(
        product_id="PRD-0001",
        quantity=100
    )

    assert isinstance(results, list)

    for supplier in results:
        assert supplier["estimated_cost"] > 0
        assert supplier["reliability_score"] >= 0.80


if __name__ == "__main__":
    test_metadata_retrieval()
    test_low_stock_query()
    test_supplier_comparison()

    print("All integration service tests passed!")
