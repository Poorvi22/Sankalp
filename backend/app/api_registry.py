"""
Central API registry for BizPilot AI.

This registry describes the API operations associated with each page.
The implemented flag distinguishes real endpoints from planned endpoints.
"""

from copy import deepcopy


API_REGISTRY = {
    "PAGE_DASHBOARD": {
        "page_id": "PAGE_DASHBOARD",
        "title": "Business Overview",
        "route": "/dashboard",
        "apis": [
            {
                "api_id": "API_DASHBOARD_OVERVIEW",
                "method": "GET",
                "path": "/api/dashboard/overview",
                "description": "Retrieve business overview KPIs.",
                "implemented": False,
            }
        ],
    },
    "PAGE_INVENTORY": {
        "page_id": "PAGE_INVENTORY",
        "title": "Inventory and Warehouse",
        "route": "/inventory",
        "apis": [
            {
                "api_id": "API_INVENTORY_LIST",
                "method": "GET",
                "path": "/api/inventory",
                "description": "Retrieve and filter inventory records.",
                "implemented": False,
            }
        ],
    },
    "PAGE_SUPPLIERS": {
        "page_id": "PAGE_SUPPLIERS",
        "title": "Supplier Management",
        "route": "/suppliers",
        "apis": [
            {
                "api_id": "API_SUPPLIERS_LIST",
                "method": "GET",
                "path": "/api/suppliers",
                "description": "Retrieve supplier information.",
                "implemented": False,
            }
        ],
    },
    "PAGE_PROCUREMENT": {
        "page_id": "PAGE_PROCUREMENT",
        "title": "Procurement and Purchase Orders",
        "route": "/procurement",
        "apis": [
            {
                "api_id": "API_PROCUREMENT_ORDERS",
                "method": "GET",
                "path": "/api/procurement/orders",
                "description": "Retrieve purchase orders.",
                "implemented": False,
            }
        ],
    },
    "PAGE_SALES": {
        "page_id": "PAGE_SALES",
        "title": "Sales and Customer Orders",
        "route": "/sales",
        "apis": [
            {
                "api_id": "API_SALES_ORDERS",
                "method": "GET",
                "path": "/api/sales/orders",
                "description": "Retrieve customer orders and sales records.",
                "implemented": False,
            }
        ],
    },
    "PAGE_LOGISTICS": {
        "page_id": "PAGE_LOGISTICS",
        "title": "Logistics and Deliveries",
        "route": "/logistics",
        "apis": [
            {
                "api_id": "API_LOGISTICS_DELIVERIES",
                "method": "GET",
                "path": "/api/logistics/deliveries",
                "description": "Retrieve delivery and shipment information.",
                "implemented": False,
            }
        ],
    },
    "PAGE_FINANCE": {
        "page_id": "PAGE_FINANCE",
        "title": "Finance and Cash Flow",
        "route": "/finance",
        "apis": [
            {
                "api_id": "API_FINANCE_OVERVIEW",
                "method": "GET",
                "path": "/api/finance/overview",
                "description": "Retrieve financial summaries and cash flow.",
                "implemented": False,
            }
        ],
    },
    "PAGE_ANALYTICS": {
        "page_id": "PAGE_ANALYTICS",
        "title": "Analytics and Business Reports",
        "route": "/analytics",
        "apis": [
            {
                "api_id": "API_ANALYTICS_REPORTS",
                "method": "GET",
                "path": "/api/analytics/reports",
                "description": "Retrieve business analytics and reports.",
                "implemented": False,
            }
        ],
    },
}


def list_page_apis():
    """Return API details for every registered application page."""
    return deepcopy(list(API_REGISTRY.values()))


def get_page_apis(page_id: str):
    """Return API details for one page, or None if it does not exist."""
    page = API_REGISTRY.get(page_id)

    if page is None:
        return None

    return deepcopy(page)