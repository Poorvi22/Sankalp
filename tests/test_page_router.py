import pytest

from backend.app.agent.page_router import PageRouter


@pytest.fixture(scope="module")
def router():
    return PageRouter()


@pytest.mark.parametrize(
    "query, expected_page",
    [
        (
            "what is happening across the business",
            "PAGE_DASHBOARD",
        ),
        (
            "show recent business expenses",
            "PAGE_FINANCE",
        ),
        (
            "compare business performance across periods",
            "PAGE_ANALYTICS",
        ),
        (
            "which products need replenishment",
            "PAGE_INVENTORY",
        ),
        (
            "compare supplier prices",
            "PAGE_SUPPLIERS",
        ),
        (
            "prepare a purchase order",
            "PAGE_PROCUREMENT",
        ),
        (
            "identify the best selling products",
            "PAGE_SALES",
        ),
        (
            "show delayed shipments",
            "PAGE_LOGISTICS",
        ),
    ],
)
def test_router_selects_expected_page(router, query, expected_page):
    result = router.route(query)

    assert result["page_id"] == expected_page
    assert result["route"] is not None


def test_empty_query_returns_no_page(router):
    result = router.route("   ")

    assert result["page_id"] is None
    assert result["route"] is None


def test_router_reports_its_method(router):
    result = router.route("show recent business expenses")

    assert result["method"] in {"rule", "semantic"}