import os
import json
import datetime
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

# Google Sheets API設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_content = os.environ.get("GSPREAD_CREDENTIALS")
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(json_content), scope)
gc = gspread.authorize(credentials)

SPREADSHEET_URL = os.environ.get("SPREADSHEET_URL")

@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("form.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "Nitiei" and password == "8823":
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="ログイン情報が間違っています")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/submit", methods=["POST"])
def submit():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    date = request.form["date"]
    site = request.form["site"]
    place = request.form["place"]
    wbgt = request.form["wbgt"]
    person = request.form["person"]
    note = request.form["note"]

    now = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
    day_of_week = ["月", "火", "水", "木", "金", "土", "日"][now.weekday()]
    timestamp = now.strftime("%Y-%m-%d %H:%M")

    try:
        sh = gc.open_by_url(SPREADSHEET_URL)
        worksheet = sh.sheet1
        worksheet.append_row([timestamp, date, day_of_week, site, place, wbgt, person, note])
    except Exception as e:
        return str(e)

    return redirect(url_for("index"))

@app.route("/records")
def records():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return redirect(SPREADSHEET_URL)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
