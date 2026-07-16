// Public landing page — Donkey Betz market-shipping surface.
//
// Ship contract (S2797):
//   - Ultra-static: no auth checks, no API calls, no analytics deps, no live widgets.
//     Rigby SIGN F1 (ledger row 69). Marketing page's only job is opening a channel.
//   - Copy lives in editable constants at top of file (below). Chris can iterate copy
//     without touching JSX. Rigby SIGN F3 (ledger row 71).
//   - Two mailto CTAs — primary open-ended + secondary pre-filled with structured
//     lead fields. Rigby SIGN F2 (ledger row 70).
//   - Mounted at unauth /welcome. Root / is unchanged — still Chris's authenticated
//     CommandCenter. Rigby SIGN F4 (ledger row 72, future_trigger) defers the
//     root-domain discoverability question until first prospect complaint / inbound
//     organic traffic observed.

import { Link } from 'react-router-dom'
import {
  TrendingUp, Brain, Zap, Target, ArrowRight, Mail, LogIn,
} from 'lucide-react'

// ─── Editable copy constants (Rigby F3) ─────────────────────────────────────
// Edit these to iterate copy without touching JSX.

const COPY = {
  brand: 'Donkey Betz',
  tagline: 'AI-powered sports betting intelligence',
  hero_headline: 'Bet smarter with an AI research team on your side.',
  hero_sub: 'Donkey Betz reads the market, tracks sharp action, surfaces edges, and remembers what you like — so you spend less time hunting picks and more time executing.',

  features: [
    {
      icon: Brain,
      title: 'AI research assistant',
      body: 'A conversational personal assistant that answers "what should I bet tonight?" — grounded in live odds, sharp action, and injury reports.',
    },
    {
      icon: TrendingUp,
      title: 'Live sharp-action + arbitrage',
      body: 'Real-time market movement tracking across every major book. Sharp side, steam moves, and arb opportunities surfaced automatically.',
    },
    {
      icon: Target,
      title: 'Top plays, ranked',
      body: 'Every day, a ranked list of the highest-edge plays across every sport in season — with the reasoning behind each pick.',
    },
    {
      icon: Zap,
      title: 'Your bankroll, tracked',
      body: 'Automatic wager logging, ROI by sport / bet type / book, and streak analysis. Know exactly what\'s working and what isn\'t.',
    },
  ],

  how_it_works: [
    {
      step: '1',
      title: 'Get access',
      body: 'Email us for early-access credentials. We\'re onboarding a small first cohort to make sure the experience is right.',
    },
    {
      step: '2',
      title: 'Meet Rigby',
      body: 'Your AI research assistant. Ask her anything — she knows every game, every line, every trend.',
    },
    {
      step: '3',
      title: 'Bet with an edge',
      body: 'Follow the top plays, track your wagers, and let the platform learn what you like. Iterate faster than the market.',
    },
  ],

  cta_primary_label: 'Get in touch',
  cta_secondary_label: 'Request early access',
  cta_login_label: 'Log in',

  // Primary CTA — open-ended mailto so anyone can just email Chris directly.
  cta_primary_href:
    'mailto:chris@donkeybetz.com' +
    '?subject=' + encodeURIComponent('Donkey Betz — hello') +
    '&body=' + encodeURIComponent('Hi Chris,\n\n'),

  // Secondary CTA — pre-filled body captures quasi-structured leads without a DB
  // (Rigby F2). Fields: name, bankroll size, state (US legal-betting state), book(s).
  cta_secondary_href:
    'mailto:chris@donkeybetz.com' +
    '?subject=' + encodeURIComponent('Donkey Betz — early access request') +
    '&body=' + encodeURIComponent(
      'Hi Chris,\n\n' +
      'I\'d like early access to Donkey Betz.\n\n' +
      '— Name:\n' +
      '— Rough bankroll size (US$):\n' +
      '— State (where you place bets):\n' +
      '— Sportsbook(s) you use:\n' +
      '— What you\'re hoping the platform helps you do:\n\n' +
      'Thanks,\n'
    ),

  footer_note: 'Donkey Betz — sports intelligence platform. For entertainment and research purposes; know your local laws and gamble responsibly.',
}

// ─── Page component ─────────────────────────────────────────────────────────

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-dark-bg text-gray-100">
      {/* Top bar */}
      <header className="border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-primary-400">{COPY.brand}</h1>
            <p className="text-xs text-gray-500">{COPY.tagline}</p>
          </div>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 text-sm text-gray-300 hover:text-primary-400 transition-colors"
          >
            <LogIn size={16} />
            {COPY.cta_login_label}
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 pt-20 pb-16 text-center">
        <h2 className="text-4xl md:text-5xl font-bold leading-tight mb-6">
          {COPY.hero_headline}
        </h2>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-10">
          {COPY.hero_sub}
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href={COPY.cta_secondary_href}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-primary-500 hover:bg-primary-600 text-white font-medium transition-colors"
          >
            {COPY.cta_secondary_label}
            <ArrowRight size={16} />
          </a>
          <a
            href={COPY.cta_primary_href}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg border border-gray-700 hover:border-primary-500 text-gray-200 hover:text-primary-400 font-medium transition-colors"
          >
            <Mail size={16} />
            {COPY.cta_primary_label}
          </a>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-gray-800">
        <div className="grid md:grid-cols-2 gap-8">
          {COPY.features.map((f) => {
            const Icon = f.icon
            return (
              <div key={f.title} className="flex gap-4">
                <div className="flex-shrink-0 h-12 w-12 rounded-lg bg-primary-500/10 border border-primary-500/30 flex items-center justify-center">
                  <Icon size={24} className="text-primary-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-1">{f.title}</h3>
                  <p className="text-sm text-gray-400 leading-relaxed">{f.body}</p>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-4xl mx-auto px-6 py-16 border-t border-gray-800">
        <h3 className="text-2xl font-bold text-center mb-12">How it works</h3>
        <div className="grid md:grid-cols-3 gap-8">
          {COPY.how_it_works.map((s) => (
            <div key={s.step} className="text-center">
              <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-primary-500 text-white font-bold text-xl mb-4">
                {s.step}
              </div>
              <h4 className="text-lg font-semibold mb-2">{s.title}</h4>
              <p className="text-sm text-gray-400">{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="max-w-3xl mx-auto px-6 py-20 text-center border-t border-gray-800">
        <h3 className="text-2xl font-bold mb-4">Ready to bet with an edge?</h3>
        <p className="text-gray-400 mb-8">
          Early access is limited — email us and we'll get you set up.
        </p>
        <a
          href={COPY.cta_secondary_href}
          className="inline-flex items-center gap-2 px-8 py-4 rounded-lg bg-primary-500 hover:bg-primary-600 text-white font-medium text-lg transition-colors"
        >
          {COPY.cta_secondary_label}
          <ArrowRight size={18} />
        </a>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-12">
        <div className="max-w-6xl mx-auto px-6 py-8 text-center text-xs text-gray-500">
          {COPY.footer_note}
        </div>
      </footer>
    </div>
  )
}
