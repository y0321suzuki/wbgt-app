
import os
import json
from flask import Flask, request, redirect, render_template, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Google Sheets 認証設定
def get_gspread_client():
    json_content = os.environ.get("GSPREAD_CREDENTIALS")
    if not json_content:
        raise ValueError("GSPREAD_CREDENTIALS が環境変数に設定されていません。")

    credentials_dict = json.loads(json_content)
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    return gspread.authorize(credentials)

# スプレッドシートのURLまたはキー
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1VkDVyJnLxHZ4K4e1JkygbGX8Kcw5Y9QMmezIMwxZomc/edit?usp=sharing"

@app.route('/')
def index():
    return redirect('/form')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        date = request.form['date']
        site = request.form['site']
        place = request.form['place']
        wbgt = request.form['wbgt']
        measurer = request.form['measurer']
        note = request.form['note']

        # 現在時刻（JST）
        jst = pytz.timezone('Asia/Tokyo')
        record_time = datetime.now(jst).strftime('%Y-%m-%d %H:%M')

        # 曜日
        day_of_week = ['月', '火', '水', '木', '金', '土', '日'][datetime.strptime(date, '%Y-%m-%d').weekday()]

        try:
            gc = get_gspread_client()
            sh = gc.open_by_url(SPREADSHEET_URL)
            worksheet = sh.sheet1
            worksheet.append_row([record_time, date, day_of_week, site, place, wbgt, measurer, note])
            session['message'] = '記録を保存しました。'
        except Exception as e:
            session['message'] = f'エラーが発生しました: {e}'

        return redirect('/form')

    message = session.pop('message', None)
    return render_template('form.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['logged_in'] = True
        return redirect('/form')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/records')
def records():
    try:
        gc = get_gspread_client()
        sh = gc.open_by_url(SPREADSHEET_URL)
        worksheet = sh.sheet1
        records = worksheet.get_all_values()[1:]  # ヘッダーを除く
        return render_template('records.html', records=records)
    except Exception as e:
        return f"エラーが発生しました: {e}"

if __name__ == '__main__':
    app.run(debug=True)
