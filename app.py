import os
import json
import datetime
from flask import Flask, render_template, request, redirect, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = "your_secret_key"

USERNAME = "Nitiei"
PASSWORD = "iw-sekkei.01"

# Google Sheets 接続設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(os.environ["GSPREAD_CREDENTIALS"]),
    scope
)
gc = gspread.authorize(credentials)
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1VkDVyJnLxHZ4K4e1JkygbGX8Kcw5Y9QMmezIMwxZomc/edit"
sheet = gc.open_by_url(spreadsheet_url).sheet1

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == USERNAME and password == PASSWORD:
            session["user"] = username
            return redirect("/form")
        else:
            return render_template("login.html", error=True)
    return render_template("login.html")

@app.route("/form", methods=["GET", "POST"])
def form():
    if "user" not in session:
        return redirect("/")
    if request.method == "POST":
        date = request.form["date"]
        site = request.form["site"]
        location = request.form["location"]
        wbgt = request.form["wbgt"]
        person = request.form["person"]
        note = request.form["note"]
        day_of_week = ["月", "火", "水", "木", "金", "土", "日"][datetime.datetime.strptime(date, "%Y-%m-%d").weekday()]
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M")
        row = [now, date, day_of_week, site, location, wbgt, person, note]
        sheet.append_row(row)
        return redirect("/form")
    return render_template("form.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")
