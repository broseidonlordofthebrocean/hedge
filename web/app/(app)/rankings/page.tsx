'use client';

import { useState } from 'react';

export default function RankingsPage() {
  const [selectedTier, setSelectedTier] = useState<string | null>(null);

  const filteredCompanies = selectedTier
    ? companies.filter((c) => c.tier === selectedTier)
    : companies;

  return (
    <div className="p-6 space-y-6">
      <h1 className="font-display text-4xl text-gold tracking-wide">SURVIVAL RANKINGS</h1>

      {/* Tier Filters */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedTier(null)}
          className={`px-4 py-2 rounded-lg border transition-colors ${
            selectedTier === null
              ? 'bg-gold text-black border-gold'
              : 'border-border text-text-dim hover:border-gold hover:text-gold'
          }`}
        >
          All
        </button>
        {tiers.map((tier) => (
          <button
            key={tier.name}
            onClick={() => setSelectedTier(tier.name)}
            className={`px-4 py-2 rounded-lg border transition-colors ${
              selectedTier === tier.name
                ? `${tier.bgColor} ${tier.textColor} ${tier.borderColor}`
                : `border-border text-text-dim hover:${tier.borderColor} hover:${tier.textColor}`
            }`}
          >
            {tier.label}
          </button>
        ))}
      </div>

      {/* Rankings Table */}
      <div className="bg-charcoal border border-border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border text-left text-sm text-text-muted bg-slate">
                <th className="px-4 py-3 font-medium">Rank</th>
                <th className="px-4 py-3 font-medium">Ticker</th>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Sector</th>
                <th className="px-4 py-3 font-medium text-right">Score</th>
                <th className="px-4 py-3 font-medium text-center">Tier</th>
                <th className="px-4 py-3 font-medium text-right">Gradual</th>
                <th className="px-4 py-3 font-medium text-right">Rapid</th>
                <th className="px-4 py-3 font-medium text-right">Hyper</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredCompanies.map((company, idx) => (
                <tr
                  key={company.ticker}
                  className="hover:bg-slate/50 transition-colors cursor-pointer"
                >
                  <td className="px-4 py-3 font-mono text-text-dim">{idx + 1}</td>
                  <td className="px-4 py-3 font-mono text-gold font-semibold">
                    {company.ticker}
                  </td>
                  <td className="px-4 py-3 text-text">{company.name}</td>
                  <td className="px-4 py-3 text-text-dim text-sm">{company.sector}</td>
                  <td className={`px-4 py-3 font-mono text-right text-lg ${getScoreColor(company.score)}`}>
                    {company.score}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-1 rounded text-xs uppercase tracking-wide ${getTierBadge(company.tier)}`}>
                      {company.tier}
                    </span>
                  </td>
                  <td className={`px-4 py-3 font-mono text-right ${getScoreColor(company.gradual)}`}>
                    {company.gradual}
                  </td>
                  <td className={`px-4 py-3 font-mono text-right ${getScoreColor(company.rapid)}`}>
                    {company.rapid}
                  </td>
                  <td className={`px-4 py-3 font-mono text-right ${getScoreColor(company.hyper)}`}>
                    {company.hyper}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-sm text-text-muted text-center">
        Showing {filteredCompanies.length} of {companies.length} companies
      </p>
    </div>
  );
}

const tiers = [
  { name: 'excellent', label: 'Excellent', textColor: 'text-green-400', bgColor: 'bg-green-400/10', borderColor: 'border-green-400/50' },
  { name: 'strong', label: 'Strong', textColor: 'text-cyan-400', bgColor: 'bg-cyan-400/10', borderColor: 'border-cyan-400/50' },
  { name: 'moderate', label: 'Moderate', textColor: 'text-gold', bgColor: 'bg-gold/10', borderColor: 'border-gold/50' },
  { name: 'vulnerable', label: 'Vulnerable', textColor: 'text-orange-500', bgColor: 'bg-orange-500/10', borderColor: 'border-orange-500/50' },
  { name: 'critical', label: 'Critical', textColor: 'text-red-500', bgColor: 'bg-red-500/10', borderColor: 'border-red-500/50' },
];

const companies = [
  { ticker: 'NEM', name: 'Newmont Corporation', sector: 'Gold Mining', score: 94, tier: 'excellent', gradual: 92, rapid: 96, hyper: 98 },
  { ticker: 'GOLD', name: 'Barrick Gold', sector: 'Gold Mining', score: 91, tier: 'excellent', gradual: 89, rapid: 93, hyper: 96 },
  { ticker: 'FNV', name: 'Franco-Nevada', sector: 'Precious Metals', score: 88, tier: 'excellent', gradual: 86, rapid: 90, hyper: 94 },
  { ticker: 'XOM', name: 'Exxon Mobil', sector: 'Oil & Gas', score: 82, tier: 'strong', gradual: 80, rapid: 84, hyper: 78 },
  { ticker: 'FCX', name: 'Freeport-McMoRan', sector: 'Copper Mining', score: 79, tier: 'strong', gradual: 77, rapid: 82, hyper: 85 },
  { ticker: 'CAT', name: 'Caterpillar', sector: 'Industrials', score: 74, tier: 'strong', gradual: 72, rapid: 70, hyper: 65 },
  { ticker: 'PG', name: 'Procter & Gamble', sector: 'Consumer Staples', score: 62, tier: 'moderate', gradual: 64, rapid: 58, hyper: 52 },
  { ticker: 'JNJ', name: 'Johnson & Johnson', sector: 'Healthcare', score: 58, tier: 'moderate', gradual: 60, rapid: 54, hyper: 48 },
  { ticker: 'JPM', name: 'JPMorgan Chase', sector: 'Banks', score: 41, tier: 'vulnerable', gradual: 45, rapid: 35, hyper: 28 },
  { ticker: 'MSFT', name: 'Microsoft', sector: 'Software', score: 32, tier: 'critical', gradual: 35, rapid: 28, hyper: 22 },
];

function getScoreColor(score: number): string {
  if (score >= 85) return 'text-green-400';
  if (score >= 70) return 'text-cyan-400';
  if (score >= 55) return 'text-gold';
  if (score >= 40) return 'text-orange-500';
  return 'text-red-500';
}

function getTierBadge(tier: string): string {
  switch (tier) {
    case 'excellent': return 'bg-green-400/20 text-green-400';
    case 'strong': return 'bg-cyan-400/20 text-cyan-400';
    case 'moderate': return 'bg-gold/20 text-gold';
    case 'vulnerable': return 'bg-orange-500/20 text-orange-500';
    case 'critical': return 'bg-red-500/20 text-red-500';
    default: return 'bg-slate text-text-dim';
  }
}
