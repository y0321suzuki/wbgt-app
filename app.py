from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

CSV_FILE = "wbgt_records.csv"
MAX_RECORDS = 100

@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    return redirect(url_for("form"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]
        if (user == "Nitiei" and pw == "iw-sekkei.01") or (user == "staff01" and pw == "staffpass01"):
            session["user"] = user
            return redirect(url_for("form"))
        return render_template("login.html", error="ログインに失敗しました")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/form", methods=["GET", "POST"])
def form():
    if not session.get("user"):
        return redirect(url_for("login"))
    if request.method == "POST":
        record = [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            request.form["date"],
            request.form["weekday"],
            request.form["site_name"],
            request.form["location"],
            request.form["wbgt"],
            request.form["measurer"],
            request.form["notes"]
        ]
        records = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                records = list(reader)

        records.append(record)
        if len(records) > MAX_RECORDS:
            records = records[-MAX_RECORDS:]

        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(records)

        return render_template("form.html", message="記録が保存されました。")
    return render_template("form.html")

@app.route("/records")
def view_records():
    if not session.get("user"):
        return redirect(url_for("login"))
    records = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            records = list(reader)
    return render_template("records.html", records=records)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
