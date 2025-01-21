import psycopg2
from psycopg2.extras import DictCursor
from utils.config.settings import POSTGRES_CONFIG

def get_postgres_connection(dbname):
    return psycopg2.connect(
        host=POSTGRES_CONFIG["host"],
        port=POSTGRES_CONFIG["port"],
        user=POSTGRES_CONFIG["user"],
        password=POSTGRES_CONFIG["password"],
        dbname=POSTGRES_CONFIG[f"{dbname}"]
    )

def execute_query(query, params=None):
    with get_postgres_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            print(query)
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            conn.commit()

def insert_data(query, data):
    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(query, data)
            conn.commit()
