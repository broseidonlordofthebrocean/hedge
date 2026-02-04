"use client";

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface FactorRadarProps {
  factors: {
    hard_assets: number;
    precious_metals: number;
    commodities: number;
    foreign_revenue: number;
    pricing_power: number;
    debt_structure: number;
    essential_services: number;
  };
}

const FACTOR_LABELS: Record<string, string> = {
  hard_assets: "Hard Assets",
  precious_metals: "Precious Metals",
  commodities: "Commodities",
  foreign_revenue: "Foreign Revenue",
  pricing_power: "Pricing Power",
  debt_structure: "Debt Structure",
  essential_services: "Essential Services",
};

export function FactorRadar({ factors }: FactorRadarProps) {
  const data = Object.entries(factors).map(([key, value]) => ({
    factor: FACTOR_LABELS[key] || key,
    score: value,
    fullMark: 100,
  }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <RadarChart data={data}>
        <PolarGrid stroke="#374151" />
        <PolarAngleAxis
          dataKey="factor"
          tick={{ fill: "#9CA3AF", fontSize: 10 }}
          tickLine={false}
        />
        <PolarRadiusAxis
          angle={30}
          domain={[0, 100]}
          tick={{ fill: "#6B7280", fontSize: 10 }}
          tickCount={5}
        />
        <Radar
          name="Score"
          dataKey="score"
          stroke="#D4AF37"
          fill="#D4AF37"
          fillOpacity={0.3}
          strokeWidth={2}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1a1a2e",
            border: "1px solid #2a2a3e",
            borderRadius: "8px",
            color: "#fff",
          }}
          formatter={(value: number) => [value, "Score"]}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
