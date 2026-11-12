from sample_data import SAMPLE_ITEMS
from matcher import find_matches

for item in SAMPLE_ITEMS:
    if item["type"] == "lost":
        print("\nLOST:", item["name"])
        matches = find_matches(item, SAMPLE_ITEMS)
        if not matches:
            print("   (no matches)")
        for m in matches:
            print("  ", m["item"]["name"], "->", m["score"], "%", "|", m["reason"])