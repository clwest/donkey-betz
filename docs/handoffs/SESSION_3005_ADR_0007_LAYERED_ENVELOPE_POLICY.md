---
title: "SESSION 3005 — ADR-0007 Layered Envelope Policy (refines ADR-0006 §3.2) + T-ENVELOPE-2 CLOSED as already-shipped + T-ENVELOPE-2-DEPRECATION introduced"
session: 3005
date: 2026-07-27
type: single_pr_close_governance
merge_shas:
  - "957fee61f"   # PR #3683 — ADR-0007 authored + ADR-0006 §3.2 refinement note + APIResponseEnvelope deprecation markers
prs:
  - 3683
related_arcs:
  - "ADR-0005/ADR-0006 typed-error-envelope corpus"
  - "I-0301 Failure-Data Safety Contract (RUR-C1) — Family E authorizing substrate"
consumes:
  - "S3004 close cascade Chris directive 'start s3005 with option A'"
  - "ADR-0005 §4.1 T-ENVELOPE-2 three-path spec (invalidated at HEAD; CLOSED via §3.5)"
  - "docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md §3 + §8 (Family E authorization)"
---

# S3005 — ADR-0007 Layered Envelope Policy

**Status:** CLOSED. 1 governance PR merged (ADR-0007 authored). ADR-0005 T-ENVELOPE-2 CLOSED-as-shipped; new T-ENVELOPE-2-DEPRECATION T-slot introduced. HEAD `957fee61f`.

## Session shape

Single-focus, single-PR, one-session governance ratification. Full Flow B with spec-invalidation early-abort clause exercised: primary-directive routing → Chris directive Option A (T-ENVELOPE-2) → pre-execution probe surfaces spec-invalidation → Rigby joint diagnosis independent verification (AGREE spec-invalidation, A4 recommendation) → three-part plain-English decision framing to Chris → Chris ratification ("yes author ADR-0007") → ADR authoring → Rigby T1 SIGN pre-merge (5 STRENGTHEN applied + 1 post-application tiny STRENGTHEN) → merge → close cascade. Zero implementation code shipped — this session establishes the substrate for the next T-slot arc.

**Playbook exercised:**
- PLAYBOOK-7.7.1 abort-early clause (§Phase 4 spec-invalidation → route to Chris before proceeding)
- PLAYBOOK-7.7.2 SIGN evidence discipline (Rigby 8+ real tool_runs; substantive, not rubber-stamp)
- PLAYBOOK-7.7.3 Chris-facing plain-English framing (do-we-lose-anything / more-work-later / ≤1 decision)

## PR #3683 (`957fee61f`) — ADR-0007 Layered Envelope Policy

**Scope (3 files, +364 / -14):**

1. **NEW** `docs/adr/ADR-0007-layered-envelope-policy.md` (9 sections, 299 lines):
   - §1 Status — accepted, Chris ratified 2026-07-27
   - §2 Context — the discovery + shape mismatch + Rigby verification + I-0301 §8.1 constraint
   - §3 Decision — layered policy (§3.1 Family E for errors / §3.2 Family B for success / §3.3 deprecations / §3.4 refinement scope on ADR-0006 §3.2 / §3.5 T-ENVELOPE-2 CLOSED + new T-slot)
   - §4 Consequences — HEAD-conformant / obligations / T-ENVELOPE-2-DEPRECATION scope / what ADR does NOT change / docs cascade
   - §5 Alternatives considered — A1 (unify to E) / A3 (unify to B) / in-place amend / defer — all rejected with rationale
   - §6 Reversibility 5 (docs + annotation-only)
   - §7 Provenance — Chris ratification citation + Rigby joint diagnosis citation + consumed sources
   - §8 Follow-on ADRs — 3 candidate future ADR-N slots
   - §9 Amendment linkage — cites ADR-0006 §3.2 as refined-not-superseded

2. **MODIFIED** `docs/adr/ADR-0006-typed-error-envelope-contract-non-provisional.md` — §3 refinement note block added after line 79 pointing to ADR-0007 as §3.2 refinement.

3. **MODIFIED** `core/api_responses.py`:
   - Class-level docstring scope banner on `APIResponseEnvelope` — "canonical for SUCCESS responses only; error helpers deprecated".
   - `.. deprecated:: ADR-0007` markers on 7 static methods: `error`, `unauthorized`, `forbidden`, `not_found`, `validation_error`, `rate_limited`, `server_error`.
   - `.. deprecated:: ADR-0007` markers on 5 module helpers: `api_error`, `api_unauthorized`, `api_forbidden`, `api_not_found`, `api_validation_error`.

