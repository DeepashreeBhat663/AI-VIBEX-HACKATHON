import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MIN_SCORE = 40  # hide matches below this percentage

# Different words for the same thing become one standard word
SYNONYMS = {
    "flask": "bottle", "tumbler": "bottle", "sipper": "bottle",
    "earbuds": "earphones", "airpods": "earphones", "headphones": "earphones",
    "backpack": "bag", "handbag": "bag", "purse": "wallet",
    "specs": "glasses", "spectacles": "glasses",
    "phone": "mobile", "smartphone": "mobile", "cellphone": "mobile",
    "id": "idcard",
}


def make_text(item):
    # Join name, category and description, then swap synonyms
    text = (item["name"] + " " + item["category"] + " " + item["description"]).lower()
    words = re.findall(r"[a-z0-9]+", text)
    words = [SYNONYMS.get(w, w) for w in words]
    return " ".join(words)


def text_scores(query_item, candidates):
    # Compare the query item's words with every candidate's words
    texts = [make_text(query_item)] + [make_text(c) for c in candidates]
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        vectors = vectorizer.fit_transform(texts)
    except ValueError:
        return [0.0] * len(candidates)
    scores = cosine_similarity(vectors[0:1], vectors[1:])[0]
    return list(scores)


def find_matches(query_item, all_items, top_n=3):
    # A lost item looks for found items, and a found item looks for lost items
    wanted_type = "found" if query_item["type"] == "lost" else "lost"
    candidates = [
        item for item in all_items
        if item["type"] == wanted_type and item.get("status", "open") == "open"
    ]
    if not candidates:
        return []

    text_part = text_scores(query_item, candidates)
    results = []

    for item, text_score in zip(candidates, text_part):
        same_location = 1 if item["location"] == query_item["location"] else 0
        same_category = 1 if item["category"] == query_item["category"] else 0

        total = 0.5 * text_score + 0.3 * same_location + 0.2 * same_category
        percent = round(total * 100)

        reasons = []
        if same_location:
            reasons.append("Same location")
        if same_category:
            reasons.append("Same category")
        if text_score > 0.1:
            reasons.append("Similar description")

        if percent >= MIN_SCORE:
            results.append({
                "item": item,
                "score": percent,
                "reason": ", ".join(reasons) if reasons else "Some matching words",
            })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_n]


if __name__ == "__main__":
    # Fake items to test with
    items = [
        {"id": 1, "type": "found", "name": "Dark steel flask", "category": "Bottle",
         "description": "steel bottle with black cap found on the table", "location": "Library"},
        {"id": 2, "type": "found", "name": "Casio calculator", "category": "Electronics",
         "description": "blue scientific calculator", "location": "Main Block"},
        {"id": 3, "type": "found", "name": "Blue ID card", "category": "ID Card",
         "description": "student id card with a photo", "location": "Canteen"},
         {"id": 4, "type": "found", "name": "Wireless earbuds", "category": "Electronics",
         "description": "white earbuds in a small case", "location": "Canteen"},
        {"id": 5, "type": "found", "name": "Black backpack", "category": "Bag",
         "description": "black bag with a laptop inside", "location": "Hostel"},
        {"id": 6, "type": "found", "name": "Steel tumbler", "category": "Bottle",
         "description": "silver bottle with a dent", "location": "Ground"},
    ]
    lost_items = [
        {"id": 10, "type": "lost", "name": "Black water bottle", "category": "Bottle",
         "description": "black steel bottle lost near the library", "location": "Library"},
        {"id": 11, "type": "lost", "name": "AirPods", "category": "Electronics",
         "description": "white airpods case", "location": "Canteen"},
        {"id": 12, "type": "lost", "name": "School bag", "category": "Bag",
         "description": "black backpack with books", "location": "Main Block"},
    ]

    for lost in lost_items:
        print("\nLOST:", lost["name"])
        for match in find_matches(lost, items):
            print("  ", match["item"]["name"], "->", match["score"], "%", "|", match["reason"])