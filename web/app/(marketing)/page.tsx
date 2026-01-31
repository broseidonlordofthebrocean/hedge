import Link from 'next/link';
import { MacroTicker } from '@/components/charts/MacroTicker';
import { SurvivalMeter } from '@/components/charts/SurvivalMeter';

export default function LandingPage() {
  return (
    <div className="bg-black">
      {/* Macro Ticker */}
      <MacroTicker />

      {/* Hero Section */}
      <section className="relative px-6 py-24 lg:px-8 lg:py-32">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="font-display text-5xl tracking-wide text-gold sm:text-7xl lg:text-8xl">
            HEDGE
          </h1>
          <p className="mt-2 font-display text-2xl tracking-widest text-text-dim sm:text-3xl">
            HARD-ASSET EQUITY DEVALUATION GUARD ENGINE
          </p>
          <p className="mt-8 text-lg leading-8 text-text sm:text-xl">
            Score stocks on their resilience to US dollar devaluation.
            Stress-test your portfolio against currency collapse scenarios.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Link
              href="/dashboard"
              className="rounded-md bg-gold px-6 py-3 text-lg font-semibold text-black shadow-sm hover:bg-gold-bright transition-colors focus-ring"
            >
              Get Started Free
            </Link>
            <Link
              href="/rankings"
              className="text-lg font-semibold text-text hover:text-gold transition-colors"
            >
              View Rankings <span aria-hidden="true">→</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Sample Rankings Preview */}
      <section className="border-t border-border px-6 py-16 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <h2 className="font-display text-3xl text-gold text-center mb-12 tracking-wide">
            TOP SURVIVAL SCORES
          </h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {sampleStocks.map((stock) => (
              <div
                key={stock.ticker}
                className="bg-charcoal border border-border rounded-lg p-6 card-hover"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-mono text-xl text-gold">{stock.ticker}</p>
                    <p className="text-sm text-text-dim mt-1">{stock.name}</p>
                    <p className="text-xs text-text-muted mt-1">{stock.sector}</p>
                  </div>
                  <div className="text-right">
                    <p className={`font-mono text-3xl ${getScoreClass(stock.score)}`}>
                      {stock.score}
                    </p>
                    <p className={`text-xs uppercase tracking-wide ${getTierClass(stock.tier)}`}>
                      {stock.tier}
                    </p>
                  </div>
                </div>
                <div className="mt-4">
                  <SurvivalMeter score={stock.score} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Factor Explanation */}
      <section className="border-t border-border px-6 py-16 lg:px-8 bg-charcoal">
        <div className="mx-auto max-w-6xl">
          <h2 className="font-display text-3xl text-gold text-center mb-4 tracking-wide">
            HOW WE SCORE
          </h2>
          <p className="text-center text-text-dim mb-12 max-w-2xl mx-auto">
            Our proprietary algorithm evaluates 7 key factors that determine how well
            a company can weather dollar devaluation scenarios.
          </p>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {factors.map((factor) => (
              <div key={factor.name} className="bg-slate border border-border rounded-lg p-5">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-2xl">{factor.icon}</span>
                  <h3 className="font-display text-lg text-text tracking-wide">
                    {factor.name}
                  </h3>
                </div>
                <p className="text-sm text-text-dim">{factor.description}</p>
                <p className="text-xs text-gold mt-2 font-mono">{factor.weight}% weight</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Scenario Section */}
      <section className="border-t border-border px-6 py-16 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <h2 className="font-display text-3xl text-gold text-center mb-4 tracking-wide">
            SCENARIO MODELING
          </h2>
          <p className="text-center text-text-dim mb-12 max-w-2xl mx-auto">
            See how your portfolio performs across different dollar devaluation scenarios.
          </p>
          <div className="grid gap-6 md:grid-cols-3">
            {scenarios.map((scenario) => (
              <div
                key={scenario.name}
                className={`border rounded-lg p-6 ${scenario.borderClass}`}
              >
                <h3 className={`font-display text-2xl tracking-wide ${scenario.textClass}`}>
                  {scenario.name}
                </h3>
                <p className="text-text-dim text-sm mt-2">{scenario.description}</p>
                <ul className="mt-4 space-y-2 text-sm">
                  <li className="text-text">
                    <span className="text-text-muted">Dollar decline:</span> {scenario.decline}
                  </li>
                  <li className="text-text">
                    <span className="text-text-muted">Timeline:</span> {scenario.timeline}
                  </li>
                  <li className="text-text">
                    <span className="text-text-muted">Inflation:</span> {scenario.inflation}
                  </li>
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="border-t border-border px-6 py-24 lg:px-8 bg-charcoal">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="font-display text-4xl text-gold tracking-wide">
            PROTECT YOUR PORTFOLIO
          </h2>
          <p className="mt-4 text-lg text-text-dim">
            Start analyzing your holdings against dollar devaluation scenarios today.
          </p>
          <Link
            href="/dashboard"
            className="mt-8 inline-block rounded-md bg-gold px-8 py-4 text-xl font-semibold text-black shadow-sm hover:bg-gold-bright transition-colors focus-ring"
          >
            Start Free Analysis
          </Link>
        </div>
      </section>
    </div>
  );
}

const sampleStocks = [
  { ticker: 'NEM', name: 'Newmont Corporation', sector: 'Gold Mining', score: 94, tier: 'excellent' },
  { ticker: 'GOLD', name: 'Barrick Gold', sector: 'Gold Mining', score: 91, tier: 'excellent' },
  { ticker: 'XOM', name: 'Exxon Mobil', sector: 'Oil & Gas', score: 82, tier: 'strong' },
  { ticker: 'FCX', name: 'Freeport-McMoRan', sector: 'Copper Mining', score: 79, tier: 'strong' },
  { ticker: 'PG', name: 'Procter & Gamble', sector: 'Consumer Staples', score: 62, tier: 'moderate' },
  { ticker: 'JPM', name: 'JPMorgan Chase', sector: 'Banks', score: 41, tier: 'vulnerable' },
];

const factors = [
  { name: 'HARD ASSETS', icon: '🏗️', weight: 25, description: 'Tangible assets like property, equipment, and inventory that retain real value.' },
  { name: 'PRECIOUS METALS', icon: '🥇', weight: 15, description: 'Direct exposure to gold, silver, and platinum through mining or holdings.' },
  { name: 'COMMODITIES', icon: '🛢️', weight: 15, description: 'Revenue from oil, copper, agricultural products, and other raw materials.' },
  { name: 'FOREIGN REVENUE', icon: '🌍', weight: 15, description: 'International sales that benefit from dollar weakness.' },
  { name: 'PRICING POWER', icon: '💪', weight: 15, description: 'Ability to pass cost increases to customers without losing volume.' },
  { name: 'DEBT STRUCTURE', icon: '📊', weight: 10, description: 'Fixed-rate, long-term debt that benefits from inflation.' },
  { name: 'ESSENTIAL SERVICES', icon: '⚡', weight: 5, description: 'Inelastic demand for utilities, healthcare, and staples.' },
];

const scenarios = [
  {
    name: 'GRADUAL',
    description: 'Slow erosion of dollar value over several years',
    decline: '15-20%',
    timeline: '3-5 years',
    inflation: '6-8%',
    borderClass: 'border-gold/30 bg-gold/5',
    textClass: 'text-gold',
  },
  {
    name: 'RAPID',
    description: 'Accelerated decline following major policy shift',
    decline: '30-40%',
    timeline: '12-18 months',
    inflation: '12-15%',
    borderClass: 'border-orange-500/30 bg-orange-500/5',
    textClass: 'text-orange-500',
  },
  {
    name: 'HYPER',
    description: 'Currency crisis with hyperinflationary conditions',
    decline: '50%+',
    timeline: '6-12 months',
    inflation: '50%+',
    borderClass: 'border-red-500/30 bg-red-500/5',
    textClass: 'text-red-500',
  },
];

function getScoreClass(score: number): string {
  if (score >= 85) return 'text-green-400';
  if (score >= 70) return 'text-cyan-400';
  if (score >= 55) return 'text-gold';
  if (score >= 40) return 'text-orange-500';
  return 'text-red-500';
}

function getTierClass(tier: string): string {
  switch (tier) {
    case 'excellent': return 'text-green-400';
    case 'strong': return 'text-cyan-400';
    case 'moderate': return 'text-gold';
    case 'vulnerable': return 'text-orange-500';
    case 'critical': return 'text-red-500';
    default: return 'text-text-dim';
  }
}
