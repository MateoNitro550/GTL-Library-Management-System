import os
import mysql.connector

db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'user'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'database': os.environ.get('DB_NAME', 'database')
}

def execute_query(query, params=None, operation="select"):
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

         # Check the operation type
        if operation.lower() == "select":
            # Fetch the data
            data = cursor.fetchall()
            conn.close()
            return data
        else:
            # For other operations ('update', 'insert', 'delete'), commit changes
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        conn.close()
        return str(e)
