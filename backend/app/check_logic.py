from logic import build_comparison, compute_metrics

df = build_comparison(cutoff_hour=9)
print(df.head())
print("rows:", len(df), "(expected 31 days x 24 = 744)")

# Sanity checks
assert (df["publishTime"] <= df["startTime"].dt.normalize()
        - __import__("pandas").Timedelta(days=1)
        + __import__("pandas").Timedelta(hours=9)).all(), "forecast published after cutoff!"
assert df["startTime"].is_unique, "duplicate target hours!"

print(compute_metrics(df))