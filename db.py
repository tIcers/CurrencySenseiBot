import os
import os
from sys import exception
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DATABASE_URL = os.environ.get("DATABASE_URL")

# try:
#     conn = psycopg2.connect(DATABASE_URL)
#     cur = conn.cursor()
#     cur.execute('SELECT version();')
#     db_version = cur.fetchone()
#     print(db_version)
#     cur.close()
# except psycopg2.OperationalError as e:
#     print(f"Unable to connect: {e}")
# finally:
#     if conn is not None:
#         conn.close()

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn

def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id SERIAL PRIMARY KEY,
            city_name VARCHAR(255) NOT NULL,
            iata_code VARCHAR(3) NOT NULL,
            lowest_price NUMERIC
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
