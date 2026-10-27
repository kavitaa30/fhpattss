import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

BASE = "https://data.elexon.co.uk/bmrs/api/v1/datasets"
# Script is at <repo>/backend/app/, so parents[2] is the repo root
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_chunks(dataset, from_param, to_param, start, end, step_days,
                 date_only=False, extra=None):
    """Fetch a long date range in small chunks and return one DataFrame.

    date_only=True: send plain dates (YYYY-MM-DD), as FUELHH requires.
    The 'to' date is inclusive then, so each chunk ends one day earlier.
    """
    rows = []
    cur = start
    while cur < end:
        nxt = min(cur + timedelta(days=step_days), end)
        if date_only:
            frm = cur.strftime("%Y-%m-%d")
            to = (nxt - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            frm = cur.strftime("%Y-%m-%dT%H:%MZ")
            to = nxt.strftime("%Y-%m-%dT%H:%MZ")
        params = {from_param: frm, to_param: to, "format": "json"}
        if extra:
            params.update(extra)
        r = requests.get(f"{BASE}/{dataset}/stream", params=params, timeout=60)
        if not r.ok:
            print("ERROR", r.status_code, r.url)
            print(r.text[:500])
            r.raise_for_status()
        rows.extend(r.json())
        print(dataset, frm, "->", to, len(rows), "rows so far")
        cur = nxt
    return pd.DataFrame(rows)


if __name__ == "__main__":
    # Actuals: FUELHH, keep only WIND
    actuals = fetch_chunks(
        "FUELHH", "settlementDateFrom", "settlementDateTo",
        datetime(2026, 1, 1), datetime(2026, 2, 2), step_days=7,
        date_only=True,
    )
    actuals = actuals[actuals["fuelType"] == "WIND"]
    actuals.to_csv(RAW_DIR / "actuals.csv", index=False)
    print("Saved actuals:", actuals.shape)

    # Forecasts: WINDFOR, fetched by publish time (from late Dec 2025)
    forecasts = fetch_chunks(
        "WINDFOR", "publishDateTimeFrom", "publishDateTimeTo",
        datetime(2025, 12, 20), datetime(2026, 2, 1), step_days=3,
    )
    forecasts.to_csv(RAW_DIR / "forecasts.csv", index=False)
    print("Saved forecasts:", forecasts.shape)