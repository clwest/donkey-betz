---
title: "Deal Flow Tracker — Phase 1 brief (products.ts-anchored)"
status: draft (Session 1135 discovery, pending Rigby review + Chris ratification)
session: 1135
generated: 2026-05-23
workspace: Donkey Betz
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md
  - apps/mentorforge_BRIEF.md
  - apps/pitchdeckforge_BRIEF.md
  - apps/contract_concierge_BRIEF.md
  - UDB_BEHAVIOR_LAYER.md
  - UDB_TRANSLATION_LAYER.md
source_of_truth: "24-7-ai-global/src/lib/products.ts PRODUCTS[3] (slug: dealflowtracker)"
authors: claude + jessica (discovery pass) → rigby (review pending)
---

# Deal Flow Tracker — Phase 1 brief

> **Source of truth:** `24-7-ai-global/src/lib/products.ts` PRODUCTS[3]. All product framing below traces back there.

## 1. What it is

**Tagline (per products.ts):** *"Kanban dealflow for angels and emerging funds."*

**Elevator (per products.ts):** *"Intake by public form or manual entry. Move deals through a six-stage pipeline, score on five dimensions, generate AI investment memos, and keep every contact, note, and stage change on one timeline. Built for funds that want institutional memory without hiring an analyst."*

**Pillar:** Intelligence. **Arc:** Grow. **Suite product #4** (no. IV).

**Phase 1 scope:** Kanban dealflow tracker — 6-stage pipeline, drag-to-move, public intake form, contact/note/stage-change timeline, 5-dimension scorecard (team · market · traction · moat · fit), AI investment memos generated from scorecard + deal data, pipeline analytics.

**Status:** **shipped, live at https://dealflowtracker.vercel.app**

## 2. Who buys it

**Target (per products.ts):** Angels · syndicates · $50M–$500M funds.

**Concrete buyer profiles:**
- Solo angel investor tracking 50-200 deals/year, needs institutional memory
- Syndicate lead managing rolling deal flow for LPs
- Emerging-fund GP ($50M-$500M AUM) without dedicated analyst headcount

**Buyer = User.** Self-serve via Stripe. Free starter; Pro/Fund self-upgrade.

## 3. What's built (per products.ts — shipped today)

| Component | Status | Source |
|---|---|---|
| 6-stage Kanban pipeline · drag to move | Shipped | products.ts features[0] |
| 5-dimension scorecard (team · market · traction · moat · fit) | Shipped | products.ts features[1] |
| AI investment memo from scorecard + deal data | Shipped | products.ts features[2] |
| Public submission form · contact mgmt · analytics | Shipped | products.ts features[3] |
| Three-tier billing (Starter / Pro / Fund) | Shipped | products.ts pricing block |
| Stack: React 19 · FastAPI · Postgres · OpenAI · Stripe-ready | Shipped | products.ts stack |
| Production URL | Live | https://dealflowtracker.vercel.app |
| Fleet runtime (localhost:8006 API, localhost:5178 web) | Live on local | Session 1126 |

## 4. What proves it's real

**Canonical proof:** Visit https://dealflowtracker.vercel.app → sign in → either use public intake form OR add deal manually → score deal on 5 dimensions → drag through 6-stage pipeline → generate AI investment memo from scorecard → keep contact/note timeline.

**Local interim proof:** localhost:5178 (web) + localhost:8006/api/health (backend).

## 5. What's missing (gap to "selling at full GTM")

### Phase 0 gating items

| Item | Status | Effort |
|---|---|---|
| Per-customer cost tracking (shared portfolio infra) | Not done | ~3 days shared |
| Daily $ cap per customer enforcement | Not done | ~1 day |
| Stripe SKU + webhook verification (Pro $39, Fund $99 per products.ts) | Verify status | Small |
| MentorForge Founder Project → DealFlowTracker handoff verification (mentor session can seed a deal) | Verify status | Small (integration smoke) |

### What's NOT needed for Phase 1
- New product copy or audience reframing — products.ts already locks both.
- Pricing — Free / $39 Pro / $99 Fund already locked in products.ts.
- Stack changes.

## 6. Buildable in one sprint?

