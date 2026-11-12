from flask import Flask, render_template, request, redirect, url_for
from matcher import find_matches

app = Flask(__name__)

all_items = []


@app.route("/")
def home():
    return render_template("index.html", items=all_items)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/report-page")
def report_page():
    return render_template("report.html")


@app.route("/report", methods=["POST"])
def report():

    item = {
        "id": len(all_items) + 1,
        "type": request.form["type"].lower(),
        "name": request.form["name"],
        "category": request.form["category"],
        "description": request.form["description"],
        "location": request.form["location"],
        "status": "open"
    }

    matches = find_matches(item, all_items)

    all_items.append(item)

    return render_template(
        "match_result.html",
        matches=matches,
        item=item
    )


if __name__ == "__main__":
    app.run(debug=True)
