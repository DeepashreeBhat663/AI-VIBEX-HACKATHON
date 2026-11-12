from flask import Flask, render_template, request, redirect, url_for
from matcher import find_matches

app = Flask(__name__)

# Store all items temporarily
all_items = []


# HOME PAGE
@app.route("/")
def home():
    return render_template(
        "index.html",
        items=all_items
    )


# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        print("Login:", email)

        return redirect(url_for("home"))

    return render_template("login.html")


# REGISTER PAGE
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        return redirect(url_for("login"))

    return render_template("register.html")


# REPORT PAGE
@app.route("/report-page")
def report_page():
    return render_template("report.html")


# SUBMIT REPORT
@app.route("/report", methods=["POST"])
def report():

    item = {
        "id": len(all_items) + 1,
        "type": request.form["type"].lower(),
        "name": request.form["title"],
        "category": request.form["category"],
        "description": request.form["description"],
        "location": request.form["location"],
        "status": "open"
    }

    matches = find_matches(item, all_items)

    all_items.append(item)

    return render_template(
        "match_result.html",
        item=item,
        matches=matches
    )


# MATCH PAGE (optional direct access)
@app.route("/match")
def match():
    return render_template(
        "match_result.html",
        matches=[]
    )


if __name__ == "__main__":
    app.run(debug=True)
