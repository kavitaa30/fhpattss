const fmt = (n) => Math.round(n).toLocaleString("en-GB");

export default function MetricCards({ m }) {
  const cards = [
    { label: "MAE", value: `${fmt(m.mae_mw)} MW`, hint: "Typical size of the forecast error" },
    { label: "RMSE", value: `${fmt(m.rmse_mw)} MW`, hint: "Like MAE, but punishes big misses more" },
    {
      label: "Bias",
      value: `${m.bias_mw > 0 ? "+" : ""}${fmt(m.bias_mw)} MW`,
      hint: m.bias_mw > 0 ? "Forecast is higher than actual on average" : "Forecast is lower than actual on average",
    },
    { label: "MAPE", value: `${m.mape_pct.toFixed(1)} %`, hint: "Average error as a share of actual output" },
    {
      label: "95% over-forecast limit",
      value: `${fmt(m.p95_over_forecast_mw)} MW`,
      hint: "In 95% of hours the forecast overshot by less than this",
    },
  ];
  return (
    <div className="cards">
      {cards.map((c) => (
        <div className="card" key={c.label}>
          <div className="card-label">{c.label}</div>
          <div className="card-value">{c.value}</div>
          <div className="card-hint">{c.hint}</div>
        </div>
      ))}
    </div>
  );
}
