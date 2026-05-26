import pandas as pd
import numpy as np
from database import init_db, insert_data, insert_validated
from sql_queries import get_anomalies_sql, get_animal_summary

def load_data(path="data/sample_wildlife.csv"):
    """
    Load wildlife GPS collar data.

    Why this exists:
    In real wildlife systems, data arrives as CSV exports from field devices,
    GPS collars, or centralized tracking systems. This function simulates
    the ingestion step of a data pipeline.
    """
    df = pd.read_csv(path)

    # convert timestamps properly (very important in real systems)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df
    
def check_missing_values(df):
    """
    Identify missing values in dataset.

    Why this matters:
    Wildlife collar data often has gaps due to:
    - signal loss in remote terrain
    - device battery failure
    - transmission issues

    Detecting missingness is a core data validation task.
    """
    missing = df.isnull().sum()
    return missing[missing > 0]
    
def check_duplicates(df):
    """
    Identify duplicate records.

    Why this matters:
    Duplicate GPS points can:
    - distort movement calculations
    - inflate animal activity estimates
    - create false ecological conclusions
    """
    duplicates = df[df.duplicated()]
    return duplicates
    
def check_valid_coordinates(df):
    """
    Identify rows with missing GPS coordinates.

    Why this matters:
    Missing latitude/longitude values represent:
    - corrupted collar transmissions
    - incomplete uploads
    - broken field data collection events
    """
    return df[
        (df["latitude"].isna()) |
        (df["longitude"].isna())
    ]
    
def detect_movement_anomalies(df):
    """
    Detect unrealistic animal movement between GPS points.

    Why this matters:
    Wildlife collar data often contains GPS errors that appear as
    sudden large jumps in location. These must be flagged before analysis.
    """

    df = df.sort_values(["animal_id", "timestamp"]).copy()

    # shift previous coordinates within each animal
    df["prev_lat"] = df.groupby("animal_id")["latitude"].shift()
    df["prev_lon"] = df.groupby("animal_id")["longitude"].shift()
    df["prev_time"] = df.groupby("animal_id")["timestamp"].shift()

    # calculate distance (simple Euclidean approximation)
    df["distance"] = np.sqrt(
        (df["latitude"] - df["prev_lat"])**2 +
        (df["longitude"] - df["prev_lon"])**2
    )

    # calculate time difference in hours
    df["time_diff_hours"] = (
        (df["timestamp"] - df["prev_time"]).dt.total_seconds() / 3600
    )

    # avoid division by zero / first rows
    df["speed"] = df["distance"] / df["time_diff_hours"]

    # flag unrealistic movement (threshold tuned for synthetic data)
    anomalies = df[
        (df["speed"] > 0.05) & df["speed"].notna()
    ]

    return anomalies

if __name__ == "__main__":
    # 1. Load raw dataset
    df = load_data()

    print("\n==============================")
    print("WILDLIFE DATA PIPELINE REPORT")
    print("==============================\n")

    print(f"Total records loaded: {len(df)}")

    # 2. Python-based validation checks
    print("\n--- PYTHON VALIDATION REPORT ---")

    missing = check_missing_values(df)
    print("\nMissing values:\n", missing)

    duplicates = check_duplicates(df)
    print("\nDuplicate rows:", len(duplicates))

    bad_coords = check_valid_coordinates(df)
    print("\nRows with missing coordinates:", len(bad_coords))

    anomalies = detect_movement_anomalies(df)

    print("\n--- MOVEMENT ANOMALY REPORT ---")
    print(f"Anomalous movement records: {len(anomalies)}")

    # 3. Database layer (SQLite)
    print("\n--- DATABASE INGESTION ---")

    conn = init_db()

    # Store raw + validated datasets
    insert_data(conn, df)
    insert_validated(conn, df)

    print("Data successfully inserted into SQLite tables:")
    print(" - wildlife_raw")
    print(" - wildlife_validated")

    # 4. SQL-based reporting layer
    print("\n--- SQL REPORTING LAYER ---")

    print("\nSample raw data (SQL query):")
    print(pd.read_sql("SELECT * FROM wildlife_raw LIMIT 5", conn))

    print("\nAnimal summary (SQL aggregation):")
    print(get_animal_summary(conn))

    print("\nSQL-based missing coordinate check:")
    print(get_anomalies_sql(conn))

    print("\n==============================\n")
    
    
    
    
    
