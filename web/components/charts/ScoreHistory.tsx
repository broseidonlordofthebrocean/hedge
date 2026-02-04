"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ScoreHistoryProps {
  history: Array<{ date: string; score: number }>;
}

export function ScoreHistory({ history }: ScoreHistoryProps) {
  const formattedData = history.map((item) => ({
    ...item,
    formattedDate: new Date(item.date).toLocaleDateString("en-US", {
      month: "short",
      year: "2-digit",
    }),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={formattedData}>
        <defs>
          <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#D4AF37" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#D4AF37" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis
          dataKey="formattedDate"
          tick={{ fill: "#9CA3AF", fontSize: 12 }}
          tickLine={false}
          axisLine={{ stroke: "#374151" }}
        />
        <YAxis
          domain={[0, 100]}
          tick={{ fill: "#9CA3AF", fontSize: 12 }}
          tickLine={false}
          axisLine={{ stroke: "#374151" }}
          tickFormatter={(value) => `${value}`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1a1a2e",
            border: "1px solid #2a2a3e",
            borderRadius: "8px",
            color: "#fff",
          }}
          formatter={(value: number) => [value.toFixed(1), "Score"]}
          labelFormatter={(label) => `Date: ${label}`}
        />
        <Area
          type="monotone"
          dataKey="score"
          stroke="#D4AF37"
          strokeWidth={2}
          fill="url(#scoreGradient)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
