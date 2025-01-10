import psycopg2
from psycopg2.extras import execute_values
from config import settings
from config.settings import POSTGRES_CONFIG

def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_CONFIG["host"],
        port=POSTGRES_CONFIG["port"],
        user=POSTGRES_CONFIG["user"],
        password=POSTGRES_CONFIG["password"],
        dbname=POSTGRES_CONFIG["dbname"]
    )
def insert_product(product):
    query = """
    INSERT INTO products (cip_code, title, brand, short_desc, long_desc, composition, posologie,
                          contre_indication, conditionnement, categorie, sous_categorie_1,
                          sous_categorie_2, price)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (cip_code) DO NOTHING;
    """
    values = (
        product.cip_code, product.title, product.brand, product.short_desc, product.long_desc,
        product.composition, product.posologie, product.contre_indication, product.conditionnement,
        product.categorie, product.sous_categorie_1, product.sous_categorie_2, product.price
    )
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, values)

def insert_images(cip_code, image_urls, source):
    query = """
    INSERT INTO images (cip_code, image_url, source)
    VALUES %s
    ON CONFLICT DO NOTHING;
    """
    values = [(cip_code, url, source) for url in image_urls]
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            execute_values(cursor, query, values)

def read_from_table(table_name, limit=50, all=False):
    """
    Reads data from a PostgreSQL table.

    :param table_name: Name of the table to read from.
    :param limit: Number of rows to read (default is 50).
    :param all: If True, read all rows, ignoring the limit (default is False).
    :return: List of rows from the table.
    """

    try:
        # Construct the query
        if all:
            query = f"SELECT * FROM {table_name};"
        else:
            query = f"SELECT * FROM {table_name} LIMIT {limit};"

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        # Fetch the results
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

def read_isbn(limit=50, all=False):
    return read_from_table('public.isbn', limit, all)

def read_gtin(limit=50, all=False):
    return read_from_table('public.gtin', limit, all)