---
title: "Signal Studio — Phase 1 brief (products.ts-anchored)"
status: draft (Session 1135 discovery, rev. 3 — corrected against products.ts canonical source, pending Chris ratification)
originating_session: 1135
generated: 2026-05-23
revised: 2026-05-23 (rev. 3 — corrected against products.ts; rev. 2 had wrong audience + wrong product framing)
workspace: Donkey Betz
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md
  - apps/contract_concierge_BRIEF.md
  - apps/rigby_standalone_BRIEF.md
  - UDB_BEHAVIOR_LAYER.md
  - UDB_TRANSLATION_LAYER.md
source_of_truth: "24-7-ai-global/src/lib/products.ts LAB[3] (slug: signal-studio)"
authors: claude + jessica (discovery pass) → rigby (review applied) → corrected against products.ts ground truth
---

# Signal Studio — Phase 1 brief

> **⚠️ Source of truth:** `24-7-ai-global/src/lib/products.ts` LAB[3] (entry no. XI). All product framing below traces back there. Rev. 3 corrected this brief against products.ts after discovering that rev. 1–2 targeted the wrong audience ("self-directed retail investor" instead of the canonical "Investors · deal sourcers · competitive analysts") and pitched a different product shape ("AI-written morning briefing" instead of canonical "Cluster web signals into evidence-backed intelligence").

## 1. What it is

**Phase 1 customer-facing pitch (per products.ts):**

> *"Cluster web signals into evidence-backed intelligence."*

**Elevator (per products.ts):** *"An intelligence engine that turns news, social, and RSS into clustered signals — each with confidence scores, evidence-card citations, and analyst-generated action steps. The data model is rigorous and runs on a hardcoded MVP action engine (no LLM dependency); ingestion pipeline forthcoming."*

