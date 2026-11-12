from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary storage
items = []


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html", items=items)


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
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        print("Registered:", name)

        return redirect(url_for("login"))

    return render_template("register.html")


# REPORT ITEM PAGE
@app.route("/report-page")
def report_page():
    return render_template("report.html")


# SUBMIT ITEM
@app.route("/report", methods=["POST"])
def report():

    item = {
        "title": request.form["title"],
        "type": request.form["type"],
        "location": request.form["location"],
        "description": request.form["description"]
    }

    items.append(item)

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)