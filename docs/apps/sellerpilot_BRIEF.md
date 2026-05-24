---
title: "SellerPilot — Phase 1 brief (products.ts-anchored)"
status: draft (Session 1135 discovery, pending Rigby review + Chris ratification)
session: 1135
generated: 2026-05-23
workspace: Donkey Betz
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md
  - apps/signal_studio_BRIEF.md
  - apps/compliancesentinel_BRIEF.md
  - apps/mentorforge_BRIEF.md
  - UDB_BEHAVIOR_LAYER.md
  - UDB_TRANSLATION_LAYER.md
source_of_truth: "24-7-ai-global/src/lib/products.ts LAB[2] (slug: sellerpilot)"
secondary_source: "/Users/donkeyking/development/sellerpilot/docs/PROJECT_WHAT_IT_IS.md"
authors: claude + jessica (discovery pass) → rigby (review pending)
---

# SellerPilot — Phase 1 brief

> **Source of truth:** `24-7-ai-global/src/lib/products.ts` LAB[2] (entry no. X). LAB tier — demo-ready, Stripe stubbed, pricing not locked. Brief proposes Phase 1 GTM additions on top of currently-demo-ready product.

## 1. What it is

**Tagline (per products.ts):** *"AI listing optimizer for Amazon, Etsy, Shopify."*

**Elevator (per products.ts):** *"GPT-driven listing optimization across the three big marketplaces. Sellers submit a product once; SellerPilot generates SEO titles, conversion-tuned bullets, descriptions, and pricing — then ranks variants for A/B testing. Demo seeded with 3 sample products; demo-mode fallback returns deterministic stub listings until an OpenAI key is connected."*

**Pillar:** Innovation. **Arc:** Optimize. **Tier:** LAB (entry no. X — alongside Signal Studio, Compliance Sentinel, context-kit, Character OS, Rigby).

**Phase 1 scope:** Cross-marketplace AI listing optimization — SEO titles, bullets, descriptions, pricing recommendations per marketplace policy. Variant A/B ranking. Batch product upload. Search-tag generation. Multi-marketplace policy-aware prompting.

**Status:** **demo-ready · Frontend Live** at https://sellerpilot-mu.vercel.app
**Repo:** https://github.com/clwest/sellerpilot
**Note (per products.ts):** "Demo login: demo@sellerpilot.dev / demo123. Render API Blueprint queued."

## 2. Who buys it

**Target (per products.ts):** Amazon FBA · multi-marketplace sellers · Etsy / Shopify ops.

**Concrete buyer profiles:**
- Amazon FBA seller managing 10-100+ SKUs, time-constrained on listing optimization
- Multi-marketplace seller cross-posting same product to Amazon / Etsy / Shopify, needs policy-aware copy per channel
- Etsy or Shopify ops lead optimizing for marketplace-specific search

**Buyer = User.** Self-serve when Stripe goes live (currently stubbed).

## 3. What's built (per products.ts — demo-ready today)

| Component | Status | Source |
|---|---|---|
| SEO title + bullet generation per marketplace | Shipped (demo) | products.ts features[0] |
| Variant scoring · A/B comparison · suggested pricing | Shipped (demo) | products.ts features[1] |
| Batch product upload · search tag generation | Shipped (demo) | products.ts features[2] |
| Multi-marketplace policy-aware prompting | Shipped (demo) | products.ts features[3] |
| Demo-mode fallback (deterministic stub listings without OpenAI key) | Shipped | products.ts elevator |
| Stack: FastAPI · React 19 · Vite · SQLite · Stripe (stubbed) | Shipped | products.ts stack |
| Demo seed (3 sample products) | Shipped | products.ts elevator |
| Production URL | Live (frontend) | https://sellerpilot-mu.vercel.app |
| Fleet runtime (localhost:8005 API, localhost:5177 web) | Live on local | Session 1126 |
| Render API Blueprint | **Queued, not deployed** | products.ts note |
| Stripe billing | **Stubbed** | products.ts stack |

