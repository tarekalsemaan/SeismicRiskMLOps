import requests
import pandas as pd
from pathlib import Path

URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

PARAMS = {
    "format": "geojson",
    "starttime": "2026-01-01",
    "endtime": "2026-09-04",
    "minmagnitude": 2.5,
    "limit": 20000,
    "orderby": "time-asc"
}

OUTPUT_FILE = Path("data") / "usgs_historical_2026.csv"


def main():
    print("Downloading historical USGS earthquake data...")

    response = requests.get(
        URL,
        params=PARAMS,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    records = []

    for feature in data["features"]:
        properties = feature["properties"]
        coordinates = feature["geometry"]["coordinates"]

        records.append({
            "id": feature["id"],
            "time": properties.get("time"),
            "magnitude": properties.get("mag"),
            "place": properties.get("place"),
            "longitude": coordinates[0],
            "latitude": coordinates[1],
            "depth": coordinates[2],
            "type": properties.get("type")
        })

    df = pd.DataFrame(records)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Downloaded {len(df)} earthquakes.")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()