---
title: "Session 1135 — App-by-app discovery sprint (apps 1 + 2 of 8)"
date: 2026-05-23
status: active
session: 1135
previous_handoff: SESSION_1134_CAPABILITY_SPECS_ATLAS_ANCHOR.md
next_session_primary: Continue discovery sprint — Contract Concierge brief (app 3 of 8) per Atlas precedence
---

# Session 1135 — Discovery sprint started; 2 of 8 app briefs landed

> **Read this if** you want to know what the first two app briefs (Rigby standalone + Signal Studio) locked, what Chris still needs to decide across both, or where the discovery-sprint pattern goes next.

## TL;DR

Session 1135 ran the app-by-app discovery process Chris greenlit at the close of Session 1134. **Pattern established + two briefs shipped:**

| App | PR | Status |
|---|---|---|
| **Rigby standalone** (Atlas Phase 1 flagship) | [#2147](https://github.com/clwest/donkey-betz-platform/pull/2147) | Awaiting Chris (6 §9 decisions) |
| **Signal Studio Markets edition** (Atlas flagship vertical) | [#2148](https://github.com/clwest/donkey-betz-platform/pull/2148) | Awaiting Chris (8 §9 decisions) |

**Process pattern discovered & validated:**
1. Jessica drives discovery in collaborator/ops voice (per `docs/UDB_TRANSLATION_LAYER.md` §1.2)
2. Claude grounds answers in Atlas + verified runtime artifacts
3. Rigby reviews for honest framing (typically catches ~12 mechanical fixes + ~2 micro-fixes per brief)
4. Brief lands at `docs/apps/<slug>_BRIEF.md` with workspace = Donkey Betz
5. PR opened; Chris ratifies open §9 decisions before brief locks as Phase 1 source-of-truth

Average session output: 1 brief per ~2 hours of focused work with Jessica + Rigby.

## What landed (per-app summary)

### App 1 — Rigby standalone (PR #2147)

- **Pitch (Atlas §C.2 canonical):** *"24/7 Global AI is your personal AI assistant that never sleeps — 80 global data sources, 80+ specialised agents on call, 100+ tools so it can actually do things, not just talk."*
- **Phase 1 scope:** research-and-draft engine. Customer ships actions; no external-account integrations (Gmail/Calendar/LinkedIn/CRM) yet — Phase 2 trigger = customer demand.
- **Audience:** solo founders + small-agency owners (hypothesis A/B, no narrowing yet).
- **Packaging:** standalone, $30/mo, 7-day free trial.
- **Phase 0 GATING:** per-customer cost tracking + daily cap (Atlas Phase 0 items 1 + 4 — shared with Signal Studio).
- **Brief authored Jessica → Claude → Rigby (double LGTM).**

### App 2 — Signal Studio Markets edition (PR #2148)

- **Pitch:** *"Signal Studio is your daily morning briefing — the top 10 emerging patterns from 80 spiders, algorithmically curated and delivered at 4:30 AM MT, with cluster cards that auto-refresh when new signals are published."*
- **Phase 1 wedge:** Markets/investing. Hybrid product = AI-written brief on top of Top-10 cluster cards.
- **Audience:** self-directed retail investor (primary) + indie creator (adjacent).
- **Packaging:** standalone product, parallel to Rigby (bundle deferred to Phase 2+). $29/mo, 7-day free trial.
- **Atlas deviation:** Bends "one polished product first" rule on the basis that engine is mostly built — remaining work is marketing + Stripe SKU + landing page, not engineering. Chris ratification required (§9 decision).
- **Phase 0 GATING:** AI brief generation, consumer landing page, email infra, cost tracking + cap (shared with Rigby), legal review for TOS/disclaimers, Stripe SKU, source URL enrichment.
- **Brief authored Jessica → Claude → Rigby (double LGTM).**

## Chris's action items — consolidated bookmark

### Per-app open decisions

**Rigby standalone (PR #2147, 6 decisions in §9):**

| # | Question |
|---|---|
| R-1 | `app.247globalai.com` build status — what's actually shipped in that repo? Unlocks proof-pick + Phase 0 timeline. |
| R-2 | Pick canonical Phase 1 proof — Candidate A (local-internal demo) or Candidate B (consumer signup flow)? |
| R-3 | Confirm $1.50/day cap + cost-tracking ships as Phase 0 GATING (not optional for $30/mo). |
| R-4 | Paid ads budget — monthly amount to test the channel. |
| R-5 | Trademark filing green-light — 1–2 hr legal work. |
| R-6 | Landing page voice deadline — when does copy have to pick founders vs agencies? |

**Signal Studio (PR #2148, 8 decisions in §9):**

| # | Question |
|---|---|
| S-1 | Signal-studio web repo consumer-app status — what's shipped vs scaffolded? |
| S-2 | Sub-domain pick — `signal-studio.247globalai.com` vs `markets.247globalai.com` vs other? |
| S-3 | Email service pick — Resend vs Postmark vs other? |
| S-4 | Confirm $29/mo + 7-day trial pricing. |
| S-5 | Same Phase 0 cost-attribution + daily cap as Rigby (Atlas-level requirement applies to both). |
| S-6 | Paid ads budget for Signal Studio (separate from Rigby's). |
| S-7 | Legal review greenlight (~$500–1500) for TOS + disclaimers. |
| S-8 | Existing u-d-b email infra check — is there messaging/notification infra we can reuse vs greenfield Resend/Postmark? |

### Cross-cutting decisions (apply to both products + future apps)

| # | Theme | Why it's cross-cutting |
|---|---|---|
| X-1 | **Atlas Phase 0 prerequisites** — `LLMCallLog.workspace` FK + daily $ cap + `ExternalAPICallLog` + cost-per-customer report. Per Atlas §H Phase 0, items 1-4. Estimated ~5-6 days combined. | Required before EITHER product can sell. Shared infrastructure. |
| X-2 | **Trademark filing** on "24/7 Global AI" — USPTO TESS check + optional Intent-to-Use 1(b). | Brand-level decision; both Rigby standalone and Signal Studio benefit. Recommended before paid ads scale visibility. |
| X-3 | **Legal review** for TOS + disclaimer language (~$500–1500). | Shared track — Rigby's TOS + Signal Studio's TOS share most of the language, especially markets-adjacent disclaimers. |
| X-4 | **Existing email infra check** — is there u-d-b infra to reuse? | Decides ~2-3 days of greenfield work for Signal Studio's email push. Likely also benefits Rigby's welcome/billing emails. |
| X-5 | **Paid ads budget allocation** — two products = two campaign pools. | Question of total monthly ad spend split across Rigby + Signal Studio. |
| X-6 | **Atlas deviation ratification** — Signal Studio shipping parallel to Rigby bends "one polished product first." | Chris-level strategic call. Rest of discovery sprint may surface more deviations. |

### Decisions Jessica ratified in-session (Chris confirmation pending)

These are captured in the briefs as "closed in Jessica discovery pass; Chris ratification pending":

| Brief | Item | Jessica decision |
|---|---|---|
| Rigby standalone | Audience narrowing | Don't narrow — target solo founders + agency owners |
| Rigby standalone | Q6 execution posture | Drafts only; customer ships (Phase 2 = external integrations) |
| Rigby standalone | Q7 always-refuse | Standard markets/medical/legal disclaimers, expandable |
| Rigby standalone | Q10 channel | Paid ads day-one + warm/personal network (no Operator Edge — audience = 0) |
| Signal Studio | Q1 pitch | Option A morning-briefing framing |
| Signal Studio | Q2 wedge | Markets, hybrid AI brief + Top-10 cards |
| Signal Studio | Q6 packaging | Standalone (bundle Phase 2+) |
| Signal Studio | Q7 pricing | $29/mo single tier, 7-day trial, monthly only |
| Signal Studio | Q4 cadence + delivery | Daily 4:30 AM MT + email push for subscribers |
| Signal Studio | Curator language | "Algorithmically curated" not "hand-picked" |
| Signal Studio | Proof path | Launch-day proof = brief + email + cards + SSE (requires Phase 0) |

## Process learnings worth keeping

**Save to future discovery passes:**

1. **Rigby's reviews are mechanical, not directional.** Both briefs returned ~12 fixes + ~2 micro-fixes; categories repeat (count alignment, hypothesis labeling, Phase 0 gating elevation, claim audit expansion). Expect this overhead per brief; bake it into time estimates.
2. **Jessica's persona contract works.** Translation layer §1.2 (collaborator/ops + [BLOCKER]/[VERIFY]/[RISK]/[ROLLBACK] tags) kept the discovery sharp and prevented marketing drift.
3. **Plain-English checks are critical when Jessica's the operator.** She caught "what is Atlas?", "what does Rigby actually do?", and "do cards or briefs make more sense visually?" — all questions Claude wouldn't have surfaced unprompted. Build in space for them.
4. **Atlas wins over Business spec on conflicts.** Confirmed twice: the v3 Business spec's per-app pricing ($49/149/349) is illustrative; Atlas's "packs inside Rigby" framing is the locked-Phase-3 model. Don't extrapolate from Business spec when discovery is happening.
5. **"Honest claim audit" (§10) catches the most consequential issues.** Both briefs needed §10 expansion based on Rigby's review (Rigby standalone: +2 bullets; Signal Studio: +3 bullets). Pre-populate aggressively in future briefs.

## Apps remaining in Session 1135 discovery sprint

| # | App | Atlas precedence | Why pre-flagged |
|---|---|---|---|
| 3 | **Contract Concierge** | Suite candidate, Draft Library demo shipped Session 1129 | Concrete shipping evidence exists (artifact push/pull + SSE), making discovery faster than apps 4-8 |
| 4-8 | MentorForge / PitchDeckForge / SellerPilot / DealFlowTracker / ComplianceSentinel | "Deferred" per Atlas; identity provisioned but no documented product intent | Atlas grounding (Session 1134) flagged these as harder briefs — Chris will need to provide intent before discovery can ground anything |

**Recommended next session priority:** Contract Concierge (app 3). Most concrete artifact evidence, fastest to brief.

## Carryover items (unchanged)

These remain queued in parallel with the discovery sprint per START_HERE — none blocked by 1135:

- **(Y) Reject-mode flip in `unified_pa_chat`** — still queued; gated on ≥3 days clean post-merge audit telemetry.
- **(A) Action-card pre-generation for curated** — still queued; ~1 session work, child rows (typed `CuratedSignalEntry`).
- **Capability spec Phase 0 scaffolding** — gated on Session 1135 discovery filling per-app intent.
- **Source URL `url=""` enrichment** — explicitly elevated to Signal Studio Phase 0 GATING per its brief (was carryover; now blocking).
- **Local-only default** still in effect — no prod deploys/verifications unless Chris flips it.

## Files touched

- `docs/apps/rigby_standalone_BRIEF.md` (new; PR #2147)
- `docs/apps/signal_studio_BRIEF.md` (new; PR #2148)
- `docs/handoffs/SESSION_1135_APP_DISCOVERY_SPRINT.md` (this file)
- `00-START-NEXT-SESSION.md` (updated to point Session 1136 here)

## Status snapshot

- **Branch state:** `docs/session-1135-rigby-standalone-brief` (PR #2147 open), `docs/session-1135-signal-studio-brief` (PR #2148 open), `docs/session-1135-handoff` (this PR pending).
- **Local fleet:** All 7 fleet Docker apps + u-d-b daphne/celery running (verified at session open).
- **Doctor:** 0 blocking, 3 warnings (inventory stale, test count drift, handoff numbering gaps — all upstream).
- **Workspace assignments:** Both briefs assigned to Donkey Betz workspace per memory rule.

---

**Handoff authored:** Session 1135 close (Claude + Jessica discovery pass, ~2 apps shipped).
**Bookmarked for Chris:** 14 open decisions (6 Rigby + 8 Signal Studio) + 6 cross-cutting items in §"Chris's action items — consolidated bookmark."
**Next session entry:** Contract Concierge brief (app 3 of 8) per Atlas precedence.