## 4. What proves it's real

**Canonical proof:** Visit https://sellerpilot-mu.vercel.app → log in (demo@sellerpilot.dev / demo123) → submit product → SellerPilot generates SEO title + bullets + description + pricing per marketplace (Amazon / Etsy / Shopify) → variants ranked for A/B testing. Works in demo mode without OpenAI key (deterministic stubs); with key, GPT generates real optimizations.

**Local interim proof:** localhost:5177 (web) + localhost:8005/api/health (backend).

## 5. What's missing (gap to "selling at full GTM")

### Phase 0 gating items

| Item | Status | Effort |
|---|---|---|
| Render API Blueprint deployed (currently queued per products.ts note) | Not done | Small |
| Stripe SKU + checkout wired (currently stubbed per products.ts) | Not done | Medium |
| Pricing tier lock (no pricing block in products.ts for LAB tier) | Not done | Chris decision |
| Per-customer cost tracking (shared portfolio infra) | Not done | ~3 days shared |
| Daily $ cap per customer enforcement | Not done | ~1 day |

### What's NOT needed for Phase 1
- New product copy or audience reframing — products.ts already locks both.
- Stack changes — FastAPI · React 19 · Vite · SQLite is shipped.
- Marketplace coverage expansion (Amazon / Etsy / Shopify cover the "three big" per products.ts).

## 6. Buildable in one sprint?

**Phase 0 wrap (~1.5-2 weeks aggregate)** — bigger than Suite products because Stripe is stubbed and pricing not locked, but smaller than Rigby Phase 0 (no consumer-app build needed; frontend already live).

## 7. GTM sketch

> **⚠️ Pricing reality:** products.ts has **no pricing block** for SellerPilot (LAB tier, Stripe stubbed). Pricing tiers proposed below are Phase 1 GTM proposal, NOT currently in market.

| Lever | Plan |
|---|---|
| **Surface** | https://sellerpilot-mu.vercel.app (live frontend) + github.com/clwest/sellerpilot |
| **Tier classification** | LAB tier per products.ts. Could graduate to Suite if revenue thresholds hit. |
| **Pricing (proposed Phase 1 — Chris ratifies)** | Suggest Free / Pro / Team tiers — Free: 5 products/mo · single marketplace. Pro $29-49: Unlimited · all 3 marketplaces · variant A/B. Team $99-149: Multi-seat · API · batch ingestion at scale. **Chris locks actual price points.** |
| **Channel (proposed)** | Amazon FBA communities (Reddit r/AmazonFBA, Twitter), Etsy seller forums, Shopify partners directory. Direct outreach to multi-marketplace sellers with 10+ SKUs. |
| **CTA** | "Try demo free — generate listings without an account" → upgrade for unlimited + key marketplaces |
| **Disclaimers** | "AI-generated listings are starting points; review for marketplace policy compliance and brand voice before publishing. We do not guarantee marketplace acceptance or sales outcomes." |
| **Forbidden in product + marketing** | "Guaranteed Amazon best-seller" / specific sales-volume claims; "policy-compliant" without per-marketplace review process; comparison to specific competitor sellers. |

## 8. Spokesperson alignment (Phase 4+, parked)

Per Atlas §C.5: Character OS / avatar / voice = parked until paying customer demands a face. Phase 1 is text-only listing generation. Phase 4+ unlocks: persona-voiced product description audio (for video listings); avatar-led marketplace strategy walkthroughs.

## 9. Decisions still needed (escalate to Chris)

**Closed by products.ts as canonical:**
- ✅ Product framing locked per products.ts LAB[2]
- ✅ Target audience locked: Amazon FBA · multi-marketplace · Etsy/Shopify ops
- ✅ Status: demo-ready · Frontend Live
- ✅ Production URL: https://sellerpilot-mu.vercel.app
- ✅ Stack: FastAPI · React 19 · Vite · SQLite

**Still open for Chris:**

