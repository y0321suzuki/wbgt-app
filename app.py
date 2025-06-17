from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
import os
import pytz
import gspread
import json

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

# Google Sheets 設定
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1VkDVyJnLxHZ4K4e1JkygbGX8Kcw5Y9QMmezIMwxZomc/edit#gid=0"

def get_gsheet():
    json_str = os.getenv("GSPREAD_CREDENTIALS")
    info = json.loads(json_str)
    gc = gspread.service_account_from_dict(info)
    sh = gc.open_by_url(SPREADSHEET_URL)
    return sh.sheet1

@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]
        if user == "Nitiei" and pw == "iw-sekkei.01":
            session["user"] = user
            return redirect(url_for("form"))
        return render_template("login.html", error="ログイン情報が間違っています。")
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
        tz = pytz.timezone("Asia/Tokyo")
        now = datetime.now(tz)
        date = request.form["date"]
        weekday = request.form["weekday"]
        site_name = request.form["site_name"]
        location = request.form["location"]
        wbgt = request.form["wbgt"]
        measurer = request.form["measurer"]
        notes = request.form["notes"]
        row = [date, site_name, location, wbgt, measurer, notes, weekday, now.strftime("%Y-%m-%d %H:%M:%S")]
        try:
            sheet = get_gsheet()
            sheet.append_row(row)
            return render_template("form.html", message="記録を保存しました。")
        except Exception as e:
            return render_template("form.html", error=f"保存中にエラーが発生しました: {str(e)}")
    return render_template("form.html")

@app.route("/records")
def records():
    return redirect(SPREADSHEET_URL)
