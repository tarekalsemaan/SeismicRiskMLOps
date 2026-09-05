import requests
import pandas as pd
import sqlite3

from datetime import datetime, timedelta, timezone
from pathlib import Path

URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(hours=24)

PARAMS = {
    "format": "geojson",
    "starttime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
    "endtime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
    "minmagnitude": 2.5,
    "orderby": "time"
}

print("Requesting earthquakes from:")
print(start_time)
print("to:")
print(end_time)

response = requests.get(URL, params=PARAMS, timeout=30)
response.raise_for_status()

data = response.json()

rows = []

for feature in data["features"]:
    properties = feature["properties"]
    coordinates = feature["geometry"]["coordinates"]

    rows.append({
        "id": feature["id"],
        "time": properties["time"],
        "magnitude": properties["mag"],
        "place": properties["place"],
        "longitude": coordinates[0],
        "latitude": coordinates[1],
        "depth": coordinates[2],
        "type": properties["type"]
    })

df = pd.DataFrame(rows)

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

csv_file = data_dir / "usgs_latest_24h.csv"
db_file = data_dir / "seismic.db"

df.to_csv(csv_file, index=False)

conn = sqlite3.connect(db_file)

conn.execute("""
CREATE TABLE IF NOT EXISTS earthquakes (
    id TEXT PRIMARY KEY,
    time INTEGER,
    magnitude REAL,
    place TEXT,
    longitude REAL,
    latitude REAL,
    depth REAL,
    type TEXT
)
""")

for _, row in df.iterrows():
    conn.execute("""
    INSERT OR REPLACE INTO earthquakes
    (
        id,
        time,
        magnitude,
        place,
        longitude,
        latitude,
        depth,
        type
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["id"],
        row["time"],
        row["magnitude"],
        row["place"],
        row["longitude"],
        row["latitude"],
        row["depth"],
        row["type"]
    ))

conn.commit()

count = conn.execute(
    "SELECT COUNT(*) FROM earthquakes"
).fetchone()[0]

conn.close()

print()
print(f"Downloaded: {len(df)} earthquakes")
print(f"CSV saved to: {csv_file}")
print(f"SQLite saved to: {db_file}")
print(f"Total earthquakes in database: {count}")