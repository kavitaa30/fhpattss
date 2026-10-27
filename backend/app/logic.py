import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

# Decisions are made in Jan 2026 for the next day's delivery: 2 Jan to 1 Feb
DELIVERY_START = pd.Timestamp("2026-01-02", tz="UTC")
DELIVERY_END = pd.Timestamp("2026-02-02", tz="UTC")  # exclusive


def load_data():
    """Read raw CSVs and parse times as UTC (UK time = UTC in January)."""
    a = pd.read_csv(RAW_DIR / "actuals.csv", usecols=["startTime", "generation"])
    f = pd.read_csv(RAW_DIR / "forecasts.csv",
                    usecols=["startTime", "publishTime", "generation"])
    a["startTime"] = pd.to_datetime(a["startTime"], utc=True)
    f["startTime"] = pd.to_datetime(f["startTime"], utc=True)
    f["publishTime"] = pd.to_datetime(f["publishTime"], utc=True)
    a = a.rename(columns={"generation": "actual_mw"})
    f = f.rename(columns={"generation": "forecast_mw"})
    return a, f


def hourly_actuals(a):
    """Forecasts are hourly, actuals half-hourly: average the two half-hours."""
    a = a.sort_values("startTime").set_index("startTime")
    return a["actual_mw"].resample("1h").mean().reset_index()


def latest_forecast_before_cutoff(f, cutoff_hour=9):
    """For each target hour, pick the latest forecast published at or before
    the decision cutoff (previous day at cutoff_hour UTC)."""
    f = f.copy()
    f["cutoff"] = (f["startTime"].dt.normalize()
                   - pd.Timedelta(days=1) + pd.Timedelta(hours=cutoff_hour))
    f = f[f["publishTime"] <= f["cutoff"]]
    f = f.sort_values("publishTime")
    return f.drop_duplicates(subset="startTime", keep="last")


def build_comparison(cutoff_hour=9):
    """One row per target hour: forecast known at cutoff vs actual, and error."""
    a, f = load_data()
    latest = latest_forecast_before_cutoff(f, cutoff_hour)
    df = latest.merge(hourly_actuals(a), on="startTime", how="inner")
    df = df[(df["startTime"] >= DELIVERY_START) & (df["startTime"] < DELIVERY_END)]
    df = df.sort_values("startTime").reset_index(drop=True)
    df["error_mw"] = df["forecast_mw"] - df["actual_mw"]   # + = over-forecast
    df["horizon_h"] = (df["startTime"] - df["publishTime"]).dt.total_seconds() / 3600
    return df


def compute_metrics(df):
    """Accuracy metrics. MAPE ignores hours where actual is 0."""
    e = df["error_mw"]
    nz = df["actual_mw"] > 0
    return {
        "n_hours": int(len(df)),
        "mae_mw": float(e.abs().mean()),
        "rmse_mw": float((e ** 2).mean() ** 0.5),
        "bias_mw": float(e.mean()),
        "mape_pct": float((e[nz].abs() / df.loc[nz, "actual_mw"]).mean() * 100),
        "p95_abs_error_mw": float(e.abs().quantile(0.95)),
        "p95_over_forecast_mw": float(e.quantile(0.95)),   # worst-case wind shortfall
        "p05_under_forecast_mw": float(e.quantile(0.05)),
    }