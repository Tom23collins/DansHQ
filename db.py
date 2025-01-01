import mysql.connector
from contextlib import closing

def connection_open(app):
    return mysql.connector.connect(
        host=app.config.get('DB_HOST'),
        user=app.config.get('DB_USER'),
        password=app.config.get('DB_PASSWORD'),
        database=app.config.get('DB_NAME')
    )

def db_update(app, sql, values):
    try:
        with connection_open(app) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(sql, values)
                connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def db_query(app, sql):
    try:
        with connection_open(app) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
                return results
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def db_query_values(app, sql, values):
    try:
        with connection_open(app) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(sql, values)
                results = cursor.fetchall()
                return results
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

