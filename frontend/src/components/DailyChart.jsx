import {
  Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

// Mean absolute error for each delivery day. Click a bar to open that day.
export default function DailyChart({ rows, selected, onSelect }) {
  const data = rows.map((r) => ({ ...r, day: r.date.slice(8) }));
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} margin={{ top: 8, right: 16, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="day" interval={0} tick={{ fontSize: 11 }} />
        <YAxis tickFormatter={(v) => `${v / 1000}k`} width={48} />
        <Tooltip
          labelFormatter={(_, p) => p?.[0]?.payload?.date ?? ""}
          formatter={(v, name) => [`${Math.round(v).toLocaleString("en-GB")} MW`, name]}
        />
        <Bar dataKey="mae_mw" name="MAE" cursor="pointer" onClick={(d) => onSelect(d.date)}>
          {data.map((d) => (
            <Cell key={d.date} fill={d.date === selected ? "#ea580c" : "#2563eb"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}