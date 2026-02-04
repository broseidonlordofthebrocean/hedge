"use client";

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SurvivalMeter } from "@/components/charts/SurvivalMeter";

interface ScreenerFilters {
  minScore: number;
  maxScore: number;
  tiers: string[];
  sectors: string[];
  minMarketCap: number | null;
  maxMarketCap: number | null;
  factors: {
    hard_assets: { min: number; max: number };
    precious_metals: { min: number; max: number };
    commodities: { min: number; max: number };
    foreign_revenue: { min: number; max: number };
    pricing_power: { min: number; max: number };
    debt_structure: { min: number; max: number };
    essential_services: { min: number; max: number };
  };
}

interface Company {
  id: string;
  ticker: string;
  name: string;
  sector: string;
  score: number;
  tier: string;
  market_cap: number;
  factors: Record<string, number>;
}

const TIERS = ["FORTRESS", "RESILIENT", "MODERATE", "VULNERABLE", "EXPOSED"];
const SECTORS = [
  "Materials",
  "Energy",
  "Utilities",
  "Consumer Staples",
  "Healthcare",
  "Industrials",
  "Financials",
  "Technology",
  "Consumer Discretionary",
  "Real Estate",
  "Communication Services",
];

const FACTOR_NAMES: Record<string, string> = {
  hard_assets: "Hard Assets",
  precious_metals: "Precious Metals",
  commodities: "Commodities",
  foreign_revenue: "Foreign Revenue",
  pricing_power: "Pricing Power",
  debt_structure: "Debt Structure",
  essential_services: "Essential Services",
};

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
const MOCK_COMPANIES: Company[] = [
  {
    id: "1",
    ticker: "NEM",
    name: "Newmont Corporation",
    sector: "Materials",
    score: 82,
    tier: "FORTRESS",
    market_cap: 45_000_000_000,
    factors: { hard_assets: 85, precious_metals: 95, commodities: 80, foreign_revenue: 70, pricing_power: 75, debt_structure: 82, essential_services: 40 },
  },
  {
    id: "2",
    ticker: "GOLD",
    name: "Barrick Gold",
    sector: "Materials",
    score: 79,
    tier: "RESILIENT",
    market_cap: 35_000_000_000,
    factors: { hard_assets: 82, precious_metals: 92, commodities: 78, foreign_revenue: 75, pricing_power: 70, debt_structure: 78, essential_services: 35 },
  },
  {
    id: "3",
    ticker: "XOM",
    name: "Exxon Mobil",
    sector: "Energy",
    score: 74,
    tier: "RESILIENT",
    market_cap: 450_000_000_000,
    factors: { hard_assets: 75, precious_metals: 15, commodities: 95, foreign_revenue: 60, pricing_power: 68, debt_structure: 80, essential_services: 85 },
  },
  {
    id: "4",
    ticker: "FCX",
    name: "Freeport-McMoRan",
    sector: "Materials",
    score: 71,
    tier: "RESILIENT",
    market_cap: 55_000_000_000,
    factors: { hard_assets: 80, precious_metals: 35, commodities: 90, foreign_revenue: 65, pricing_power: 60, debt_structure: 68, essential_services: 55 },
  },
  {
    id: "5",
    ticker: "CVX",
    name: "Chevron",
    sector: "Energy",
    score: 72,
    tier: "RESILIENT",
    market_cap: 280_000_000_000,
    factors: { hard_assets: 70, precious_metals: 10, commodities: 92, foreign_revenue: 55, pricing_power: 65, debt_structure: 82, essential_services: 80 },
  },
  {
    id: "6",
    ticker: "BHP",
    name: "BHP Group",
    sector: "Materials",
    score: 76,
    tier: "RESILIENT",
    market_cap: 150_000_000_000,
    factors: { hard_assets: 85, precious_metals: 25, commodities: 95, foreign_revenue: 85, pricing_power: 70, debt_structure: 75, essential_services: 45 },
  },
  {
    id: "7",
    ticker: "AAPL",
    name: "Apple Inc.",
    sector: "Technology",
    score: 45,
    tier: "VULNERABLE",
    market_cap: 3_000_000_000_000,
    factors: { hard_assets: 25, precious_metals: 5, commodities: 15, foreign_revenue: 60, pricing_power: 90, debt_structure: 70, essential_services: 30 },
  },
  {
    id: "8",
    ticker: "MSFT",
    name: "Microsoft",
    sector: "Technology",
    score: 42,
    tier: "VULNERABLE",
    market_cap: 2_800_000_000_000,
    factors: { hard_assets: 20, precious_metals: 5, commodities: 10, foreign_revenue: 55, pricing_power: 85, debt_structure: 75, essential_services: 40 },
  },
];

