import pandas as pd

df = pd.read_csv("data/usgs_historical_2026.csv")

print("Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nMagnitude statistics:")
print(df["magnitude"].describe())

print("\nDepth statistics:")
print(df["depth"].describe())

print("\nEvent types:")
print(df["type"].value_counts())

print("\nFirst 10 rows:")
print(df.head(10))