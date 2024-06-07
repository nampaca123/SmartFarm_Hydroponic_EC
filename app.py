from flask import Flask, g, jsonify, request, render_template
from flask import redirect, url_for, session
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime, timedelta
import threading
import time
import subprocess
import sys
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dateutil"])
    from dateutil.relativedelta import relativedelta
import sqlite3
from insert_EC import insert_EC
from making_db import making_db
from read_EC import read_EC

app = Flask(__name__)
app.secret_key = os.urandom(24)

# DB 생성
connection, cursor = making_db()
tmp_ec_data = pd.read_csv('tmp_ec_data.csv')
tmp_ec_data2 = pd.read_csv('tmp_ec_data2.csv')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('onboard.db')
    return g.db

@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

# 10초 간격으로 데이터를 삽입하는 함수
def inserting_data_10sec():
    global stop_thread
    try:
        with app.app_context():
            connection = get_db()
            cursor = connection.cursor()
            tmp_ec_data = pd.read_csv('tmp_ec_data.csv')['feed_ec'].to_list()
            tmp_ec_data2 = pd.read_csv('tmp_ec_data2.csv')['feed_ec'].to_list()
            n = 0
            while not stop_thread:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                outerEC = tmp_ec_data[n]
                spongeEC = tmp_ec_data2[n]
                n += 1
                insert_EC(connection, cursor, current_time, outerEC, spongeEC)
                time.sleep(10)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if 'db' in g:
            g.db.close()

stop_thread = False
thread = None

# 데이터 삽입 시작 함수
def start_insert_EC():
    global stop_thread, thread
    stop_thread = False
    thread = threading.Thread(target=run_in_thread_with_context)
    thread.start()

# 스레드에서 애플리케이션 컨텍스트를 설정하여 데이터 삽입 함수 실행
def run_in_thread_with_context():
    with app.app_context():
        inserting_data_10sec()

# 데이터 삽입 종료 함수
def stop_insert_EC():
    global stop_thread, thread
    stop_thread = True
    if thread is not None:
        thread.join()
        thread = None

# 시간 범위를 반환하는 함수
def returning_time_range(option):
    now = datetime.now()
    if option == '6_hours':
        return now - timedelta(hours=6), now
    elif option == '1_day':
        return now - timedelta(days=1), now
    elif option == '1_week':
        return now - timedelta(weeks=1), now
    elif option == '1_month':
        return now - relativedelta(months=1), now
    elif option == '6_months':
        return now - relativedelta(months=6), now
    else:
        raise ValueError("Invalid option")

def returning_time_range_ti(num, unit):
    now = datetime.now()
    if unit == 'second':
        return now - timedelta(seconds=num), now
    elif unit == 'minute':
        return now - timedelta(minutes=num), now
    elif unit == 'hour':
        return now - timedelta(hours=num), now
    elif unit == 'month':
        return now - relativedelta(months=num), now
    elif unit == 'year':
        return now - relativedelta(years=num), now
    else:
        raise ValueError("Invalid option")

