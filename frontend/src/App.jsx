import { useEffect, useState } from "react";
import { getByHour, getComparison, getDaily, getDistribution, getMetrics } from "./api";
import MetricCards from "./components/MetricCards";
import DayChart from "./components/DayChart";
import DailyChart from "./components/DailyChart";
import { ByHour, Distribution } from "./components/ErrorCharts";
import "./App.css";

// Small data-loading hook: runs fn() whenever deps change, ignores stale replies.
function useApi(fn, deps) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));
    fn()
      .then((data) => !cancelled && setState({ data, error: null, loading: false }))
      .catch((e) => !cancelled && setState({ data: null, error: e.message, loading: false }));
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return state;
}

const fmt = (n) => Math.round(n).toLocaleString("en-GB");

function Section({ title, subtitle, state, children }) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      {subtitle && <p className="sub">{subtitle}</p>}
      {state.loading && <p className="muted">Loading…</p>}
      {state.error && <p className="error">Could not load data: {state.error}</p>}
      {state.data && children(state.data)}
    </section>
  );
}

export default function App() {
  const [date, setDate] = useState("2026-01-12");
  const [cutoff, setCutoff] = useState(9);

  const day = useApi(() => getComparison(date, cutoff), [date, cutoff]);
  const month = useApi(() => getMetrics(cutoff), [cutoff]);
  const byHour = useApi(() => getByHour(cutoff), [cutoff]);
  const dist = useApi(() => getDistribution(cutoff), [cutoff]);
  const daily = useApi(() => getDaily(cutoff), [cutoff]);

  const prev = new Date(`${date}T00:00:00Z`);
  prev.setUTCDate(prev.getUTCDate() - 1);
  const decisionDay = prev.toISOString().slice(0, 10);
  const hh = String(cutoff).padStart(2, "0");

  return (
    <main>
      <header>
        <h1>UK wind generation: forecast vs actual</h1>
        <p className="muted">
          Day-ahead purchase decisions, January 2026. Source: Elexon (WINDFOR forecasts, FUELHH actuals).
        </p>
      </header>

      <section className="controls">
        <label>
          Delivery day
          <input type="date" value={date} min="2026-01-02" max="2026-02-01"
                 onChange={(e) => e.target.value && setDate(e.target.value)} />
        </label>
        <label>
          Decision cutoff (UTC, previous day)
          <select value={cutoff} onChange={(e) => setCutoff(Number(e.target.value))}>
            {Array.from({ length: 24 }, (_, h) => (
              <option key={h} value={h}>{String(h).padStart(2, "0")}:00</option>
            ))}
          </select>
        </label>
        <p className="muted">
          Decision made on <b>{decisionDay} at {hh}:00 UTC</b> for delivery on <b>{date}</b>.
          Each hour uses the latest forecast published before that moment.
        </p>
      </section>

      <Section title="January 2026 accuracy" state={month}
               subtitle="All delivery days (2 Jan – 1 Feb), forecast as known at the cutoff.">
        {(m) => (
          <>
            <MetricCards m={m} />
            <p className="insight">
              On average the forecast was {fmt(Math.abs(m.bias_mw))} MW {m.bias_mw > 0 ? "above" : "below"} actual
              output. In 95% of hours it overshot by no more than {fmt(m.p95_over_forecast_mw)} MW, so a
              buffer of about that size of non-wind supply would have covered the downside in 95% of hours.
            </p>
          </>
        )}
      </Section>

      <Section title="Error for each day of January" state={daily}
               subtitle="Mean absolute error per delivery day. Click a bar to open that day below.">
        {(rows) => <DailyChart rows={rows} selected={date} onSelect={setDate} />}
      </Section>

      <Section title={`Forecast vs actual on ${date}`} state={day}
               subtitle="Hourly wind generation in MW (actual = average of the two half-hours).">
        {(d) =>
          d.rows.length === 0 ? <p className="muted">No data for this day.</p> : (
            <>
              <DayChart rows={d.rows} />
              <p className="muted small">
                {(() => {
                  const times = [...new Set(d.rows.map((r) => r.publishTime.replace("T", " ").slice(0, 16)))];
                  return times.length === 1
                    ? `Every hour uses the forecast published at ${times[0]} UTC, the latest one before the cutoff.`
                    : `Forecast versions used were published between ${times[0]} and ${times.at(-1)} UTC.`;
                })()}
              </p>
            </>
          )
        }
      </Section>

      <div className="two-col">
        <Section title="Error distribution" state={dist}
                 subtitle="Hours by error size (forecast minus actual). Blue = over-forecast, orange = under-forecast.">
          {(bins) => <Distribution bins={bins} />}
        </Section>
        <Section title="Error by hour of day" state={byHour}
                 subtitle="Is the forecast worse at certain times?">
          {(rows) => <ByHour rows={rows} />}
        </Section>
      </div>
    </main>
  );
}