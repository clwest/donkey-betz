---
title: "ComplianceSentinel — Phase 1 brief (products.ts-anchored)"
status: draft (Session 1135 discovery, pending Rigby review + Chris ratification)
session: 1135
generated: 2026-05-23
workspace: Donkey Betz
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md
  - apps/sellerpilot_BRIEF.md
  - apps/signal_studio_BRIEF.md
  - apps/contract_concierge_BRIEF.md
  - UDB_BEHAVIOR_LAYER.md
  - UDB_TRANSLATION_LAYER.md
source_of_truth: "24-7-ai-global/src/lib/products.ts LAB[4] (slug: compliancesentinel)"
secondary_source: "/Users/donkeyking/development/compliancesentinel/README.md"
authors: claude + jessica (discovery pass) → rigby (review pending)
---

# ComplianceSentinel — Phase 1 brief

> **Source of truth:** `24-7-ai-global/src/lib/products.ts` LAB[4] (entry no. XII). LAB tier — demo-ready, Stripe stubbed, pricing not locked. Brief proposes Phase 1 GTM additions on top of currently-demo-ready product.

## 1. What it is

**Tagline (per products.ts):** *"Regulatory monitoring with AI-drafted compliance memos."*

**Elevator (per products.ts):** *"An alerting + memo engine for compliance officers. RSS and news sources flow in, severity-tiered alerts route to assignees, and GPT-4 drafts one-page compliance review memos with evidence quotes and recommended actions. Demo-mode fallback returns a structured memo with the alert's actual evidence quotes whenever an OpenAI key isn't connected."*

**Pillar:** Intelligence. **Arc:** Guard. **Tier:** LAB (entry no. XII — alongside Signal Studio, SellerPilot, context-kit, Character OS, Rigby).

**Phase 1 scope:** Regulatory feed monitoring + alerting + AI compliance memo generation. Multi-source RSS / news ingestion. Severity-tiered alerts routed to assignees. GPT-4 drafted memos with evidence quotes and recommended actions. Demo-mode fallback works without OpenAI key.

**Status:** **demo-ready · Frontend Live** at https://compliancesentinel.vercel.app
**Repo:** https://github.com/clwest/compliancesentinel
**Note (per products.ts):** "Generates evidence-grounded memos with or without an OpenAI key. Render API Blueprint queued."

## 2. Who buys it

**Target (per products.ts):** Compliance officers · legal counsel · risk analysts.

**Concrete buyer profiles:**
- Compliance officer at SMB / mid-market firm without dedicated regulatory intelligence headcount
- In-house legal counsel managing compliance review backlog
- Risk analyst tracking sector-specific regulatory changes (finance / healthcare / SaaS / etc.)

**Buyer = User** for individual contributor tier; **buyer ≠ user** for team/enterprise tier (procurement / IT decision).

## 3. What's built (per products.ts — demo-ready today)

| Component | Status | Source |
|---|---|---|
| Multi-source feed ingestion · active/inactive toggle | Shipped (demo) | products.ts features[0] |
| Severity-tiered alerts · assignment · due dates | Shipped (demo) | products.ts features[1] |
| AI compliance memos with evidence quotes | Shipped (demo) | products.ts features[2] |
| Audit trail · status lifecycle · org scoping | Shipped (demo) | products.ts features[3] |
| Demo-mode fallback (structured memo with evidence quotes, no OpenAI key required) | Shipped | products.ts elevator |
| Stack: FastAPI · React 19 · Vite · SQLite · OpenAI · Stripe (stubbed) | Shipped | products.ts stack |
| Production URL | Live (frontend) | https://compliancesentinel.vercel.app |
| Fleet runtime (localhost:8008 API, localhost:5180 web) | Live on local | Session 1126 |
| Render API Blueprint | **Queued, not deployed** | products.ts note |
| Stripe billing | **Stubbed** | products.ts stack |
| u-d-b fleet routing default | **`null` (intentionally disabled)** | Session 1128 routing config |

## 4. What proves it's real

**Canonical proof:** Visit https://compliancesentinel.vercel.app → log in → connect RSS/news source → ingest alerts → severity-tier triages auto-routes to assignee → AI compliance memo drafted with evidence quotes + recommended actions → audit-trail logged. Demo mode works without OpenAI key (structured memo from evidence quotes).

**Local interim proof:** localhost:5180 (web) + localhost:8008/api/health (backend).

