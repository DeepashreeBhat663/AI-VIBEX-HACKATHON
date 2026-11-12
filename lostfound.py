
from flask import Flask, request, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Database connection
def connect_db():
    return sqlite3.connect("findit.db")


# Create database table
def create_table():
    db = connect_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            name TEXT,
            description TEXT,
            location TEXT,
            date TEXT,
            photo TEXT
        )
    """)

    db.commit()
    db.close()


# 1. Report Lost or Found Item
@app.route("/report", methods=["POST"])
def report_item():

    item_type = request.form.get("type")
    name = request.form.get("name")
    description = request.form.get("description")
    location = request.form.get("location")
    date = request.form.get("date")

    if not all([item_type, name, description, location, date]):
        return jsonify({"error": "Please fill all fields"}), 400

    if item_type not in ["Lost", "Found"]:
        return jsonify({"error": "Invalid item type"}), 400

    photo = request.files.get("photo")
    filename = ""

    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(UPLOAD_FOLDER, filename))

    db = connect_db()

    db.execute("""
        INSERT INTO items
        (type, name, description, location, date, photo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (item_type, name, description,
          location, date, filename))

    db.commit()
    db.close()

    return jsonify({
        "message": "Item reported successfully!"
    })


# 2. View All Items
@app.route("/items", methods=["GET"])
def view_items():

    db = connect_db()
    db.row_factory = sqlite3.Row

    items = db.execute(
        "SELECT * FROM items ORDER BY id DESC"
    ).fetchall()

    db.close()

    return jsonify([dict(item) for item in items])


# 3. Search Items
@app.route("/search", methods=["GET"])
def search_items():

    keyword = request.args.get("q", "")

    db = connect_db()
    db.row_factory = sqlite3.Row

    items = db.execute("""
        SELECT * FROM items
        WHERE name LIKE ?
        OR description LIKE ?
        OR location LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    )).fetchall()

    db.close()

    return jsonify([dict(item) for item in items])


# 4. AI Matching
@app.route("/match/<int:item_id>", methods=["GET"])
def match_items(item_id):

    db = connect_db()
    db.row_factory = sqlite3.Row

    target = db.execute(
        "SELECT * FROM items WHERE id = ?",
        (item_id,)
    ).fetchone()

    if not target:
        db.close()
        return jsonify({"error": "Item not found"}), 404

    opposite_type = (
        "Found" if target["type"] == "Lost" else "Lost"
    )

    candidates = db.execute(
        "SELECT * FROM items WHERE type = ?",
        (opposite_type,)
    ).fetchall()

    db.close()

    if not candidates:
        return jsonify({"matches": []})

    descriptions = [
        target["description"]
    ] + [
        item["description"] for item in candidates
    ]

    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(descriptions)

    scores = cosine_similarity(
        matrix[0:1], matrix[1:]
    )[0]

    matches = []

    for item, score in zip(candidates, scores):

        location_score = (
            1 if item["location"].lower()
            == target["location"].lower() else 0
        )

        name_score = (
            1 if item["name"].lower()
            == target["name"].lower() else 0
        )

        final_score = (
            score * 70
            + location_score * 20
            + name_score * 10
        )

        if final_score >= 25:

            matches.append({
                "id": item["id"],
                "name": item["name"],
                "description": item["description"],
                "location": item["location"],
                "match_score": round(final_score, 2)
            })

    matches.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return jsonify({"matches": matches})


# 5. Start Server
if __name__ == "__main__":

    create_table()

    print("FindIt Backend Started!")

    app.run(debug=True)
