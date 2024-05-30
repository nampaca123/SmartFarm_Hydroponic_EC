import cx_Oracle
from datetime import datetime

# 데이터베이스 연결
dsn_tns = cx_Oracle.makedsn('localhost', '1521', sid='xe')
connection = cx_Oracle.connect(user='system', password='9357', dsn=dsn_tns)

cursor = connection.cursor()

# 데이터 삽입 함수
def insert_EC(time, beforeEC, spongeEC, afterEC):
    insert_query = """
    INSERT INTO EC_Value (time, beforeEC, spongeEC, afterEC)
    VALUES (:time, :beforeEC, :spongeEC, :afterEC)
    """
    cursor.execute(insert_query, {
        'time': time,
        'beforeEC': beforeEC,
        'spongeEC': spongeEC,
        'afterEC': afterEC
    })
    connection.commit()

# 현재 시간으로 current_time 지정
current_time = datetime.now()

# 정상 작동 시험 확인
# insert_EC(current_time, 1.23, 0.98, 0.75)
# 정상 작동함!

# 연결 종료
cursor.close()
connection.close()
