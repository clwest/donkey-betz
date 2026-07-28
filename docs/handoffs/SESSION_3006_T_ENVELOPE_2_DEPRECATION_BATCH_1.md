---
title: "SESSION 3006 — T-ENVELOPE-2-DEPRECATION Batch 1: 11 Family B error call-sites migrated + lint gate"
session: 3006
date: 2026-07-27
type: single_pr_close
merge_shas:
  - "197174a60"   # PR #3685 — Batch 1 migrations + lint gate
prs:
  - 3685
related_arcs:
  - "ADR-0007 Layered Envelope Policy (ratified S3005)"
  - "I-0301 Failure-Data Safety Contract (Family E authorizing substrate)"
consumes:
  - "S3005 close cascade batch-order recommendation (smallest-to-largest)"
  - "ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION T-slot"
  - "ADR-0007 §4.2 lint gate obligation"
---

# S3006 — T-ENVELOPE-2-DEPRECATION Batch 1

**Status:** CLOSED. 1 feature PR merged. 11 Family B error call-sites migrated to Family E. Lint gate authored + CI workflow wired. HEAD `197174a60`.

## Session shape

Single-focus, single-PR, one-session close. Clean Flow B: primary-directive routing (Chris "start s3006 with batch 1") → Rigby joint agreement on 11 reason_code mappings + lint gate shape + details-drop tradeoff → Chris course-correction opportunity ("proceed") → implementation → 29/29 test verification → Rigby A2 SIGN pre-merge with 2 STRENGTHEN applied → merge → celery-recycle → close cascade. Third consecutive S3xxx→S3xxx+1 continuous-engineering cascade (S3003→S3004→S3005→S3006).

## PR #3685 (`197174a60`) — Batch 1 migrations + lint gate

**Scope (5 files, +259 / -22):**

### Migrations (11 call-sites)

**`core/views_odds_sports.py` (3 sites):**
- Line 78-84 (originally L73): `invalid_input` (400) — float() parse failure in odds parsing
- Line 89-96 (originally L84): `validation_error` (400) — non-zero business rule for non-fractional formats
- Line 244-251 (originally L239): `validation_error` (400) — Kelly Criterion input range/enum failures
- Import: removed `api_validation_error`, added `JsonResponse` + `build_user_facing_envelope`

**`core/views_revenue_analytics.py` (8 sites):**
- Line 177-183 (originally L172): `not_authenticated` (401) — inline auth check
- Line 189-198 (originally L180): `not_found` (404) — platform lookup failure
- Line 203-213 (originally L189): `validation_error` (400) — linked-account precondition. **Refined from Claude's initial `not_found` (404) to Rigby's `validation_error` (400)** per safety-contract §9.2 existence-oracle concern (returning 404 for "user hasn't linked an account" could leak "does the platform support linking at all?")
- Line 456-462 (originally L438): `not_authenticated` (401)
- Line 550-556 (originally L529): `not_authenticated` (401)
- Line 649-655 (originally L624): `not_authenticated` (401)
- Line 665-672 (originally L640): `invalid_input` (400) — JSON parse failure
- Line 734-740 (originally L708): `not_authenticated` (401)
- Import: removed `api_error`, added `JsonResponse` + `build_user_facing_envelope`

### Per-site pattern

Applied uniformly per Rigby A2 SIGN STRENGTHEN (ii):

```python
payload = build_user_facing_envelope(reason_code=X)
logger.warning(
    "envelope_emit reason=%s support=%s endpoint=%s [hint=%s]",
    payload['reason_code'], payload['support_code'], request.path,
    {redacted_hint_dict},  # optional
)
return JsonResponse(payload, status=X)
```

User-facing `details` payload DROPPED per safety-contract §3.1 permitted-fields allowlist. Debuggability preserved via structured `logger.warning`: emits `reason_code + support_code + request.path + optional redacted hint`. No user input echoed verbatim — hint dict contains only enum-tag categorization (`{'parse_error': 'json_decode'}`, `{'rule': 'kelly_criterion', 'error_keys': [...]}`, `{'precondition': 'no_linked_account', 'platform': name}`).

### Lint gate (ADR-0007 §4.2)

**`scripts/lint_no_deprecated_family_b.py`** — NEW, 128 LOC:
- `MIGRATED_FILES` tuple = 2 Batch 1 files (grows per future batch)
- `DEPRECATED_USAGES` regex covers all 7 static methods + 5 module helpers
- `DEPRECATED_IMPORT_NAMES` blocks reimport of banned symbols (Rigby STRENGTHEN — dead imports are regression signal too)
- `APIResponseEnvelope` class not banned (still canonical for success responses per ADR-0007 §3.2)
- Exit 1 on any violation (proper CI gate behavior)
- `--list` flag prints tracked files

