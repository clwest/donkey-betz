---
title: "Signal Studio — Markets edition Phase 1 brief"
status: draft (Session 1135 discovery, rev. 2 post-Rigby review, pending Chris ratification)
session: 1135
generated: 2026-05-23
revised: 2026-05-23 (Rigby review pass + Jessica's 4 confirmations applied)
workspace: Donkey Betz
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md
  - specs/FLEET_CAPABILITY_BUSINESS_SPEC.md
  - apps/rigby_standalone_BRIEF.md
  - UDB_BEHAVIOR_LAYER.md
  - UDB_TRANSLATION_LAYER.md
authors: claude + jessica (discovery pass) → rigby (review applied)
---

# Signal Studio — Markets edition Phase 1 brief

## 1. What it is

**Phase 1 customer-facing pitch:**

> *"Signal Studio is your daily morning briefing — the top 10 emerging patterns from 80 spiders, algorithmically curated and delivered at 4:30 AM MT, with cluster cards that auto-refresh when new signals are published."*

**Phase 1 wedge: Markets/investing.** The brief is written by AI from live spider data and surfaces emerging patterns across public data feeds. Hybrid product shape: AI-written morning narrative on top of 10 ranked cluster cards underneath. **Packaging direction: standalone product** (Jessica discovery decision; not yet separately purchasable — separate Stripe SKU + landing page are Phase 0 gating items, see §5.1), marketed parallel to Rigby standalone. Bundling deferred to Phase 2+.

*Time zone shorthand: "MT" throughout = US Mountain Time (MDT in summer, MST in winter); times computed from `13:00 UTC` and `9:30 UTC` regardless of season.*

*AI is the voice (how the brief is written), not the marketing claim. Customers see "morning intelligence briefing," not "AI-powered."*

**Current state vs Phase 1 target (honesty note):**
- **Brief generation cadence** currently runs `13:00 UTC = 6:00 AM MT` on local. Phase 1 target is `9:30 UTC = 4:30 AM MT` for east-coast pre-market delivery — a 5-minute Celery beat config change.
- **"Auto-refresh"** today = SSE pill appears in the UI when the daily curator publishes a new snapshot (Session 1132). It is **not** continuous intraday re-curation. Underlying cluster data does update live as spiders find new patterns.
- **AI brief generation** is NOT yet built — see §5.1 Phase 0 gating.

## 2. Who buys it

**Primary user: Self-directed retail investor (solo).**
- Manages own portfolio via Robinhood / IBKR / Fidelity / Schwab
- Reads markets daily, watches FinTwit, subscribes to a few Substacks
- Wants an edge but can't afford Bloomberg ($2k+/mo) and finds Koyfin/Stockanalysis too data-heavy
- Mobile-first, scan-first, low attention

**Adjacent secondary user: Indie newsletter writer / FinTwit creator.**
- Uses signals as research material for their own content
- Higher LTV, smaller TAM
- Same product surface; different ad copy

**Buyer = User.** Self-serve via Stripe. No team/seat pricing. No firm-level sales. No procurement.

*Marketing voice deliberately not narrowed yet — both adjacent audiences share the same product; first 10 paying customers tell us which converts better.*

## 3. What's built (real shipping evidence)

*Counts and behavior below verified on local as of 2026-05-23 against `ai_core/spiders/`, `core/services/signal_aggregation_service.py`, `core/services/signal_curator_agent.py`, signal-studio repo (`signal_studio_api` + `signal_studio_web`), and Session 1131-1132 handoffs. Production parity not asserted.*

| Component | Status | Notes |
|---|---|---|
| Spider network (data source) | Live | 80 spiders across 41 categories. **Markets-relevant spiders include:** equities/macro — polygon, finnhub, sec_edgar, yahoo_finance, financial; **crypto** — coingecko, etherscan. Spiders can overlap publishers, so spider count ≠ unique source count |
| Signal cluster pipeline (u-d-b → fleet event → signal-studio Postgres) | Live | `signal.cluster_promoted` event flow shipped Session 1131 (PR #2138 + signal-studio #12) |
| Signal cluster store | Live | 131 clusters in local DB (5 seed + 126 real from spider network) |
| `SignalCuratorAgent` (daily Top 10 curator) | Live | Scoring `0.9 × strength + 0.1 × recency_decay`; dedup by `(pattern_type, topic_key)`; capped 3 per pattern. Shipped Session 1131 Phase 2 |
| Celery beat schedule (`curate-signal-clusters`) | Live | Currently 13:00 UTC = 6:00 AM MT; needs shift to 9:30 UTC = 4:30 AM MT for east-coast pre-market |
| `signal.curated_published` event | Live | Emits when daily curator produces snapshot |
| Live SSE refresh (browser) | Live | "🟢 New curated set — refresh" pill appears in signal-studio UI within ~5s of new snapshot (Session 1132 PR #14) |
| Signal Studio Docker app (`signal_studio_api` + `signal_studio_web`) | Live on local | Backend `localhost:8007`, frontend `localhost:5173` |
| Top-10 cards UI (Curated tab) | Live | Cards with rank badges 1-10, amber-bordered |
| `GET /api/signals/events` SSE endpoint | Live | Backend → browser event stream |
| Fleet routing config for `signal-studio` | Live | *Internal routing policy, not customer-facing feature.* `force_allowed = true`, default agent `trend_analysis_agent`, also allows `market_intelligence_agent` |
| Brand domain `247globalai.com` | Live | Vercel-served, marketing site |
| Consumer-facing landing page at sub-domain | **Not built** | See §5 |

## 4. What proves it's real

**Canonical Phase 1 proof: AI-written morning brief + Top-10 cluster cards + live SSE refresh, demoed via embedded landing-page screenshot/video.**

**Today's interim proof (developer-grade, available on local):**
> Open `localhost:5173` → click "Curated Top 10" tab → see 10 amber-bordered cluster cards with rank badges 1-10. Then trigger `curate_and_emit()` on u-d-b → within ~5s, "🟢 New curated set — refresh" pill appears in the Curated tab. Click pill → list refetches with new snapshot.
>
> Backend smoke: `curl http://localhost:8007/api/signals | jq '.total'` returns `131`.

**Launch-day proof (post-Phase 0, customer-facing):**
> Visit `signal-studio.247globalai.com` (or chosen sub-domain) → see 30-second hero video of morning brief landing in inbox at 4:30 AM MT → scroll → 10 cluster cards demo with the live refresh pill → CTA: *"Start your free 7-day trial — $29/mo"*.

**[BLOCKER]** Launch-day proof requires the AI brief generation, consumer landing page, and email delivery to ship first. See §5.

## 5. What's missing (gap to "could sell for real")

### 5.1 [PHASE 0 GATING — launch-blocking]

| Item | Status | Effort | Why gating |
|---|---|---|---|
| AI brief generation (LLM writes 3-paragraph sectioned narrative from cluster data) | **Not built** | ~1 sprint | This IS the product per Q1 + Q2. Without it, Signal Studio is "just a dashboard" and the $29 price collapses |
| Consumer landing page at `signal-studio.247globalai.com` (or chosen sub-domain) | **Not built** | ~1 sprint | No customer acquisition without it |
| Email infra (Resend or Postmark) + brief delivery + welcome + receipts + one-click unsubscribe | **Not built** | ~1–1.5 weeks | Email IS the product per Q9 (distribution = retention for newsletter-shape products) |
| Per-customer cost tracking (`LLMCallLog.workspace` FK, shared with Rigby Phase 0) | **Not done** | ~3 days | Same Atlas gating as Rigby — no cost attribution = uninsurable multi-tenant pricing |
| Daily $ spending cap per customer (shared with Rigby Phase 0) | **Not done** | ~1 day | Without this, paid ads can produce negative unit economics during free trial alone |
| TOS + privacy policy + disclaimer language legal review | **Not done** | 1–2 hr legal work (~$500–1500) | Required for any markets-adjacent paid product (Q10) |
| Stripe SKU + checkout for Signal Studio (separate from Rigby's) | **Not built** | Small (parallel to Rigby's hook work) | Revenue plumbing |
| Source URL enrichment on cluster cards (currently `url=""` placeholder) | **Carryover from START_HERE** | Small | Without source URLs, cluster cards undercut the briefing's credibility — brief sentences can't link to provenance |

### 5.2 Other prerequisites

| Item | Status | Effort |
|---|---|---|
| Auth/signup flow for retail trader (in signal-studio web repo) | **TBC** — Chris confirms repo state | TBD |
| Brief time shift Celery beat: 13:00 UTC → 9:30 UTC (4:30 AM MT) | **Not done** (confirmed Phase 1 priority per Jessica) | ~5 min config change |
| Email template QA across Gmail/Outlook/Apple Mail | **Not built** | ~1–2 days |

### 5.3 Not gaps, but worth naming

- **No paying customer exists.**
- No external-account integrations (broker APIs, portfolio trackers). Phase 2 trigger = customer demand.
- No domain coverage beyond markets in Phase 1 (legal, content, jobs/skills, crypto deferred to per-vertical sub-products later).

## 6. Buildable in one sprint?

**No — not buildable in one sprint end-to-end.** Phase 0 in aggregate: **LARGE (~4–5 weeks).** Parallel-able with Rigby standalone's Phase 0 (~3–4 weeks) — most items are separate engineering.

Per-item sizing:
- Brief time shift (Celery): **SMALL** (5 min)
- Stripe SKU + checkout: **SMALL**
- Source URL enrichment: **SMALL**
- Legal review of TOS + disclaimers: **SMALL** (~1–2 hr legal time)
- AI brief generation: **MEDIUM** (~1 sprint)
- Consumer landing page: **MEDIUM** (~1 sprint)
- Email infra + delivery + templates + unsubscribe: **MEDIUM** (~1–1.5 weeks)
- Cost tracking + daily cap (shared with Rigby Phase 0): **MEDIUM** (~1 week)
- Auth/signup flow: **BLOCKED on Chris repo status confirmation**

## 7. GTM sketch

| Lever | Plan |
|---|---|
| **Channel** | *Proposed (pending Chris greenlight + budget):* Paid ads from day one (Meta, Twitter/X, Reddit r/investing-adjacent), warm/personal network. No newsletter funnel (audience = 0, same as Rigby). |
| **Pricing** | $29/mo flat, single tier, 7-day free trial, monthly billing only in Phase 1 |
| **Cap behavior** | Daily $ cap per customer (same number as Rigby's, pending Chris confirmation — Atlas suggests $1.50/day) |
| **CTA** | "Start your free 7-day trial — $29/mo" → Stripe → onboarding |
| **What's included** | *Planned Phase-1 offer (post-Phase-0 gating, see §5.1):* Daily AI-written morning brief (email + web), Top 10 cluster cards with live refresh, AI commentary on any cluster (click-through), save signals to watchlist, ask Rigby about a cluster (chat), export to workspace as deliverable. 1 seat per subscription. |
| **Customer-facing surface** | `signal-studio.247globalai.com` (or chosen sub-domain) — own landing page, own Stripe SKU, separate from Rigby |
| **Brief delivery** | Daily at 4:30 AM MT to all active subscribers' inboxes (single batch, no per-user picker in Phase 1) |
| **Disclaimers** | "Not investment advice / AI-generated / educational only / past patterns ≠ future / consult licensed advisor / US-only" — in TOS, landing footer, every email, every brief, every AI chat reply |
| **Forbidden in product + marketing** | Buy/sell framing, price targets, accuracy claims without backing, SEC/FINRA registration implications, return-based marketing, personalized advice (Rigby chat hard-refuses) |
| **Scope** | Information service for US adult retail investors. NOT advisor, NOT trading platform, NOT recommendation engine. |
| **Execution posture** | Read + internal actions only (watchlist, chat about cluster, export). No outbound action on customer's external accounts. |

## 8. Spokesperson alignment (Phase 4+, parked)

Per Atlas §C.5, J.2.8: Character OS / avatar / voice = parked until a paying customer demands a face. Phase 1 is text-only (email + web). Clean upgrade path:

- **Phase 4+:** AI-voiced narration of the morning brief (audio-first delivery).
- **Phase 4+:** Persona-narrated video version of the brief for premium tier.
- **Phase 4+:** Brand-voice-locked avatar variants for white-label deployments (e.g., "Markets brief co-branded with X creator's persona").

## 9. Decisions still needed (escalate to Chris)

**Closed in Jessica discovery pass** (Chris ratification pending, captured for record):
- ✅ **Standalone vs bundled** — packaging direction locked as standalone, parallel to Rigby. Separately-purchasable infra (Stripe SKU, landing page) still Phase 0 work (see §5.1). Bundle deferred to Phase 2+.
- ✅ **"Hand-picked" vs "curated" language** — locked as "algorithmically curated."
- ✅ **4:30 AM MT brief generation shift** — locked as Phase 1 priority.
- ✅ **Canonical proof path** — locked as launch-day proof (brief + email + cards + SSE), requires Phase 0 gating items first.

**Still open for Chris:**

| # | Question | Why it matters |
|---|---|---|
| 1 | **Signal-studio web repo consumer-app status — what's actually shipped vs scaffolded?** | Same shape as Rigby's `app.247globalai.com` question. Unlocks Phase 0 timeline math + auth/signup effort sizing. |
| 2 | **Sub-domain pick** — `signal-studio.247globalai.com` vs `markets.247globalai.com` vs other? | Atlas §G lists `markets.247globalai.com` as proposed for the vertical; product name vs vertical name is a brand decision. |
| 3 | **Email service pick** — Resend vs Postmark vs other? | Drives Phase 0 integration effort + monthly cost ($10–50/mo at launch volume). |
| 4 | **Confirm $29/mo + 7-day trial as Phase 1 pricing** | Locks Stripe SKU. |
| 5 | **Same Phase 0 cost-attribution + daily cap as Rigby (Atlas-level requirement applies to both products)** | Without this, paid ads at $29 can produce negative unit economics during trial alone. |
| 6 | **Paid ads budget for Signal Studio (separate from Rigby's)** | Two parallel paid-ad campaigns = two budget pools. |
| 7 | **Legal review greenlight (~$500–1500) for TOS + disclaimers** | Required before launching any markets-adjacent paid product. |
| 8 | **Existing u-d-b email infra check** — is there already messaging/notification infra we can reuse vs greenfield Resend/Postmark integration? | If u-d-b already sends transactional email, save 2–3 days of integration work. |

## 10. Honest claim audit (per translation layer §2)

**We do NOT claim:**
- Signal Studio provides investment, financial, or trading advice.
- Specific accuracy or prediction rates for our signals.
- A paying Signal Studio customer exists.
- The AI brief generation is built (it's not — Phase 0 gating item).
- The consumer landing page exists (it doesn't — Phase 0 gating item).
- Email delivery to subscribers is wired (it isn't — Phase 0 gating item).
- A Stripe SKU for Signal Studio exists (it doesn't — separate from Rigby's).
- Auth/signup flow in the signal-studio repo is consumer-ready (status TBC — see §9).
- SEC, FINRA, or other regulatory registration.
- International availability (US-only Phase 1).
- Continuous 24/7 personalized monitoring or watchlist alerts (Phase 1 is daily batch only).
- **Humans hand-pick the Top 10.** Curation is algorithmic (scoring formula + dedup) + the `SignalCuratorAgent`, not human editorial selection.
- **Continuous intraday re-curation.** The morning curator runs once daily; the SSE-pill UI refresh fires when the next daily snapshot lands, not continuously throughout the day.
- **Real-time market data quotes or guaranteed source completeness.** Spider coverage is what it is; downstream APIs (polygon/finnhub/etc.) have their own latency, rate limits, and coverage gaps. We surface patterns, not live tape.

**We DO claim:**
- The signal cluster pipeline (u-d-b spider → fleet event → signal-studio Postgres) is operational on local today; 131 clusters in DB; verifiable via `curl localhost:8007/api/signals`.
- The daily curator agent (`SignalCuratorAgent`) runs on Celery beat with documented scoring formula; produces Top-10 snapshot with provenance.
- The live SSE refresh from signal-studio backend to browser is working on local; pill appears within ~5s of new snapshot.
- The Top-10 cards UI is shipping in the signal-studio web app on local.
- The brand domain `247globalai.com` is owned and live.

---

**Brief authored:** Session 1135 (Claude + Jessica discovery pass).
**Rev. 2:** Rigby review pass applied — 12 mechanical fixes (§1 honesty rewrite + current-vs-target state note, "curated" not "hand-picked", spider list disambiguation, fleet routing labeled as internal policy, `url=""` enrichment elevated to Phase 0 gating, §6 explicit "not buildable in one sprint", §7 "What's included" prefixed as planned not shipped, §9 reduced by Jessica's 4 confirmations, §10 expanded with 3 new "we do not claim" bullets). Jessica's 4 in-session decisions ratified (standalone / curated / 4:30 AM MT priority / canonical proof path).
**Next step:** Rigby quick "looks good?" pass on rev. 2. Then Chris ratifies the 8 remaining decisions in §9. Then brief becomes locked Phase 1 source-of-truth for Signal Studio.
