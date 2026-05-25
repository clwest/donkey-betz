---
title: "Mentor Forge — Phase 1 brief (products.ts-anchored)"
status: draft (Session 1135 discovery, pending Rigby review + Chris ratification)
originating_session: 1135
generated: 2026-05-23
workspace: Donkey Betz
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md
  - apps/contract_concierge_BRIEF.md
  - apps/pitchdeckforge_BRIEF.md
  - apps/dealflowtracker_BRIEF.md
  - apps/rigby_standalone_BRIEF.md
  - UDB_BEHAVIOR_LAYER.md
  - UDB_TRANSLATION_LAYER.md
source_of_truth: "24-7-ai-global/src/lib/products.ts PRODUCTS[0] (slug: mentorforge)"
secondary_source: "docs/spokesperson/10_mentorforge.md (editorial / spokesperson framing)"
authors: claude + jessica (discovery pass) → rigby (review pending)
---

# Mentor Forge — Phase 1 brief

> **Source of truth:** `24-7-ai-global/src/lib/products.ts` PRODUCTS[0] + `docs/spokesperson/10_mentorforge.md` (editorial). All product framing below traces back there.

## 1. What it is

**Tagline (per products.ts):** *"Eight AI mentors. Seven session modes. On demand."*

**Elevator (per products.ts):** *"Pick a mentor persona — code reviewer, system designer, mock interviewer, build planner — and run a session in the mode that fits. Compounds into a Founder Project that flows into the rest of the kit: brief Pitch Deck Forge, prefill a Contract Concierge agreement, seed a Deal Flow Tracker deal."*

**Pillar:** Impact. **Arc:** Mentor. **Suite product #1** (no. I).

**Phase 1 scope:** Eight mentor personas × seven session modes; each session writes to a Founder Project that exports to Pitch Deck Forge, Contract Concierge, and Deal Flow Tracker. Mentor isn't a generic chatbot — it's a persona with a session mode, and the session leaves an artifact behind.

**Status:** **shipped, live at https://mentorforge.vercel.app**

## 2. Who buys it

**Target (per products.ts):** Engineers · founders · architects.

**Per spokesperson doc (`docs/spokesperson/10_mentorforge.md`):** *"working alone or in small teams who need a thinking partner that doesn't keep office hours."*

**Buyer = User.** Self-serve via Stripe. Free tier available; Pro/Enterprise self-upgrade.

## 3. What's built (per products.ts — shipped today)

| Component | Status | Source |
|---|---|---|
| 8 mentor personas · 7 session modes | Shipped | products.ts features |
| Session modes: Freeform · code review · system design · mock interview · guided lessons · debugging · build planning | Shipped | products.ts features (spokesperson doc enumerates) |
| Founder Projects (session → project artifact) | Shipped | products.ts elevator + spokesperson doc |
| Cross-Suite export: Pitch Deck Forge · Contract Concierge · Deal Flow Tracker | Shipped | products.ts features[3] |
| Three-tier billing (Free / Pro / Enterprise) | Shipped | products.ts pricing block |
| Stack: React 19 · FastAPI · Postgres · OpenAI · Stripe-ready | Shipped | products.ts stack |
| Production URL | Live | https://mentorforge.vercel.app |
| Fleet runtime (localhost:8002 API, localhost:5174 web) | Live on local | Session 1126 |

## 4. What proves it's real

**Canonical proof:** Visit https://mentorforge.vercel.app → sign in → pick mentor persona + session mode → run session → session writes to Founder Project → export to Pitch Deck Forge / Contract Concierge / Deal Flow Tracker.

**Local interim proof:** localhost:5174 (web) + localhost:8002/api/health (backend).

## 5. What's missing (gap to "selling at full GTM")

### Phase 0 gating items

| Item | Status | Effort |
|---|---|---|
| Per-customer cost tracking (`LLMCallLog.workspace` FK, shared portfolio infra) | Not done | ~3 days shared |
| Daily $ cap per customer enforcement | Not done | ~1 day |
| Stripe SKU + webhook verification (Pro $39, Enterprise $99 per products.ts) | Verify status | Small |
| Cross-Suite Founder Project handoff verification (works end-to-end across all 4 Suite products) | Verify status | Small (integration smoke) |

### What's NOT needed for Phase 1
- New product copy or audience reframing — products.ts already locks both.
- Pricing — Free / $39 Pro / $99 Enterprise already locked in products.ts.
- Stack changes — React 19 · FastAPI · Postgres · OpenAI · Stripe-ready per products.ts.

## 6. Buildable in one sprint?

**Phase 0 wrap (~1 week aggregate)** — small, because shipped. Same shape as Contract Concierge: verify + cost/cap infra (shared with portfolio) + Stripe SKU verify.

## 7. GTM sketch

