# Session 3023 — U4-H Boardroom bulk decisions hardening

**Date:** 2026-07-28 · **HEAD at close:** `3140ba512` (PR #3731 merged) + docs cascade

## What shipped

**PR #3731 (`3140ba512`) — `feat(s3023): U4-H — Boardroom bulk decisions hardening (mutation-path tests + updated_at fix)`**

Follow-up to S3022 close (Chris ratified S3023 primary directive: "begin with Option A — U4 (AgentDecisionSummary bulk-decide)"). Cycle 1A verify-before-build turned up a big surprise: **the capability was already shipped in S942** — `bulk_promote_decisions` + `bulk_reject_decisions` at `core/views_agent_learning.py:2278-2393`, with auth-blocking coverage in S2785, CSRF exemption in S2787, frontend API client + `BoardroomTab.tsx` bulk-selection UI + sticky action bar. What DID NOT exist: mutation-path tests (same shape as the S3013 finding on `BulkAttentionDecideView`).

**Chris ratified Path 1** with explicit naming ("U4-H: Boardroom bulk decisions hardening") and required the "capability originally shipped in S942" caveat in PR body + session log to avoid double-counting progress.

### Change 1 — Fix A (`core/views_agent_learning.py:2384-2386`)

```diff
-    # Bulk update
-    queryset.update(status='rejected')
+    # S3023 U4-H: pass updated_at explicitly. queryset.update() bypasses auto_now
+    # so without this the row would carry a stale updated_at through audit/ordering.
+    queryset.update(status='rejected', updated_at=timezone.now())
```

Kept `.update()` shape per Rigby A1 recommendation — preserves bulk O(1) DB roundtrip. Alternative (iterate per-instance `.save()`) rejected as premature: no signals depend on the reject path today, and iterating would scale poorly for future large bulk-rejects.

### Change 2 — Test suite (`core/tests/test_s3023_bulk_agent_decision_mutation.py` +228 lines, 11 tests)

**`BulkPromoteDecisionsMutationTests` (5 tests):**

1. `test_bulk_promote_sets_canonical_status_and_is_canonical_and_promoted_at` — happy path: `status='canonical'` + `is_canonical=True` + `promoted_at NOT NULL` + `promoted_by='human-bulk'`.
2. `test_bulk_promote_only_touches_draft_status` — already-canonical rows unchanged.
3. `test_bulk_promote_by_decision_type_filter` — filter branch coverage (product vs experiment).
4. `test_bulk_promote_missing_ids_and_type_returns_400` — validation.
5. `test_bulk_promote_invalid_json_returns_400` — JSON decode error handling.

**`BulkRejectDecisionsMutationTests` (4 tests):**

6. `test_bulk_reject_sets_rejected_status_and_touches_updated_at` — **Fix A regression:** rewinds `updated_at` by 6h then asserts endpoint moved it forward.
7. `test_bulk_reject_only_touches_draft_status` — already-canonical rows unchanged.
8. `test_bulk_reject_missing_ids_and_type_returns_400` — validation.
9. `test_bulk_reject_invalid_json_returns_400` — JSON decode error handling.

**`BulkDecisionsTokenAuthParityTests` (2 tests, S3016 Fold E parity):**

10. `test_bulk_promote_reachable_via_token_auth` — Token-auth path (React frontend) via `_require_boardroom_staff` (S887).
11. `test_bulk_reject_reachable_via_token_auth` — same, for bulk-reject.

### Results

| Metric | Actual |
|---|---|
| New suite | **11/11 pass in 1.111s** |
| Regression bundle (S3013 + S3014 + S3015 + S2785 + S2787 + S3023) | **90/90 pass in 6.545s** |
| Post-merge `make recycle-all` | HEAD `3140ba512`, all services + workers restarted clean |

## Cycle 1A verify-before-build wins

**Eighth consecutive session where reuse cut scope** (largest one this arc):

- **Bulk endpoints already shipped** (`core/views_agent_learning.py:2278-2393`, S942).
- **Auth-blocking tests already exist** (`test_decision_approve_auth_regression_2785.py`).
- **CSRF exemption tests already exist** (`test_csrf_enforcement_2787.py`).
- **Frontend API client already exists** (`frontend/src/lib/api.ts:596-597`, S942).
- **Frontend UI already wired** (`BoardroomTab.tsx` at `WorkspacePageNew.tsx:1303-1305` under `system/boardroom`).
- **Zero net-new code paths** — 3 lines Fix A + 228 lines test suite.

If Rigby hadn't pressure-tested the S3014 forward-carry note (which claimed `_get_pending_decisions` returns both `HumanAttentionItem` AND `AgentDecisionSummary` — false; it only returns HAI), the arc could have shipped a redundant parallel endpoint + duplicate UI, doubling the surface area for no capability gain.

## Rigby SIGN quality this session

**2 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** — matches S3010 → S3022 pattern (**9 sessions continuous**).

Cycle summary:

1. **A1 SIGN discovery + shape recalibration.** Claude presented 4 discovery findings (existing endpoints / existing auth tests / existing frontend / missing mutation-path tests) + alt-shape proposal (U4-as-hardening). Rigby ran her own tool_runs and independently verified all 4 findings. AGREED with hardening shape + endorsed Fix A shape (`.update()` with explicit timestamp). Zoom-out flagged the naming mismatch: "U4 AgentDecisionSummary bulk-decide" reads like net-new capability but is actually hardening — mis-labeling risk in progress reports.
2. **A2 SIGN.** AGREE clean. Zoom-out: the new tests ratify the status-string + lifecycle contract (`draft/canonical/rejected`, `promoted_by='human-bulk'`); future governance unification is now a conscious breaking-change requiring backend+frontend migration.

## Folds (pattern evidence, not automatic escalation)

### Fold A `informational` — S3014-style stale forward-carry premise

The S3014 forward-carry note ("`_get_pending_decisions` returns AgentDecisionSummary too") was wrong. `_get_pending_decisions` only reads `HumanAttentionItem`. Codification candidate: **pressure-test any 2-session-old forward-carry note before spec'ing off of it**. First trigger; watch for 2nd.

### Fold B `informational` — Single vs bulk side-effect divergence

Single `promote_decision` (line 2140) triggers Redis broadcast + `KnowledgeTransfer` creation (S657). Bulk-promote iterates one-by-one but does NOT trigger the same side effects. Silent semantic asymmetry — bulk-promoted canonicals silently skip the collective-intelligence broadcast. **Note (per Rigby A2):** this is a single-promote-vs-bulk-promote semantic gap, NOT a regression introduced by U4-H. Ledger candidate.

### Fold C `informational` — Masked AttributeError in single `promote_decision`

Line 2177 references `decision.summary` (field doesn't exist on `AgentDecisionSummary`; canonical fields are `rationale` / `recommended_stance` / `key_insights`). Same for line 2193 `decision.summary` + line 2194 `decision.agents_involved`. All wrapped in `try/except Exception` so `learning_created=False` silently on every single-promote call. **Note (per Rigby A2):** this is a single-promote semantic bug, NOT a regression in the bulk endpoints. Ledger candidate.

### Fold D `1st trigger` — Test suite ratifies lifecycle contract (breaking-change surface)

The new mutation-path tests ratify the current status-string + lifecycle contract (`draft/canonical/rejected`, `promoted_by='human-bulk'`, `is_canonical=True` on promote). Any future governance unification arc (Rigby's zoom-out concern) is now a conscious breaking change — must migrate BOTH backend enums and frontend assumptions coherently. **Discovery candidate:** if a "unify Boardroom + Governance decision lifecycle" arc opens, tests here + S3013 U1 + S3014 U2 + S3015 U3 constitute the coupled contract to migrate. First trigger — watch for 2nd (any related unification proposal).

## Forward carries

### New from S3023

- **Fold A `informational`** — pressure-test 2-session-old forward-carry notes before spec'ing (codification candidate).
- **Fold B `informational`** — single-promote → Redis/KnowledgeTransfer side effects don't fire in bulk-promote. Rigby-flagged as "not U4-H's regression to fix." Single-promote semantics only.
- **Fold C `informational`** — masked AttributeError in single `promote_decision` (`decision.summary` field doesn't exist). Rigby-flagged as "not U4-H's regression to fix." Single-promote semantics only.
- **Fold D `1st trigger`** — U4-H tests ratify current status/lifecycle contract; future governance unification is a conscious breaking change.
- **Decision lifecycle parity (Rigby A1 zoom-out):** HAI has decide/defer/verify/execute; ADS has promote/reject/approve + bulk variants. If product intent is "one governance queue", unification hasn't happened. Standing carry, not an action item.

### Carried from S3022 (STATUS PRESERVED)

- **S3022 Fold A `informational`** — audit-first-then-shape-decide for backfill scope.
- **S3022 Fold B `informational`** — `RunPython.noop` reverse for deterministic-linkage backfills.
- **Management command for FK backfill** — still deferred per Rigby (no 2nd batch of stranded rows).

### Carried from S3021 / S3020 / S3019 / S3018 / older — all preserved from S3022 close 00-START.

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008. No open ADR successor arcs.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (discovery → shape recalibration via A1 → implement → A2 → ship → recycle-all).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles.** Zero rubber-stamp. **15 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive ("begin with Option A — U4 (AgentDecisionSummary bulk-decide)") + mid-session Path 1/2 decision with plain-English framing (do we lose anything / more work later) + merge decision via Rigby.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once — post-PR-3731 merge, clean recycle event recorded (`sha=3140ba512f0d`).
- **Fold classification (PLAYBOOK-6.10.8):** 4 folds total. Folds A/B/C `informational`. Fold D `1st trigger` on codification path. Fix A classified `same_pr_mitigatable` and bundled with test suite in single PR.
- **Verify-before-build (Cycle 1A):** **8th consecutive trigger** — largest scope reduction of the arc. Original directive would have written parallel bulk endpoint + duplicate UI; discovery found the entire stack already existed at S942. PR reduced to 3-line Fix A + 228-line test suite.

## Chris directive transcript

**T1 (S3023 open):** "Please orient yourself and begin with Option A — U4 (AgentDecisionSummary bulk-decide)." Claude ran context-kit orient + absorbed 00-START/MEMORY/CLAUDE + read S3022 handoff. Session pin `pa-fc571abfdc1b4b7e` was fresh from S3022 close (no rotation needed).

**T2 (mid-session Path 1/2 ratification):** Chris ratified Path 1 (U4-as-hardening) with explicit renaming to "U4-H: Boardroom bulk decisions hardening" and required the "capability originally shipped in S942" caveat in PR body + session log.

**T3 (merge):** Routed to Rigby (per `feedback_rigby_comms`). Rigby AGREED merge; Claude executed `gh pr merge --admin --squash --delete-branch 3731` per `feedback_gh_pr_merge_admin_until_billing_fixed`.

## Wrapper pin

Active PA conversation pin at S3023 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3023 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
