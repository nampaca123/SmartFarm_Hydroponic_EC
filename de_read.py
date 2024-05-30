import cx_Oracle
from datetime import datetime
import pandas as pd

# 데이터베이스 연결
dsn_tns = cx_Oracle.makedsn('localhost', 1521, sid='xe')
connection = cx_Oracle.connect(user='system', password='9357', dsn=dsn_tns)

cursor = connection.cursor()

# 데이터 조회 함수
def read_EC(start_time, end_time):
    select_query = """
    SELECT time, beforeEC, spongeEC, afterEC
    FROM EC_Value
    WHERE time BETWEEN :start_time AND :end_time
    """
    
    cursor.execute(select_query, {
        'start_time': start_time,
        'end_time': end_time
    })
    
    rows = cursor.fetchall()
    
    ectable = pd.DataFrame(rows, columns=['Time', 'BeforeEC', 'SpongeEC', 'AfterEC'])
    print(ectable)
    
# 실험 시간
start_time = datetime(2024, 5, 30, 0, 0, 0)
end_time = datetime(2024, 5, 31, 0, 0, 0)

# 데이터 조회
read_EC(start_time, end_time)

# 커서와 연결 종료
cursor.close()
connection.close()

