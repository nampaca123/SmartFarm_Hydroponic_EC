from making_db import making_db
from insert_EC import insert_EC
from read_EC import read_EC
from datetime import datetime

# DB 생성
connection, cursor = making_db()

# 데이터 삽입
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
insert_EC(connection, cursor, current_time, 1.23, 0.98)
insert_EC(connection, cursor, '2024-05-30 12:00:00', 1.45, 1.25)

# 데이터 읽기
start_time = '2024-05-30 00:00:00'
end_time = datetime.now()

ectable = read_EC(cursor, start_time, end_time)
print(ectable)

# 연결 종료
cursor.close()
connection.close()
