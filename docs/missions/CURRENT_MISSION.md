<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md).
> **Note:** Draft refresh in flight — Session 1143 update. Content below replaces the Session 814 "$10K MRR by Q1 2026" framing with the 24/7 Global AI Suite framing locked by the Atlas (v1) + Jessica's Phase 1–4 ratification (Sessions 1137/1141). **Requires Chris sign-off** before considered locked; see § Decision Needed at the bottom.
> This file is **runtime-load-bearing**: `core/services/docs_context_builder.py:185` reads from it and feeds it to every agent. Stay at this path; refresh-in-place.

# Current Mission

**Status:** ACTIVE — DRAFT REFRESH (awaiting Chris sign-off)
**Period:** 2026 portfolio cycle (open-ended; tied to Atlas Phase 1 progress, not a calendar quarter)
**Last refreshed:** Session 1143 (2026-05-25) — Draft
**Previous version:** Session 814, "Q1 2026 / $10K MRR" framing (superseded by Atlas v1 + Jessica ratification)

> **Chris: reply with the 7 answers in § Decision Needed at the bottom; once answered, we lock the mission.**

---

## Mission Statement

> **Ship the 24/7 Global AI portfolio. One polished Suite product at a time, paying customers before features, soft-cut architecture preserved.**

**24/7 Global AI** is the public brand. "Donkey Betz" remains the internal platform codename. Sports/betting is one vertical among many, deferred to Phase 3+ per the Atlas.

---

## Strategic frame (locked by Atlas v1 + Jessica ratification)

