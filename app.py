
from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ユーザー認証情報（例: ユーザー名: Nitiei, パスワード: iw-sekkei.01）
users = {
    "Nitiei": "iw-sekkei.01"
}

# スプレッドシート認証
def connect_to_gspread():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = json.loads(os.environ['GSPREAD_CREDENTIALS'])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(credentials)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1VkDVyJnLxHZ4K4e1JkygbGX8Kcw5Y9QMmezIMwxZomc/edit#gid=0").sheet1
    return sheet

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('form'))
        else:
            error = 'ログイン情報が間違っています'
    return render_template('login.html', error=error)

@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        date = request.form['date']
        place = request.form['place']
        site = request.form['site']
        temperature = request.form['temperature']
        measurer = request.form['measurer']
        notes = request.form['notes']
        username = session['username']

        jst = pytz.timezone('Asia/Tokyo')
        now = datetime.datetime.now(jst)
        day_of_week = ['月', '火', '水', '木', '金', '土', '日'][now.weekday()]
        timestamp = now.strftime('%Y-%m-%d %H:%M')

        sheet = connect_to_gspread()
        sheet.insert_row([timestamp, username, date, day_of_week, place, site, temperature, measurer, notes], 2)
        return redirect(url_for('form'))

    return render_template('form.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
