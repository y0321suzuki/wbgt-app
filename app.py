from flask import Flask, render_template, request, redirect, url_for, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ログイン情報
USERNAME = "Nitiei"
PASSWORD = "iw-sekkei.01"

# スプレッドシート設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(os.environ["GSPREAD_CREDENTIALS"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)

spreadsheet_url = "https://docs.google.com/spreadsheets/d/1VkDVyJnLxHZ4K4e1JkygbGX8Kcw5Y9QMmezIMwxZomc/edit?usp=sharing"
sh = gc.open_by_url(spreadsheet_url)
worksheet = sh.get_worksheet(0)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("form"))
        else:
            return render_template("login.html", error="ログイン情報が間違っています")
    return render_template("login.html")

@app.route("/form", methods=["GET", "POST"])
def form():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if request.method == "POST":
        date = request.form["date"]
        site = request.form["site"]
        place = request.form["place"]
        wbgt = request.form["wbgt"]
        measurer = request.form["measurer"]
        note = request.form["note"]

        jst = pytz.timezone("Asia/Tokyo")
        timestamp = datetime.now(jst).strftime("%Y-%m-%d %H:%M")
        weekday = datetime.now(jst).strftime("月火水木金土日"[datetime.now(jst).weekday()])
        row = [timestamp, date, weekday, site, place, wbgt, measurer, note]
        worksheet.append_row(row)

        return redirect(url_for("form"))
    return render_template("form.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
