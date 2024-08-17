import psycopg2
import os

CONFIG = {'host':'localhost',
        'database':'postgres',
        'user':os.environ['POSTGRES_USER'],
        'password': os.environ['POSTGRES_PASSWORD'],
        }


def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            # Successfully connected
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def execute_select_sql(query, params, config=CONFIG):
    conn = connect(config)
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
    finally:
        conn.close()
    
    return result

def execute_insert_update_sql(query, params, config=CONFIG):
    conn = connect(config)
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if cursor:
                result = cursor.fetchone()
        conn.commit()

    finally:
        conn.close()
    
    return result