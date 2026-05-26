import pandas as pd


def get_anomalies_sql(conn):
    """
    Detect anomalies using SQL instead of Python.

    Why this matters:
    Real data teams often run SQL-based QA checks directly in databases.
    """

    query = """
    SELECT *
    FROM wildlife_raw
    WHERE latitude IS NULL
       OR longitude IS NULL
    """

    return pd.read_sql(query, conn)


def get_animal_summary(conn):
    """
    Summarize movement records per animal.
    """

    query = """
    SELECT animal_id,
           COUNT(*) as total_points,
           MIN(timestamp) as start_time,
           MAX(timestamp) as end_time
    FROM wildlife_raw
    GROUP BY animal_id
    """

    return pd.read_sql(query, conn)
