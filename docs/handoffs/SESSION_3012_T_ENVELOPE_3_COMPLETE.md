---
title: "SESSION 3012 — T-ENVELOPE-3 arc CLOSED: api_helpers.api_error retired across 72 real caller sites"
session: 3012
date: 2026-07-28
type: multi_pr_arc_close_with_helper_retirement
merge_shas:
  - "04bc553ea"   # PR #3701 — PR 1: views_ab_testing.py 36 sites (dead + wired)
  - "3cffe6f0d"   # PR #3702 — PR 2: views_learning_loop.py 24 sites (auth guards + validation)
  - "055bd8734"   # PR #3703 — PR 3: views_rag_observability.py 12 sites + bundled status_code kwarg bug fix
  - "dd2a527ee"   # PR #3704 — PR 4: retire api_error() from core/api_helpers.py + ADR-0007 §4.3 close-note
prs:
  - 3701
  - 3702
  - 3703
  - 3704
arcs_closed:
  - "T-ENVELOPE-3 — retire api_helpers.api_error across all real caller sites (successor to T-ENVELOPE-2-DEPRECATION which closed at S3011)"
related_arcs:
  - "ADR-0007 §4.3 Layered Envelope Policy (T-ENVELOPE-3 out-of-scope disposition CLOSED)"
consumes:
  - "S3011 00-START primary directive (T-ENVELOPE-3 successor arc)"
  - "S3011 audit (92 caller sites — real count was 72 after false-positive reality-check)"
---

# S3012 — T-ENVELOPE-3 arc CLOSED

**Status:** CLOSED. Four PRs shipped (3701 → 3702 → 3703 → 3704). `api_helpers.api_error` fully retired. Zero real callers remain. `ImportError` at the Python import layer confirms retirement (stronger than any lint). HEAD `dd2a527ee`.

**Massive audit reality-check:** S3011 close-out audit counted 92 caller sites across 4 primary + 6 minor files. Real count was **72 sites across 3 files** — 20 grep hits were false positives (11 `except Exception as api_error:` variable names in `tasks_conversations.py`; 6 string literal `'api_error'` error-type labels in 6 minor files that were never actual callers). PRs 4/5 planned in S3011 collapsed to nothing; the actual PR 4 became the trivial helper retirement.

## Session shape

Four sequential PRs following the S3012 00-START recommended shape (per-file mini-PRs), with two audit-driven pivots:

