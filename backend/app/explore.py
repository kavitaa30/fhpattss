import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
a = pd.read_csv(RAW_DIR / "actuals.csv")
f = pd.read_csv(RAW_DIR / "forecasts.csv")

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

print("=== ACTUALS ===")
print(a.shape, a.columns.tolist())
print(a.head(3))

print("\n=== FORECASTS ===")
print(f.shape, f.columns.tolist())
print(f.head(5))

# Time columns ko datetime me badlo
f["startTime"] = pd.to_datetime(f["startTime"], utc=True)
f["publishTime"] = pd.to_datetime(f["publishTime"], utc=True)
a["startTime"] = pd.to_datetime(a["startTime"], utc=True)

print("\n=== RANGES ===")
print("actuals startTime :", a["startTime"].min(), "->", a["startTime"].max())
print("forecast startTime:", f["startTime"].min(), "->", f["startTime"].max())
print("forecast publishTime:", f["publishTime"].min(), "->", f["publishTime"].max())

print("\n=== KITNE FORECASTS HAIN HAR startTime KE LIYE ===")
print(f.groupby("startTime").size().describe())

# Horizon = target time minus publish time (ghanton me)
f["horizon_h"] = (f["startTime"] - f["publishTime"]).dt.total_seconds() / 3600
print("\n=== HORIZON (ghante) ===")
print(f["horizon_h"].describe())

print("\n=== DUPLICATES (startTime + publishTime) ===")
print(f.duplicated(["startTime", "publishTime"]).sum())

print("\n=== MISSING VALUES ===")
print(a.isna().sum())
print(f.isna().sum())