**Phase 0 wrap (~1 week aggregate)** — small, because shipped. Same shape as MentorForge + PitchDeckForge + Contract Concierge.

## 7. GTM sketch

| Lever | Plan |
|---|---|
| **Surface** | https://dealflowtracker.vercel.app (shipped) + 24-7-ai-global studio site listing |
| **Pricing (per products.ts)** | Free Starter / $39 Pro / $99 Fund |
| **What's included per tier** | Starter Free: 10 deals · Kanban · scorecards. Pro $39: Unlimited · analytics · PDF memos. Fund $99: 10 seats · LP exports · API. |
| **CTA** | "Start free — 10 deals · full Kanban + scorecards" → upgrade to Pro for unlimited + PDF memos |
| **Cross-Suite hook** | MentorForge session can seed a deal in DealFlowTracker (per MentorForge spokesperson doc). |
| **Disclaimers** | "AI investment memos are starting points; deal decisions should rely on your full due-diligence process and applicable regulatory frameworks." |
| **Forbidden in product + marketing** | "Picks winners" / specific-return guarantees; "investment advice" framing; specific portfolio-performance comparisons. |

## 8. Spokesperson alignment (Phase 4+, parked)

Per Atlas §C.5: Character OS / avatar / voice = parked until paying customer demands a face. Phase 1 is text-only. Phase 4+ unlocks: AI-narrated memo readouts for LP review meetings; persona-voiced scorecard explanations for new analysts learning the framework.

## 9. Decisions still needed (escalate to Chris)

**Closed by products.ts as canonical:**
- ✅ Product framing locked per products.ts PRODUCTS[3]
- ✅ Pricing locked: Free / $39 Pro / $99 Fund
- ✅ Audience locked: Angels · syndicates · $50M-$500M funds
- ✅ Status: shipped
- ✅ Production URL: https://dealflowtracker.vercel.app
- ✅ 6-stage pipeline + 5-dim scorecard + AI memos

**Still open for Chris:**

| # | Question | Why it matters |
|---|---|---|
| 1 | **Stripe SKU + webhook verification** — Pro $39 + Fund $99 live in prod? | Reveals true Phase 0 effort for billing |
| 2 | **Phase 0 cost-attribution shared across portfolio** | Atlas-level requirement (5th product in shared infra need) |
| 3 | **MentorForge → DealFlowTracker handoff verification** — does mentor session correctly seed a deal? | Suite cross-product story |
| 4 | **LP exports (Fund tier)** — what format(s)? PDF / CSV / Excel / custom report? | Fund tier value-prop clarity |
| 5 | **API (Fund tier)** — exposed/documented for fund customers? Authentication model? | Enterprise sales motion |
| 6 | **Public intake form embedding** — can fund customers embed the public form on their own site/branded? | Distribution mechanic |

## 10. Honest claim audit (per translation layer §2)

**We do NOT claim:**
- Deal Flow Tracker provides investment advice, recommends specific deals, or predicts returns.
- Specific number of paying customers.
- Cross-Suite handoff (MentorForge → DealFlowTracker) is operational today without verification.
- LP exports include any specific format until Chris confirms (per §9 #4).
- API access for Fund tier is documented/SLA-supported (verify per §9 #5).

**We DO claim (per products.ts ground truth):**
- Deal Flow Tracker is shipped and live at https://dealflowtracker.vercel.app.
- 6-stage Kanban pipeline with drag-to-move.
- 5-dimension scorecard: team · market · traction · moat · fit.
- AI investment memo generated from scorecard + deal data.
- Public submission form + contact mgmt + analytics.
- Pricing: Free / $39 Pro / $99 Fund per products.ts.
- Pillar: Intelligence. Arc: Grow. Suite product #4.
- Stack: React 19 · FastAPI · Postgres · OpenAI · Stripe-ready.
- Fleet runtime on local (localhost:8006 API, localhost:5178 web).

---

**Brief authored:** Session 1135 (Claude + Jessica discovery pass, products.ts-anchored).
**Source of truth:** `24-7-ai-global/src/lib/products.ts` PRODUCTS[3].
**Next step:** Rigby review for honest framing. Then Chris ratifies the 6 open decisions in §9. Then brief becomes locked Phase 1 source-of-truth for Deal Flow Tracker.
