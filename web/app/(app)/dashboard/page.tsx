'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function DashboardPage() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="font-display text-4xl text-gold tracking-wide">DASHBOARD</h1>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Portfolio Score Card */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Portfolio Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <p className="font-mono text-6xl text-cyan-400">72.5</p>
              <p className="text-sm text-text-dim mt-2 uppercase tracking-wide">Strong</p>
              <div className="mt-4 grid grid-cols-3 gap-2 text-center text-sm">
                <div>
                  <p className="text-text-muted">Gradual</p>
                  <p className="font-mono text-gold">74.1</p>
                </div>
                <div>
                  <p className="text-text-muted">Rapid</p>
                  <p className="font-mono text-orange-500">65.2</p>
                </div>
                <div>
                  <p className="text-text-muted">Hyper</p>
                  <p className="font-mono text-red-500">58.9</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Top Movers Card */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Top Movers (24h)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-text-muted mb-2">Gainers</p>
                <div className="space-y-2">
                  {movers.gainers.map((stock) => (
                    <div key={stock.ticker} className="flex justify-between items-center">
                      <span className="font-mono text-gold">{stock.ticker}</span>
                      <span className="font-mono text-green-400">+{stock.change}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm text-text-muted mb-2">Losers</p>
                <div className="space-y-2">
                  {movers.losers.map((stock) => (
                    <div key={stock.ticker} className="flex justify-between items-center">
                      <span className="font-mono text-gold">{stock.ticker}</span>
                      <span className="font-mono text-red-500">{stock.change}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Holdings Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Your Holdings</CardTitle>
          <button className="text-sm text-gold hover:text-gold-bright transition-colors">
            Edit Portfolio →
          </button>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border text-left text-sm text-text-muted">
                  <th className="pb-3 font-medium">Rank</th>
                  <th className="pb-3 font-medium">Ticker</th>
                  <th className="pb-3 font-medium">Name</th>
                  <th className="pb-3 font-medium text-right">Value</th>
                  <th className="pb-3 font-medium text-right">Score</th>
                  <th className="pb-3 font-medium text-right">Weight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {holdings.map((holding, idx) => (
                  <tr key={holding.ticker} className="hover:bg-slate/50 transition-colors">
                    <td className="py-3 font-mono text-text-dim">{idx + 1}</td>
                    <td className="py-3 font-mono text-gold">{holding.ticker}</td>
                    <td className="py-3 text-text">{holding.name}</td>
                    <td className="py-3 font-mono text-right text-text">{holding.value}</td>
                    <td className={`py-3 font-mono text-right ${getScoreColor(holding.score)}`}>
                      {holding.score}
                    </td>
                    <td className="py-3 font-mono text-right text-text-dim">{holding.weight}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

const movers = {
  gainers: [
    { ticker: 'GOLD', change: '3.2' },
    { ticker: 'NEM', change: '2.8' },
    { ticker: 'FCX', change: '2.1' },
    { ticker: 'XOM', change: '1.5' },
  ],
  losers: [
    { ticker: 'JPM', change: '-2.1' },
    { ticker: 'BAC', change: '-1.9' },
    { ticker: 'MSFT', change: '-1.2' },
    { ticker: 'AAPL', change: '-0.8' },
  ],
};

const holdings = [
  { ticker: 'NEM', name: 'Newmont Corporation', value: '$10,200', score: 94, weight: '25%' },
  { ticker: 'XOM', name: 'Exxon Mobil', value: '$8,500', score: 82, weight: '21%' },
  { ticker: 'FCX', name: 'Freeport-McMoRan', value: '$6,300', score: 79, weight: '15%' },
  { ticker: 'PG', name: 'Procter & Gamble', value: '$5,800', score: 62, weight: '14%' },
  { ticker: 'JPM', name: 'JPMorgan Chase', value: '$4,200', score: 41, weight: '10%' },
];

function getScoreColor(score: number): string {
  if (score >= 85) return 'text-green-400';
  if (score >= 70) return 'text-cyan-400';
  if (score >= 55) return 'text-gold';
  if (score >= 40) return 'text-orange-500';
  return 'text-red-500';
}