The Atlas ([`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md)) defines the path:

- **Phase 1 (current):** Rigby standalone at $30/mo (Decision 5). Text only, no avatar, no vertical add-ons. The personal AI assistant with the existing 101 tools / 80 spiders / 83 agents behind it.
- **Phase 2:** Suite — Signal Studio + SellerPilot + Contract Concierge, Stripe sequenced 1-by-1 in that order (Decision 10).
- **Phase 3+:** Verticals (Markets, Content, Studio, Legal) — deferred until Suite converts paying customers.
- **Phase 4+:** Character OS merge — parked; unlock if Suite revenue exists AND customers ask for a face.

**Take-public trigger (Decision 1):** Rigby launches publicly only when ≥2 Suite products each sustain ≥$500 MRR AND a concrete Rigby standalone GTM answer exists.

**Architecture stays soft-cut:** monorepo, shared Django + Postgres + Celery + spider runtime + agent registry. Per-app personas, route prefixes, billing tiers — no rewrites.

---

## Current operating constraints

These are real and govern every priority below:

- **Cleanup mode (April 2026 →).** Chris stepping back from feature work. New surface area is the exception, not the rule.
- **LLM budget tight.** Recent baseline: ~$50 OpenAI credits at last refresh; cost-attribution work (Decision 9 + Phase 0 schema) is gating multi-tenant pricing readiness.
- **Local-only default** (`feedback_local_only_default.md`). Don't drive prod verification / deploys / Jessica follow-ups unless Chris flips the switch. **Interpretation:** default posture is **no autonomous prod actions** (deploys, outbound comms, irreversible data changes) unless explicitly approved.
- **Per-workspace cost attribution is a hard prerequisite** for any external SaaS launch. Without `LLMCallLog.workspace` FK + `ExternalAPICallLog`, multi-tenant pricing is uninsurable.

---

## Primary objectives — DECISION NEEDED for exact ordering

The Atlas implies a sequence but the explicit "top 3 for this period" lock is Chris's call. Candidates:

**A. Land Phase 0 cost-attribution schema (Decision 9).** This unblocks Phase 2 Stripe wiring for Signal Studio + SellerPilot + Contract Concierge. Without it, "per-app pricing" is undefendable.

**B. Get Signal Studio to ≥$500 MRR.** Per Decision 10, this is the first Stripe SKU. Until at least one Suite product earns, take-public trigger is unreachable.

**C. Keep Rigby's daily-driver surface stable for Chris.** The internal PA must keep functioning as Chris's working assistant while the Suite GTM work happens. Rigby's value as a paid product depends on her value as an internal one staying intact.

**D. Maintain docs/corpus hygiene at "good enough" to prevent drift regressions.** No new cleanup projects unless they block Phase 1/2. Sessions 1142/1143 just landed the foundation; defend it cheaply, don't expand it.

> See § Decision Needed at the bottom — Chris locks the top 3 + the order.

---

## Focus areas (preserved from prior mission where still valid)

### 1. Quality Over Quantity

**Do:** Generate expert-level, production-ready content.
**Don't:** Generate high volumes of mediocre content.

Atlas alignment: Phase 1 is "ship ONE polished product before fragmenting attention across verticals."

### 2. Cost Consciousness

**Do:** Use the right model for the task — cheap/fast for routine ops; premium tier only for genuinely hard work. Provider-agnostic; let the budget controller / downgrade policy decide the specific model.
**Don't:** Use expensive models for routine operations.

Verifiable via `LLMCallLog`. Phase 0 cost-attribution work (Decision 9) makes this enforceable per-workspace.

### 3. Human Experience First

**Do:** Reduce Chris's cognitive load. Rigby exists so Chris doesn't have to remember everything.
**Don't:** Create more work through excessive notifications, half-built dashboards, or PR ping-pong.

Success metric (subjective): Chris feels the system is helpful, not overwhelming. This metric is Chris-judged, not auto-instrumented.

### 4. Compound Value

**Do:** Build reusable assets — playbooks, canon docs, templates, search_docs corpus, kb_tool embeddings.
**Don't:** Generate one-off content that's immediately forgotten.

Atlas alignment: every app shares the same agent registry, spider feeds, canon. Soft-cut is the architectural realization of "compound value."

### 5. Verifiable claims only (Session 1142 lesson)

**Do:** Mark unimplemented capabilities as "aspirational." Every external platform claim must be runtime-verifiable via `verify_doc_claims` or `PLATFORM_INVENTORY.md`.
**Don't:** Ship marketing copy that promises features the code doesn't have. (Reinforced by Session 1137 Decision 12 rebrand audit.)

---

## Agent alignment

Every agent decision filters through:

1. **Does this advance the mission?** (move toward Phase 1 paying-customer state, or shore up Phase 0 prerequisites)
2. **Is this the right time?** (priorities + dependencies — don't open new fronts while Phase 0 schema is unmet)
3. **Is this the right cost?** (model selection, token usage, per-workspace budget)
4. **Will this compound?** (reusable across Suite apps, or one-off?)
5. **Is the claim verifiable?** (runtime-checked vs marketing-prose)

If any answer is "no" or "unclear" → pause and reconsider.

---

## What NOT to do

- Don't launch Rigby standalone publicly until Decision 1 trigger met (≥2 Suite products at ≥$500 MRR + concrete Rigby GTM answer).
- Don't ship multi-tenant pricing without `LLMCallLog.workspace` FK + `ExternalAPICallLog` cost telemetry.
- Don't start new experimental features without Chris approval — cleanup mode is the default posture.
- Don't generate content that won't be used; don't optimize for volume.
- Don't deploy to prod or chase Jessica follow-ups without explicit Chris flip from local-only mode.
- Don't make platform claims (in marketing, sales, GTM) that `verify_doc_claims` doesn't confirm.
- Don't add complexity to the docs corpus — Session 1143 just spent significant cleanup work to compress it.

---

## Mission metrics — DECISION NEEDED for targets

The Session 814 metrics ($10K MRR by Q1 2026, 20+ canon docs, 10+ playbooks, daily LLM cost <$50) are stale. New verifiable anchors below. **Chris locks the target column.**

| Metric | Old target (Session 814) | Verifiable now? | Proposed target | DECISION |
|---|---|---|---|---|
| Suite product count at ≥$500 MRR | n/a | Stripe dashboard (source of truth) + mirrored in `revenue_tracker_tool` | ≥2 (Decision 1 trigger) | Lock or revise |
| First Suite product Stripe SKU live | n/a | Stripe dashboard (source of truth) + `LLMCallLog` for cost-side | Signal Studio (Decision 10) | Lock or revise |
| Phase 0 cost-attribution schema in prod | n/a | Migration applied + `ExternalAPICallLog` populating | Yes/No | Lock target date |
| Daily LLM cost | < $50/day | `LLMCallLog` aggregation | TBD per Decision 9 cap | Lock per-workspace cap |
| Canon docs (`docs/canon/`) | 20+ | `ls docs/canon/*.md \| wc -l` (current: 2) | TBD | Lock target OR retire metric |
| Playbooks (`docs/playbooks/`) | 10+ | `ls docs/playbooks/*.md \| wc -l` (current: 5) | TBD | Lock target OR retire metric |
| Cognitive load (Chris-judged) | "decreasing" | Subjective | "Rigby remains daily-driver-stable" | Confirm framing |

---

## Mission review

This mission will be reviewed:
- **Per Rigby session:** quick alignment check at session close
- **Monthly:** full metrics review when revenue data exists
- **On every Atlas phase trigger:** when a Suite product hits ≥$500 MRR, when the take-public trigger fires, etc.

---

## DECISION NEEDED (Chris signs off here before this draft locks)

Rigby's banner-only deferral pattern means this draft replaces the file at the same path the moment Chris approves. Items below need explicit ratification:

1. **Top 3 objectives, ranked.** Pick from the (A) / (B) / (C) / (D) list in § Primary Objectives, or write your own. Order matters — what's actually #1 this period?
2. **Primary revenue anchor for the period.** Old: "$10K MRR by Q1 2026." New: ? (Decision 1 is binary trigger, not a target — Chris's call whether to set a leading indicator like "Signal Studio hits $500 MRR" or run open-ended.)
3. **Cost-attribution sub-decisions** (Jessica clarifications still pending — Decision 9):
   - Soft-degrade scope (what triggers automatic model downgrade to cheaper tiers?)
   - Hard-kill threshold (what budget / SLO limits make the platform refuse a call entirely?)
   - Internal-spend accounting (is Chris's personal Rigby use counted against the per-workspace cap?)
4. **Canon / playbook targets — retire or refresh?** Old numeric goals (20+ canon, 10+ playbooks) were aspirational; current is 2 and 5 respectively. Either pick a number that means something, or retire as metrics and replace with "no broken canon refs" or similar.
5. **Red lines explicitly to add to "What NOT to do."** Anything you want hard-coded into agent prompts via DocsContextBuilder?
6. **Period framing.** Old: "Q1 2026." New proposal: open-ended, tied to Atlas Phase 1 progress. Confirm or pick a calendar quarter.
7. **Mission review cadence.** Weekly / monthly / per-Rigby-session — pick.

---

*This document is injected into all agent prompts via `core/services/docs_context_builder.py:185`. Last updated: Session 1143 — DRAFT, awaiting Chris sign-off.*