# 시간 범위에 따른 데이터를 조회하는 함수
def search_based_time_range(num, unit):
    connection = get_db()
    cursor = connection.cursor()
    start_time, end_time = returning_time_range_ti(num, unit)
    ectable = read_EC(cursor, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'))
    return ectable

# 전날 특정 시간대의 데이터를 조회하는 함수
def yeasterday_4division():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    slots = [
        (datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0), datetime(yesterday.year, yesterday.month, yesterday.day, 6, 0, 0)),
        (datetime(yesterday.year, yesterday.month, yesterday.day, 6, 0, 0), datetime(yesterday.year, yesterday.month, yesterday.day, 12, 0, 0)),
        (datetime(yesterday.year, yesterday.month, yesterday.day, 12, 0, 0), datetime(yesterday.year, yesterday.month, yesterday.day, 18, 0, 0)),
        (datetime(yesterday.year, yesterday.month, yesterday.day, 18, 0, 0), datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)),
    ]

    yesterday_dataframes = []
    for start_time, end_time in slots:
        ectable = read_EC(cursor, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'))
        yesterday_dataframes.append(ectable)

    return yesterday_dataframes

matplotlib.use('agg')

# AI Hub Data
global all_plant_data
all_plant_data = pd.read_csv('plant_data.csv')

start_insert_EC()

# Define endpoints
@app.route('/') # 가져와야하는 데이터 : 양액 그래프, 양액이 적절하니? 제공해야 하는 온도는?  
def first_login():
    return render_template('page-login.html') #, datas=result)

@app.route('/login_failed') # 가져와야하는 데이터 : 양액 그래프, 양액이 적절하니? 제공해야 하는 온도는?  
def login_failed():
    return render_template('page-login-fail.html') #, datas=result)

@app.route('/dologin', methods=['POST'])
def dologin():
    #작물정보 있다고 가정. 작물데이터 불러오기
    plant = request.form.get('plant')
    if plant in list(set(all_plant_data['kind'])):
        return redirect(url_for('home', plt=plant))
    else:
        print("해당 작물에 대한 데이터가 없습니다 :(")
        return redirect(url_for('login_failed'))

@app.route('/dashboard')
def home():
    # 시작날짜, 현재부터 nday 전까지의 dataframe = get_ndays_data()
    # growup_day(키운 날짜)  = 현재날짜 - 시작날짜
    # 총 수확일 90일 가정
    growup_day = 39
    if 0 < growup_day <= 30:
        stage = '정식기'
    elif 30 < growup_day <= 60:
        stage = '생육기'
    elif 30 < growup_day <= 90:
        stage = '수확기'
    else:
        return redirect(url_for('home2'))
    info = {}
    plant = request.args.get('plt', default='상추', type=str)
    data = all_plant_data.loc[all_plant_data.kind == plant]
    info['date'] = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))#.split()[0]#'2024-06-02' ## 받아와야할거. 현재날짜

    if info['date'].split('-')[1] in ['03', '04', '05']:
        info['season'] = '1봄'
    elif info['date'].split('-')[1] in ['06', '07', '08']:
        info['season'] = '2여름'
    elif info['date'].split('-')[1] in ['09', '10', '11']:
        info['season'] = '3가을'
    elif info['date'].split('-')[1] in ['12', '01', '02']:
        info['season'] = '4겨울'

    # data에 season 정보가 없을 경우
    possible_seasons = list(set(data.loc[data.stage == stage]['season']))
    if info['season'] not in possible_seasons:
        num = [abs(int(i[0]) - int(info['season'][0])) for i in possible_seasons]
        data2 = data.loc[data.season == possible_seasons[num.index(min(num))]]
    else:
        data2 = data.loc[data.season == info['season']]

    info['plant'], info['stage'], info['ec_min'], info['ec_max'] = plant, stage, data2['feed_ec_range'].values[0].split(',')[0][1:], data2['feed_ec_range'].values[0].split(',')[1][1:-1]
    info['temp_min'], info['temp_max'], info['light_min'], info['light_max'] = data2['in_temp_range'].values[0].split(',')[0][1:], data2['in_temp_range'].values[0].split(',')[1][1:-1], data2['light_range'].values[0].split(',')[0][1:], data2['light_range'].values[0].split(',')[1][1:-1]
    info['ec_temp_min'], info['ec_temp_max'], info['ph_min'], info['ph_max'] = data2['feed_temp_range'].values[0].split(',')[0][1:], data2['feed_temp_range'].values[0].split(',')[1][1:-1], data2['feed_ph_range'].values[0].split(',')[0][1:], data2['feed_ph_range'].values[0].split(',')[1][1:-1]

    ## 그래프 그리기
    ec_range = [float(info['ec_min']), float(info['ec_max'])]
    info['plot_outer'], _ = plotting_outer(ec_range)  
    info['plot_sponge'], abnormal_ec = plotting_sponge(ec_range)  
    info['plot_outer'] += '?time='+str(datetime.now()).split()[1]
    info['plot_sponge'] += '?time='+str(datetime.now()).split()[1]
    
    # weekly overview / 편의상7일로 했지만 시간 계산은 나중에
    info['ab_ec'] = abnormal_ec
    info['date_past'], info['date_diff'] = time_delta(info['date'], num= 120, unit = 'second')

    return render_template('home.html', data=info)

