import pandas as pd
from logic import build_comparison, load_data, hourly_actuals, latest_forecast_before_cutoff

df = build_comparison(cutoff_hour=9)
print("mean forecast:", round(df["forecast_mw"].mean()), " mean actual:", round(df["actual_mw"].mean()))
print("ratio forecast/actual:", round(df["forecast_mw"].sum() / df["actual_mw"].sum(), 3))
print("correlation:", round(df["forecast_mw"].corr(df["actual_mw"]), 3))

# Alignment test: shift actual by -3..+3 hours and see which fits best
a, f = load_data()
act = hourly_actuals(a).set_index("startTime")["actual_mw"]
fc = latest_forecast_before_cutoff(f, 9).set_index("startTime")["forecast_mw"]
print("\nshift(h)  MAE   corr")
for s in range(-3, 4):
    joined = pd.concat([fc, act.shift(s)], axis=1, join="inner").dropna()
    joined.columns = ["f", "a"]
    joined = joined[(joined.index >= "2026-01-02") & (joined.index < "2026-02-02")]
    print(s, round((joined["f"] - joined["a"]).abs().mean()), round(joined["f"].corr(joined["a"]), 3))

# Bias by day: constant over-forecast, or only on some days?
df["day"] = df["startTime"].dt.date
print("\nbias by day (MW):")
print(df.groupby("day")["error_mw"].mean().round().to_string())