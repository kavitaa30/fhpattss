import {
  Bar, BarChart, CartesianGrid, Cell, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

export function Distribution({ bins }) {
  // Bar label = start of the 1,000 MW bin. Bins starting at 0 or above are over-forecasts.
  const data = bins.map((b) => ({
    label: `${(b.from_mw / 1000).toFixed(0)}k`,
    hours: b.count,
    over: b.from_mw >= 0,
  }));
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 8, right: 16, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" />
        <YAxis width={40} />
        <Tooltip
          labelFormatter={(v) => `Error from ${v} MW (1,000 MW wide bin)`}
          formatter={(v) => [`${v} hours`, "Count"]}
        />
        <Bar dataKey="hours">
          {data.map((d, i) => (
            <Cell key={i} fill={d.over ? "#2563eb" : "#ea580c"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function ByHour({ rows }) {
  const data = rows.map((r) => ({ hour: `${String(r.hour).padStart(2, "0")}:00`, MAE: r.mae_mw, Bias: r.bias_mw }));
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 8, right: 16, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="hour" interval={2} />
        <YAxis tickFormatter={(v) => `${v / 1000}k`} width={48} />
        <Tooltip formatter={(v) => `${Math.round(v).toLocaleString("en-GB")} MW`} />
        <Legend />
        <Bar dataKey="MAE" fill="#2563eb" />
        <Bar dataKey="Bias" fill="#ea580c" />
      </BarChart>
    </ResponsiveContainer>
  );
}