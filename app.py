
from flask import Flask, render_template, request, redirect, url_for, session
import gspread
import json
import os
import pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ログイン認証用
USER_CREDENTIALS = {
    "username": "Nitiei",
    "password": "iw-sekkei.01"
}

# Google Sheets 認証設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(os.environ['GSPREAD_CREDENTIALS']), scope
)
gc = gspread.authorize(credentials)

# スプレッドシートIDとシート名
SPREADSHEET_KEY = "1VkDVyJnLxHZ4K4e1JkygbGX8Kcw5Y9QMmezIMwxZomc"
SHEET_NAME = "シート1"

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    if username == USER_CREDENTIALS["username"] and password == USER_CREDENTIALS["password"]:
        session['logged_in'] = True
        session['username'] = username
        return redirect('/form')
    return render_template('login.html', error='ログイン情報が間違っています')

@app.route('/form')
def form():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('logged_in'):
        return redirect('/')

    date = request.form['date']
    site = request.form['site']
    location = request.form['location']
    temperature = request.form['temperature']
    operator = request.form['operator']
    notes = request.form['notes']

    # 現在時刻（日本時間）を取得
    now = datetime.now(pytz.timezone('Asia/Tokyo'))
    weekday = ['月', '火', '水', '木', '金', '土', '日'][now.weekday()]
    now_str = now.strftime('%Y-%m-%d %H:%M')

    try:
        sh = gc.open_by_key(SPREADSHEET_KEY)
        worksheet = sh.worksheet(SHEET_NAME)

        worksheet.append_row([
            now_str,
            date,
            weekday,
            site,
            location,
            temperature,
            operator,
            notes
        ])
    except Exception as e:
        return f"エラーが発生しました: {e}"

    return redirect('/form')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/records')
def records():
    if not session.get('logged_in'):
        return redirect('/')
    return redirect("https://docs.google.com/spreadsheets/d/1VkDVyJnLxHZ4K4e1JkygbGX8Kcw5Y9QMmezIMwxZomc/edit?usp=sharing")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
