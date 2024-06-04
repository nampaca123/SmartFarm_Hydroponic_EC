def insert_EC(connection, cursor, time, outerEC, spongeEC):
    
    insert_query = """
    INSERT INTO EC_Value (time, outerEC, spongeEC)
    VALUES (?, ?, ?)
    """
    
    cursor.execute(insert_query, (time, outerEC, spongeEC))
    connection.commit()