**`.github/workflows/check-envelope-migration.yml`** — NEW, 30 lines:
- Runs on PR + push to `main`
- 2-minute timeout
- Invokes `python scripts/lint_no_deprecated_family_b.py`

**`scripts/verify_repo_guardrails.py`** — Header docstring updated (:1-15) with "Related but INTENTIONALLY SEPARATE guardrails" cross-link block pointing to envelope-migration lint + fold-back instructions (Rigby STRENGTHEN (i)).

## Design decisions ratified

### 11 reason_code mappings

10/11 initial Claude proposals AGREE'd by Rigby without change. 1 refined (L189: `not_found` → `validation_error`) per safety-contract §9.2 existence-oracle concern. Full breakdown in Batch 1 dispatch conversation.

### Details-drop tradeoff

User-facing `details` payload was echoing user input (odds values, form field maps) which was arguably a §3.2 anti-pattern in Family B. Dropping is a §3.2 upgrade, not a debuggability regression — reason_code + human_message + support_code carries the semantic signal.

### Debuggability preservation via structured logging

Rigby A2 STRENGTHEN (ii): explicit `JsonResponse(build_user_facing_envelope(...))` returns don't pass through the DRF exception handler / middleware paths that emit operator envelopes to `OpsRunEvent.detail`. Without operator envelope emission, we'd lose operator-side diagnostic. Structured `logger.warning` at each error return preserves that debuggability without violating the user-facing allowlist. Not a substitute for a future full operator-envelope-from-explicit-emissions arc, but a solid interim.

### Lint gate shape choice (α over β)

File-scoped zero-tolerance (α) chosen over repo-wide baseline (β). Reasons per joint agreement:
- Matches ADR-0007 §4.3 explicit file enumeration
- Simpler machinery (128 LOC vs ~150 LOC + baseline JSON maintenance)
- Migration cadence maps naturally (batch ships → add file to MIGRATED_FILES tuple)

### Not applied this batch (deferred to future arcs)

- **DRF-decorator refactor** for the 5 inline auth checks in views_revenue_analytics.py. Idiomatic replacement would be `@api_view + @permission_classes([IsAuthenticated])` + let DRF handler auto-emit. But has bigger behavioral surface (renderer/CSRF/throttling). Deferred as follow-on batch; noted as carry-forward.
- **`core/api_helpers.py` consumer cleanup** (4 more files: views_ab_testing, views_learning_loop, views_rag_observability, error_messages). Separate substrate per ADR-0007 §4.3 out-of-scope note; future arc.
- **Operator-envelope-from-explicit-emissions** wiring. Structured logging is the interim; full wiring would be a substrate change to `build_user_facing_envelope` API or a new helper. Not on the roadmap yet.

## Rigby A2 SIGN quality signal

**10+ real tool_runs across two turns.** Substantive per PLAYBOOK-7.7.2, not rubber-stamp.

**2 STRENGTHEN applied pre-merge:**
- **(i)** guardrails cross-link — `scripts/verify_repo_guardrails.py` header docstring updated to note envelope-migration lint is intentionally separate entry point with fold-back instructions.
- **(ii)** operator-context preservation — all 11 error returns use `assign-payload → logger.warning → return JsonResponse` pattern; preserves debuggability via reason_code + support_code + endpoint + redacted hint.

## Verifications performed at HEAD `197174a60`

- `pytest tests/security/test_failure_envelope_conformance.py -v` → 29/29 passed in 198s
- `python scripts/lint_no_deprecated_family_b.py` → `✅ ADR-0007 Family B deprecation lint OK (2 files checked)`
- `grep -c "envelope_emit reason=" core/views_odds_sports.py core/views_revenue_analytics.py` → 3 + 8 = 11 log lines (matches 11 error returns)
- `grep "api_error\|api_validation_error\|api_unauthorized\|api_forbidden\|api_not_found" core/views_odds_sports.py core/views_revenue_analytics.py` → 0 matches
- `make celery-recycle` post-merge — all 3 workers + beat restarted cleanly

## γ mechanism state (unchanged from S3005 close)

Layer 1 + Layer 2 + Layer 3 still all LIVE at HEAD `197174a60`. This session shipped code (11 call-sites migrated + lint script + workflow); runtime error emission path shifted from Family B to Family E for the 2 migrated view files. ADR-0005 T-slot progress:

- **CLOSED (S3005):** T-ENVELOPE-2 (as already-shipped by I-0301)
- **PROGRESS this session:** T-ENVELOPE-2-DEPRECATION Batch 1 (2-of-5 files complete, 11-of-108 call-sites migrated, lint gate operational)
- **SHIPPED (prior sessions):** T-ENVELOPE-0/1/3 (S3002), T-VIP-1 (S3003), §3.5 UX widening (S3004)
- **REMAINING T-ENVELOPE-2-DEPRECATION:** 3 files, 97 call-sites (auth_middleware 10 / views_auto_distribution 25 / views_platform_integrations 62). Estimate 3-5 more sessions.
- **REMAINING T-slots:** T-ENVELOPE-4 (largely subsumed), T-ENVELOPE-5 (optional), T-ENVELOPE-6 (Group 1700 pending)