| # | Question | Why it matters |
|---|---|---|
| 1 | **Render API Blueprint deployment** — products.ts notes it's queued; ready to deploy? | Backend live = real Phase 1 launch |
| 2 | **Pricing lock** — no pricing block in products.ts; recommend Free / $29-49 Pro / $99-149 Team? | Required before any paid acquisition |
| 3 | **Stripe SKU wiring** — currently stubbed per products.ts. Path to live billing? | Revenue plumbing |
| 4 | **Phase 0 cost-attribution shared across portfolio** | Atlas-level requirement |
| 5 | **GTM channel pick** — Reddit r/AmazonFBA, Etsy forums, Shopify partners, direct outreach, or other? | Acquisition strategy |
| 6 | **Marketplace policy review** — who validates that our generated listings comply with Amazon/Etsy/Shopify TOS? | UPL-equivalent compliance risk |
| 7 | **Suite vs Lab positioning long-term** — products.ts treats as LAB today. Graduate to Suite if revenue thresholds hit? | Brand portfolio strategy |

## 10. Honest claim audit (per translation layer §2)

**We do NOT claim:**
- SellerPilot guarantees marketplace acceptance, search ranking, or sales outcomes.
- Specific number of paying customers.
- Backend API is deployed to Render (Blueprint is queued per products.ts note).
- Stripe billing is live (stubbed per products.ts).
- Pricing tiers are locked (no pricing block in products.ts).
- AI-generated listings are guaranteed policy-compliant per each marketplace's TOS.
- Any specific competitor comparison or sales-volume benchmark.

**We DO claim (per products.ts ground truth):**
- SellerPilot is demo-ready · Frontend Live at https://sellerpilot-mu.vercel.app.
- Demo login works: demo@sellerpilot.dev / demo123.
- Covers Amazon, Etsy, Shopify marketplaces.
- Generates SEO titles, conversion-tuned bullets, descriptions, pricing.
- Variant A/B ranking included.
- Batch product upload + search tag generation included.
- Demo-mode fallback returns deterministic stubs without OpenAI key.
- LAB tier classification (entry no. X, alongside Signal Studio, Compliance Sentinel, context-kit, Character OS, Rigby).
- Stack: FastAPI · React 19 · Vite · SQLite · Stripe (stubbed).
- Fleet runtime on local (localhost:8005 API, localhost:5177 web).
- Repo public: https://github.com/clwest/sellerpilot.

---

**Brief authored:** Session 1135 (Claude + Jessica discovery pass, products.ts-anchored).
**Source of truth:** `24-7-ai-global/src/lib/products.ts` LAB[2].
**Next step:** Jessica ratified §9 decisions in Session 1137 (2026-05-24) — see `docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md`.

## Session 1137 ratification status

| §9 Q | Status | Source |
|---|---|---|
| Q1 Render API Blueprint deployment | 🔧 Chris queue — ops decision | handoff Chris queue #6 |
| Q2 Pricing lock | ✅ **Decision 7** — Free + $39 Pro + $99 Team | handoff Decision 7 |
| Q3 Stripe SKU wiring | ✅ **Decision 10** — 2nd in sequence (Signal Studio → SellerPilot → ComplianceSentinel) | handoff Decision 10 |
| Q4 Phase 0 cost-attribution | ✅ **Decision 9** — portfolio rule covers SellerPilot | handoff Decision 9 |
| Q5 GTM channel pick | ✅ **Decision 15b** — (d) Sequenced: Reddit r/AmazonFBA first → direct outreach when ≥10 customers → Shopify Partner | handoff Decision 15b |
| Q6 Marketplace policy review | ⏸ Phase 5 #25 — Claude research + Jessica review | handoff Phase 5 queue |
| Q7 Suite vs Lab positioning long-term | ✅ **Decision 4** — graduates to Suite at ≥$1K MRR sustained ≥2 months | handoff Decision 4 |

6 of 7 §9 items ratified or queued; Q1 stays Chris queue (ops). Brief now reads as the ratified Phase 1 source-of-truth for SellerPilot.
