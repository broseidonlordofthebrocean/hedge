"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SurvivalMeter } from "@/components/charts/SurvivalMeter";
import { FactorRadar } from "@/components/charts/FactorRadar";
import { ScoreHistory } from "@/components/charts/ScoreHistory";

interface Holding {
  id: string;
  ticker: string;
  name: string;
  shares: number;
  price: number;
  value: number;
  weight: number;
  score: number;
  tier: string;
  contribution: number;
}

interface Portfolio {
  id: string;
  name: string;
  description?: string;
  score: number;
  tier: string;
  total_value: number;
  holdings: Holding[];
  factors: Record<string, number>;
  scenarios: { gradual: number; rapid: number; hyper: number };
  history: Array<{ date: string; score: number }>;
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

export default function PortfolioClient({ id }: { id: string }) {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockPortfolio: Portfolio = {
      id,
      name: "Inflation Hedge Portfolio",
      description: "Gold miners and commodity producers",
      score: 78,
      tier: "RESILIENT",
      total_value: 125000,
      holdings: [
        { id: "1", ticker: "NEM", name: "Newmont Corporation", shares: 200, price: 45.5, value: 9100, weight: 7.28, score: 82, tier: "FORTRESS", contribution: 5.97 },
        { id: "2", ticker: "GOLD", name: "Barrick Gold", shares: 300, price: 18.75, value: 5625, weight: 4.5, score: 79, tier: "RESILIENT", contribution: 3.56 },
        { id: "3", ticker: "XOM", name: "Exxon Mobil", shares: 150, price: 105.0, value: 15750, weight: 12.6, score: 74, tier: "RESILIENT", contribution: 9.32 },
      ],
      factors: { hard_assets: 78, precious_metals: 72, commodities: 85, foreign_revenue: 65, pricing_power: 68, debt_structure: 76, essential_services: 58 },
      scenarios: { gradual: 82, rapid: 76, hyper: 65 },
      history: [
        { date: "2024-01-01", score: 72 },
        { date: "2024-02-01", score: 74 },
        { date: "2024-03-01", score: 75 },
        { date: "2024-04-01", score: 77 },
        { date: "2024-05-01", score: 76 },
        { date: "2024-06-01", score: 78 },
      ],
    };
    setTimeout(() => { setPortfolio(mockPortfolio); setLoading(false); }, 500);
  }, [id]);

  if (loading) return <div className="min-h-screen bg-charcoal p-6"><div className="animate-pulse"><div className="h-8 w-48 bg-charcoal-light rounded" /></div></div>;
  if (!portfolio) return <div className="min-h-screen bg-charcoal p-6 flex items-center justify-center"><p className="text-gray-400">Portfolio not found</p></div>;

  const formatCurrency = (value: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", minimumFractionDigits: 0 }).format(value);

  return (
    <div className="min-h-screen bg-charcoal">
      <div className="border-b border-charcoal-light p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-white">{portfolio.name}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${TIER_BG[portfolio.tier]} ${TIER_COLORS[portfolio.tier]}`}>{portfolio.tier}</span>
            </div>
            {portfolio.description && <p className="text-gray-400 mt-1">{portfolio.description}</p>}
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="border-charcoal-lighter text-gray-300">Edit Holdings</Button>
            <Button className="bg-gold hover:bg-gold-dark text-charcoal font-semibold">Analyze</Button>
          </div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardHeader><CardTitle className="text-white">Portfolio Score</CardTitle></CardHeader>
            <CardContent className="flex items-center justify-between">
              <SurvivalMeter score={portfolio.score} size="lg" />
              <div className="text-right">
                <p className="text-4xl font-bold text-gold">{portfolio.score}</p>
                <p className="text-sm text-gray-400">Weighted Avg</p>
                <p className="text-lg text-white mt-2">{formatCurrency(portfolio.total_value)}</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardHeader><CardTitle className="text-white">Portfolio Factors</CardTitle></CardHeader>
            <CardContent><FactorRadar factors={portfolio.factors as any} /></CardContent>
          </Card>
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardHeader><CardTitle className="text-white">Scenario Resilience</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(portfolio.scenarios).map(([scenario, value]) => (
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
          <CardContent><ScoreHistory history={portfolio.history} /></CardContent>
        </Card>
        <Card className="bg-charcoal-light border-charcoal-lighter">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white">Holdings</CardTitle>
            <Button variant="ghost" className="text-gold hover:text-gold-dark">+ Add Holding</Button>
          </CardHeader>
          <CardContent>
            <table className="w-full">
              <thead>
                <tr className="border-b border-charcoal-lighter">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Stock</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Shares</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Value</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Score</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.holdings.map((h) => (
                  <tr key={h.id} className="border-b border-charcoal-lighter hover:bg-charcoal/50">
                    <td className="py-3 px-4">
                      <Link href={`/stock/${h.ticker}`} className="hover:text-gold">
                        <span className="font-semibold text-white">{h.ticker}</span>
                        <span className={`ml-2 px-1.5 py-0.5 text-xs rounded ${TIER_BG[h.tier]} ${TIER_COLORS[h.tier]}`}>{h.tier}</span>
                      </Link>
                    </td>
                    <td className="text-right py-3 px-4 text-white">{h.shares}</td>
                    <td className="text-right py-3 px-4 text-white">{formatCurrency(h.value)}</td>
                    <td className="text-right py-3 px-4 text-gold font-semibold">{h.score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
