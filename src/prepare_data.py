import pandas as pd
from pathlib import Path

INPUT_FILE = "data/usgs_historical_2026.csv"
OUTPUT_FILE = "data/usgs_clean_2026.csv"

print("Loading historical USGS data...")

df = pd.read_csv(INPUT_FILE)

print(f"Original rows: {len(df)}")

# --------------------------------------------------
# 1. Keep real earthquakes only
# --------------------------------------------------

df = df[df["type"] == "earthquake"].copy()

print(f"Earthquakes only: {len(df)}")

# --------------------------------------------------
# 2. Convert USGS timestamp
# USGS time is stored in milliseconds
# --------------------------------------------------

df["datetime"] = pd.to_datetime(
    df["time"],
    unit="ms",
    utc=True
)

# --------------------------------------------------
# 3. Create useful time features
# --------------------------------------------------

df["year"] = df["datetime"].dt.year
df["month"] = df["datetime"].dt.month
df["day"] = df["datetime"].dt.day
df["hour"] = df["datetime"].dt.hour
df["day_of_week"] = df["datetime"].dt.dayofweek

# --------------------------------------------------
# 4. Create depth information
# --------------------------------------------------

df["is_shallow"] = (df["depth"] <= 70).astype(int)

# --------------------------------------------------
# 5. Remove duplicate earthquake IDs
# --------------------------------------------------

df = df.drop_duplicates(subset=["id"])

# --------------------------------------------------
# 6. Save prepared dataset
# --------------------------------------------------

Path("data").mkdir(exist_ok=True)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("===================================")
print("DATA PREPARATION COMPLETE")
print("===================================")

print(f"Final rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {OUTPUT_FILE}")

print()
print("Columns:")
print(df.columns.tolist())

print()
print(df.head())