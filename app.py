from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import tempfile
import pytz

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

json_content = os.getenv("GSPREAD_CREDENTIALS_JSON")
with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tmp_file:
    tmp_file.write(json_content)
    tmp_file.flush()
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        tmp_file.name,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(credentials)

sh = gc.open_by_key("1plcKipsn5Xqv2kdfppKMmhHxaswsOnvt3DMNRzn5Tmk")
worksheet = sh.get_worksheet(0)

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
        tz = pytz.timezone("Asia/Tokyo")
        now = datetime.now(tz)
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M")
        weekday_ja = ["月", "火", "水", "木", "金", "土", "日"][now.weekday()]

        record = [
            formatted_datetime,                # 記録日時（日本時間）
            weekday_ja,                        # 曜日
            request.form["site_name"],         # 現場名
            request.form["location"],          # 場所
            request.form["wbgt"],              # WBGT
            request.form["measurer"],          # 測定者
            request.form["notes"]              # 備考
        ]
        worksheet.append_row(record)
        return render_template("form.html", message="記録が保存されました。")
    return render_template("form.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