| Lever | Plan |
|---|---|
| **Surface** | https://mentorforge.vercel.app (shipped) + 24-7-ai-global studio site listing |
| **Pricing (per products.ts)** | Free / $39 Pro / $99 Enterprise |
| **What's included per tier** | Free: Limited sessions · 3 mentors. Pro $39: All mentors · all 7 modes. Enterprise $99: Team seats · custom personas. |
| **CTA** | "Start free — 3 mentors · limited sessions" → upgrade to Pro for full access |
| **Cross-Suite hook** | Sessions export to Pitch Deck Forge / Contract Concierge / Deal Flow Tracker (per products.ts elevator). |
| **Disclaimers** | "Mentor personas are AI assistants, not licensed professionals. For mock interviews, system design, and code review use cases — not for legal, medical, or financial advice." |
| **Forbidden in product + marketing** | Per spokesperson doc: do not invent mentor personas (8 fixed) or session modes (7 fixed); do not promise hand-offs outside Suite of 4; do not improvise pricing. |

## 8. Spokesperson alignment (Phase 4+, parked)

Per Atlas §C.5: Character OS / avatar / voice = parked until paying customer demands a face. Phase 1 is text-only. Phase 4+ unlocks persona-voiced mentor sessions (each of the 8 personas could get a distinct voice/avatar).

## 9. Decisions still needed (escalate to Chris)

**Closed by products.ts + spokesperson doc as canonical:**
- ✅ Product framing locked per products.ts PRODUCTS[0]
- ✅ Pricing locked: Free / $39 Pro / $99 Enterprise
- ✅ Audience locked: Engineers · founders · architects
- ✅ Status: shipped
- ✅ Production URL: https://mentorforge.vercel.app
- ✅ Off-limits language locked per spokesperson doc

**Still open for Chris:**

| # | Question | Why it matters |
|---|---|---|
| 1 | **Stripe SKU + webhook verification** — Pro $39 + Enterprise $99 live in prod? | Reveals true Phase 0 effort for billing |
| 2 | **Phase 0 cost-attribution shared across portfolio** (Rigby + Contract Concierge + Signal Studio + MentorForge + PitchDeckForge + DealFlowTracker) | Atlas-level requirement |
| 3 | **Cross-Suite handoff verification** — does session → Founder Project → export flow work end-to-end to PitchDeckForge / ContractConcierge / DealFlowTracker today? | Core differentiator per products.ts elevator |
| 4 | **Mentor persona inventory** — spokesperson doc says 8 personas but names them as not-for-spokesperson-enumeration. Are persona names locked + published anywhere? | Marketing copy may need persona names |
| 5 | **Operator Edge cross-promo** — when Operator Edge launches as paid channel, surface MentorForge in sponsor placements? | Acquisition channel |

## 10. Honest claim audit (per translation layer §2)

**We do NOT claim:**
- Mentor personas are licensed professionals.
- Specific number of paying customers (verify separately).
- That cross-Suite handoffs (session → PitchDeckForge / ContractConcierge / DealFlowTracker) work end-to-end in current production (verify per §9 decision #3).
- Mentor persona names beyond the products.ts features list (spokesperson doc explicitly forbids enumerating personas not on public marketing).
- Session mode count beyond the 7 listed (per spokesperson doc forbid).

**We DO claim (per products.ts ground truth):**
- Mentor Forge is shipped and live at https://mentorforge.vercel.app.
- 8 mentor personas × 7 session modes.
- Session modes include: Freeform, code review, system design, mock interview, guided lessons, debugging, build planning.
- Sessions write to Founder Projects (per products.ts elevator).
- Pricing tiers: Free / $39 Pro / $99 Enterprise per products.ts.
- Pillar: Impact. Arc: Mentor. Suite product #1.
- Stack: React 19 · FastAPI · Postgres · OpenAI · Stripe-ready.
- Fleet runtime on local (localhost:8002 API, localhost:5174 web).

---

**Brief authored:** Session 1135 (Claude + Jessica discovery pass, products.ts-anchored).
**Source of truth:** `24-7-ai-global/src/lib/products.ts` PRODUCTS[0] + `docs/spokesperson/10_mentorforge.md`.
**Next step:** Jessica ratified §9 decisions in Session 1137 (2026-05-24) — see `docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md`.

## Session 1137 ratification status

| §9 Q | Status | Source |
|---|---|---|
| Q1 Stripe SKU + webhook verification | ⏸ Phase 5 F7 — audit on Stripe (Jessica + Chris's access) | handoff Phase 5 queue |
| Q2 Phase 0 cost-attribution shared across portfolio | ✅ **Decision 9** — portfolio rule covers MentorForge | handoff Decision 9 |
| Q3 Cross-Suite handoff verification | ⏸ Phase 5 #23 — Jessica drives E2E matrix | handoff Phase 5 queue |
| Q4 Mentor persona inventory — locked + published | ✅ **Decision 18** + F3 — (a) Stay functional types (code reviewer, system designer, etc.); no individual or famous-style names; F3 fixed BUILD_PLAN.md 12-vs-8 drift | handoff Decision 18 + F3 |
| Q5 Operator Edge cross-promo | ✅ **Decision 16** — (b+d) Inline-only now; rotated paid placements when Operator Edge ≥2K subscribers | handoff Decision 16 |

5 of 5 §9 items ratified or queued. Brief now reads as the ratified Phase 1 source-of-truth for Mentor Forge.
