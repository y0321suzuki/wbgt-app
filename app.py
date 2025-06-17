from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import pytz
import gspread
import os
import json

from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Google Sheets 設定
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds_dict = json.loads(os.getenv("GSPREAD_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1VkDVyJnLxHZ4K4e1JkygbGX8Kcw5Y9QMmezIMwxZomc/edit").sheet1

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "Nitiei" and password == "iw-sekkei.01":
            session["user"] = username
            return redirect(url_for("form"))
        else:
            error = "ログイン情報が間違っています"
    return render_template("login.html", error=error)

@app.route("/form", methods=["GET", "POST"])
def form():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        now = datetime.now(pytz.timezone("Asia/Tokyo"))
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M")
        weekday = ["月", "火", "水", "木", "金", "土", "日"][now.weekday()]
        row = [
            date,
            weekday,
            request.form["site_name"],
            request.form["location"],
            request.form["wbgt"],
            request.form["person"],
            request.form["notes"]
        ]
        sheet.append_row(row)
        return render_template("form.html", message="記録を保存しました。")
    return render_template("form.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