## Design decisions ratified

### The layered policy shape

Rather than unify to one envelope (either direction would be high-churn + break authorizing substrate), ADR-0007 declares distinct canonical shapes per response direction:

- **Errors → Family E** (`build_user_facing_envelope` at `core/security/error_envelope.py:72-114`). Emission surfaces: DRF exception handler (Layer 1), non-DRF middleware (Layer 2), template overrides (Layer 3), explicit view-code emission using the construction function (authorized per safety-contract §8 line 317 construction-boundary requirement).
- **Success → Family B** (`APIResponseEnvelope.success` + `.paginated` at `core/api_responses.py:15-140`). Existing 14-ish success call-sites keep working unchanged.

### T-ENVELOPE-2 disposition

ADR-0005 §4.1 T-ENVELOPE-2 was framed as "install one of three paths (a/b/c)". At HEAD, paths (a) and (b) are ALREADY shipped (pointing at Family E, not Family B) — spec-invalidation. ADR-0007 §3.5 marks T-ENVELOPE-2 CLOSED-as-shipped and introduces a NEW T-slot **T-ENVELOPE-2-DEPRECATION** for the Family B → Family E migration of 108 call-sites across 5 files:

- `core/views_platform_integrations.py` — 62 call-sites
- `core/views_auto_distribution.py` — 25 call-sites
- `core/auth_middleware.py` — 10 call-sites
- `core/views_revenue_analytics.py` — 8 call-sites
- `core/views_odds_sports.py` — 3 call-sites

