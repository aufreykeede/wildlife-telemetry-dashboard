import sqlite3
import pandas as pd


def init_db(db_name="wildlife.db"):
    """
    Initialize SQLite database.

    Why this matters:
    Wildlife data systems need structured storage so multiple users
    (analysts, field staff, researchers) can query consistent data.
    """
    conn = sqlite3.connect(db_name)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wildlife_raw (
        animal_id TEXT,
        timestamp TEXT,
        latitude REAL,
        longitude REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wildlife_validated (
        animal_id TEXT,
        timestamp TEXT,
        latitude REAL,
        longitude REAL
    )
    """)

    conn.commit()
    return conn


def insert_data(conn, df):
    df.to_sql("wildlife_raw", conn, if_exists="replace", index=False)
    
def insert_validated(conn, df):
    df.to_sql("wildlife_validated", conn, if_exists="replace", index=False)

def query_all(conn):
    """
    Simple test query to confirm data exists.
    """
    return pd.read_sql("SELECT * FROM wildlife_movements LIMIT 5", conn)
