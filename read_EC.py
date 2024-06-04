import pandas as pd

def read_EC(cursor, start_time, end_time):
    
    select_query = """
    SELECT time, outerEC, spongeEC
    FROM EC_Value
    WHERE time BETWEEN ? AND ?
    """
    
    cursor.execute(select_query, (start_time, end_time))
    rows = cursor.fetchall()
    
    ectable = pd.DataFrame(rows, columns=['Time', 'OuterEC', 'SpongeEC'])
    return ectable