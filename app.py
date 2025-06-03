from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os
import json
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

# Google Sheets 認証
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.getenv("GSPREAD_CREDENTIALS"))
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
gc = gspread.authorize(creds)

# スプレッドシートIDとシート名
SPREADSHEET_ID = "1plcKipsn5Xqv2kdfppKMmhHxaswsOnvt3DMNRzn5Tmk"
SHEET_NAME = "シート1"

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
            datetime.now().strftime("%H:%M"),
            session["user"],
            request.form["site_name"],
            request.form["location"],
            request.form["wbgt"],
            request.form["observer"],
            request.form["notes"]
        ]
        worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        worksheet.append_row(record)
        return render_template("form.html", message="記録が保存されました。")
    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)
