
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import csv
import os
import json
import gspread

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

# Google Sheets 接続設定
GSPREAD_CREDENTIALS = json.loads(os.environ.get("GSPREAD_CREDENTIALS", "{}"))
SPREADSHEET_ID = os.getenv("SPREADSHEET_KEY", "")
SHEET_NAME = "シート1"

gc = gspread.service_account_from_dict(GSPREAD_CREDENTIALS)

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
            session["user"],
            request.form["site_name"],
            request.form["location"],
            request.form["wbgt"],
            request.form["person"],
            request.form["notes"]
        ]
        worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        worksheet.append_row(record)
        return render_template("form.html", message="記録が保存されました。")
    return render_template("form.html")

@app.route("/records")
def records():
    if not session.get("user"):
        return redirect(url_for("login"))
    worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    records = worksheet.get_all_values()
    headers = records[0] if records else []
    data = records[1:] if len(records) > 1 else []
    return render_template("records.html", headers=headers, data=data)
