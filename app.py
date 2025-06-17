
from flask import Flask, render_template, request, redirect, url_for, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ログイン情報
USERNAME = 'Nitiei'
PASSWORD = 'iw-sekkei.01'

# スプレッドシート接続設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(os.environ.get('GSPREAD_CREDENTIALS'))
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1VkDVyJnLxHZ4K4e1JkygbGX8Kcw5Y9QMmezIMwxZomc/edit?usp=sharing")
worksheet = spreadsheet.sheet1

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['username'] = username
            return redirect('/form')
        else:
            return render_template('login.html', error='ログイン情報が間違っています')
    return render_template('login.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        date = request.form['date']
        site = request.form['site']
        location = request.form['location']
        wbgt = request.form['wbgt']
        measurer = request.form['measurer']
        notes = request.form['notes']
        weekday = datetime.strptime(date, "%Y-%m-%d").strftime('%a')
        jst = pytz.timezone('Asia/Tokyo')
        record_time = datetime.now(jst).strftime("%Y-%m-%d %H:%M")
        worksheet.append_row([record_time, date, weekday, site, location, wbgt, measurer, notes])
        return redirect('/form')
    return render_template('form.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    pass
