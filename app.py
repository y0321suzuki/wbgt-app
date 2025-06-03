
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import csv
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

def get_gspread_client():
    json_str = os.getenv("GSPREAD_CREDENTIALS")
    if not json_str:
        raise ValueError("GSPREAD_CREDENTIALS is not set")
    json_data = json.loads(json_str)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_data, scope)
    return gspread.authorize(credentials)

def append_to_google_sheet(data):
    gc = get_gspread_client()
    sh = gc.open_by_key(os.getenv("SPREADSHEET_KEY"))
    worksheet = sh.sheet1
    worksheet.append_row(data)

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
            request.form["date"],
            request.form["weekday"],
            request.form["site_name"],
            request.form["location"],
            request.form["wbgt"],
            request.form["measurer"],
            request.form["notes"],
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            session["user"]
        ]
        try:
            append_to_google_sheet(record)
            message = "Googleスプレッドシートに保存されました。"
        except Exception as e:
            message = f"保存に失敗しました: {e}"
        return render_template("form.html", message=message)
    return render_template("form.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
