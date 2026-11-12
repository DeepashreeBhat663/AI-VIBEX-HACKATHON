from flask import render_template, send_from_directory
from lostfound import app, connect_db, create_table, UPLOAD_FOLDER

create_table()   # makes sure the items table exists


# Home page: shows all items
@app.route("/")
def home():
    db = connect_db()
    items = db.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
    db.close()
    return render_template("index.html", items=items)


# Report form page
@app.route("/report-page")
def report_page():
    return render_template("report.html")


# Lets the browser open uploaded photos
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)