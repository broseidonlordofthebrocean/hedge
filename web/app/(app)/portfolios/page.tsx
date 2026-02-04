"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SurvivalMeter } from "@/components/charts/SurvivalMeter";

interface Portfolio {
  id: string;
  name: string;
  description?: string;
  score: number;
  tier: string;
  holdings_count: number;
  total_value: number;
  created_at: string;
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

// Mock data
const MOCK_PORTFOLIOS: Portfolio[] = [
  {
    id: "1",
    name: "Inflation Hedge",
    description: "Gold miners and commodity producers",
    score: 78,
    tier: "RESILIENT",
    holdings_count: 8,
    total_value: 125000,
    created_at: "2024-01-15",
  },
  {
    id: "2",
    name: "Dollar Collapse",
    description: "Maximum protection portfolio",
    score: 85,
    tier: "FORTRESS",
    holdings_count: 5,
    total_value: 75000,
    created_at: "2024-02-20",
  },
  {
    id: "3",
    name: "Balanced Approach",
    description: "Mixed traditional and hedge assets",
    score: 62,
    tier: "MODERATE",
    holdings_count: 12,
    total_value: 200000,
    created_at: "2024-03-01",
  },
];

export default function PortfoliosPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>(MOCK_PORTFOLIOS);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const formatValue = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    }).format(value);
  };

  const averageScore = portfolios.length > 0
    ? Math.round(portfolios.reduce((sum, p) => sum + p.score, 0) / portfolios.length)
    : 0;

  return (
    <div className="min-h-screen bg-charcoal">
      {/* Header */}
      <div className="border-b border-charcoal-light p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Portfolios</h1>
            <p className="text-gray-400 mt-1">
              Manage and analyze your investment portfolios
            </p>
          </div>
          <Link href="/portfolios/new">
            <Button className="bg-gold hover:bg-gold-dark text-charcoal font-semibold">
              + New Portfolio
            </Button>
          </Link>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardContent className="p-4">
              <p className="text-sm text-gray-400">Total Portfolios</p>
              <p className="text-2xl font-bold text-white">{portfolios.length}</p>
            </CardContent>
          </Card>
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardContent className="p-4">
              <p className="text-sm text-gray-400">Total Holdings</p>
              <p className="text-2xl font-bold text-white">
                {portfolios.reduce((sum, p) => sum + p.holdings_count, 0)}
              </p>
            </CardContent>
          </Card>
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardContent className="p-4">
              <p className="text-sm text-gray-400">Total Value</p>
              <p className="text-2xl font-bold text-white">
                {formatValue(portfolios.reduce((sum, p) => sum + p.total_value, 0))}
              </p>
            </CardContent>
          </Card>
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardContent className="p-4">
              <p className="text-sm text-gray-400">Avg Survival Score</p>
              <p className="text-2xl font-bold text-gold">{averageScore}</p>
            </CardContent>
          </Card>
        </div>

        {/* Portfolio Grid */}
        {portfolios.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {portfolios.map((portfolio) => (
              <Link href={`/portfolios/${portfolio.id}`} key={portfolio.id}>
                <Card className="bg-charcoal-light border-charcoal-lighter hover:border-gold/50 transition-colors cursor-pointer h-full">
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-white">{portfolio.name}</CardTitle>
                        {portfolio.description && (
                          <p className="text-sm text-gray-400 mt-1">
                            {portfolio.description}
                          </p>
                        )}
                      </div>
                      <span
                        className={`px-2 py-1 text-xs rounded ${TIER_BG[portfolio.tier]} ${TIER_COLORS[portfolio.tier]}`}
                      >
                        {portfolio.tier}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between mb-4">
                      <SurvivalMeter score={portfolio.score} size="sm" />
                      <div className="text-right">
                        <p className="text-2xl font-bold text-gold">{portfolio.score}</p>
                        <p className="text-xs text-gray-500">Survival Score</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Holdings</p>
                        <p className="text-white font-medium">{portfolio.holdings_count}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Value</p>
                        <p className="text-white font-medium">
                          {formatValue(portfolio.total_value)}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardContent className="p-12 text-center">
              <p className="text-gray-400 mb-4">No portfolios yet</p>
              <Link href="/portfolios/new">
                <Button className="bg-gold hover:bg-gold-dark text-charcoal font-semibold">
                  Create Your First Portfolio
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
