from making_db import making_db
from insert_EC import insert_EC
from read_EC import read_EC
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
import pandas as pd
from flask import g
import sqlite3

# DB 생성
connection, cursor = making_db()
tmp_ec_data = pd.read_csv('tmp_ec_data.csv')
tmp_ec_data2 = pd.read_csv('tmp_ec_data2.csv')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('onboard.db') 
    return g.db

# 10초 간격으로 데이터를 삽입하는 함수
def inserting_data_10sec():
    global stop_thread
    # 각 스레드에서 새로운 데이터베이스 연결 생성
    connection, cursor = making_db()
    tmp_ec_data = pd.read_csv('tmp_ec_data.csv')
    tmp_ec_data2 = pd.read_csv('tmp_ec_data2.csv')  
    tmp_ec_data = tmp_ec_data['feed_ec'].to_list()
    tmp_ec_data2 = tmp_ec_data2['feed_ec'].to_list()
    n = 0
    while not stop_thread:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 예시값임. 추후 실제 센서의 값으로 변경
        outerEC = tmp_ec_data[n]
        spongeEC = tmp_ec_data2[n]
        n += 1
        insert_EC(connection, cursor, current_time, outerEC, spongeEC)
        time.sleep(10)
    cursor.close()
    connection.close()

stop_thread = False
thread = None

# 데이터 삽입 시작 함수
def start_insert_EC():
    global stop_thread, thread
    stop_thread = False
    thread = threading.Thread(target=inserting_data_10sec)
    thread.start()

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
    
def returning_time_range_ti(num,unit):
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
def search_based_time_range(num,unit):
    connection = get_db()
    cursor = connection.cursor()
    start_time, end_time = returning_time_range_ti(num,unit)
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


# 밑부터는 정상 가동 여부 실험. 최종 완성 작업 시 메인 구동 파일에 복사붙여넣기 시에는 불필요한 코드들임
'''
# 데이터를 10초 간격으로 삽입 시작
start_insert_EC()

# 60초 후 데이터 삽입 중지
time.sleep(420)
stop_insert_EC()

# 6시간 동안의 데이터 조회
sixhoursdata = search_based_time_range('6_hours')
print("6시간 동안의 데이터: ")
print(sixhoursdata)

# 전날 특정 시간대의 데이터 조회
ydf1, ydf2, ydf3, ydf4 = yeasterday_4division()
print("00:00 ~ 06:00 데이터:")
print(ydf1)
print("06:00 ~ 12:00 데이터:")
print(ydf2)
print("12:00 ~ 18:00 데이터:")
print(ydf3)
print("18:00 ~ 24:00 데이터:")
print(ydf4)

# 연결 종료
cursor.close()
connection.close()
'''