export default function ScreenerPage() {
  const [filters, setFilters] = useState<ScreenerFilters>({
    minScore: 0,
    maxScore: 100,
    tiers: [],
    sectors: [],
    minMarketCap: null,
    maxMarketCap: null,
    factors: {
      hard_assets: { min: 0, max: 100 },
      precious_metals: { min: 0, max: 100 },
      commodities: { min: 0, max: 100 },
      foreign_revenue: { min: 0, max: 100 },
      pricing_power: { min: 0, max: 100 },
      debt_structure: { min: 0, max: 100 },
      essential_services: { min: 0, max: 100 },
    },
  });

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [sortBy, setSortBy] = useState<"score" | "ticker" | "market_cap">("score");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const filteredCompanies = useMemo(() => {
    let result = MOCK_COMPANIES.filter((company) => {
      // Score filter
      if (company.score < filters.minScore || company.score > filters.maxScore) {
        return false;
      }

      // Tier filter
      if (filters.tiers.length > 0 && !filters.tiers.includes(company.tier)) {
        return false;
      }

      // Sector filter
      if (filters.sectors.length > 0 && !filters.sectors.includes(company.sector)) {
        return false;
      }

      // Market cap filters
      if (filters.minMarketCap && company.market_cap < filters.minMarketCap) {
        return false;
      }
      if (filters.maxMarketCap && company.market_cap > filters.maxMarketCap) {
        return false;
      }

      // Factor filters
      for (const [factor, range] of Object.entries(filters.factors)) {
        const score = company.factors[factor];
        if (score !== undefined && (score < range.min || score > range.max)) {
          return false;
        }
      }

      return true;
    });

    // Sort
    result.sort((a, b) => {
      let comparison = 0;
      if (sortBy === "score") {
        comparison = a.score - b.score;
      } else if (sortBy === "ticker") {
        comparison = a.ticker.localeCompare(b.ticker);
      } else if (sortBy === "market_cap") {
        comparison = a.market_cap - b.market_cap;
      }
      return sortDir === "asc" ? comparison : -comparison;
    });

    return result;
  }, [filters, sortBy, sortDir]);

  const toggleTier = (tier: string) => {
    setFilters((prev) => ({
      ...prev,
      tiers: prev.tiers.includes(tier)
        ? prev.tiers.filter((t) => t !== tier)
        : [...prev.tiers, tier],
    }));
  };

  const toggleSector = (sector: string) => {
    setFilters((prev) => ({
      ...prev,
      sectors: prev.sectors.includes(sector)
        ? prev.sectors.filter((s) => s !== sector)
        : [...prev.sectors, sector],
    }));
  };

  const resetFilters = () => {
    setFilters({
      minScore: 0,
      maxScore: 100,
      tiers: [],
      sectors: [],
      minMarketCap: null,
      maxMarketCap: null,
      factors: {
        hard_assets: { min: 0, max: 100 },
        precious_metals: { min: 0, max: 100 },
        commodities: { min: 0, max: 100 },
        foreign_revenue: { min: 0, max: 100 },
        pricing_power: { min: 0, max: 100 },
        debt_structure: { min: 0, max: 100 },
        essential_services: { min: 0, max: 100 },
      },
    });
  };

  const formatMarketCap = (value: number) => {
    if (value >= 1_000_000_000_000) {
      return `$${(value / 1_000_000_000_000).toFixed(1)}T`;
    }
    if (value >= 1_000_000_000) {
      return `$${(value / 1_000_000_000).toFixed(0)}B`;
    }
    return `$${(value / 1_000_000).toFixed(0)}M`;
  };

  return (
    <div className="min-h-screen bg-charcoal">
      {/* Header */}
      <div className="border-b border-charcoal-light p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-white">Stock Screener</h1>
          <p className="text-gray-400 mt-1">
            Filter and find companies based on survival scores and factors
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            <Card className="bg-charcoal-light border-charcoal-lighter">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-white text-lg">Filters</CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={resetFilters}
                  className="text-gray-400 hover:text-white"
                >
                  Reset
                </Button>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Score Range */}
                <div>
                  <label className="text-sm text-gray-400 block mb-2">
                    Score Range
                  </label>
                  <div className="flex gap-2 items-center">
                    <input
                      type="number"
                      min={0}
                      max={100}
                      value={filters.minScore}
                      onChange={(e) =>
                        setFilters((prev) => ({
                          ...prev,
                          minScore: parseInt(e.target.value) || 0,
                        }))
                      }
                      className="w-20 bg-charcoal border border-charcoal-lighter rounded px-2 py-1 text-white text-sm"
                    />
                    <span className="text-gray-500">to</span>
                    <input
                      type="number"
                      min={0}
                      max={100}
                      value={filters.maxScore}
                      onChange={(e) =>
                        setFilters((prev) => ({
                          ...prev,
                          maxScore: parseInt(e.target.value) || 100,
                        }))
                      }
                      className="w-20 bg-charcoal border border-charcoal-lighter rounded px-2 py-1 text-white text-sm"
                    />
                  </div>
                </div>

                {/* Tiers */}
                <div>
                  <label className="text-sm text-gray-400 block mb-2">Tiers</label>
                  <div className="flex flex-wrap gap-2">
                    {TIERS.map((tier) => (
                      <button
                        key={tier}
                        onClick={() => toggleTier(tier)}
                        className={`px-2 py-1 text-xs rounded border transition-colors ${
                          filters.tiers.includes(tier)
                            ? `${TIER_BG[tier]} ${TIER_COLORS[tier]} border-current`
                            : "border-charcoal-lighter text-gray-400 hover:text-white"
                        }`}
                      >
                        {tier}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Sectors */}
                <div>
                  <label className="text-sm text-gray-400 block mb-2">Sectors</label>
                  <div className="flex flex-wrap gap-2">
                    {SECTORS.slice(0, 6).map((sector) => (
                      <button
                        key={sector}
                        onClick={() => toggleSector(sector)}
                        className={`px-2 py-1 text-xs rounded border transition-colors ${
                          filters.sectors.includes(sector)
                            ? "bg-gold/10 text-gold border-gold"
                            : "border-charcoal-lighter text-gray-400 hover:text-white"
                        }`}
                      >
                        {sector}
                      </button>
                    ))}
                  </div>
                  <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="text-xs text-gold mt-2 hover:underline"
                  >
                    {showAdvanced ? "Show less" : "Show more sectors..."}
                  </button>
                  {showAdvanced && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {SECTORS.slice(6).map((sector) => (
                        <button
                          key={sector}
                          onClick={() => toggleSector(sector)}
                          className={`px-2 py-1 text-xs rounded border transition-colors ${
                            filters.sectors.includes(sector)
                              ? "bg-gold/10 text-gold border-gold"
                              : "border-charcoal-lighter text-gray-400 hover:text-white"
                          }`}
                        >
                          {sector}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Advanced Factor Filters */}
                <div>
                  <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="flex items-center justify-between w-full text-sm text-gray-400 hover:text-white"
                  >
                    <span>Factor Filters</span>
                    <span>{showAdvanced ? "−" : "+"}</span>
                  </button>
                  {showAdvanced && (
                    <div className="mt-4 space-y-3">
                      {Object.entries(FACTOR_NAMES).map(([key, label]) => (
                        <div key={key}>
                          <label className="text-xs text-gray-500 block mb-1">
                            {label}
                          </label>
                          <div className="flex gap-2 items-center">
                            <input
                              type="number"
                              min={0}
                              max={100}
                              value={filters.factors[key as keyof typeof filters.factors].min}
                              onChange={(e) =>
                                setFilters((prev) => ({
                                  ...prev,
                                  factors: {
                                    ...prev.factors,
                                    [key]: {
                                      ...prev.factors[key as keyof typeof prev.factors],
                                      min: parseInt(e.target.value) || 0,
                                    },
                                  },
                                }))
                              }
                              className="w-14 bg-charcoal border border-charcoal-lighter rounded px-2 py-1 text-white text-xs"
                            />
                            <span className="text-gray-500 text-xs">-</span>
                            <input
                              type="number"
                              min={0}
                              max={100}
                              value={filters.factors[key as keyof typeof filters.factors].max}
                              onChange={(e) =>
                                setFilters((prev) => ({
                                  ...prev,
                                  factors: {
                                    ...prev.factors,
                                    [key]: {
                                      ...prev.factors[key as keyof typeof prev.factors],
                                      max: parseInt(e.target.value) || 100,
                                    },
                                  },
                                }))
                              }
                              className="w-14 bg-charcoal border border-charcoal-lighter rounded px-2 py-1 text-white text-xs"
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Results */}
          <div className="lg:col-span-3">
            {/* Sort Controls */}
            <div className="flex items-center justify-between mb-4">
              <p className="text-gray-400 text-sm">
                {filteredCompanies.length} companies found
              </p>
              <div className="flex gap-2 items-center">
                <span className="text-sm text-gray-400">Sort by:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="bg-charcoal-light border border-charcoal-lighter rounded px-2 py-1 text-white text-sm"
                >
                  <option value="score">Score</option>
                  <option value="ticker">Ticker</option>
                  <option value="market_cap">Market Cap</option>
                </select>
                <button
                  onClick={() => setSortDir(sortDir === "asc" ? "desc" : "asc")}
                  className="p-1 text-gray-400 hover:text-white"
                >
                  {sortDir === "asc" ? "↑" : "↓"}
                </button>
              </div>
            </div>

            {/* Results Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredCompanies.map((company) => (
                <Link href={`/stock/${company.ticker}`} key={company.id}>
                  <Card className="bg-charcoal-light border-charcoal-lighter hover:border-gold/50 transition-colors cursor-pointer">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-lg font-semibold text-white">
                              {company.ticker}
                            </span>
                            <span
                              className={`px-2 py-0.5 text-xs rounded ${TIER_BG[company.tier]} ${TIER_COLORS[company.tier]}`}
                            >
                              {company.tier}
                            </span>
                          </div>
                          <p className="text-sm text-gray-400">{company.name}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {company.sector} • {formatMarketCap(company.market_cap)}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-gold">
                            {company.score}
                          </div>
                          <p className="text-xs text-gray-500">Score</p>
                        </div>
                      </div>
                      {/* Mini factor bars */}
                      <div className="mt-3 grid grid-cols-7 gap-1">
                        {Object.values(company.factors).map((value, i) => (
                          <div key={i} className="h-1 bg-charcoal rounded overflow-hidden">
                            <div
                              className="h-full bg-gold/60"
                              style={{ width: `${value}%` }}
                            />
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>

            {filteredCompanies.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-400">No companies match your filters</p>
                <Button
                  variant="ghost"
                  onClick={resetFilters}
                  className="mt-2 text-gold"
                >
                  Reset filters
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
