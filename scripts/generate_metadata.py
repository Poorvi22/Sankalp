
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "metadata"
OUTPUT.mkdir(parents=True, exist_ok=True)

# Page ID, name, route, description, business API
PAGE_DEFINITIONS = [
    (
        "PAGE_DASHBOARD",
        "Business Overview",
        "/dashboard",
        "Executive KPIs, revenue, alerts and business health",
        "API_DASHBOARD_SUMMARY"
    ),
    (
        "PAGE_INVENTORY",
        "Inventory & Warehouse",
        "/inventory",
        "Products, stock levels, reorder points and warehouses",
        "API_INVENTORY_LIST"
    ),
    (
        "PAGE_SUPPLIERS",
        "Supplier Management",
        "/suppliers",
        "Supplier prices, reliability, lead times and offers",
        "API_SUPPLIERS_LIST"
    ),
    (
        "PAGE_PROCUREMENT",
        "Procurement",
        "/procurement",
        "Purchase orders, draft creation and approvals",
        "API_PURCHASE_ORDERS_LIST"
    ),
    (
        "PAGE_SALES",
        "Sales & Orders",
        "/sales",
        "Customer orders, revenue and sales performance",
        "API_SALES_LIST"
    ),
    (
        "PAGE_LOGISTICS",
        "Logistics & Deliveries",
        "/logistics",
        "Shipment tracking, delivery dates and delays",
        "API_DELIVERIES_LIST"
    ),
    (
        "PAGE_FINANCE",
        "Finance & Cash Flow",
        "/finance",
        "Cash receipts, payments, expenses and cash flow",
        "API_FINANCE_LIST"
    ),
    (
        "PAGE_ANALYTICS",
        "Analytics & Reports",
        "/analytics",
        "Business trends, comparisons and historical reports",
        "API_ANALYTICS_SUMMARY"
    ),
    (
        "PAGE_APPROVALS",
        "Approvals",
        "/approvals",
        "Purchase order approvals and pending decisions",
        "API_APPROVALS_LIST"
    ),
    (
        "PAGE_AGENT_ACTIVITY",
        "Agent Activity",
        "/agent-activity",
        "Agent task history, execution logs and latency",
        "API_AGENT_ACTIVITY_LIST"
    )
]

pages = []
apis = []

for page_id, name, route, description, api_id in PAGE_DEFINITIONS:

    pages.append({
        "page_id": page_id,
        "name": name,
        "route": route,
        "description": description,
        "widgets": [
            {
                "widget_id": f"{page_id}_GRID",
                "type": "data_grid",
                "description": f"Records displayed on {name}"
            },
            {
                "widget_id": f"{page_id}_CHART",
                "type": "chart",
                "description": f"Analytics displayed on {name}"
            }
        ],
        "filters": [
            {
                "filter_id": "date_range",
                "type": "date_range"
            },
            {
                "filter_id": "region",
                "type": "multi_select"
            },
            {
                "filter_id": "status",
                "type": "multi_select"
            }
        ],
        "sort_options": [
            "date_asc",
            "date_desc"
        ],
        "api_ids": [api_id]
    })

    apis.append({
        "api_id": api_id,
        "method": "GET",
        "path": f"/api{route}",
        "description": f"Retrieve data for {name}",
        "required_permission": "business.read",
        "read_only": True
    })

metadata = {
    "application": "BizPilot AI",
    "version": "1.0.0",
    "pages": pages
}

api_registry = {
    "version": "1.0.0",
    "apis": apis
}

with open(
    OUTPUT / "application_metadata.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(metadata, file, indent=2)

with open(
    OUTPUT / "api_registry.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(api_registry, file, indent=2)

print("Application metadata generated!")
print("Pages:", len(pages))
print("APIs:", len(apis))
