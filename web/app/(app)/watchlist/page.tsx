"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface WatchlistItem {
  id: string;
  ticker: string;
  name: string;
  sector: string;
  score: number;
  tier: string;
  change_24h: number;
  price: number;
  added_at: string;
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
const MOCK_WATCHLIST: WatchlistItem[] = [
  {
    id: "1",
    ticker: "NEM",
    name: "Newmont Corporation",
    sector: "Materials",
    score: 82,
    tier: "FORTRESS",
    change_24h: 1.5,
    price: 45.5,
    added_at: "2024-05-15",
  },
  {
    id: "2",
    ticker: "GOLD",
    name: "Barrick Gold",
    sector: "Materials",
    score: 79,
    tier: "RESILIENT",
    change_24h: -0.8,
    price: 18.75,
    added_at: "2024-05-20",
  },
  {
    id: "3",
    ticker: "XOM",
    name: "Exxon Mobil",
    sector: "Energy",
    score: 74,
    tier: "RESILIENT",
    change_24h: 2.1,
    price: 105.0,
    added_at: "2024-05-22",
  },
  {
    id: "4",
    ticker: "CVX",
    name: "Chevron",
    sector: "Energy",
    score: 72,
    tier: "RESILIENT",
    change_24h: 0.5,
    price: 155.25,
    added_at: "2024-06-01",
  },
];

export default function WatchlistPage() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>(MOCK_WATCHLIST);
  const [searchTicker, setSearchTicker] = useState("");
  const [sortBy, setSortBy] = useState<"score" | "change" | "added">("added");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const removeFromWatchlist = (id: string) => {
    setWatchlist((prev) => prev.filter((item) => item.id !== id));
  };

  const addToWatchlist = () => {
    if (!searchTicker.trim()) return;

    // In production, this would search the API
    const newItem: WatchlistItem = {
      id: Date.now().toString(),
      ticker: searchTicker.toUpperCase(),
      name: `${searchTicker.toUpperCase()} Company`,
      sector: "Unknown",
      score: Math.floor(Math.random() * 40) + 50,
      tier: "MODERATE",
      change_24h: (Math.random() - 0.5) * 4,
      price: Math.random() * 100 + 20,
      added_at: new Date().toISOString().split("T")[0],
    };

    setWatchlist((prev) => [newItem, ...prev]);
    setSearchTicker("");
  };

  const sortedWatchlist = [...watchlist].sort((a, b) => {
    let comparison = 0;
    if (sortBy === "score") {
      comparison = a.score - b.score;
    } else if (sortBy === "change") {
      comparison = a.change_24h - b.change_24h;
    } else if (sortBy === "added") {
      comparison = new Date(a.added_at).getTime() - new Date(b.added_at).getTime();
    }
    return sortDir === "asc" ? comparison : -comparison;
  });

  return (
    <div className="min-h-screen bg-charcoal">
      {/* Header */}
      <div className="border-b border-charcoal-light p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-white">Watchlist</h1>
          <p className="text-gray-400 mt-1">
            Track companies you&apos;re interested in
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Add to Watchlist */}
        <Card className="bg-charcoal-light border-charcoal-lighter mb-6">
          <CardContent className="p-4">
            <div className="flex gap-4">
              <input
                type="text"
                value={searchTicker}
                onChange={(e) => setSearchTicker(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addToWatchlist()}
                placeholder="Enter ticker symbol (e.g., AAPL)"
                className="flex-1 bg-charcoal border border-charcoal-lighter rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:border-gold focus:outline-none"
              />
              <Button
                onClick={addToWatchlist}
                className="bg-gold hover:bg-gold-dark text-charcoal font-semibold"
              >
                Add to Watchlist
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Sort Controls */}
        <div className="flex items-center justify-between mb-4">
          <p className="text-gray-400 text-sm">
            {watchlist.length} stocks in watchlist
          </p>
          <div className="flex gap-2 items-center">
            <span className="text-sm text-gray-400">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-charcoal-light border border-charcoal-lighter rounded px-2 py-1 text-white text-sm"
            >
              <option value="added">Date Added</option>
              <option value="score">Score</option>
              <option value="change">24h Change</option>
            </select>
            <button
              onClick={() => setSortDir(sortDir === "asc" ? "desc" : "asc")}
              className="p-1 text-gray-400 hover:text-white"
            >
              {sortDir === "asc" ? "↑" : "↓"}
            </button>
          </div>
        </div>

        {/* Watchlist Table */}
        {sortedWatchlist.length > 0 ? (
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardContent className="p-0">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-charcoal-lighter">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">
                      Stock
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">
                      Price
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">
                      24h
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">
                      Score
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">
                      Tier
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">
                      Added
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400"></th>
                  </tr>
                </thead>
                <tbody>
                  {sortedWatchlist.map((item) => (
                    <tr
                      key={item.id}
                      className="border-b border-charcoal-lighter hover:bg-charcoal/50"
                    >
                      <td className="py-3 px-4">
                        <Link href={`/stock/${item.ticker}`} className="hover:text-gold">
                          <div className="font-semibold text-white">{item.ticker}</div>
                          <div className="text-sm text-gray-400">{item.name}</div>
                        </Link>
                      </td>
                      <td className="text-right py-3 px-4 text-white">
                        ${item.price.toFixed(2)}
                      </td>
                      <td className="text-right py-3 px-4">
                        <span
                          className={
                            item.change_24h >= 0 ? "text-green-500" : "text-red-500"
                          }
                        >
                          {item.change_24h >= 0 ? "+" : ""}
                          {item.change_24h.toFixed(2)}%
                        </span>
                      </td>
                      <td className="text-right py-3 px-4">
                        <span className="text-gold font-semibold">{item.score}</span>
                      </td>
                      <td className="text-right py-3 px-4">
                        <span
                          className={`px-2 py-1 text-xs rounded ${TIER_BG[item.tier]} ${TIER_COLORS[item.tier]}`}
                        >
                          {item.tier}
                        </span>
                      </td>
                      <td className="text-right py-3 px-4 text-gray-400 text-sm">
                        {new Date(item.added_at).toLocaleDateString()}
                      </td>
                      <td className="text-right py-3 px-4">
                        <button
                          onClick={() => removeFromWatchlist(item.id)}
                          className="text-gray-400 hover:text-red-500 p-1"
                          title="Remove from watchlist"
                        >
                          ✕
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        ) : (
          <Card className="bg-charcoal-light border-charcoal-lighter">
            <CardContent className="p-12 text-center">
              <p className="text-gray-400 mb-4">Your watchlist is empty</p>
              <p className="text-sm text-gray-500">
                Add stocks above to track their survival scores
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
