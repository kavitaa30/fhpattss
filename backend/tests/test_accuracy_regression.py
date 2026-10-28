import sys
from pathlib import Path
import pandas as pd
import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.logic import build_comparison, compute_metrics


def test_delivery_day_publishtime_before_cutoff():
    """For delivery day 2026-01-12 with cutoff 08:00 UTC, the chosen publishTime
    is 2026-01-11 07:30 UTC for every hour.
    """
    df = build_comparison(cutoff_hour=8)
    day_df = df[df["startTime"].dt.date == pd.to_datetime("2026-01-12").date()]

    assert len(day_df) == 24
    expected_publishtime = pd.Timestamp("2026-01-11 07:30:00", tz="UTC")
    assert (day_df["publishTime"] == expected_publishtime).all()


def test_sample_hour_values():
    """For 2026-01-12 00:00 the forecast is 20,790 MW, the actual hourly
    average is 14,032.0 MW, and the error is +6,758.0 MW.
    """
    df = build_comparison(cutoff_hour=8)
    target_time = pd.Timestamp("2026-01-12 00:00:00", tz="UTC")
    row = df[df["startTime"] == target_time].iloc[0]

    assert row["forecast_mw"] == 20790
    assert row["actual_mw"] == pytest.approx(14032.0, abs=0.1)
    assert row["error_mw"] == pytest.approx(6758.0, abs=0.1)


def test_january_month_metrics():
    """Over all 744 hours of January the bias is about +1,748 MW and
    MAE about 2,039 MW (use pytest.approx).
    """
    df = build_comparison(cutoff_hour=8)
    metrics = compute_metrics(df)

    assert metrics["n_hours"] == 744
    assert metrics["bias_mw"] == pytest.approx(1748.0, abs=1.0)
    assert metrics["mae_mw"] == pytest.approx(2039.0, abs=1.0)
