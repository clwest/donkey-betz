---
title: "Contract Concierge — Phase 1 brief (products.ts-anchored)"
status: draft (Session 1135 discovery, rewritten post-products.ts discovery, pending Rigby review + Chris ratification)
session: 1135
generated: 2026-05-23
revised: 2026-05-23 (rewritten — supersedes Colorado Family Law Concierge brief which was based on engine-mismatch misread)
workspace: Donkey Betz
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md
  - specs/FLEET_CAPABILITY_BUSINESS_SPEC.md
  - apps/colorado_family_law_concierge_FUTURE_CONCEPT.md
  - apps/rigby_standalone_BRIEF.md
  - apps/signal_studio_BRIEF.md
  - UDB_BEHAVIOR_LAYER.md
  - UDB_TRANSLATION_LAYER.md
source_of_truth: "24-7-ai-global/src/lib/products.ts PRODUCTS[2] (slug: contract-concierge)"
authors: claude + jessica (discovery pass) → rigby (review pending)
---

# Contract Concierge — Phase 1 brief

> **Source of truth:** `24-7-ai-global/src/lib/products.ts` PRODUCTS[2]. All product-positioning claims below trace back there. This brief captures Phase-1 GTM additions + Phase-0 gaps against current shipping state.

## 1. What it is

**Phase 1 customer-facing pitch** (per products.ts):

> *"Templates to e-signed and archived — no lawyers required."*

**Elevator** (per products.ts): *"Pick a template (SOW · Contractor · NDA), fill a guided form with live preview, add signers, send. Unique signing links per recipient, full audit trail with IP and user-agent stamps, optional AI clause explanations. Works end-to-end with zero AI or email required — both are optional layers."*

