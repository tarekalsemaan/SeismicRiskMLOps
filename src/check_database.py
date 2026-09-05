import sqlite3
import pandas as pd

DB_FILE = "data/seismic.db"

conn = sqlite3.connect(DB_FILE)

count = conn.execute(
    "SELECT COUNT(*) FROM earthquakes"
).fetchone()[0]

print(f"Total earthquakes: {count}")
print()

df = pd.read_sql_query("""
SELECT
    id,
    magnitude,
    depth,
    latitude,
    longitude,
    place
FROM earthquakes
ORDER BY time DESC
LIMIT 10
""", conn)

conn.close()

print(df)