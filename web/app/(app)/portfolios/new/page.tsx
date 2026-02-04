"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface Holding {
  ticker: string;
  shares: number;
  cost_basis?: number;
}

export default function NewPortfolioPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [holdings, setHoldings] = useState<Holding[]>([{ ticker: "", shares: 0 }]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const addHolding = () => {
    setHoldings([...holdings, { ticker: "", shares: 0 }]);
  };

  const removeHolding = (index: number) => {
    setHoldings(holdings.filter((_, i) => i !== index));
  };

  const updateHolding = (index: number, field: keyof Holding, value: string | number) => {
    const updated = [...holdings];
    updated[index] = { ...updated[index], [field]: value };
    setHoldings(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Filter out empty holdings
    const validHoldings = holdings.filter((h) => h.ticker && h.shares > 0);

    try {
      // In production, this would call the API
      console.log("Creating portfolio:", { name, description, holdings: validHoldings });

      // Mock delay
      await new Promise((resolve) => setTimeout(resolve, 500));

      router.push("/portfolios");
    } catch (error) {
      console.error("Error creating portfolio:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-charcoal">
      {/* Header */}
      <div className="border-b border-charcoal-light p-6">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-2xl font-bold text-white">Create New Portfolio</h1>
          <p className="text-gray-400 mt-1">
            Build a portfolio to track its combined survival score
          </p>
        </div>
      </div>

      <div className="max-w-3xl mx-auto p-6">
        <form onSubmit={handleSubmit}>
          {/* Basic Info */}
          <Card className="bg-charcoal-light border-charcoal-lighter mb-6">
            <CardHeader>
              <CardTitle className="text-white">Portfolio Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Portfolio Name *
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g., Inflation Hedge Portfolio"
                  required
                  className="w-full bg-charcoal border border-charcoal-lighter rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:border-gold focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Description (optional)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe your portfolio strategy..."
                  rows={3}
                  className="w-full bg-charcoal border border-charcoal-lighter rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:border-gold focus:outline-none resize-none"
                />
              </div>
            </CardContent>
          </Card>

          {/* Holdings */}
          <Card className="bg-charcoal-light border-charcoal-lighter mb-6">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-white">Holdings</CardTitle>
              <Button
                type="button"
                variant="ghost"
                onClick={addHolding}
                className="text-gold hover:text-gold-dark"
              >
                + Add Holding
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {holdings.map((holding, index) => (
                  <div key={index} className="flex gap-4 items-start">
                    <div className="flex-1">
                      <label className="block text-xs text-gray-500 mb-1">
                        Ticker Symbol
                      </label>
                      <input
                        type="text"
                        value={holding.ticker}
                        onChange={(e) =>
                          updateHolding(index, "ticker", e.target.value.toUpperCase())
                        }
                        placeholder="e.g., NEM"
                        className="w-full bg-charcoal border border-charcoal-lighter rounded px-3 py-2 text-white placeholder-gray-500 focus:border-gold focus:outline-none"
                      />
                    </div>
                    <div className="w-32">
                      <label className="block text-xs text-gray-500 mb-1">
                        Shares
                      </label>
                      <input
                        type="number"
                        value={holding.shares || ""}
                        onChange={(e) =>
                          updateHolding(index, "shares", parseInt(e.target.value) || 0)
                        }
                        placeholder="0"
                        min={0}
                        className="w-full bg-charcoal border border-charcoal-lighter rounded px-3 py-2 text-white placeholder-gray-500 focus:border-gold focus:outline-none"
                      />
                    </div>
                    <div className="w-32">
                      <label className="block text-xs text-gray-500 mb-1">
                        Cost Basis ($)
                      </label>
                      <input
                        type="number"
                        value={holding.cost_basis || ""}
                        onChange={(e) =>
                          updateHolding(
                            index,
                            "cost_basis",
                            parseFloat(e.target.value) || 0
                          )
                        }
                        placeholder="0.00"
                        min={0}
                        step={0.01}
                        className="w-full bg-charcoal border border-charcoal-lighter rounded px-3 py-2 text-white placeholder-gray-500 focus:border-gold focus:outline-none"
                      />
                    </div>
                    {holdings.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeHolding(index)}
                        className="mt-6 p-2 text-gray-400 hover:text-red-500"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {holdings.length === 0 && (
                <p className="text-gray-500 text-center py-4">
                  No holdings added yet
                </p>
              )}
            </CardContent>
          </Card>

          {/* Import Option */}
          <Card className="bg-charcoal-light border-charcoal-lighter mb-6">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Import from Broker</p>
                  <p className="text-sm text-gray-400">
                    Connect your brokerage account to automatically import holdings
                  </p>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  disabled
                  className="border-charcoal-lighter text-gray-400"
                >
                  Coming Soon
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex gap-4 justify-end">
            <Button
              type="button"
              variant="ghost"
              onClick={() => router.back()}
              className="text-gray-400 hover:text-white"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!name || isSubmitting}
              className="bg-gold hover:bg-gold-dark text-charcoal font-semibold disabled:opacity-50"
            >
              {isSubmitting ? "Creating..." : "Create Portfolio"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
