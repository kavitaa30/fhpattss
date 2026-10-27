from functools import lru_cache

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.logic import DELIVERY_END, DELIVERY_START, build_comparison, compute_metrics

app = FastAPI(title="Wind forecast accuracy API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"],
                   allow_headers=["*"])

CutoffHour = Query(9, ge=0, le=23, description="Decision cutoff hour (UTC) on the day before delivery")


@lru_cache(maxsize=24)
def comparison(cutoff_hour: int) -> pd.DataFrame:
    """Compute once per cutoff hour and reuse."""
    return build_comparison(cutoff_hour)


def to_records(df: pd.DataFrame) -> list[dict]:
    out = df.copy()
    for c in ("startTime", "publishTime"):
        out[c] = out[c].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out[["startTime", "publishTime", "forecast_mw", "actual_mw",
                "error_mw", "horizon_h"]].round(1).to_dict("records")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/comparison")
def get_comparison(date: str, cutoff_hour: int = CutoffHour):
    """Forecast (latest before cutoff) vs actual for one delivery day."""
    day = pd.Timestamp(date, tz="UTC")
    if not (DELIVERY_START <= day < DELIVERY_END):
        raise HTTPException(400, "date must be between 2026-01-02 and 2026-02-01")
    df = comparison(cutoff_hour)
    sel = df[df["startTime"].dt.normalize() == day]
    return {"date": date, "cutoff_hour": cutoff_hour, "rows": to_records(sel)}


@app.get("/api/v1/metrics")
def get_metrics(cutoff_hour: int = CutoffHour, start: str | None = None,
                end: str | None = None):
    """Accuracy metrics over the whole month, or a date range (inclusive)."""
    df = comparison(cutoff_hour)
    if start:
        df = df[df["startTime"] >= pd.Timestamp(start, tz="UTC")]
    if end:
        df = df[df["startTime"] < pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1)]
    if df.empty:
        raise HTTPException(404, "no data in this range")
    return compute_metrics(df)


@app.get("/api/v1/errors/by-hour")
def errors_by_hour(cutoff_hour: int = CutoffHour):
    df = comparison(cutoff_hour)
    g = df.groupby(df["startTime"].dt.hour)["error_mw"]
    return [{"hour": int(h), "mae_mw": round(v.abs().mean(), 1),
             "bias_mw": round(v.mean(), 1)} for h, v in g]


@app.get("/api/v1/errors/distribution")
def errors_distribution(cutoff_hour: int = CutoffHour, bins: int = Query(20, ge=5, le=60)):
    df = comparison(cutoff_hour)
    cuts = pd.cut(df["error_mw"], bins=bins)
    counts = cuts.value_counts().sort_index()
    return [{"from_mw": round(i.left), "to_mw": round(i.right), "count": int(c)}
            for i, c in counts.items()]