def time_delta(now_date, num, unit):
    now = datetime.strptime(now_date, "%Y-%m-%d %H:%M:%S")
    if unit == 'second':
        past = now - timedelta(seconds=num)#, now
    elif unit == 'minute':
        past = now - timedelta(minutes=num)#, now
    elif unit == 'hour':
        past = now - timedelta(hours=num)#, now
    elif unit == 'month':
        past = now - relativedelta(months=num)#, now
    elif unit == 'year':
        past = now - relativedelta(years=num)#, now
    else:
        raise ValueError("Invalid option")
    # past = now - timedelta(days=7)
    return str(past), now - past#.split()[0] 

def plotting_outer(ec_range_list):#, sensor_data):
    EC_table = search_based_time_range(120, 'second') # Time, OuterEC, SpongeEC
    sensor_data = EC_table['OuterEC'].to_list()
    y = np.array(sensor_data)
    x = np.arange(len(y))
    below_threshold = y < ec_range_list[0]
    above_threshold = y > ec_range_list[1]
    abnormal_ec = sum(below_threshold) + sum(above_threshold)
    plt.plot(x, y, color='olive', linewidth=4, alpha=0.3)
    plt.scatter(x[below_threshold], y[below_threshold], color='red')
    plt.scatter(x[above_threshold], y[above_threshold], color='red')
    plt.hlines(ec_range_list[0], 0, len(y), color='gray', linestyle='--', linewidth=2)
    plt.hlines(ec_range_list[1], 0, len(y), color='gray', linestyle='--', linewidth=2)
    plt.xlabel('time step', size=10)
    plt.ylabel('EC', size=10)
    plt.title('Outer EC timeline', size=15)
    plt.savefig("./static/assets/img/test_outer.png")
    plt.pause(1)
    plt.close()
    return '../static/assets/img/test_outer.png', abnormal_ec

def plotting_sponge(ec_range_list):#, sensor_data):
    EC_table = search_based_time_range(120, 'second') # Time, OuterEC, SpongeEC
    sensor_data2 = EC_table['SpongeEC'].to_list()
    y = np.array(sensor_data2)
    x = np.arange(len(y))
    below_threshold = y < ec_range_list[0]
    above_threshold = y > ec_range_list[1]
    abnormal_ec = sum(below_threshold) + sum(above_threshold)
    plt.plot(x, y, color='olive', linewidth=4, alpha=0.3)
    plt.scatter(x[below_threshold], y[below_threshold], color='red')
    plt.scatter(x[above_threshold], y[above_threshold], color='red')
    plt.hlines(ec_range_list[0], 0, len(y), color='gray', linestyle='--', linewidth=2)
    plt.hlines(ec_range_list[1], 0, len(y), color='gray', linestyle='--', linewidth=2)
    plt.xlabel('time step', size=10)
    plt.ylabel('EC', size=10)
    plt.title('Sponge EC timeline', size=15)
    plt.savefig("./static/assets/img/test_sponge.png")
    plt.pause(1)
    plt.close()
    return '../static/assets/img/test_sponge.png', abnormal_ec

@app.route('/dashboard_already_growup')
def home2():
    return render_template('home2.html')

'''
@app.route('/login')
def login():
    return render_template('page-login.html')

@app.route('/profile')
def profile():
    return render_template('page-profile.html')
'''
# Entry point to run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
