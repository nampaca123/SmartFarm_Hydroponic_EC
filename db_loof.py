from making_db import making_db
from app import start_insert_EC, stop_insert_EC, app  # app도 import
import time
import sqlite3
from flask import g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('onboard.db') 
    return g.db

if __name__ == '__main__':
    with app.app_context():  # 애플리케이션 컨텍스트 설정
        connection = get_db()  # 함수 호출로 수정
        cursor = connection.cursor()
        start_insert_EC()

        # 60초 후 데이터 삽입 중지
        time.sleep(60)
        stop_insert_EC()
