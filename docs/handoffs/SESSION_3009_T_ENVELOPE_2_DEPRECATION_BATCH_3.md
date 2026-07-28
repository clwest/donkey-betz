---
title: "SESSION 3009 — T-ENVELOPE-2-DEPRECATION B1 auth_middleware retrofit + Batch 3 views_auto_distribution"
session: 3009
date: 2026-07-27
type: two_pr_close
merge_shas:
  - "75aa57631"   # PR #3691 — B1: 9-site auth_middleware retrofit warm-up
  - "546985106"   # PR #3692 — Batch 3: 25 sites in views_auto_distribution.py
prs:
  - 3691
  - 3692
related_arcs:
  - "ADR-0007 Layered Envelope Policy (ratified S3005)"
  - "I-0301 Failure-Data Safety Contract (Family E authorizing substrate)"
consumes:
  - "S3008 close cascade — Fold A `future_trigger` promoted to S3009 Option B1 recommendation"
  - "S3008 helper substrate — emit_error_envelope() from core/security/error_envelope.py:117-154"
  - "ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION T-slot (Batch 3 of 5 file-scoped batches)"
---

# S3009 — T-ENVELOPE-2-DEPRECATION B1 auth_middleware retrofit + Batch 3 views_auto_distribution

**Status:** CLOSED. 2 feature PRs merged. `core/auth_middleware.py` now at **0 raw-pattern sites** (all 10 emit sites use the helper). `core/views_auto_distribution.py` fully migrated (25 sites) and added to the lint MIGRATED_FILES tuple (**3 → 4 tracked files**). HEAD `546985106`.

## Session shape

Two-PR sequential close following the S3008 joint recommendation shape. Flow: B1 warm-up (spec pre-ratified at S3008) → Rigby A2 SIGN → merge → `make restart` → live-smoke → A Phase 1 (Rigby A1 SIGN on Batch 3 mapping table) → A Phase 2 migration → A2 SIGN → merge → `make restart` → 4-site smoke → close cascade. **6th consecutive continuous S-cascade** (see Fold D). One substantive Rigby hallucination detected and resolved at A2 D3 (see Fold A — new pattern, first trigger).

## PR #3691 (`75aa57631`) — B1: 9-site auth_middleware retrofit warm-up

