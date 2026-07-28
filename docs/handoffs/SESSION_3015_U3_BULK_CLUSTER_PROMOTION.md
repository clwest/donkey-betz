# Session 3015 — U3 Bulk-promote SignalClusters to Initiatives (+ optional briefs)

**Date:** 2026-07-28
**HEAD at close:** `c388f006a` (PR #3710 merged) + docs cascade PR
**Session shape:** Fresh engineering, continuation of user-facing trajectory (S3013 U1 → S3014 U2 → S3015 U3 — 3 consecutive user-facing sessions).

---

## What shipped

### PR #3710 — `feat(s3015): U3 — Bulk-promote SignalClusters to Initiatives (+ optional briefs)` (`c388f006a`)

**Backend refactor + new bulk endpoint (`core/views_platform_command.py` + `core/urls.py`):**
- Extracted `_resolve_target_workspace(user, workspace_override_id)` — shared workspace-resolution fallback chain.
- Extracted `_create_initiative_from_cluster_core(cluster, user, name_override, generate_brief, target_workspace)` — returns `(status_code, result_dict)`. Shared by single-cluster (S3014 U2) + bulk (S3015 U3) views.
- Single-cluster view refactored to thin wrapper — **S3014's 8/8 tests still PASS after refactor** (validated pre-commit).
- New view `bulk_create_initiatives_from_clusters_view` wired at `POST /api/platform/signal-cluster/bulk-create-initiative/`.
- Body: `{cluster_ids: [...], generate_brief?: bool (default true), workspace_id?: str}`.
- Returns 200 for well-formed requests; per-row failures reported in `results` array (partial-failure semantics).
- Response shape: `{success, summary: {requested, succeeded, failed, briefs_requested, briefs_succeeded, briefs_failed}, results: [{cluster_id, initiative?, deliverable?, deliverable_error?, error?, existing_initiative?}]}`.
- **Rigby A2 zoom-out mitigation:** 100-item batch cap (frontend paginates at 25, 4x headroom).
- De-dupes `cluster_ids` within request + preserves request order.

**Frontend (`frontend/src/lib/api.ts` +25 lines, `SignalsClustersView.tsx` +~250 lines):**
- Added `signalsApi.bulkCreateInitiativesFromClusters()` method.
- Checkbox column on Cluster Explorer table (stopPropagation preserves row-click → drawer).
- Header controls: "Select all visible" / "Deselect all" + N-selected counter.
- Sticky action bar when ≥1 selected: single CTA `Create N initiatives` (per U3 spec — bulk = one action, unlike U1's 3).
- New `BulkPromoteModal` component:
  - Cluster name preview (first 10 + "and X more") — **Rigby A1 UX tweak adopted**.
  - Generate Signal Brief checkbox (default ON, applies to all rows).
  - Loading spinner during mutation.
  - Info: "One Initiative (TRIAGE) per cluster. Names auto-generate."
- New `BulkPromoteResultCard` (bottom-right, dismissible, z-40):
  - Summary: "M of N initiatives created" + brief counts.
  - Amber icon if any failures; green if all succeeded.
  - Expandable "View failures" panel — per-cluster error strings + deep link to `existing_initiative` (dedupe pointer).

**Test suite (`core/tests/test_s3015_bulk_create_initiatives_from_clusters.py` +190 lines, 10 tests, all PASS in ~1s):**

1. `test_bulk_creates_multiple_initiatives_with_briefs` — 3 clusters → 3 initiatives + 3 briefs, ORM verifies `parent_topic` + `target_workspace` on all.
2. `test_generate_brief_false_skips_all_briefs` — `briefs_requested=0`, `briefs_succeeded=0`.
3. `test_partial_failure_unknown_cluster_reported_per_row` — real cluster succeeds, fake UUID → per-row error, order preserved.
4. `test_partial_failure_dedupe_hit_reported_per_row` — dedupe returns per-row error with `existing_initiative` pointer.
5. `test_dedupes_ids_within_request` — duplicate `cluster_ids` collapse to 1.
6. `test_empty_cluster_ids_returns_400`.
7. `test_missing_cluster_ids_returns_400`.
8. `test_invalid_json_returns_400`.
9. `test_bulk_cluster_limit_enforced` — **Rigby A2 zoom-out regression** — >100 items returns 400.
10. `test_preserves_request_order`.

**Live smoke (Rigby web_fetch_tool):** POST with 3 real chris cluster ids returned `{success: true, summary: {requested: 3, succeeded: 2, failed: 1, ...}, results: [...]}` — 1 dedupe hit correctly carried `existing_initiative` pointer.

---

## Cycle 1A verify-before-build wins

Third consecutive session where reuse cut scope. This session's wins:

- **Reused S3014 U2 core creation path** by refactoring into `_create_initiative_from_cluster_core`. Bulk endpoint gets workspace resolution, provenance, brief generation, quality gate metadata — all identical to single-cluster path.
- **Parallels S3013 U1 `BulkAttentionDecideView` shape** for response envelope + summary counters + per-row error structure.
- **Zero new model fields** (same as U2).
- **Refactor safety:** ran S3014 suite before committing to catch shared-helper regressions.

---

## Rigby SIGN quality this session

**3 substantive SIGN cycles** (U3 was smaller scope than U1/U2 — one clean A1 + one A2 + zoom-out adoption). All tool-grounded. **Zero hallucination triggers** (matches S3010 → S3014 pattern — **6 sessions continuous**).

Cycle summary:
1. **Session-open kickoff.** Rigby joint recommendation: bulk endpoint (Option B, not sequential frontend calls); UI shape confirmed with cluster-name-preview tweak; partial-failure semantics separated initiative-level from brief-level.
2. **A2 SIGN APPROVE.** Live-probed the endpoint with 3 real chris cluster ids; shape + dedupe pointer confirmed correct.
3. **A2 zoom-out adoption:** max-batch-size cap (100). Adopted + tested + shipped in same PR.

---

## Folds (pattern evidence, not automatic escalation)

### Fold A `1st trigger` — Bulk-endpoint scope-limit-cap as standard pattern

Rigby A2 zoom-out flagged the need for a batch-size cap on the new bulk endpoint. Same pattern would apply to S3013 `BulkAttentionDecideView` (currently uncapped) and any future bulk create/mutate endpoint. **Codification candidate:** any user-triggered bulk endpoint should have an explicit `MAX_BATCH_SIZE` constant + 400 response above cap. Watch for 2nd trigger.

### Fold B `informational` — Refactor-first for U-N when U-(N-1) shipped shared logic

The U2 single-cluster view had the entire "create initiative from cluster" logic inline. U3 needed the same logic on N items. Rather than duplicate, extracted to shared helper first. **Discovery candidate:** future U-N sessions should probe whether U-(N-1) has extractable helpers before writing new code. Extends Cycle 1A verify-before-build one layer down.

### Fold C `informational` — Preserve-request-order + de-dupe are non-obvious bulk contract requirements

Bulk endpoint had to handle: (1) client-side duplicate cluster_ids (accidental double-select), (2) response ordering that matches request (UI displays failures in submission order for user recognition). Neither is called out in S3013 `BulkAttentionDecideView` docstring. **Docs candidate:** if a 3rd bulk endpoint gets built, codify these as "bulk endpoint invariants" in the Playbook or an ADR.

### Fold D `2nd trigger` — Cycle 1A verify-before-build saves scope

S3013 U1 (BulkAttentionDecideView already existed). S3014 U2 (create_initiative_from_decision_view precedent + create_deliverable factory). S3015 U3 (refactored U2 helper). **3rd trigger this session.** Pattern is real. Not codification — already implicit — but if drift signals ever surface, this is the reinforcement evidence.

---

## Forward carries

**New from S3015:**

- **U4 candidate:** AgentDecisionSummary bulk-decide (referenced in S3014 handoff).
- **U5 candidate:** post-create auto-link cluster ↔ initiative via embeddings (initiative_signal_linker).
- **Fold A `1st trigger`** — bulk-endpoint scope-limit-cap pattern (retrofit to `BulkAttentionDecideView`?).
- **Fold B `informational`** — refactor-first for U-N when U-(N-1) shipped shared logic.
- **Fold C `informational`** — bulk-endpoint invariants (order preserved + de-dupe within request).
- **Fold D `3rd trigger`** — Cycle 1A verify-before-build. 3 consecutive triggers.
- **UI improvement candidate:** allow name editing per cluster before bulk-create (currently bulk always uses defaults). Would need per-row editable input in modal.
- **UI improvement candidate:** progress bar during bulk create (server sends single response but N clusters can take multi-second — show "Creating 3 of 10..." optimistically or via SSE).

**Carried from S3014 (STATUS PRESERVED):**

- **Rigby non-blocking A2 suggestion (S3013):** 9th test coupling `governance_view.pending_decisions[].id` → `HumanAttentionItem.id`.
- **Batch Defer for Governance (S3013):** UI has 3 actions (Approve/Ignore/Reject). Batch Defer would need new bulk endpoint OR per-item iteration.
- **Fold A `1st trigger` (S3014)** — "Diagnostic on create" invariant codification. Rigby zoom-out from A2 SIGN. Watch for 2nd.
- **Fold B `informational` (S3014)** — `create_deliverable` factory `trigger_source` bypass documentation.
- **Fold C `informational` (S3014)** — Session 843 `parent_object_type/id` may be write-only (no known consumers audited).
- **Fold D `2nd trigger` (S3013 Fold C rolled)** — Rigby web_fetch_tool auth clarification. Rigby Tool Gap Ledger candidate.

**Carried from S3013 (STATUS PRESERVED):**

- **Fold A `1st trigger` (S3013)** — Cycle 1A verify-before-build. **3rd trigger this session — see Fold D above.**
- **Fold B `1st trigger` (S3013)** — S2785 auth-regression contract has mutation-path blind spot.
- **Fold D `future_trigger` (S3013)** — `BulkAttentionDecideView` uses Family B envelope shape.
- **Fold E `informational` (S3013)** — Bulk endpoint decision enum inconsistency.

**Carried from S3012 and earlier — see previous handoffs for the full list.**

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0007. No open ADR successor arcs.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (kickoff → A1-fold→ implement → A2 APPROVE + zoom-out adopt → ship → recycle-all post-merge).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **3× substantive Rigby SIGN cycles.** Zero hallucination triggers. **6 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing this session was single-turn ("continue with U3" = ratifying joint recommendation).
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` used pre-merge (smoke) and post-merge (constitutional).
- **Verify-before-build (Cycle 1A):** **3rd consecutive trigger** — reused S3014's newly-extracted helpers.
- **Fold classification (PLAYBOOK-6.10.8):** Rigby A2 zoom-out concern classified `same_pr_actionable` and fixed (100-cap) in same PR.

---

## Chris directive transcript

**T1 (S3014 close):** Chris "continue with U3" ratified S3015 primary directive (joint recommendation for bulk-cluster promotion).

**T2 (mid-session):** Chris "Internet blip continue" — resumed after connection interruption. No scope change.

**T3 (execution):** No further Chris routing needed. A1 + A2 APPROVE + zoom-out all Claude↔Rigby. Session close.

---

## Wrapper pin

Active PA conversation pin at S3015 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3015 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
