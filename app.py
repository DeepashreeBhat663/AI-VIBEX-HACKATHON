from flask import render_template
from lostfound import app   # the backend app with /report, /items, /search, /match


# Pretend nobody is logged in (we have no login system)
class GuestUser:
    is_authenticated = False
    username = "Guest"
    name = "Guest"


@app.context_processor
def inject_user():
    return {"current_user": GuestUser()}


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