**Scope (1 file, +41 / -59 = -18 net):** Retrofit the 9 remaining raw 3-line envelope-emit pattern sites in `core/auth_middleware.py` to the `emit_error_envelope()` helper shipped at S3008 (PR #3689). File is now at 0 raw sites, all 10 emit sites use the helper.

Sites converted (all auto-infer `typical_status` from `ReasonCode`; no explicit `status_code=` kwargs):

| Line | Source key | reason_code | Status |
|------|-----------|-------------|--------|
| 85  | `decorator_missing_token` | `not_authenticated` | 401 |
| 628 | `session_staff_required` | `permission_denied` | 403 |
| 637 | `session_reviewer_blocked_path` | `permission_denied` | 403 |
| 646 | `session_reviewer_write_blocked` | `permission_denied` | 403 |
| 685 | `auth_backend_unavailable` | `busy` | 503 |
| 693 | `invalid_token` | `not_authenticated` | 401 |
| 703 | `token_staff_required` | `permission_denied` | 403 |
| 712 | `token_reviewer_blocked_path` | `permission_denied` | 403 |
| 720 | `token_reviewer_write_blocked` | `permission_denied` | 403 |

Hint dicts preserved verbatim. Pre-emit f-string operator logs (`Staff access required...`, `Invalid authentication token...`) preserved. S1171 auth-backend-unavailable intent comment block preserved verbatim above the `busy` emit.

**Import cleanup:** dropped unused `build_user_facing_envelope` from the import line — no callers remain in file after this PR. `JsonResponse` retained (still used by `RateLimitingMiddleware` inline 429 at line 935 — S3007 Fold E carry-forward, out of B1 scope; see Fold E).

**Rigby A2 SIGN (task 03:51 UTC):** AGREE D1/D2/D3/D4 with tool-grounded line citations (`repo_tool.search` for `reason_code='` + `emit_error_envelope(` + `build_user_facing_envelope`, `read_file` on rate-limit region). **D5 PARTIAL — Rigby-tool-surface limitation** (no shell-exec surface to run `lint_no_deprecated_family_b.py` or `manage.py check`); code-level indicators clean. Substantive per PLAYBOOK-7.7.2 (Rigby offered to inspect MIGRATED_FILES tuple if requested). **Zoom-out Z1**: notes coupling risk low (mechanical transform, single module), invalid_token/no_credentials standardization to 401 (accepted), dual-logging f-string+helper rationale documented in file header — approves B1 as-is.

**Live-smoke (post `make restart`):** curl unauthed `/api/workspaces/` → 401 + Family E envelope + `envelope_emit reason=not_authenticated support=RUR-AUTH-260728-97a1 hint={'source': 'no_credentials'}` sourced from `error_envelope` module (S3008 proof site at line 660). Curl w/ invalid token → 401 + support_code `RUR-AUTH-260728-f35f` + `hint={'source': 'invalid_token'}` — this directly verifies one of the 9 B1-converted sites (L693). Both paths preserve pre-emit `auth_middleware` f-string log; helper is the emit source.

## PR #3692 (`546985106`) — Batch 3: 25 sites in views_auto_distribution.py

**Scope (2 files, +167 / -26 = +141 net):** All 25 `return api_error(...)` sites in `core/views_auto_distribution.py` converted to `return emit_error_envelope(...)`. Covers all 6 endpoints: `create_auto_distribution` (8 sites), `batch_distribute` (5), `reschedule_distribution` (4), `cancel_scheduled_distribution` (3), `auto_distribution_settings` (2), `apply_distribution_template` (3).

**Reason-code taxonomy:**

| Reason code | Count | Sites |
|---|---|---|
| `not_authenticated` (401) | 6 | 77, 297, 468, 515, 576, 734 |
| `invalid_input` (400) | 9 | 82, 87, 142, 302, 306, 487, 603, 739, 751 |
| `validation_error` (400) | 6 | 96, 109, 309, 327, 479, 526 |
| `not_found` (404) | 4 | 122, 130, 476, 523 |

All 25 sites auto-infer `typical_status`; no explicit `status_code=` kwargs.

**Behavior change (Rigby A1 D3 flag, documented in PR description):** `create_auto_distribution` Image/Video not_found paths at L122/L130 previously returned implicit **HTTP 400** via `api_error` default; under `reason_code='not_found'` they now return **HTTP 404** — semantically correct and consistent with the two `reschedule/cancel Distribution not found` sites that already used `status_code=404`. Consumers keyed on 400 for these two paths must be updated to handle 404. Not verified in live-smoke (would require setting up UserPlatformAccount test data for chris); flagged as forward-carry test-data-needed if a consumer regresses.

**Rigby A1 D4 optional enhancements applied:**
- L109 + L327 (`no_matching_platforms`): added `requested_platforms` to hint dict (target_platforms / platforms local var respectively).
- L479 + L526 (`invalid_state`): added `allowed_statuses: ['draft', 'pending']` alongside existing `current_status`.

**Defensive dict access (Rigby A1 Z1 sub-ask):** Both Image and Video not_found paths use `data.get('image_history_id')` / `data.get('video_history_id')` in the hint dict — defensive per Z1 concern about reachability without the key.

**Import cleanup:**
- Dropped `api_error` from `from core.api_responses import ...` (0 callers remain in file).
- Kept `api_success` (still used at ~13 200/201-response sites).
- Added `from core.security.error_envelope import emit_error_envelope`.

**Lint gate update:** Added `core/views_auto_distribution.py` to `MIGRATED_FILES` tuple in `scripts/lint_no_deprecated_family_b.py` (**3 → 4** tracked files). Comment block noting Batch 3 provenance.

**Rigby A1 SIGN (task 03:58 UTC):** AGREE 5/5 with tool-grounded enumeration of all 25 sites (grouped by function with per-endpoint code excerpts). One nuance callout on D2 (agreed with `validation_error` for `no_matching_platforms` per business-precondition framing). One behavior-change flag on D3 (Image/Video 400→404 — accepted). Two optional D4 enhancements (both applied).

**Rigby A2 SIGN (task 04:04 UTC):** AGREE D1/D2/D4/D5, **DISAGREE D3** — but the DISAGREE was **spurious**. Rigby quoted `'id': data.get('video_history_id'),` in her evidence excerpt then labeled it "not defensive" and said "should be `data.get('video_history_id')`" (identical string). Re-verify dispatched: Rigby then claimed the file bytes were `'id': data['video_history_id'],` (direct indexing). Independent verification via 3 channels — my Read, my Grep, and `git show HEAD:core/views_auto_distribution.py | sed -n '167,170p'` — all showed defensive `.get()` at L169. Definitive push-back dispatched with 3-channel proof; Rigby then confirmed **AGREE — proceed to merge, and log the ledger entry**. Effective A2 verdict: AGREE 5/5. See Fold A (new pattern, first trigger — Rigby LLM-side hallucination, not tool bug).

**Live-smoke (post `make restart`) — 4 sites verified out of 25:**

| Smoke | Path | Auth | Expected | Actual | Support code |
|---|---|---|---|---|---|
| 1 (curl) | POST `/api/distribution/auto/create/` | unauthed | 401 + `not_authenticated` L77 | ✓ HTTP 401 | `RUR-AUTH-260728-dfba` |
| 2b (Client) | POST `/api/distribution/auto/create/` | session | 400 + `invalid_input` json_decode L82 | ✓ HTTP 400 | `RUR-INPUT-260728-12ae` |
| 3b (Client, bonus) | POST `/api/distribution/auto/create/` | session | (intended L122 not_found but chris has no connected accounts) | ✓ HTTP 400 + `validation_error` L96 no_platforms_connected | `RUR-VALIDATE-260728-0e59` |
| 4b (Client) | POST `/api/distribution/templates/apply/` | session | 400 + `invalid_input` unknown_template L751 | ✓ HTTP 400 + `hint={'template': 'nonexistent_template'}` preserved | `RUR-INPUT-260728-4c5d` |

All 4 log source = `error_envelope` module (helper). All hint dicts preserved including D4 enhancements. `/api/distribution/` is in `PUBLIC_PATHS` (auth middleware skips), so unauthed requests hit view-layer L77 not_authenticated check with AnonymousUser — this is the actual code path being exercised, not middleware auth.

## Folds

### Fold A — Rigby LLM-side hallucination on file-level code claim (**1st trigger — new pattern**)

**Trigger:** Rigby A2 D3 on PR #3692 (04:04 UTC). Verdict text contradicted own `repo_tool.read_file` excerpt (both showed `.get()`; verdict claimed "not defensive"). Re-verify then hallucinated different file bytes (`data['video_history_id']` direct) than what git blob confirmed. Ledger-worthy because:
- (a) `repo_tool` output was internally consistent (correct bytes)
- (b) LLM synthesis contradicted its own tool output
- (c) Re-verify amplified rather than corrected the hallucination
- (d) Only Claude's independent 3-channel verification (Read + Grep + `git show HEAD:...`) caught it
- (e) Rigby acknowledged the mistake was on her side, not a tool bug

**Consolidation candidate:** Extends memory rule `feedback_verify_rigby_tool_runs_before_trusting_sign` from "empty tool_runs = rubber-stamp signal" to "**substantive tool_runs + verdict text contradicting the tool_run excerpt = hallucination signal — verify at raw file/git-blob before accepting DISAGREE**".

**Rigby Tool Gap Ledger workspace:** `b4503364-2573-4401-9e28-61a739e0ce50` (`deliverable_type='engineering_backlog'`). Entry to be created post-close.

**Threshold:** 1 trigger. Watch for 2nd/3rd before formalizing into Playbook amendment. Not a 3rd-trigger cascade yet.

**Class assignment:** Distinct from S3008 Fold B (`repo_tool.search` no total_matches — that's a tool-surface limitation). This is LLM-side (Rigby-response-synthesis). Two different substrate arcs.

### Fold B — Middleware/view restart discipline (**3rd trigger — Fold C precedent extended**)

S3007 Fold C = 1st trigger (learned rule: middleware/URL/settings/installed_apps → `make restart`, not `make celery-recycle`). S3008 Fold C = 2nd trigger (successful pattern application). S3009 = 3rd trigger — both PRs required `make restart` and used it from outset. PR #3691 was middleware, PR #3692 was view module — both Daphne-request-path.

**3-trigger threshold met** per `project_deployment_state_between_merged_and_active.md` pattern (four-trigger for stricter cases; three-trigger for less risky). Consider Playbook amendment: extend `feedback_recycle_after_merge` with explicit rule "Any change to files loaded by Daphne request path (middleware / views / URLs / settings / installed_apps) requires `make restart` or `make recycle-all`, not `make celery-recycle` alone."

**Deferral rationale:** The `feedback_recycle_after_merge` memory rule already contains this in its "S2978 refinement" body. This 3rd trigger CORROBORATES the existing rule; it doesn't require a new one. Formalization into PLAYBOOK-7.4.5 or extension of PLAYBOOK-7.4.4 could happen at S3010 or a dedicated Playbook amendment session — not urgent.

### Fold C — Rigby A2 D5 PARTIAL: shell-exec tool-surface gap (**1st trigger — new capability need**)

**Trigger:** PR #3691 A2 SIGN D5. Rigby noted she can't execute `python scripts/lint_no_deprecated_family_b.py --list` or `python manage.py check` via `repo_tool` — those are shell operations, `repo_tool` is file-read/search only. Code-level indicators clean (raw pattern count = 0 grep, MIGRATED_FILES tuple correct), but she couldn't run the actual gate.

**Rigby Tool Gap Ledger candidate:** Add a `shell_read_only_exec` capability to Rigby tool surface (or dispatch to a `repo_tool.run_command` action with a whitelist of read-only commands: `python manage.py check`, `python scripts/lint_*.py`, `grep`, `pytest --collect-only`).

**Ledger workspace:** `b4503364-2573-4401-9e28-61a739e0ce50`. Entry to be created post-close.

**Distinct from Fold A:** Fold A is LLM-side hallucination; Fold C is tool-surface capability gap. Both go to the same ledger workspace but as separate entries.

### Fold D — 6th consecutive continuous S-cascade (**class distinction: same-arc-scope batch progression**)

S3002→S3003→...→S3007→S3008→S3009 = 6 continuous cascades. S3007→S3008 = "helper-extraction-after-batch-completion" (sub-shape). S3008→S3009 = "helper-substrate-consumption-across-batches" (sub-shape — S3008 shipped helper, S3009 consumed it in Batch 3 + retrofitted Batch 2 leftovers). Continuous-cascade pattern now at **6 instances across ≥3 sub-classes**.

**Observation stays on the queue.** No amendment triggered. Watch for cascade-class break — e.g., if S3010 does NOT continue T-ENVELOPE-2-DEPRECATION (unlikely per queue: Batch 4 = 62 sites in views_platform_integrations, which is next per S3008 close-out plan).

### Fold E — RateLimitingMiddleware inline 429 dict (**S3007 carry-forward, still open**)

`core/auth_middleware.py:935` still uses inline `JsonResponse({'success': False, 'error': {'code': 'rate_limited', ...}}, status=429)` pattern (Family B shape) in `RateLimitingMiddleware.process_request`. Now trivial with helper: `return emit_error_envelope(reason_code='rate_limited', request=request, retry_after_seconds=N)`. ~15 min PR.

**S3009 status:** Chris did not respond to the yes/no ask embedded in the B1 per-PR summary + A Phase 1 dispatch on whether to fold Option C into S3009. Default = defer to S3010. Rigby A2 Z1 didn't push back on the deferral. Still on carry-forward queue.

**Trigger for S3010:** Chris ratification of "yes bundle Fold E into S3010" OR standalone opportunity (e.g., someone hits a rate limit in prod and asks for consistent envelope shape).

## Forward carries (open at S3009 close)

### New from S3009

- **Fold A `1st trigger` (Rigby LLM-side hallucination on file-level code claim)** — Ledger entry post-close. Watch for 2nd trigger before formalizing.
- **Fold B `3rd trigger` (middleware/view restart discipline)** — Threshold met; consider Playbook amendment as Ch 7 §7.4 extension.
- **Fold C `1st trigger` (Rigby shell-exec tool-surface gap)** — Ledger entry post-close. Watch for 2nd trigger before capability expansion arc.
- **Fold D `6th cascade`** — Observation stays; watch for break.
- **Fold E `future_trigger` (carry-forward S3007)** — RateLimiting 429 → helper. Chris deferred implicitly.
- **Batch 3 400→404 behavior change verification** — direct live-smoke skipped for lack of test data. Forward-carry: consumer regression check OR write a management-command probe that creates a UserPlatformAccount + tests the L122/L130 flow.

### T-ENVELOPE-2-DEPRECATION queue after S3009

- **S3010 (candidate primary directive):** Batch 4 — `core/views_platform_integrations.py` (62 sites). 2-3 sessions minimum with helper. Highest-value remaining migration by site count.
- **Batch 5 (post-Batch 4):** `core/api_helpers.py` disposition — separate substrate arc. Currently: Family B helpers with deprecation docstrings; disposition = retire vs keep-with-warning.

### Carried from S3008 (STILL OPEN)

- **Fold A `future_trigger` (SHIPPED at S3009 as B1)** — RESOLVED. Retrofit done.
- **Fold B `1st trigger`** — `repo_tool.search` no `total_matches` field. Ledger workspace `b4503364-2573-4401-9e28-61a739e0ce50`. Distinct from S3009 Fold C (that's shell-exec gap; this is search-result-count gap).
- **Fold C `2nd trigger` (SUPERSEDED by S3009 Fold B 3rd trigger)** — middleware-restart discipline. See S3009 Fold B for continuation.
- **Fold D `5th continuous cascade` (SUPERSEDED by S3009 Fold D 6th cascade)** — see S3009 Fold D.
- **Fold E `future_trigger` (carried through S3009 as Fold E, still open)** — RateLimiting 429.

### Older carry-forward (STILL OPEN)

_[See S3008 handoff §Forward carries for complete inherited list — S3005-S2989 items unchanged this session.]_

## HEAD at close

- Merge commit for B1: `75aa57631` (PR #3691)
- Merge commit for Batch 3: `546985106` (PR #3692)
- Close cascade PR (this file + 00-START refresh + INDEX regen + wrapper pin bump): TBD

## Cross-cutting workflow references

- **Constitutional governance:** Playbook v0.10.0. No amendments this session. Fold B (3rd trigger) is the closest candidate for a v0.11.x MINOR — extends existing feedback rule into Ch 7 §7.4.
- **ADR corpus:** ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION now at **4-of-5 files migrated** (was 3-of-5 at S3008 close). `views_platform_integrations.py` and `api_helpers.py` remaining.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **2× Flow B clean spec→ship** this session (B1 = helper substrate pre-ratified at S3008 A2, straight to A2; Batch 3 = full A1→implement→A2→ship cycle). Both PRs merged same-session.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. 3× Rigby SIGN cycles this session (B1 A2 + Batch 3 A1 + Batch 3 A2), all substantive per rule. **Plus 2× re-verify dispatches on the Fold A hallucination** — Rigby's third response acknowledged the mistake was hers, not the tool's.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. 1 mid-flight decision surface (Fold E in-S3009 vs S3010) — not answered by Chris; default = defer applied. Otherwise executed to plan without Chris intervention (session-open "Please begin" opener + jointly recommended B1+A shape from S3008 close).
- **Recycle discipline:** middleware/view diff → `make restart` used correctly on both PRs from outset (Fold B 3rd trigger).