Estimate: 4-6 sessions once policy is ratified (revised up from initial 2-3 sessions after Rigby's fresh grep surfaced 108, not ~14). Sub-task: author lint / CI-grep gate to prevent Family B error-shape regression.

### Out of scope

`core/api_helpers.py` is a SEPARATE module (`smart_truncate` + its own `api_error` / `api_success`). Used by `core/views_ab_testing.py`, `core/views_learning_loop.py`, `core/views_rag_observability.py`, `core/error_messages.py`. This is a different substrate — disposition is a future arc, not part of T-ENVELOPE-2-DEPRECATION.

## Rigby T1 SIGN quality signal

**8 real tool_runs across three turns.** Substantive per PLAYBOOK-7.7.2, not rubber-stamp.

**5 STRENGTHEN applied pre-merge:**
- **Q2**: §8 line 317 construction-boundary framing (initially cited §8.4 which is Regression Suite; §8 body has the construction requirement). Applied with follow-up tiny STRENGTHEN.
- **Q3**: 108-count correction (my initial estimate of "~14" from stale ADR-0005 metric was materially wrong; fresh grep required per `feedback_verify_at_raw_orm_before_trusting_tool_no_data`). Also added `core/api_helpers.py` out-of-scope note.
- **Q4**: T-ENVELOPE-2 CLOSED-as-shipped + new T-slot framing (was "superseded" — cleaner governance framing).
- **Q5**: §5.1 rejection rationale semantic-clarity note (Family E doesn't model success payloads).
- **Q6(i)**: class-level scope banner on `APIResponseEnvelope` docstring (prevents "half-deprecated class" anti-pattern).
- **Q6(ii)**: §4.2 lint / CI-grep gate obligation named as MUST-author under T-ENVELOPE-2-DEPRECATION (prevents Family B error-shape regression).

**1 post-application tiny STRENGTHEN:** §3.1 §8.4 citation wording refined — §8.4 is Regression Suite, not the construction layer; four enforcement layers (§8.1-§8.3) all invoke the same construction function.

## γ mechanism state (unchanged from S3004 close)

Layer 1 + Layer 2 + Layer 3 still all LIVE at HEAD `957fee61f`. This session was docs-only + annotation-only; runtime behavior unchanged. ADR-0005 T-slot progress:

- **CLOSED (this session):** T-ENVELOPE-2 (already-shipped per PR #3085 I-0301)
- **SHIPPED (prior sessions):** T-ENVELOPE-0/1/3 (S3002), T-VIP-1 (S3003), §3.5 UX widening (S3004)
- **NEW (this session):** T-ENVELOPE-2-DEPRECATION (Family B error migration, 108 call-sites)
- **REMAINING:** T-ENVELOPE-4 (migration ramp — largely subsumed by T-ENVELOPE-2-DEPRECATION), T-ENVELOPE-5 (interceptor elevation — optional), T-ENVELOPE-6 (telemetry pending Group 1700)

## Folds

- **Fold A — `same_pr_mitigatable` closed at pre-execution probe.** Chris's Option A directive would have executed the wrong spec. Pre-execution probe per `feedback_cycle_1a_verify_before_build` caught the spec-invalidation before any implementation was touched. **1st concrete instance of the PLAYBOOK-7.7.1 abort-early clause firing in the S3xxx session series.** Watch for 2nd — if recurs, propose Playbook amendment codifying "pre-execution HEAD-verification probe REQUIRED for any T-slot spec authored more than N sessions ago" (candidate rule; needs 2nd trigger).

- **Fold B — `informational` — stale-baseline propagation.** ADR-0005 §2 line 25 asserted "EXCEPTION_HANDLER absent" as baseline. That claim was accurate at ADR-0005 AUTHORING TIME (S3001) but became stale post-hoc via a different arc (I-0301, PR #3085, shipped 2026-07-10 well before ADR-0005 was drafted 2026-07-27). ADR-0005 §Emission-count-sharpening at line 316 similarly cited "14 emission sites" which turned out to be off-by-8x (actual: 108). **1st concrete instance in the S3xxx series of ADR-baseline drift being discovered after ratification.** Watch for 2nd — if recurs, propose amendment discipline for ADR baseline claims requiring re-verification at HEAD before any T-slot execution.

- **Fold C — `informational` — "refines" as a governance framing between "supersedes" and "in-place amend".** ADR-0001 §3.6 lifecycle only defines proposed / accepted / superseded / retracted. ADR-0007 introduced a NEW frontmatter field `refines: ADR-0006 §3.2` (non-schema, grep-target) to record a NEW ADR that amends a specific §-scope of a prior ADR without full supersession. **1st concrete instance** of this pattern. Watch for 2nd — if recurs, propose formal `refines:` field addition to ADR-0001 frontmatter schema §3.3.

- **Fold D — `future_trigger` — lint/CI-grep gate obligation named but not authored.** ADR-0007 §4.2 + §4.3 name a lint / CI-grep gate as MUST-author under T-ENVELOPE-2-DEPRECATION. This obligation gets authored during T-slot execution (next arc), not this session. Watch that it doesn't slip.

## Carry-forward

- **All S3004 carry-forwards unchanged.**
- **New S3005 carry-forwards:**
  - **Fold A (1st trigger)** — PLAYBOOK-7.7.1 abort-early clause firing (spec-invalidation caught pre-execution). Watch for 2nd.
  - **Fold B (1st trigger)** — ADR-baseline post-ratification drift discovery. Watch for 2nd.
  - **Fold C (1st trigger)** — `refines:` frontmatter field for §-scoped amendment. Watch for 2nd.
  - **Fold D `future_trigger`** — lint / CI-grep gate authoring under T-ENVELOPE-2-DEPRECATION arc.
- **T-slot queue update:**
  - **T-ENVELOPE-2:** CLOSED as already-shipped ✅
  - **T-ENVELOPE-2-DEPRECATION:** NEW (this session) — 108 call-sites, 4-6 sessions estimated
  - **T-ENVELOPE-4/5/6:** unchanged, remaining

## Governance

**ADR-0007 ratified this session.** No Playbook amendments. Candidate seed from S3005 Fold A (abort-early trigger) if pattern recurs.

**Ratification workflow:**
- Chris joint agreement reached with Rigby BEFORE routing plain-English decision (per `feedback_claude_rigby_agree_first_chris_yes_no`)
- Three-part plain-English framing (per `feedback_plain_english_decision_framing_for_chris` + PLAYBOOK-7.7.3)
- Rigby T1 SIGN pre-merge with substantive tool_runs (per PLAYBOOK-7.7.2 + `feedback_verify_rigby_tool_runs_before_trusting_sign`)
- STRENGTHENs folded pre-merge, not deferred (per PLAYBOOK-6.10.9 fold-authoring evidence-admission)

**No twin-mirror this session** (session_lifecycle close --allow-no-mirror). Ratification twin-mirror per `feedback_twin_deliverable_at_every_ratification` should be minted in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` as a post-close ADR-0007 provenance record. Deferred to a future PA-tool dispatch (Chris can request Rigby to author it at any time via `deliverable_tool.create` in the Architecture & Research workspace).

## Wrapper pin

Retired at close: `pa-330f207235344b8f` (S3004 mint, 3 rows updated during S3005). Minted for S3006: (assigned by `session_lifecycle close --label s3005-adr-0007-layered-envelope-policy`). Wrapper `tools/pa_local.sh` atomically rewritten and committed in the S3005 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
