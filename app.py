import os
import json
import datetime
import pytz
import tempfile
from flask import Flask, render_template, request, redirect, url_for, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Google Sheetsの設定
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
SHEET_ID = "1VkDVyJnLxHZ4K4e1JkygbGX8Kcw5Y9QMmezIMwxZomc"  # 新しいシートID

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]
        if (user == "Nitiei" and pw == "iw-sekkei.01") or (user == "staff01" and pw == "staffpass01"):
            session["user"] = user
            return redirect(url_for("form"))
        else:
            error = "ログインに失敗しました"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/form", methods=["GET", "POST"])
def form():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        date = request.form["date"]
        site = request.form["site"]
        location = request.form["location"]
        wbgt = request.form["wbgt"]
        person = request.form["person"]
        memo = request.form["memo"]

        # 現在時刻と曜日を取得
        tz = pytz.timezone("Asia/Tokyo")
        now = datetime.datetime.now(tz)
        timestamp = now.strftime("%Y-%m-%d %H:%M")
        weekday = ["月", "火", "水", "木", "金", "土", "日"][now.weekday()]

        # JSONキーをtempfileに一時保存
        json_content = os.getenv("GSPREAD_CREDENTIALS")
        tmp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json")
        tmp_file.write(json_content)
        tmp_file.close()

        creds = ServiceAccountCredentials.from_json_keyfile_name(tmp_file.name, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        sheet.append_row([timestamp, weekday, site, location, wbgt, person, memo])

    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)
