import pandas as pd
import random
from datetime import datetime, timedelta

def generate_wildlife_data():
    animals = ["elk_001", "deer_002", "moose_003"]

    rows = []
    start_time = datetime(2024, 1, 1, 0, 0, 0)

    # Starting location (Colorado-ish)
    base_lat = 39.0
    base_lon = -105.5

    for animal in animals:
        lat = base_lat + random.uniform(-0.2, 0.2)
        lon = base_lon + random.uniform(-0.2, 0.2)

        for i in range(200):
            # simulate movement
            lat += random.uniform(-0.01, 0.01)
            lon += random.uniform(-0.01, 0.01)

            rows.append({
                "animal_id": animal,
                "timestamp": start_time + timedelta(hours=i),
                "latitude": lat,
                "longitude": lon
            })

    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    df = generate_wildlife_data()

    output_path = "data/sample_wildlife.csv"
    df.to_csv(output_path, index=False)

    print(f"Generated dataset with {len(df)} rows → {output_path}")