## 5. What's missing (gap to "selling at full GTM")

### Phase 0 gating items

| Item | Status | Effort |
|---|---|---|
| Render API Blueprint deployed (currently queued per products.ts note) | Not done | Small |
| Stripe SKU + checkout wired (currently stubbed per products.ts) | Not done | Medium |
| Pricing tier lock (no pricing block in products.ts for LAB tier) | Not done | Chris decision |
| u-d-b fleet routing — currently `null` per Session 1128 (intentionally disabled). Decide: route to `security_agent` (named in `config/fleet_agent_routing.json:23` roles), keep `null`, or skip u-d-b integration entirely | Chris decision | ~1-3 days depending on path |
| Per-customer cost tracking (shared portfolio infra) | Not done | ~3 days shared |
| Daily $ cap per customer enforcement | Not done | ~1 day |
| Per-org data isolation verification (multi-tenant compliance data is sensitive) | Verify | ~2-3 days verify + harden |
| Legal review for compliance-product disclaimers + data-handling commitments | Not done | ~$1-3K legal time |

### What's NOT needed for Phase 1
- New product copy or audience reframing — products.ts already locks both.
- Stack changes — FastAPI · React 19 · Vite · SQLite is shipped.

## 6. Buildable in one sprint?

**Phase 0 wrap (~2-3 weeks aggregate)** — middle-ground effort. Bigger than Suite products (Stripe stubbed + pricing unlocked + multi-tenant compliance hardening) but smaller than Rigby/CFL Concierge Phase 0.

## 7. GTM sketch

> **⚠️ Pricing reality:** products.ts has **no pricing block** for ComplianceSentinel (LAB tier, Stripe stubbed). Pricing tiers below are Phase 1 GTM proposal.

| Lever | Plan |
|---|---|
| **Surface** | https://compliancesentinel.vercel.app (live frontend) + github.com/clwest/compliancesentinel |
| **Tier classification** | LAB tier per products.ts. Could graduate to Suite if revenue thresholds hit. |
| **Pricing (proposed Phase 1 — Chris ratifies)** | Suggest Free / Pro / Team tiers — Free: 1 feed · 10 alerts/mo. Pro $49-79: Unlimited feeds · all alerts · AI memos. Team $149-249: Multi-seat · custom regulatory sources · API + audit export. **Chris locks actual price points** (compliance buyers often have higher willingness-to-pay than retail SaaS). |
| **Channel (proposed)** | Compliance officer communities (e.g., Compliance Week, ABA tech committees, sector-specific Slack groups), direct outreach to in-house counsel at SMB / mid-market, partner with compliance consulting firms. Slower sales cycle than retail SaaS. |
| **CTA** | "Try demo free — see how AI memos work with sample regulatory alerts" → upgrade for unlimited feeds + AI memos |
| **Disclaimers** | "AI compliance memos are starting points; final compliance decisions and filings should be reviewed by qualified legal counsel and compliance professionals. Not legal advice. Not a substitute for licensed regulatory expertise." |
| **Forbidden in product + marketing** | "Guaranteed compliance" / "audit-proof" claims; specific regulatory-outcome guarantees; "replaces legal counsel" framing; specific competitor comparisons. |

## 8. Spokesperson alignment (Phase 4+, parked)

Per Atlas §C.5: Character OS / avatar / voice = parked until paying customer demands a face. Phase 1 is text-only memo drafting. Phase 4+ unlocks: AI-narrated memo readouts for compliance committee meetings; persona-voiced regulatory-update briefings for non-compliance staff training.

## 9. Decisions still needed (escalate to Chris)

**Closed by products.ts as canonical:**
- ✅ Product framing locked per products.ts LAB[4]
- ✅ Target audience locked: Compliance officers · legal counsel · risk analysts
- ✅ Status: demo-ready · Frontend Live
- ✅ Production URL: https://compliancesentinel.vercel.app
- ✅ Stack: FastAPI · React 19 · Vite · SQLite · OpenAI · Stripe (stubbed)

**Still open for Chris:**