**Pillar:** Intelligence. **Arc:** Scout. **Tier:** LAB (Lab #4 — no. XI). **Status:** demo-ready · Frontend Live.

**Phase 1 scope:** Signal clustering with 0-1 confidence scoring, evidence cards with direct URL citations, source deduplication + multi-category filtering, action card generation, dashboard signal-strength view. **The MVP action engine runs without any LLM key** — LLM is an optional enhancement layer, not the core product.

**Live URL:** https://signal-studio-ten.vercel.app
**Repo:** https://github.com/clwest/signal-studio
**Tier note:** LAB tier (alongside SellerPilot, ComplianceSentinel, context-kit, Character OS, Rigby). NOT a Suite product. NOT a flagship vertical.

**Engineering reality on local** (separate from products.ts framing): Session 1131-1132 wired the signal-studio fleet repo to u-d-b's signal cluster pipeline + SSE refresh + daily curator at 13:00 UTC. This is the **engine-side enrichment** that could feed the products.ts-described product, but is not the core product.

## 2. Who buys it

**Target per products.ts:** Investors · deal sourcers · competitive analysts.

Three concrete buyer profiles:
- **Investor** (angel / emerging-fund GP / scout) tracking emerging signals across sectors
- **Deal sourcer** (VC platform team / scout) needing evidence-backed signal flow
- **Competitive analyst** (corp strategy / product marketing) tracking competitor and category signals

**Buyer = User** (self-serve via Stripe — note Stripe is *stubbed* per products.ts, not live).

*Rev. 1-2 misframed audience as "self-directed retail investor." That was extrapolation, not what products.ts targets.*

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

> **⚠️ Pricing reality:** products.ts marks Stripe as **stubbed** (not live). Pricing tiers below are *Phase 1 proposal*, not currently in-market — products.ts has no pricing block for Signal Studio (unlike Suite products which do).

| Lever | Plan |
|---|---|
| **Surface** | https://signal-studio-ten.vercel.app (live, frontend-only per products.ts) + https://github.com/clwest/signal-studio (public repo) |
| **Tier classification** | LAB tier per products.ts (alongside SellerPilot, ComplianceSentinel, context-kit, Character OS). NOT a Suite product. |
| **Channel (proposed Phase 1)** | Reach via 24-7-ai-global studio site + Operator Edge cross-promo to the deal-sourcer / VC analyst audience. No paid ads until Stripe SKU is live + pricing locked. |
| **Pricing (proposed Phase 1 — NOT currently locked in products.ts)** | Suggest Free / Pro / Team tiers similar to other LAB products. Free: limited signal clusters + evidence cards. Pro: full clusters + action cards. Team: API + multi-seat. **Chris ratifies actual price points at GTM lock.** |
| **What's actually in-market today** | Signal clustering with confidence scoring, evidence cards with URL citations, source dedup, multi-category filtering, action card generation. Stripe stubbed. |
| **Engine-side enrichment (separate from products.ts product)** | Session 1131-1132 wired u-d-b signal cluster pipeline + SSE refresh + daily curator. Could power an enhanced version of the products.ts product, but the products.ts product runs without LLM dependency on a hardcoded MVP action engine. |
| **Disclaimers** | "Not investment advice / signals are pattern observations, not predictions / consult appropriate advisors before acting" — in TOS, landing footer, any analyst-output context. |
| **Forbidden in product + marketing** | Buy/sell recommendations, price targets, accuracy/win-rate claims without backing, SEC/FINRA registration implications, return-based marketing. |
| **Scope** | Intelligence engine for investors / deal sourcers / competitive analysts. NOT a trading platform, NOT a financial advisor, NOT a recommendation engine. |
| **Execution posture** | Read + cluster + cite + suggest action. No outbound actions, no customer-account integrations. |

## 8. Spokesperson alignment (Phase 4+, parked)

Per Atlas §C.5, J.2.8: Character OS / avatar / voice = parked until a paying customer demands a face. Phase 1 is text-only (email + web). Clean upgrade path:

- **Phase 4+:** AI-voiced narration of the morning brief (audio-first delivery).
- **Phase 4+:** Persona-narrated video version of the brief for premium tier.
- **Phase 4+:** Brand-voice-locked avatar variants for white-label deployments (e.g., "Markets brief co-branded with X creator's persona").

## 9. Decisions still needed (escalate to Chris)

**Closed by products.ts as canonical source of truth:**
- ✅ **Product framing** — locked per products.ts LAB[3]
- ✅ **Target audience** — Investors · deal sourcers · competitive analysts per products.ts
- ✅ **Status** — demo-ready · Frontend Live per products.ts
- ✅ **Production URL** — https://signal-studio-ten.vercel.app
- ✅ **Tier classification** — LAB tier (not Suite, not flagship vertical)
- ✅ **Core product = MVP action engine without LLM dependency** per products.ts elevator

**Still open for Chris:**

| # | Question | Why it matters |
|---|---|---|
| 1 | **Pricing tiers + price points** — products.ts has no pricing block for Signal Studio (Stripe stubbed). Lock Free / Pro / Team price points before Stripe SKU work. | Required before any paid acquisition |
| 2 | **Stripe SKU wiring** — Stripe is stubbed per products.ts. Path to live billing? | Revenue plumbing |
| 3 | **Engine-side enrichment integration** — should the products.ts product use the u-d-b cluster pipeline + SSE + daily curator (Session 1131-1132 work), or stay on its own MVP action engine per products.ts? | Determines whether the engineering work is a Signal Studio v2 (richer data) or stays separate (engine reveal product) |
| 4 | **Phase 0 cost-attribution shared with Rigby + Contract Concierge** | Atlas-level requirement once paid |
| 5 | **TOS + privacy + investment-disclaimer legal review** | Required for any markets-adjacent paid product |
| 6 | **GTM channel** — Operator Edge cross-promo, direct outreach to deal-sourcer audiences, both? | Acquisition strategy |
| 7 | **Suite vs Lab positioning long-term** — products.ts treats as LAB today. Should it graduate to Suite if it hits revenue thresholds? | Brand portfolio strategy |

## 10. Honest claim audit (per translation layer §2)

**We do NOT claim:**
- Signal Studio provides investment, financial, or trading advice.
- Specific accuracy or prediction rates for our signals.
- A paying Signal Studio customer exists.
- A live Stripe SKU exists (products.ts marks Stripe stubbed).
- Pricing is locked (products.ts has no pricing block; tiers are Phase 1 proposal).
- The u-d-b engine-side enrichment (Session 1131-1132 cluster pipeline + SSE + daily curator) is currently wired into the products.ts product — those are separate engineering streams.
- SEC, FINRA, or other regulatory registration.
- International compliance beyond US.
- Continuous 24/7 personalized monitoring or watchlist alerts.
- **Real-time market data quotes** — Signal Studio is pattern observation, not live tape.

**We DO claim (per products.ts ground truth):**
- Signal Studio is **demo-ready · Frontend Live** at https://signal-studio-ten.vercel.app per products.ts.
- Core capabilities (per products.ts): signal clustering with 0-1 confidence scoring, evidence cards with direct URL citations, source deduplication + multi-category filtering, action card generation, dashboard signal-strength view.
- **MVP action engine runs without any LLM key** (per products.ts elevator).
- LAB tier classification (entry no. XI, alongside SellerPilot, ComplianceSentinel, context-kit, Character OS, Rigby).
- Target audience: Investors · deal sourcers · competitive analysts (per products.ts).
- Stack per products.ts: FastAPI · React 19 · Vite · SQLite · Stripe (stubbed).
- Repo: https://github.com/clwest/signal-studio.

**We DO claim (engine-side, separate from products.ts product):**
- The u-d-b signal cluster pipeline (Session 1131 Phase 1 PR #2138) is operational on local; 131 clusters in DB at time of last verification.
- `SignalCuratorAgent` daily curator (Session 1131 Phase 2) runs on Celery beat.
- SSE refresh (Session 1132 PR #14) operational on local.
- These could be wired into the products.ts product as enrichment (see §9 decision #3) but currently are separate engineering streams.

---

**Brief authored:** Session 1135 (Claude + Jessica discovery pass).
**Rev. 2:** Rigby review pass applied — 12 mechanical fixes + Jessica's 4 in-session decisions ratified (standalone / curated / 4:30 AM MT priority / canonical proof path).
**Rev. 3:** Discovery of `24-7-ai-global/src/lib/products.ts` as canonical source of truth revealed rev. 1-2 targeted the wrong audience (retail traders vs canonical investors/deal sourcers/competitive analysts) and pitched wrong product shape (AI-written morning briefing vs canonical MVP action engine without LLM dependency). §1 / §2 / §7 / §9 / §10 rewritten to align with products.ts LAB[3]. Engine-side u-d-b work (Session 1131-1132) preserved as separate engineering stream.
**Next step:** Jessica ratified §9 decisions in Session 1137 (2026-05-24) — see `docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md`.

## Session 1137 ratification status

| §9 Q | Status | Source |
|---|---|---|
| Q1 Pricing tiers + price points | ✅ **Decision 6** — Free + $49 Pro + $99 Team | handoff Decision 6 |
| Q2 Stripe SKU wiring | ✅ **Decision 10** — 1st in sequence (Signal Studio → SellerPilot → ComplianceSentinel) | handoff Decision 10 |
| Q3 Engine-side enrichment integration | 🔧 Chris queue — architecture decision; v2 question | handoff Chris queue #2 |
| Q4 Phase 0 cost-attribution shared with Rigby + Contract Concierge | ✅ **Decision 9** — portfolio rule covers Signal Studio | handoff Decision 9 |
| Q5 TOS + privacy + investment-disclaimer legal review | ✅ **Decision 13** + F1 spec — demand-gated $2K cap; trigger: ≥5 users / 90d OR ≥1 user willing-pay ≥$49/mo OR Jessica override; affordance spec at `docs/specs/SIGNAL_STUDIO_PAID_INTEREST_SIGNAL_SPEC.md` | handoff Decision 13 + F1 |
| Q6 GTM channel | ✅ **Decision 15a** — (c) Direct outreach + Operator Edge cross-promo | handoff Decision 15a |
| Q7 Suite vs Lab positioning long-term | ✅ **Decision 4** — graduates to Suite at ≥$1K MRR sustained ≥2 months | handoff Decision 4 |

6 of 7 §9 items ratified; Q3 stays Chris queue (architecture). Brief now reads as the ratified Phase 1 source-of-truth for Signal Studio.
