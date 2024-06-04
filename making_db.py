import sqlite3

def making_db():
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    create_table_query = """
    CREATE TABLE EC_Value (
        time TIMESTAMP NOT NULL,
        outerEC REAL NOT NULL,
        spongeEC REAL NOT NULL,
        PRIMARY KEY (time)
    )
    """
    
    cursor.execute(create_table_query)
    connection.commit()
    
    return connection, cursor