
from pathlib import Path
import json

DATA = Path(__file__).resolve().parents[1] / "data" / "metadata"

with open(DATA / "application_metadata.json", encoding="utf-8") as f:
    metadata = json.load(f)

query = "Find products with low stock"
words = set(query.lower().split())

results = []

for page in metadata["pages"]:
    text = (
        page["name"] + " " +
        page["description"]
    ).lower()

    score = sum(
        1 for word in words
        if word in text.split()
    )

    if score:
        results.append((score, page))

results.sort(key=lambda item: item[0], reverse=True)

print("Query:", query)

for score, page in results[:5]:
    print(
        page["page_id"],
        page["route"],
        "Score:", score
    )
