
from pathlib import Path
import json

DATA = Path(__file__).resolve().parents[1] / "data" / "metadata"

with open(DATA / "application_metadata.json", encoding="utf-8") as f:
    app = json.load(f)

with open(DATA / "api_registry.json", encoding="utf-8") as f:
    registry = json.load(f)

pages = app["pages"]
apis = registry["apis"]

page_ids = [p["page_id"] for p in pages]
routes = [p["route"] for p in pages]
api_ids = [a["api_id"] for a in apis]

assert len(pages) == 10
assert len(page_ids) == len(set(page_ids))
assert len(routes) == len(set(routes))
assert len(api_ids) == len(set(api_ids))

for page in pages:
    assert page["page_id"]
    assert page["description"]
    assert page["route"].startswith("/")

    widget_ids = [
        w["widget_id"] for w in page["widgets"]
    ]
    assert len(widget_ids) == len(set(widget_ids))

    for api_id in page["api_ids"]:
        assert api_id in api_ids

for api in apis:
    assert api["method"] in [
        "GET", "POST", "PATCH", "PUT", "DELETE"
    ]
    assert api["path"].startswith("/api/")
    assert api["required_permission"]

print("Metadata validation passed!")
print("Pages:", len(pages))
print("Registered APIs:", len(apis))
