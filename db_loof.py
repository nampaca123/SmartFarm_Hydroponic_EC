from making_db import making_db
from db_control import start_insert_EC,stop_insert_EC
import time




if __name__ == '__main__':
    connection, cursor = making_db()
    start_insert_EC()

    # 60초 후 데이터 삽입 중지
    time.sleep(420)
    stop_insert_EC()