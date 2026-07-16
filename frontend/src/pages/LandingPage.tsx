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
//
// Positioning (S2797 Chris directive at T2): "AI with receipts" — the operating
// model IS the product. Two AIs collaborate: Claude proposes, Rigby verifies with
// tool_runs, pushes back with concrete edits, and both cite their evidence before
// anything reaches Chris. The "in practice" section pulls real examples from
// S2795/S2796/S2797 to make the abstract pattern concrete.

import { Link } from 'react-router-dom'
import {
  ShieldCheck, Search, FileCheck, ListChecks, ArrowRight,
  Mail, LogIn, Quote,
} from 'lucide-react'

// ─── Editable copy constants (Rigby F3) ─────────────────────────────────────
// Edit these to iterate copy without touching JSX.

const COPY = {
  brand: 'Donkey Betz',
  tagline: 'AI with receipts',
  hero_headline: 'AI that shows its work.',
  hero_sub: 'Most AI gives you an answer. Donkey Betz gives you two AIs that verify each other, push back with evidence, and hand you the receipts. One proposes. One audits. Neither trusts the other blindly. You decide with proof, not promises.',

  features: [
    {
      icon: Search,
      title: 'Verification, not vibes',
      body: 'Every AI claim gets tool-grounded verification. The verifier opens the codebase, runs the searches, cross-checks the schemas. If something can\'t be verified, that fact ships out loud — not silently glossed over.',
    },
    {
      icon: ShieldCheck,
      title: 'Structured pushback',
      body: 'The verifier doesn\'t rubber-stamp. She names the risks, flags coupling, identifies what\'s being over-claimed, and proposes concrete edits — before anything ships. Disagreement in the open, resolved together, ratified by you.',
    },
    {
      icon: FileCheck,
      title: 'Proof of work, on every decision',
      body: 'Every ship carries a stable-state pointer (git SHA), file-and-line evidence for every claim, and an explicit admission list of what was NOT verified this round. No hand-waving. No "trust me." Receipts by default.',
    },
    {
      icon: ListChecks,
      title: 'An auditable trail',
      body: 'Concerns raised during review get classified — actionable now, mitigatable now, or future-trigger — and persisted to a ledger BEFORE the human ratifies. You can replay any decision: what was flagged, what was adopted, what was deferred, and why.',
    },
  ],

  in_practice_heading: 'How it looks in practice',
  in_practice_sub: 'Trust but verify — three real examples from real sessions.',

  examples: [
    {
      when: 'Session 2795 — duplicate work prevented',
      claim: 'Claude proposed building a new `build_pa_tools_gap_map` command to surface untested PA tools.',
      rigby: 'Rigby opened the codebase (six tool calls). Found `build_pa_tool_audit` already existed. Found `PA_TOOL_AUDIT.md` (84 KB, two months stale). Found `test_pa_tool_schema_drift.py` — an existing CI guard for exactly this concern.',
      result: 'Ship shape reshaped from "build new command" to "extend existing command behind opt-in flags." Zero duplicate code. Full backwards compatibility preserved.',
    },
    {
      when: 'Session 2796 — pushback on over-claiming',
      claim: 'Claude proposed marking new validation docs as "validated_full" the moment they exist in the repo.',
      rigby: 'Rigby pushed back: doc-only presence doesn\'t equal runtime verification. Marking things "validated_full" without evidence would oversell what actually happened.',
      result: 'Every validation doc now includes a mandatory "Evidence" section — either a real observed-run snippet OR an explicit "runtime-not-executed" admission. Honest by construction.',
    },
    {
      when: 'Session 2797 — admitting the limit of the check',
      claim: 'Claude claimed "no Waitlist model exists in the backend" while scoping this very landing page.',
      rigby: 'Rigby ran a repo-wide search — zero matches for "Waitlist" across the entire codebase. Strong support for the claim. Then she flagged, unprompted: "I did the search, but I didn\'t do a direct read of core/models.py, so I can\'t strictly certify the exact-file version of your claim."',
      result: 'That admission — "here\'s what I verified, here\'s what I didn\'t" — is exactly the pattern. Verifiable AI names its own verification limits.',
    },
  ],

  how_it_works_heading: 'How it works',
  how_it_works: [
    {
      step: '1',
      title: 'You send a task',
      body: 'Research this. Build that. Decide between these. Anything from a one-line question to a multi-session build.',
    },
    {
      step: '2',
      title: 'Two AIs work it',
      body: 'One proposes, one verifies. They disagree in the open, cite evidence, classify every concern, and reach joint agreement — all before anything reaches you.',
    },
    {
      step: '3',
      title: 'You get proof, not promises',
      body: 'The decision, the reasoning trail, the risks flagged, the things admitted as unverified. Then you ratify. The trail is replayable forever.',
    },
  ],

  bottom_cta_heading: 'See it work on your problem.',
  bottom_cta_sub: 'Early access is limited. Email us with what you\'re working on — you\'ll get a walkthrough of Claude + Rigby working on it, receipts included.',

  cta_primary_label: 'Get in touch',
  cta_secondary_label: 'Request early access',
  cta_login_label: 'Log in',

  // Primary CTA — open-ended mailto so anyone can just email Chris directly.
  cta_primary_href:
    'mailto:chris@donkeybetz.com' +
    '?subject=' + encodeURIComponent('Donkey Betz — hello') +
    '&body=' + encodeURIComponent('Hi Chris,\n\n'),

  // Secondary CTA — pre-filled body captures quasi-structured leads without a DB
  // (Rigby F2). Fields shifted from sports-betting to operating-model framing.
  cta_secondary_href:
    'mailto:chris@donkeybetz.com' +
    '?subject=' + encodeURIComponent('Donkey Betz — early access request') +
    '&body=' + encodeURIComponent(
      'Hi Chris,\n\n' +
      'I\'d like early access to Donkey Betz.\n\n' +
      '— Name:\n' +
      '— What kind of work you\'d want AI to help with (research / analysis / building / decisions / other):\n' +
      '— What\'s frustrated you about AI so far (hallucinations, no receipts, no pushback, other):\n' +
      '— A specific problem you\'d want to see Claude + Rigby work on:\n\n' +
      'Thanks,\n'
    ),

  footer_note: 'Donkey Betz — verifiable AI operating model. Two AIs, mutual verification, receipts on every decision.',
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

      {/* In practice — real examples from real sessions */}
      <section className="max-w-4xl mx-auto px-6 py-16 border-t border-gray-800">
        <div className="text-center mb-12">
          <h3 className="text-2xl font-bold mb-2">{COPY.in_practice_heading}</h3>
          <p className="text-sm text-gray-500">{COPY.in_practice_sub}</p>
        </div>
        <div className="space-y-8">
          {COPY.examples.map((ex, i) => (
            <div key={i} className="card p-6">
              <div className="flex items-start gap-3 mb-4">
                <Quote size={18} className="text-primary-400 flex-shrink-0 mt-1" />
                <p className="text-xs uppercase tracking-wide text-primary-400 font-semibold">
                  {ex.when}
                </p>
              </div>
              <dl className="space-y-4 pl-8">
                <div>
                  <dt className="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">
                    Claude proposed
                  </dt>
                  <dd className="text-sm text-gray-300 leading-relaxed">{ex.claim}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">
                    Rigby verified
                  </dt>
                  <dd className="text-sm text-gray-300 leading-relaxed">{ex.rigby}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">
                    Result
                  </dt>
                  <dd className="text-sm text-gray-200 leading-relaxed">{ex.result}</dd>
                </div>
              </dl>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-4xl mx-auto px-6 py-16 border-t border-gray-800">
        <h3 className="text-2xl font-bold text-center mb-12">{COPY.how_it_works_heading}</h3>
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
        <h3 className="text-2xl font-bold mb-4">{COPY.bottom_cta_heading}</h3>
        <p className="text-gray-400 mb-8">
          {COPY.bottom_cta_sub}
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
