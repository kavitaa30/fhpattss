import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

const mw = (v) => `${Math.round(v).toLocaleString("en-GB")} MW`;

export default function DayChart({ rows }) {
  const data = rows.map((r) => ({
    hour: r.startTime.slice(11, 16),
    Forecast: r.forecast_mw,
    Actual: r.actual_mw,
  }));
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="hour" interval={2} />
        <YAxis tickFormatter={(v) => `${v / 1000}k`} width={48} />
        <Tooltip formatter={mw} />
        <Legend />
        <Line type="monotone" dataKey="Forecast" stroke="#2563eb" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="Actual" stroke="#ea580c" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
