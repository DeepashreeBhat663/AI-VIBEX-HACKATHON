from flask import render_template
from lostfound import app   # the backend app with /report, /items, /search, /match


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Login page (only works if templates/login.html exists)
@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)