## Folds

- **Fold A `informational`** — per-site logger.warning pattern established. **1st concrete instance** of the envelope-emit-with-structured-log pattern in the S3xxx series. Watch for 2nd occurrence in Batch 2; if pattern proves clean, propose extraction to a helper (`emit_error_envelope(reason_code, request, hint=None) → JsonResponse`) that wraps the 3-line pattern.

- **Fold B `informational`** — reason_code-to-status_code coupling opportunity. Currently every migrated site passes both `reason_code=X` AND `status=Y` explicitly. But `ReasonCode.typical_status` is already in the enum (`core/security/reason_codes.py:38-45`). A helper could look up the status automatically: `emit_error_envelope(reason_code)` → auto-emit with typical_status. **1st concrete instance** — if helper extraction happens (per Fold A), fold the status inference in same PR.

- **Fold C `future_trigger`** — DRF-decorator refactor for inline auth checks. 5 sites in views_revenue_analytics use `if not request.user.is_authenticated: return 401`. DRF idiomatic replacement is decorator-based + let handler auto-emit. Bigger behavioral surface. Deferred; carry-forward.

- **Fold D `informational`** — session-shape observation. **3rd concrete continuous cascade in S3xxx series** (S3003→S3004 same-file, S3004→S3005 substrate-invalidation-cascade, S3005→S3006 implementation-of-just-ratified-ADR). Fold-Drain-Same-Surface (S3004 Fold A) at **2nd trigger**; broader "cascade" observation (S3002 Fold A) now at **3rd trigger** if we count this session. Watch — if 4th, propose Playbook rule codifying "S<N> ratification directly unblocks S<N+1> implementation → recommend automatic batch-1 dispatch in the ratifying session's close cascade."

## Carry-forward

- **All S3005 carry-forwards unchanged EXCEPT:**
  - S3005 Fold D `future_trigger` (lint gate authoring under T-ENVELOPE-2-DEPRECATION) ✅ CLOSED this session.
- **New S3006 carry-forwards:**
  - **Fold A + Fold B combined** — helper extraction candidate: `emit_error_envelope(reason_code, request, hint=None) → JsonResponse` that wraps 3-line pattern + auto-infers `status` from `ReasonCode.typical_status`. Watch for 2nd batch usage; if pattern holds, extract in Batch 3 or as separate refactor.
  - **Fold C `future_trigger`** — DRF-decorator refactor for 5 inline auth checks in views_revenue_analytics (and any similar pattern in future batches). Larger behavioral surface; separate arc.
  - **Fold D `informational`** — 3rd continuous-cascade instance. Watch for 4th.
  - **Operator-envelope-from-explicit-emissions** wiring — full substrate change to `build_user_facing_envelope` API OR new `emit_error_with_operator_envelope` helper. Currently: interim structured logging via `logger.warning`. Not on roadmap.

- **T-ENVELOPE-2-DEPRECATION queue after Batch 1:**
  - **Batch 2** (S3007 candidate): `core/auth_middleware.py` (10 call-sites) — middleware placement invariants require extra care per PLAYBOOK 3.2.3-ish patterns; likely 1 session.
  - **Batch 3** (S3008 candidate): `core/views_auto_distribution.py` (25 call-sites) — 2 sessions if verbose.
  - **Batch 4** (S3009-3010 candidate): `core/views_platform_integrations.py` (62 call-sites) — 2 sessions minimum.
  - **Batch 5** (post-2-4): `core/api_helpers.py` disposition — separate substrate arc.

## Governance

No Playbook amendments this session. No ADR authored (ADR-0007 was ratified S3005; this session implements §4.3).

**Ratification workflow:**
- Chris joint agreement reached with Rigby BEFORE implementation (per `feedback_claude_rigby_agree_first_chris_yes_no`)
- Course-correction opportunity framed for Chris (per `feedback_plain_english_decision_framing_for_chris` — variant on Chris-facing decision framing; Chris said "proceed" = no course-correction needed)
- Rigby A2 SIGN pre-merge with substantive tool_runs (per PLAYBOOK-7.7.2)
- STRENGTHENs folded pre-merge, not deferred (per PLAYBOOK-6.10.9)
- Backend-only diff → `make celery-recycle` per `feedback_recycle_after_merge` + `feedback_local_truth_no_production`

## Wrapper pin

Retired at close: `pa-b5f66b31fc014f34` (S3005 mint). Minted for S3007: (assigned by `session_lifecycle close --label s3006-t-envelope-2-deprecation-batch-1`). Wrapper `tools/pa_local.sh` atomically rewritten and committed in the S3006 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
