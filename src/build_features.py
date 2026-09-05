import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data") / "usgs_clean_2026.csv"
OUTPUT_FILE = Path("data") / "usgs_ml_ready_2026.csv"


def main():
    print("Loading cleaned earthquake data...")

    df = pd.read_csv(INPUT_FILE)

    df["strong_earthquake"] = (df["magnitude"] >= 5.0).astype(int)

    features = [
        "latitude",
        "longitude",
        "depth",
        "month",
        "day",
        "hour",
        "day_of_week"
    ]

    target = "strong_earthquake"

    ml_df = df[features + [target]].copy()

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    ml_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Rows: {len(ml_df)}")
    print(f"Columns: {len(ml_df.columns)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print()
    print("Target distribution:")
    print(ml_df[target].value_counts())


if __name__ == "__main__":
    main()