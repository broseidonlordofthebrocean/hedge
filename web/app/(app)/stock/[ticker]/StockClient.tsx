"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SurvivalMeter } from "@/components/charts/SurvivalMeter";
import { FactorRadar } from "@/components/charts/FactorRadar";
import { ScoreHistory } from "@/components/charts/ScoreHistory";

interface StockData {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  score: number;
  tier: string;
  confidence: number;
  factors: {
    hard_assets: number;
    precious_metals: number;
    commodities: number;
    foreign_revenue: number;
    pricing_power: number;
    debt_structure: number;
    essential_services: number;
  };
  scenarios: {
    gradual: number;
    rapid: number;
    hyper: number;
  };
  history: Array<{ date: string; score: number }>;
  fundamentals: {
    market_cap: number;
    revenue: number;
    total_assets: number;
    total_debt: number;
    foreign_revenue_pct: number;
    gross_margin: number;
  };
}

const TIER_COLORS: Record<string, string> = {
  FORTRESS: "text-gold",
  RESILIENT: "text-green-500",
  MODERATE: "text-yellow-500",
  VULNERABLE: "text-orange-500",
  EXPOSED: "text-red-500",
};

const TIER_BG: Record<string, string> = {
  FORTRESS: "bg-gold/10",
  RESILIENT: "bg-green-500/10",
  MODERATE: "bg-yellow-500/10",
  VULNERABLE: "bg-orange-500/10",
  EXPOSED: "bg-red-500/10",
};

export default function StockClient({ ticker }: { ticker: string }) {
  const [stock, setStock] = useState<StockData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockStock: StockData = {
      ticker: ticker.toUpperCase(),
      name: `${ticker.toUpperCase()} Corporation`,
      sector: "Materials",
      industry: "Gold",
      score: 78.5,
      tier: "RESILIENT",
      confidence: 0.85,
      factors: {
        hard_assets: 82,
        precious_metals: 95,
        commodities: 75,
        foreign_revenue: 68,
        pricing_power: 72,
        debt_structure: 85,
        essential_services: 45,
      },
      scenarios: {
        gradual: 82,
        rapid: 76,
        hyper: 68,
      },
      history: [
        { date: "2024-01-01", score: 72 },
        { date: "2024-02-01", score: 74 },
        { date: "2024-03-01", score: 75 },
        { date: "2024-04-01", score: 73 },
        { date: "2024-05-01", score: 76 },
        { date: "2024-06-01", score: 78.5 },
      ],
      fundamentals: {
        market_cap: 45_000_000_000,
        revenue: 12_500_000_000,
        total_assets: 58_000_000_000,
        total_debt: 8_500_000_000,
        foreign_revenue_pct: 42,
        gross_margin: 38.5,
      },
    };

    setTimeout(() => {
      setStock(mockStock);
      setLoading(false);
    }, 500);
  }, [ticker]);

  if (loading) {
    return (
      <div className="min-h-screen bg-charcoal p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-48 bg-charcoal-light rounded" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="h-64 bg-charcoal-light rounded" />
            <div className="h-64 bg-charcoal-light rounded" />
            <div className="h-64 bg-charcoal-light rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (!stock) {
    return (
      <div className="min-h-screen bg-charcoal p-6 flex items-center justify-center">
        <p className="text-gray-400">Company not found</p>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    if (value >= 1_000_000_000) {
      return `$${(value / 1_000_000_000).toFixed(1)}B`;
    }
    if (value >= 1_000_000) {
      return `$${(value / 1_000_000).toFixed(1)}M`;
    }
    return `$${value.toLocaleString()}`;
  };

  return (
    <div className="min-h-screen bg-charcoal">
      <div className="border-b border-charcoal-light p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-4">
                <h1 className="text-3xl font-bold text-white">{stock.ticker}</h1>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${TIER_BG[stock.tier]} ${TIER_COLORS[stock.tier]}`}>
                  {stock.tier}
                </span>
              </div>
              <p className="text-gray-400 mt-1">{stock.name}</p>
              <p className="text-sm text-gray-500">{stock.sector} • {stock.industry}</p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-gold">{stock.score.toFixed(1)}</div>
              <p className="text-sm text-gray-400">Survival Score</p>
              <p className="text-xs text-gray-500 mt-1">{Math.round(stock.confidence * 100)}% confidence</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardHeader><CardTitle className="text-white">Survival Meter</CardTitle></CardHeader>
            <CardContent className="flex justify-center">
              <SurvivalMeter score={stock.score} size="lg" />
            </CardContent>
          </Card>
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardHeader><CardTitle className="text-white">Factor Analysis</CardTitle></CardHeader>
            <CardContent><FactorRadar factors={stock.factors} /></CardContent>
          </Card>
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardHeader><CardTitle className="text-white">Scenario Resilience</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(stock.scenarios).map(([scenario, value]) => (
                <div key={scenario}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400 capitalize">{scenario}</span>
                    <span className="text-white">{value}</span>
                  </div>
                  <div className="h-2 bg-charcoal rounded-full overflow-hidden">
                    <div className="h-full bg-gold rounded-full" style={{ width: `${value}%` }} />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
        <Card className="bg-charcoal-light border-charcoal-lighter">
          <CardHeader><CardTitle className="text-white">Score History</CardTitle></CardHeader>
          <CardContent><ScoreHistory history={stock.history} /></CardContent>
        </Card>
        <Card className="bg-charcoal-light border-charcoal-lighter">
          <CardHeader><CardTitle className="text-white">Factor Breakdown</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(stock.factors).map(([factor, score]) => (
                <div key={factor} className="p-4 bg-charcoal rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-400 capitalize">{factor.replace(/_/g, " ")}</span>
                    <span className="text-lg font-semibold text-white">{score}</span>
                  </div>
                  <div className="h-2 bg-charcoal-light rounded-full overflow-hidden">
                    <div className="h-full bg-gold rounded-full" style={{ width: `${score}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        <Card className="bg-charcoal-light border-charcoal-lighter">
          <CardHeader><CardTitle className="text-white">Key Fundamentals</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {[
                { label: "Market Cap", value: formatCurrency(stock.fundamentals.market_cap) },
                { label: "Revenue", value: formatCurrency(stock.fundamentals.revenue) },
                { label: "Total Assets", value: formatCurrency(stock.fundamentals.total_assets) },
                { label: "Total Debt", value: formatCurrency(stock.fundamentals.total_debt) },
                { label: "Foreign Rev %", value: `${stock.fundamentals.foreign_revenue_pct}%` },
                { label: "Gross Margin", value: `${stock.fundamentals.gross_margin}%` },
              ].map((item) => (
                <div key={item.label} className="text-center p-4 bg-charcoal rounded-lg">
                  <p className="text-sm text-gray-400">{item.label}</p>
                  <p className="text-xl font-semibold text-white">{item.value}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