**Pillar:** Automation. **Arc:** Execute. **No.:** III (Suite product #3).

**Phase 1 scope: commercial contracts, multi-signer e-signature workflow with audit trail.** The product produces signed, archived contracts (SOW / Contractor / NDA) end-to-end without requiring lawyer involvement. AI and email are *optional layers*; the core workflow runs without either.

**Status:** **shipped, live at https://contract-concierge.vercel.app**

## 2. Who buys it

**Primary target (per products.ts):** Solo founders · freelancers · SMB legal.

Three concrete use cases:
- **Solo founder** signing contractor agreements without engaging counsel for each
- **Freelancer** sending SOWs to clients with auditable e-signature
- **SMB legal/ops lead** standardizing template-driven contract workflows across a small team

**Buyer = User** (self-serve via Stripe). Free tier exists; Pro/Business tiers self-upgrade.

## 3. What's built (per products.ts — shipped today)

| Component | Status | Source |
|---|---|---|
| Three templates: SOW · Contractor · NDA | Shipped | products.ts features[0] |
| Live HTML preview · multi-signer flow | Shipped | products.ts features[1] |
| E-signature with IP · UA · timestamp audit trail | Shipped | products.ts features[2] |
| Optional AI layer: explain · tighten · custom clauses | Shipped (optional) | products.ts features[3] |
| Stripe-ready checkout (Free / Pro / Business tiers) | Shipped | products.ts pricing block |
| Production URL | Live | https://contract-concierge.vercel.app |
| Stack: React 19 · FastAPI · Postgres · Gmail SMTP · Stripe-ready | Shipped | products.ts stack |
| Fleet runtime (localhost:8003 API, localhost:5175 web, fleet-net) | Live on local | Session 1126 + 1129 |
| Draft Library + artifact persistence + per-user isolation | Live on local (Session 1129) | u-d-b PA dispatch via `legal_doc_drafter_agent` (engine wiring detail — see §5 NOTE) |

## 4. What proves it's real

**Canonical proof:** Visit https://contract-concierge.vercel.app → sign in → pick template (SOW / Contractor / NDA) → fill guided form with live preview → add signers → send → recipients use unique signing links → contract gets IP + UA + timestamp audit trail → archived.

**Today's interim proof on local:** localhost:5175 (web) + localhost:8003/api/health (backend). Session 1129 Draft Library flow verifiable end-to-end.

## 5. What's missing (gap to "selling at full GTM")

### NOTE on the fleet routing engine

The fleet routing default for `contract-concierge` in `config/fleet_agent_routing.json:10` is `legal_doc_drafter_agent`, which is purpose-built for Colorado family law (per `core/prompts/tool_descriptions.py:449`). **This is a wiring detail that does NOT reflect what the product is**, and was the source of an early session-1135 misread (see `docs/apps/colorado_family_law_concierge_FUTURE_CONCEPT.md` for that exploration).

The actual Contract Concierge product produces commercial-contract artifacts via its own backend pipeline; the u-d-b PA dispatch through `legal_doc_drafter_agent` covers a specific draft-library flow added in Session 1129. **Phase 0 task: route Contract Concierge to a commercial-contract agent (likely a new `contract_drafter_agent` or extend an existing one) instead of `legal_doc_drafter_agent`** to remove the mismatch.

### Phase 0 gating items

| Item | Status | Effort | Why gating |
|---|---|---|---|
| Fleet routing default updated from `legal_doc_drafter_agent` to a commercial-contract agent (or extend the legal agent's scope) | Not done | ~1-3 days depending on path | Removes engine-mismatch; aligns u-d-b routing with the shipped product |
| Per-customer cost tracking (`LLMCallLog.workspace` FK, shared with rest of portfolio) | Not done | ~3 days shared | Atlas Phase 0 gating for any paid product |
| Daily $ cap per customer enforcement | Not done | ~1 day | Same |
| Stripe SKU configured for Pro / Business tiers per products.ts pricing | Verify status | Small | products.ts marks as "Stripe-ready" — need confirm webhook/SKU wired |
| TOS + privacy policy + e-signature legal review | Verify status | Legal time | E-signature regulatory exposure (ESIGN Act / UETA) |

### What's NOT needed for Phase 1

- New product copy or audience reframing — products.ts already locks both.
- New pricing — Free / $29 / $79 tiers already locked in products.ts pricing block.
- Email infrastructure — Gmail SMTP already in stack per products.ts.
- AI features — explicitly *optional* per products.ts elevator ("Works end-to-end with zero AI or email required").

## 6. Buildable in one sprint?

**Phase 0 wrap (~1-2 weeks aggregate)** — much smaller than Rigby or Signal Studio Phase 0 because the product is already shipped.

Per-item:
- Fleet routing update: **SMALL-MEDIUM** (~1-3 days)
- Cost tracking + cap (shared infra): **MEDIUM** (~1 week, shared)
- Stripe SKU verify: **SMALL**
- TOS + e-sign legal review: **SMALL** (review only — TOS likely exists)

## 7. GTM sketch

| Lever | Plan (per products.ts where defined) |
|---|---|
| **Channel** | *Proposed (pending Chris greenlight):* paid ads + warm/personal network + Operator Edge integration. Contract Concierge URL surfaces on `247globalai.com/suite` per Atlas Suite framing. |
| **Pricing** | Per products.ts: **Free / $29 Pro / $79 Business** |
| **What's included per tier** | Free: 3 contracts/mo · NDA + LOI. Pro $29: Unlimited · all templates · e-sign. Business $79: 10 seats · template builder · API. |
| **CTA** | "Start free — 3 contracts/mo, no credit card" → upgrade to Pro for unlimited |
| **Customer-facing surface** | https://contract-concierge.vercel.app (shipped) |
| **Disclaimers** | "Not legal advice — templates are starting points; consult a licensed attorney for matters with significant stakes." Per Atlas + UDB_BEHAVIOR_LAYER. |
| **Forbidden in product + marketing** | "Replaces a lawyer" (it doesn't — it's template-based with optional AI clause explanation); guaranteed legal outcomes; jurisdiction-specific legal opinions. |
| **Execution posture** | Read + draft + send (multi-signer) + archive. Customer signs and sends; e-signature happens via unique recipient links. |

## 8. Spokesperson alignment (Phase 4+, parked)

Per Atlas §C.5: Character OS / avatar / voice = parked until paying customer demands a face. Phase 1 is text-only (web + email). Phase 4+ unlocks:
- Persona-narrated walkthrough videos ("Here's how to send your first SOW")
- Brand-voice-locked avatar variants for white-label deployments

## 9. Decisions still needed (escalate to Chris)

**Closed by products.ts as canonical source of truth:**
- ✅ **Product framing** — locked per products.ts PRODUCTS[2]
- ✅ **Pricing** — Free / $29 / $79 per products.ts pricing block
- ✅ **Audience** — Solo founders · freelancers · SMB legal per products.ts target
- ✅ **Status** — shipped per products.ts status
- ✅ **Production URL** — https://contract-concierge.vercel.app

**Still open for Chris:**

| # | Question | Why it matters |
|---|---|---|
| 1 | **Fleet routing fix path** — route to new `contract_drafter_agent` OR extend `legal_doc_drafter_agent` scope OR remove the default and use the app's own pipeline? | Removes engine-mismatch; ~1-3 days depending on path |
| 2 | **Stripe SKU verification** — Pro $29 + Business $79 webhooks live in prod? | Reveals true Phase 0 effort for billing plumbing |
| 3 | **Phase 0 cost-attribution shared with Rigby + Signal Studio** | Atlas-level requirement; applies to all paid products |
| 4 | **TOS + e-signature legal review status** — done, in progress, or needed? | E-signature law (ESIGN Act / UETA) compliance |
| 5 | **Colorado Family Law Concierge as Phase 2+ spin-off concept** — explore further (per `colorado_family_law_concierge_FUTURE_CONCEPT.md`), park, or kill? | The engine exists; the concept is real but separate from this product |
| 6 | **Operator Edge → Suite cross-promo strategy** | When Operator Edge launches as a paid channel, Contract Concierge surface in its sponsor placements? |

## 10. Honest claim audit (per translation layer §2)

**We do NOT claim:**
- Contract Concierge provides legal advice or attorney representation.
- Generated contracts are jurisdiction-specific or guaranteed to enforce.
- Replacement for a licensed attorney for matters with significant stakes.
- A specific paying-customer count (verify status separately).
- The fleet routing default in `config/fleet_agent_routing.json:10` matches the product's actual agent needs (it doesn't — see §5 NOTE).
- AI features are required (they're explicitly optional per products.ts).
- Email delivery is required (Gmail SMTP is in stack but the workflow is described as zero-email-required-optional per products.ts).
- International e-signature compliance beyond US (verify regulatory scope per market expansion).
- HIPAA, SOC 2, or other enterprise compliance certifications.

**We DO claim (per products.ts ground truth):**
- Contract Concierge is shipped and live at https://contract-concierge.vercel.app.
- Three commercial-contract templates ship: SOW, Contractor, NDA.
- Multi-signer e-signature with IP, UA, timestamp audit trail is included.
- Live HTML preview of generated contracts is included.
- Pricing tiers per products.ts: Free / $29 Pro / $79 Business.
- Pillar: Automation. Arc: Execute. Suite product #3.
- Stack: React 19 · FastAPI · Postgres · Gmail SMTP · Stripe-ready.
- Fleet runtime on local (localhost:8003 API, localhost:5175 web).
- Draft Library + artifact persistence + per-user isolation works on local per Session 1129.

---

**Brief authored:** Session 1135 (Claude + Jessica discovery pass, rewritten post-products.ts discovery).
**Supersedes:** The earlier `colorado_family_law_concierge_BRIEF.md` (renamed to `_FUTURE_CONCEPT.md`) which was based on the legal_doc_drafter_agent engine-mismatch misread.
**Source of truth:** `24-7-ai-global/src/lib/products.ts` PRODUCTS[2].
**Next step:** Jessica ratified §9 decisions in Session 1137 (2026-05-24) — see `docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md`.

## Session 1137 ratification status

| §9 Q | Status | Source |
|---|---|---|
| Q1 Fleet routing fix path | 🔧 Chris queue — architecture decision (new agent / extend / remove) | handoff Chris queue #1 |
| Q2 Stripe SKU verification | ⏸ Phase 5 F7 — audit on Stripe (Jessica + Chris's access) | handoff Phase 5 queue |
| Q3 Phase 0 cost-attribution | ✅ **Decision 9** — portfolio rule covers Contract Concierge | handoff Decision 9 |
| Q4 TOS + e-signature legal review status | ⏸ Phase 5 #24 — Jessica pings lawyer | handoff Phase 5 queue |
| Q5 Colorado Family Law Concierge spin-off | ✅ **Decision 3** — (b) Park until portfolio >$5K MRR OR active vertical-add decision | handoff Decision 3 |
| Q6 Operator Edge cross-promo | ✅ **Decision 16** — (b+d) Inline-only now; rotated paid placements when Operator Edge ≥2K subscribers | handoff Decision 16 |

4 of 6 §9 items ratified or queued; Q1 stays Chris queue (architecture). Brief now reads as the ratified Phase 1 source-of-truth for Contract Concierge.