1. **PR 1 (04bc553ea)** — `core/views_ab_testing.py` 36 sites. Dead-code discovery: 26 of the 36 sites live in dead A/B testing handlers (URL routes removed at S1103c per `docs/audit-2026/HALF_BUILT_FEATURES_AUDIT.md`); only 10 sites in wired `/api/goals/*` handlers. Rigby DECIDE Shape A: migrate all 36 to prevent str(e) leaks if re-exposed. Header comment marks the dead block. Follow-up task #7 queued for dead-handler deletion.
2. **PR 2 (3cffe6f0d)** — `core/views_learning_loop.py` 24 sites. First use of a Python migration script (15 boilerplate auth-guards). Script had line-shift bugs (3 source-name mis-attributions + 1 orphaned `insight.is_dismissed = True` line). Self-audit script caught all 4 pre-ship. Rigby Tool Gap Ledger entry queued (task #9, dispatched at close as workspace deliverable `505dbdc1-9184-478a-b186-1f9e3912807a`).
3. **PR 3 (055bd8734)** — `core/views_rag_observability.py` 12 sites + **bundled behavior-restoration bug fix**. 10 sites used `status_code=` kwarg which `api_error` REJECTS (`(message, status=400, errors=None)`). Prior behavior: TypeError → middleware caught → generic 500. Intent: 401/403/500 per site. Migration to `emit_error_envelope()` (typical_status inference) incidentally restores intended semantics. Live smoke verified: `curl /api/rag/observability/dashboard/` now returns HTTP 401 with clean Family E envelope (was silently 500 pre-PR).
4. **PR 4 (dd2a527ee)** — 1-line function retirement + module docstring update + ADR-0007 §4.3 close-note (Rigby-suggested "(Close-note; no policy change)" clarifier adopted). `python -c 'from core.api_helpers import api_error'` → `ImportError` confirms retirement.

**Chris interactions during session:** brief. Chris ratified initial arc kickoff ("Begin with T-ENVELOPE-3"), aggressive pipelining ("continue with PR 3" / "continue with PR 4" mid-flight), single scope check ("It looks like we have two follow-ups and a Rigby tool gap will those be included in the close cascade or do we need to do them first?"), and close cascade ("Proceed"). All PR-level shape decisions handled Claude ↔ Rigby per `feedback_claude_rigby_agree_first_chris_yes_no`.

## PR #3701 (`04bc553ea`) — PR 1: views_ab_testing.py 36 sites

**Scope (3 files, +317/-37):**
- `core/views_ab_testing.py` (+247/-37): 15 exception fallbacks → `internal_error` (500) with `logger.exception` + `hint={source, exc_type}` (str(e) leaks eliminated); 10 not_found (404); 3 missing_field + 2 invalid_json → invalid_input (400); 6 validation state-transitions → validation_error (400). Dead-code header comment added at top marking L~40-501 as dead handlers pending HALF_BUILT_FEATURES_AUDIT deletion.
- `core/tests/test_s3012_ab_testing_envelope.py` (+100 new): 5 tests — not_found / invalid_input missing-field / invalid_input json-decode / invalid_input missing-current-value / internal_error + secret-leak assertion (`assertNotIn('db-blew-up-secret-connstring', body)` PASS).
- `scripts/lint_no_deprecated_family_b.py` (+6): file added to MIGRATED_FILES (6-of-N locked).

**Rigby SIGN:** A1 (8 tool_runs — repo_tool.search × 4, repo_tool.read_file × 4): AGREE mapping + primary risk + import plan + 4 STRENGTHENs (add tests / bare `logger.exception` / omit `status_code` / MIGRATED_FILES). DECIDE bundle single PR + Option A logging. A1 follow-up (dead-code discovery): DECIDE Shape A (migrate all 36). A2 (4 tool_runs): AGREE scope/mechanics/tests. 3 informational STRENGTHENs (hint schema drift low-severity, dead-code testing sufficient via py_compile+grep, pyright variants type debt orthogonal). **DECIDE: Ship it.**

**Smoke:** post-`make recycle-all` at sha `04bc553ea33d` — `curl /api/goals/` returned Family E envelope with fresh `RUR-AUTH-260728-3415`.

## PR #3702 (`3cffe6f0d`) — PR 2: views_learning_loop.py 24 sites

**Scope (3 files, +210/-25):**
- `core/views_learning_loop.py` (+123/-25): 15 auth-required → `not_authenticated` (401) with per-handler source; 3 not_found; 3 invalid_json; 2 missing_field; 1 orchestrator-returned-False → `validation_error` (400) at L1054 track_learning_outcome with `hint={source, reason='track_failed'}`. No logger added (0 str(e) sites).
- `core/tests/test_s3012_learning_loop_envelope.py` (+83 new): 5 tests — unauthenticated / not_found / invalid_json / missing_field / validation_error (Rigby A2 optional add-on).
- `scripts/lint_no_deprecated_family_b.py` (+4): file added to MIGRATED_FILES (7-of-N).

**Rigby SIGN:** A1 (5 tool_runs): AGREE mapping + no-logger reasoning + L1054 → validation_error to preserve 400 semantics. STRENGTHEN assert hint structure `{source, reason}` in tests. DISAGREE inline DRF decorator refactor (defer as follow-up task #8). DECIDE mechanical migration. A2 (8 tool_runs): AGREE + AGREE ledger entry + narrow Playbook rule candidate. **DECIDE: Ship PR 2** + suggested optional validation_error test (adopted as test #5).

**Migration-script line-shift bugs — caught pre-ship via self-audit:**
- **Class 1 — Source-name mis-attribution (3 sites):** L812 mark_insight_read had `source='get_performance_comparison'` (leaked from previous handler iteration in script's `handler` closure variable); L1101 + L1110 track_learning_outcome had `source='get_agent_learnings'`; L615 update_learning_profile had `source='list_insights'`. Root cause: handler boundary calculations became stale after each in-place text insertion shifted line numbers.
- **Class 2 — Wrong-block insertion (1 site):** The 'Insight not found' migration for `dismiss_insight` landed at wrong line INSIDE the try block, orphaning `insight.is_dismissed = True`. Detected only via `git show HEAD` comparison.
- **Rescue mechanism (proves audit is feasible):** Second Python script that walked each `'source': 'X'` hint and cross-referenced containing `def` line via handler boundary regex. 4 mismatches surfaced + fixed manually before A2 SIGN.

**Rigby Tool Gap Ledger entry dispatched** at close cascade: workspace deliverable `505dbdc1-9184-478a-b186-1f9e3912807a` in workspace `b4503364-2573-4401-9e28-61a739e0ce50` (`engineering_backlog`).

**Smoke:** post-`make recycle-all` at sha `3cffe6f0d896` — `curl /api/learning/loop/stats/` returned HTTP 200 with real data (70 active learnings, 4312 applied); code loaded cleanly.

## PR #3703 (`055bd8734`) — PR 3: views_rag_observability.py 12 sites + status_code bug fix

**Scope (3 files, +148/-13):**
- `core/views_rag_observability.py` (+73/-12): 9 auth → `not_authenticated` (401); 1 staff → `permission_denied` (403); 1 exception → `internal_error` (500) + `logger.exception` + str(e) leak elimination (was `f"Classification failed: {str(e)}"`); 1 missing_field → invalid_input (400). Uniform `source='rag_observability'` for the 8 auth sites (single subsystem; endpoint already logged by `emit_error_envelope`).
- `core/tests/test_s3012_rag_observability_envelope.py` (+67 new): 2 tests — unauthenticated_dashboard_returns_401_not_500 (locks bug fix) + internal_error_no_secret_leak (locks str(e) elimination). One test dropped: `permission_denied` test hit unreachable code because `rag_run_classification` has `@superuser_required` decorator that intercepts BEFORE the in-view is_authenticated + is_staff checks.
- `scripts/lint_no_deprecated_family_b.py` (+8): file added to MIGRATED_FILES (8-of-N).

**Bundled bug fix — behavior restoration.** 10 of 12 sites used `status_code=` kwarg that `api_error()` REJECTS (its signature is `(message, status=400, errors=None)`). Prior behavior: TypeError → middleware caught → generic 500 envelope. Intent: 401/403/500 per site. This PR restores intended semantics via `emit_error_envelope()` typical_status inference. **Live smoke post-recycle proved the fix:** `curl /api/rag/observability/dashboard/` returned HTTP 401 with clean Family E envelope + fresh `RUR-AUTH-260728-8133`.

**Discovery (defensive fallback note):** `rag_run_classification` in-view auth/staff checks (L271-284) are unreachable via URL router — `@superuser_required` decorator runs first with its own legacy Family B envelope (`{success: false, error: ...}`, status 401/403). The `superuser_required` decorator itself is a Family B → Family E migration candidate for a separate arc.

**Rigby SIGN:** A1 (compact re-request after truncated verdict): AGREE bundle bug fix + ship without frontend grep (500-behavior was buggy; anything coupling to it was also buggy). STRENGTHEN behavior-restoration language + tests asserting 401/403/500 + str(e) invariant. DECIDE one PR. A2 (5 tool_runs): AGREE ready to ship + drop-unreachable-test correct. DISAGREE bundling api_helpers.api_error retirement into this PR (higher substrate change; cleaner rollback boundary). **DECIDE: Merge as-is** + separate PR 4 for retirement.

## PR #3704 (`dd2a527ee`) — PR 4: retire api_error() + ADR-0007 §4.3 close-note

**Scope (2 files, +24/-9):**
- `core/api_helpers.py`: delete `api_error()` function (was L73-81); add Session 3012 retirement note in module docstring pointing to `emit_error_envelope`.
- `docs/adr/ADR-0007-layered-envelope-policy.md` §4.3: append execution-record close-notes for both T-ENVELOPE-2-DEPRECATION (S3011) and T-ENVELOPE-3 (S3012), citing all 4 PR SHAs and the S3011 audit reality-check finding. Rigby-suggested "(Close-notes below are execution records, not policy changes.)" clarifier included per ADR-0001 §3.6 discipline.

**Verification:**
- `python -c 'from core.api_helpers import api_error'` → `ImportError: cannot import name 'api_error'` (retirement confirmed at Python import layer — stronger than any lint).
- `python scripts/lint_no_deprecated_family_b.py` → OK (8 files, 32 grandfathered).
- Grep sweep: zero `import api_error` from `api_helpers` across the codebase.

**Kept the deprecation lint's `\bapi_error\s*\(` regex as belt-and-suspenders** — zero cost, catches regression if the helper is ever re-added.

**Out-of-scope stragglers preserved:**
- `agents/views_monitoring.py:16` uses `core.api_responses.api_error` (DIFFERENT function, DIFFERENT signature). Separate arc candidate.
- `core/error_messages.py::parse_api_error` is unrelated (different helper).

**Rigby SIGN:** A2 (5 tool_runs, then compact re-request): AGREE ready to ship. ADR §4.3 in-place amendment appropriate for close-notes per ADR-0001 §3.6 (execution records, not decision changes). STRENGTHEN "(Close-note; no policy change)" clarifier + capture merge SHA. DISAGREE adding a new §4.6 close-block (adds structure without meaning; increases drift risk). **DECIDE: Merge as-is with the clarifier.**

**Smoke:** post-`make recycle-all` at sha `dd2a527ee77a` — `curl /api/goals/` (PR 1 migrated endpoint) returned Family E envelope with `RUR-AUTH-260728-a248`. All 3 migrated view files load cleanly.

## Session folds

### Fold A `1st trigger` — S3011 audit counted grep matches, not real callers

**Class:** informational, low-severity. **Same-PR mitigation:** NO (captured in handoff + task #10). **Trigger count:** 1. **Watch for:** 2nd trigger before promoting to Playbook rule.

**Details:** S3011 close-out audit counted `api_error` caller sites via `grep -c "\bapi_error\b"`. This yielded 92 across 4 primary + 6 minor files. Real callers (call sites, not variable names or string literals) were 72 across 3 primary files. The 20 false positives:
- `tasks_conversations.py`: 11 grep hits were `except Exception as api_error:` — using `api_error` as an exception variable name (Python `as` binding).
- 6 "minor files" (2 tests + 2 services + 2 models): 6 grep hits were all string literal `'api_error'` used as an error-type classification label (Django CHOICES field / classify_error() return / list of error-type strings).

**Impact:** PR 4 (retire helper) became trivial 1-line deletion instead of full ~30-line migration. PRs 4/5 planned in S3011 collapsed to nothing.

**Mitigation candidate:** future arc audits should count `grep -c "\bapi_error\s*\("` (with open paren) instead of `\bapi_error\b`, OR use AST-aware caller detection. First trigger only — do not codify yet.

### Fold B `2nd trigger` — Migration-script text-replacement without line-offset tracking

**Class:** tooling gap, mitigable. **Same-PR mitigation:** YES (self-audit script caught 4 mismatches pre-ship). **Trigger count:** would be 1st for THIS specific pattern (in-place text-replacement). **Watch for:** 2nd trigger before Playbook rule; **workspace deliverable `505dbdc1-...` already logged.**

**Details:** See PR #3702 section above. Fold triggers Playbook rule candidate: "Any scripted multi-site migration must include an automated post-pass audit that checks (1) per-handler source matches containing def, and (2) envelope emission is in the correct exception/control block." Deferred pending 2nd trigger.

### Fold C `informational` — In-view auth/staff checks unreachable behind @superuser_required decorator

**Class:** informational, deferred. **Same-PR mitigation:** NO (out of scope — deleting unreachable checks was scope creep past T-ENVELOPE-3).

**Details:** `rag_run_classification` (PR #3703) has `@superuser_required` decorator that intercepts BEFORE the in-view is_authenticated + is_staff checks. Those in-view checks (L271-284) are dead code but were migrated as defensive fallback. **`superuser_required` decorator itself is a separate Family B → Family E migration candidate** (returns `{success: false, error: "..."}` legacy shape). Deferred to future arc — possibly T-ENVELOPE-4.

### Fold D `1st trigger` — Aggressive pipelining safe when audits are read-only

**Class:** workflow, informational. **Same-PR mitigation:** N/A. **Trigger count:** 1. **Watch for:** 2nd trigger.

**Details:** Chris directive mid-flight ("continue with PR 3" / "continue with PR 4") had me start PR 3 audit + PR 4 audit while PR 2 tests were still running. I paused before code writes to avoid branch conflicts on `MIGRATED_FILES`. Chris flagged: "Shit I just saw you are waiting for PR 2, don't let me fuck things up!!" — but the parallel audit-in-background approach WAS safe (read-only greps + reads don't create merge conflicts). It also surfaced the PR 4 no-op discovery earlier, saving one full A1→A2→ship cycle. Pattern: **during test wait cycles, forward-scout the next PR's audit + Rigby A1 is safe. Code writes still gate on prior PR merge.**

### Fold E `informational` — Test-writing gotcha: handler-side ordering matters

**Class:** test-authoring lesson. **Same-PR mitigation:** YES (2 tests re-written mid-PR).

**Details:** Twice in this session, tests failed because I assumed handler-branch ordering.
- PR #3701: `update_goal_progress` runs `UserGoal.objects.get()` BEFORE validating `current_value`. Test with random UUID + missing current_value returned 404 (from DoesNotExist), not 400 (from validation). Fixed by creating a real UserGoal fixture.
- PR #3703: `rag_run_classification` has `@superuser_required` decorator BEFORE in-view checks. Test with non-superuser returned decorator's legacy 401/403 envelope, not my Family E `permission_denied`. Fixed by using a real superuser for the internal_error test + dropping the permission_denied test.

Same-class lesson: **read the handler function top-to-bottom to identify which check fires first before writing tests that exercise a specific branch.** Not a rule — just an internal practice.

## Forward carry (S3013 candidates)

### High-priority engineering (task list)

- **Task #7 — Delete dead A/B testing handlers** per HALF_BUILT_FEATURES_AUDIT. ~11 dead handlers in `core/views_ab_testing.py` L82-501 (~600 lines). Needs Chris ratification (scope creep beyond retirement — pure feature-audit cleanup). Rigby offered to SIGN one-paragraph ticket scope (delete-only + URL cleanup + tests).
- **Task #8 — DRF-decorator refactor for 15 auth guards in `views_learning_loop.py`**. Replace boilerplate `if not request.user.is_authenticated: return emit_error_envelope('not_authenticated', ...)` with `@api_view` + `permission_classes([IsAuthenticated])`. Rigby offered SIGN. ~1 session.

### Deferred / speculative

- **`superuser_required` decorator Family B → Family E migration** (Fold C). Would touch ~N decorated endpoints. Separate T-slot arc candidate.
- **`agents/views_monitoring.py` 7 sites** using `core.api_responses.api_error` (different helper). Separate arc — evaluate whether `core.api_responses.api_error` should also be retired.
- **`core/error_messages.py::parse_api_error`** — unrelated helper. No action needed unless the whole error-messages substrate gets reviewed.

### Watches (folds pending 2nd trigger)

- **Fold A** (audit-vs-reality): grep-count vs actual-caller distinction. Watch next arc audit.
- **Fold B** (migration script AST/audit): logged as workspace deliverable `505dbdc1-...`. Next scripted migration adopts AST rewrite or line-offset tracking.
- **Fold D** (aggressive pipelining safe for audits): watch next multi-PR arc.

### Carried from earlier sessions (still open — unchanged this session)

See S3011 handoff `docs/handoffs/SESSION_3011_ENVELOPE_CLOSEOUT_B1_B2.md` §"Forward-carry" for the full list. No S3011 forward-carry items closed or advanced this session (S3012 was scoped tightly to T-ENVELOPE-3).

**Notable S3011 forward-carries still open:**
- Fold B `5th trigger imminent` — PLAYBOOK-7.4.5 amendment (`make restart` requirement for Daphne request path). This session used `make recycle-all` (broader superset) for all 4 PRs — trigger count unclear whether recycle-all satisfies the same signal. Assess at S3013 open.
- Sports odds leak drain arc — 32 grandfathered DRF Response `str(e)` sites in `core/views_odds_sports.py`.
- Various from S2988-S3010 (see S3011 handoff).

## Session close artifacts

- **Feature PRs:** #3701 / #3702 / #3703 / #3704 (all merged).
- **Docs cascade PR:** this file + 00-START-NEXT-SESSION refresh + INDEX regen + wrapper pin bump. (See docs cascade PR body.)
- **Workspace deliverables:** `505dbdc1-9184-478a-b186-1f9e3912807a` (Rigby Tool Gap Ledger entry, workspace `b4503364-...`).
- **HEAD at close:** `dd2a527ee` + docs cascade PR.

## Rigby SIGN quality this session

**8 substantive SIGN cycles** across 4 PRs (PR 1: A1 + A1-followup + A2; PR 2: A1 + A2; PR 3: A1 + A2; PR 4: A2 + verdict-retrieval). All tool-grounded. **ZERO hallucination triggers** — matches S3010 + S3011 pattern (**3 sessions continuous** of zero-hallucination Rigby SIGN).

Total tool_runs across SIGN cycles: ~35 (repo_tool.search / repo_tool.read_file / repo_tool.git_info / deliverable_tool.create).

## Chris interactions

Terse but decisive. Full transcript of Chris directives this session:
1. **"Begin with T-ENVELOPE-3"** — arc kickoff after Claude presented Options T-ENVELOPE-3/B/C/D/E.
2. **"continue"** — mid-flight confirmations (~4 times when tests were running / Monitor pending).
3. **"continue with PR 3"** and **"continue with PR 4"** — aggressive pipelining directives that surfaced Fold D.
4. **"Shit I just saw you are waiting for PR 2, don't let me fuck things up!!"** — anxiety check about the parallel audit approach (I reassured him it was safe).
5. **"ship PR 4"** — retirement + ADR close.
6. **"It looks like we have two follow-ups and a Rigby tool gap will those be included in the close cascade or do we need to do them first?"** — scope clarification. I split follow-ups (future PRs) from Rigby ledger (this session's cascade).
7. **"Proceed"** — close cascade authorization.

Chris did NOT ratify individual PR shapes — all PR-level shape decisions (bundle vs split; migrate-dead-code Shape A vs delete-dead Shape C; bundle bug fix vs separate; ledger vs Playbook rule) were handled Claude ↔ Rigby per `feedback_claude_rigby_agree_first_chris_yes_no`. Chris ratified the arc-level decisions only.