| # | Question | Why it matters |
|---|---|---|
| 1 | **Render API Blueprint deployment** — products.ts notes it's queued; ready to deploy? | Backend live = real Phase 1 launch |
| 2 | **Pricing lock** — no pricing block in products.ts; recommend Free / $49-79 Pro / $149-249 Team? | Required before any paid acquisition; compliance customers tolerate higher prices |
| 3 | **Stripe SKU wiring** — currently stubbed per products.ts | Revenue plumbing |
| 4 | **Fleet routing decision** — `null` today (Session 1128 intentionally disabled). Route to `security_agent`, keep null, or skip u-d-b integration? | Determines whether the products.ts product uses u-d-b agents or stays on its own pipeline |
| 5 | **Phase 0 cost-attribution shared across portfolio** | Atlas-level requirement |
| 6 | **Multi-tenant org isolation verification** — compliance data is highly sensitive; needs hardening before any paid org customer | Privacy / trust gate |
| 7 | **Legal review** for compliance-product disclaimers + data-handling commitments (~$1-3K legal) | Required before launching to compliance customers |
| 8 | **GTM channel pick** — compliance communities, direct outreach to in-house counsel, partner with consulting firms? | Slower sales cycle than retail SaaS |
| 9 | **Suite vs Lab positioning long-term** — products.ts treats as LAB today. Graduate to Suite if revenue thresholds hit? | Brand portfolio strategy |

## 10. Honest claim audit (per translation layer §2)

**We do NOT claim:**
- ComplianceSentinel provides legal advice or licensed regulatory expertise.
- AI compliance memos are guaranteed accurate, complete, or audit-defensible.
- Specific number of paying customers.
- Backend API is deployed to Render (Blueprint is queued per products.ts note).
- Stripe billing is live (stubbed per products.ts).
- Pricing tiers are locked (no pricing block in products.ts).
- u-d-b agent integration is wired (fleet routing currently `null` per Session 1128).
- Multi-tenant compliance data isolation is hardened (verify per §9 #6).
- SOC 2, HIPAA, or other enterprise compliance certifications.

**We DO claim (per products.ts ground truth):**
- ComplianceSentinel is demo-ready · Frontend Live at https://compliancesentinel.vercel.app.
- Multi-source feed ingestion + severity-tiered alerts + AI memos + audit trail are shipped.
- Demo-mode fallback returns structured memos with evidence quotes (no OpenAI key required).
- LAB tier classification (entry no. XII, alongside Signal Studio, SellerPilot, context-kit, Character OS, Rigby).
- Stack: FastAPI · React 19 · Vite · SQLite · OpenAI · Stripe (stubbed).
- Fleet runtime on local (localhost:8008 API, localhost:5180 web).
- Repo public: https://github.com/clwest/compliancesentinel.

---

**Brief authored:** Session 1135 (Claude + Jessica discovery pass, products.ts-anchored).
**Source of truth:** `24-7-ai-global/src/lib/products.ts` LAB[4].
**Next step:** Jessica ratified §9 decisions in Session 1137 (2026-05-24) — see `docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md`.

## Session 1137 ratification status

| §9 Q | Status | Source |
|---|---|---|
| Q1 Render API Blueprint deployment | 🔧 Chris queue — ops decision | handoff Chris queue #7 |
| Q2 Pricing lock | ✅ **Decision 8** — Free + $79 Pro + $249 Team (deliberately above portfolio norm for compliance market) | handoff Decision 8 |
| Q3 Stripe SKU wiring | ✅ **Decision 10** — 3rd in sequence (Signal Studio → SellerPilot → ComplianceSentinel) | handoff Decision 10 |
| Q4 Fleet routing decision | 🔧 Chris queue — architecture decision (security_agent / null / skip u-d-b) | handoff Chris queue #3 |
| Q5 Phase 0 cost-attribution | ✅ **Decision 9** — portfolio rule covers ComplianceSentinel | handoff Decision 9 |
| Q6 Multi-tenant org isolation verification | ⏸ Phase 5 #26 — Chris-led security audit | handoff Phase 5 queue |
| Q7 Legal review | ✅ **Decision 14** — (b) Pre-approve $3K cap; deploy on Stripe-ready (compliance market makes demand-gate impractical) | handoff Decision 14 |
| Q8 GTM channel pick | ✅ **Decision 15c** — (e) Sequenced: Content + Communities first (compliance buyers buy on authority) | handoff Decision 15c |
| Q9 Suite vs Lab positioning long-term | ✅ **Decision 4** — graduates to Suite at ≥$1K MRR sustained ≥2 months | handoff Decision 4 |

7 of 9 §9 items ratified or queued; Q1 + Q4 stay Chris queue. Brief now reads as the ratified Phase 1 source-of-truth for ComplianceSentinel.
