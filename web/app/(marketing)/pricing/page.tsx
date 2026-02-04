"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const PLANS = [
  {
    name: "Free",
    price: 0,
    interval: null,
    description: "Get started with basic access",
    features: [
      "Top 10 ranked companies",
      "Basic macro dashboard",
      "Weekly email digest",
      "Limited score history",
    ],
    cta: "Get Started",
    highlighted: false,
  },
  {
    name: "Pro",
    price: 29,
    interval: "month",
    yearlyPrice: 290,
    description: "Full access for serious investors",
    features: [
      "Full rankings access (500+ companies)",
      "Real-time macro data",
      "Custom screener filters",
      "Portfolio tracking (up to 3)",
      "Custom alerts",
      "API access (1,000 calls/month)",
      "Factor breakdown analysis",
      "Score history (1 year)",
    ],
    cta: "Start Pro Trial",
    highlighted: true,
  },
  {
    name: "Institutional",
    price: 199,
    interval: "month",
    yearlyPrice: 1990,
    description: "For funds and professional investors",
    features: [
      "Everything in Pro",
      "Unlimited portfolios",
      "Priority data updates",
      "Unlimited API access",
      "Custom factor weights",
      "Bulk data export",
      "Dedicated support",
      "Score history (full)",
      "White-label reports",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-charcoal">
      {/* Header */}
      <header className="border-b border-charcoal-light">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-gold">
            HEDGE
          </Link>
          <nav className="flex items-center gap-6">
            <Link href="/rankings" className="text-gray-300 hover:text-white">
              Rankings
            </Link>
            <Link href="/pricing" className="text-gold">
              Pricing
            </Link>
            <Link href="/login">
              <Button variant="outline" className="border-gold text-gold hover:bg-gold/10">
                Sign In
              </Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-400">
            Choose the plan that fits your investment strategy
          </p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="pb-16 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {PLANS.map((plan) => (
              <Card
                key={plan.name}
                className={`bg-charcoal-light border-charcoal-lighter relative ${
                  plan.highlighted ? "border-gold ring-1 ring-gold" : ""
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gold text-charcoal px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </div>
                )}
                <CardHeader className="text-center pb-4">
                  <CardTitle className="text-white text-2xl">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-gold">
                      ${plan.price}
                    </span>
                    {plan.interval && (
                      <span className="text-gray-400">/{plan.interval}</span>
                    )}
                  </div>
                  {plan.yearlyPrice && (
                    <p className="text-sm text-gray-500 mt-1">
                      or ${plan.yearlyPrice}/year (save 17%)
                    </p>
                  )}
                  <p className="text-gray-400 mt-2">{plan.description}</p>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-gold mt-0.5">✓</span>
                        <span className="text-gray-300 text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button
                    className={`w-full ${
                      plan.highlighted
                        ? "bg-gold hover:bg-gold-dark text-charcoal font-semibold"
                        : "bg-charcoal border border-charcoal-lighter text-white hover:border-gold"
                    }`}
                  >
                    {plan.cta}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-16 px-6 border-t border-charcoal-light">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            <div className="p-6 bg-charcoal-light rounded-lg border border-charcoal-lighter">
              <h3 className="text-lg font-semibold text-white mb-2">
                Can I cancel anytime?
              </h3>
              <p className="text-gray-400">
                Yes, you can cancel your subscription at any time. Your access will
                continue until the end of your billing period.
              </p>
            </div>
            <div className="p-6 bg-charcoal-light rounded-lg border border-charcoal-lighter">
              <h3 className="text-lg font-semibold text-white mb-2">
                What payment methods do you accept?
              </h3>
              <p className="text-gray-400">
                We accept all major credit cards (Visa, Mastercard, American Express)
                through our secure payment processor, Stripe.
              </p>
            </div>
            <div className="p-6 bg-charcoal-light rounded-lg border border-charcoal-lighter">
              <h3 className="text-lg font-semibold text-white mb-2">
                Is there a free trial?
              </h3>
              <p className="text-gray-400">
                Yes! Pro plans include a 14-day free trial. No credit card required to
                start.
              </p>
            </div>
            <div className="p-6 bg-charcoal-light rounded-lg border border-charcoal-lighter">
              <h3 className="text-lg font-semibold text-white mb-2">
                How is the survival score calculated?
              </h3>
              <p className="text-gray-400">
                Our proprietary scoring engine evaluates companies across 7 key factors
                that indicate resilience to currency devaluation: hard assets, precious
                metals exposure, commodity production, foreign revenue, pricing power,
                debt structure, and essential services.
              </p>
            </div>
            <div className="p-6 bg-charcoal-light rounded-lg border border-charcoal-lighter">
              <h3 className="text-lg font-semibold text-white mb-2">
                What companies are covered?
              </h3>
              <p className="text-gray-400">
                We cover 500+ US-listed companies across all sectors, with a focus on
                those with significant exposure to inflation-hedging characteristics.
                New companies are added regularly.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-6 bg-charcoal-light border-t border-charcoal-lighter">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Protect Your Portfolio?
          </h2>
          <p className="text-gray-400 mb-8">
            Start with our free tier and upgrade when you&apos;re ready
          </p>
          <Link href="/signup">
            <Button className="bg-gold hover:bg-gold-dark text-charcoal font-semibold text-lg px-8 py-3">
              Get Started Free
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-charcoal-light py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="text-gold font-bold text-xl">HEDGE</div>
          <div className="flex gap-8 text-sm text-gray-400">
            <Link href="/privacy" className="hover:text-white">
              Privacy
            </Link>
            <Link href="/terms" className="hover:text-white">
              Terms
            </Link>
            <Link href="/contact" className="hover:text-white">
              Contact
            </Link>
          </div>
          <p className="text-sm text-gray-500">
            © 2024 HEDGE. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
