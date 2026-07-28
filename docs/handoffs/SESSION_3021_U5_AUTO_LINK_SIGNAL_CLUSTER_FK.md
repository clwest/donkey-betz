# Session 3021 — U5 Auto-Link Signal Cluster FK

**Date:** 2026-07-28 · **HEAD at close:** `68bc94510` (PR #3727) + docs cascade

## What shipped

**PR #3727 (`68bc94510`) — `feat(s3021): U5 — direct-link Initiative.signal_cluster FK in cluster→initiative factory`**

Fresh engineering — breaks the 5-session substrate-hardening streak per Chris directive to bias engineering over audit. Ratified path: S3020 close 00-START Option A → U5 auto-link.

### Change

- `core/views_platform_command.py:1006` — added `signal_cluster=cluster` kwarg to the `Initiative.objects.create()` call inside `_create_initiative_from_cluster_core`. Both single-cluster (U2, S3014) and bulk (U3, S3015) endpoints get the fix via the shared helper.

### Design decision — direct-set over embedding search

The 00-START phrased U5 as "auto-link via `initiative_signal_linker.auto_link_initiative_signals()`". But the linker does an embedding-based similarity search over 50 recent clusters — designed for the *unknown-source* case (conversation, integration, autonomous flows).

For U2/U3 create, the source cluster is known deterministically. Using an embedding search here is strictly worse:
- Embedding roundtrips per initiative (~50 clusters compared).
- Risk of mismatch (linker could pick a "better" match than the actual source, silently degrading provenance).

**Precedent match:** `hivemind_execution_pipeline.py:503+519` uses this exact pattern — sets `signal_cluster=getattr(session, 'signal_cluster', None)` deterministically first, then falls back to `auto_link_initiative_signals()` only when `signal_cluster_id` is still NULL. Extends Cycle 1A verify-before-build.

### Tests

- **NEW** `test_signal_cluster_fk_set_at_create_time` (S3014 single path)
- **NEW** `test_signal_cluster_fk_set_at_create_time_bulk` (S3015 bulk path — with Rigby A2 fold: parent_topic + FK pair locked in same assertion block)

Both assert:
1. `initiative.signal_cluster_id == cluster.id`
2. `parent_topic` string form preserved (`f"signal_cluster:{cluster.id}"`)
3. Reverse accessor `cluster.initiatives.all()` includes the new initiative

### Results

| Scope | Result |
|---|---|
| S3014 + S3015 suite | 22/22 pass in 2.520s (was 20 tests + 2 new) |
| S3013-S3020 subset (7 modules) | 60/60 pass in 8.502s |
| `tests.security.test_public_paths_gate_invariant_s3018` | 2/2 pass |

### Live smoke (Rigby web_fetch_tool + orm_inspect_tool)

- Cluster: `2795af6c-c096-4832-ba90-d4854cbd2b6d` ("Continue, Everyone skill demand")
- POST `/api/platform/signal-cluster/<uuid>/create-initiative/` → HTTP 200
- Initiative created: `ce474a55-32fa-4505-867b-77e764c59247`
- **ORM verify:** `signal_cluster=2795af6c-c096-4832-ba90-d4854cbd2b6d` ✅ (FK set, not NULL)
- **ORM verify:** `parent_topic="signal_cluster:2795af6c-c096-4832-ba90-d4854cbd2b6d"` ✅ (string form preserved)

## Cycle 1A verify-before-build wins

Sixth consecutive session where reuse cut scope. This session's wins:

- **Reused the shared U2/U3 helper** — one-line change in the shared `_create_initiative_from_cluster_core` propagates to both single-cluster and bulk endpoints. Zero factory divergence.
- **Reused hivemind's direct-set-then-fallback pattern** — validated my Option 2 approach matches an existing codebase discipline, not a novel invention.
- **Reused the S3014/S3015 test scaffolding** — dropped one test each next to the existing suites; no new test file, no new fixtures.

## Rigby SIGN quality this session

**2 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** — matches S3010 → S3020 pattern (**7 sessions continuous**). **Rigby T1 REVISE catches 5 sessions in a row** — 4 sessions of REVISE + 1 fold that landed same-PR at A2. Zoom-out ask remains validated.

Cycle summary:

1. **Design-fork routing (session-open).** Claude proposed Option 2 (direct-set FK) over Option 1 (literal `auto_link_initiative_signals` call). Rigby endorsed Option 2, pushed back with 4 concerns (source-of-truth semantics, retry idempotency, `parent_topic` consumer audit, save/clean override check). All 4 verified pre-implementation.
2. **A2 SIGN with tool-grounded diff verification.** Rigby read `core/views_platform_command.py` lines 960-1080 via `repo_tool`, confirmed the exact single-line addition. Zoom-out surfaced 3 concerns:
   - Test tightening (assert `parent_topic` + FK pair in same block) — **folded same-PR** (`same_pr_actionable`).
   - Backfill (pre-U5 initiatives have `signal_cluster_id=NULL`) — **deferred to S3022+** (`future_arc` — different risk profile: malformed parent_topic parsing, deleted clusters, batching/monitoring).
   - Diagnostic-flag concern from setting FK at create — verified no negative impact (should reduce missing-linkage diagnostics, not create new ones).

## Folds (pattern evidence, not automatic escalation)

### Fold A `1st trigger` — Backfill-as-separate-PR for FK-population changes

When adding a new deterministic FK to a factory that previously left a field NULL, historical rows are stranded with the null value. Backfill has different risk (malformed parse, deleted parent rows, batch/monitor concerns) and belongs in a follow-up PR. **Codification candidate:** any PR that adds a new deterministic-linkage field to a create factory should explicitly acknowledge whether stranded rows exist and defer backfill scope. Watch for 2nd trigger.

### Fold B `informational` — Hivemind's direct-set-then-fallback pattern as reference for known-source vs unknown-source flows

Hivemind was the only pre-U5 call site that combined direct-set (line 503) with `auto_link_initiative_signals` fallback (line 519 guarded by `if not initiative.signal_cluster_id`). U5 now brings U2/U3 into alignment with this pattern. Other 4 call sites (conversation, integration, models_unified_system, autonomous_action_executor) are pure unknown-source flows and remain unchanged. **Discovery candidate:** codify direct-set-first / linker-as-fallback as the canonical shape for cluster→initiative linkage. If a 3rd flow surfaces with known cluster + only linker call, that's the 2nd trigger.

### Fold C `informational` — Rigby A2 SIGN caught a test-tightening opportunity same-PR

Bulk test didn't repeat the `parent_topic == f"signal_cluster:{cluster.id}"` assertion that the single-path test carried. Rigby zoom-out surfaced it. **Pattern:** Rigby A2 tool-grounded review keeps catching class-adjacent tightening opportunities that Claude misses on first pass. **Rigby T1 REVISE-catches-real-bug pattern** now at **5 consecutive sessions** (S3017 F-3 sibling, S3018 split-snapshot, S3019 test-helper, S3020 cluster ownership, S3021 test tightening).

## Forward carries

### New from S3021

- **Backfill for pre-U5 initiatives** — populate `Initiative.signal_cluster_id` from `parent_topic='signal_cluster:<uuid>'` where FK is NULL. Rigby follow-up suggestion: audit query first (count eligible + failure-parse tail), then batched management command with dry-run mode. Candidate for S3022+.
- **Fold A `1st trigger`** — backfill-as-separate-PR for FK-population changes (codification candidate).
- **Fold B `informational`** — hivemind direct-set-then-fallback pattern as canonical shape.
- **Fold C** — Rigby A2 tool-grounded test-tightening catch (5th consecutive REVISE-catches-something session).

### Carried from S3020 (STATUS PRESERVED)

- **S3020 Fold A** — audit script per-hit / per-function suppression refactor. Still open.
- **S3020 Fold B** — `scope_queryset_memory_cluster` predicate candidate (watch for 2nd trigger).
- **Audit multiline chained `.filter(...).get(...)` regex extension** — still open.
- **Predicate universe expansion** as new predicates land in `object_authz.py`.
- **Rigby T1 REVISE-catches-real-bug pattern** — now at 5 consecutive sessions (S3017-S3021).

### Carried from S3019 (STATUS PRESERVED)

- **S3019 Fold B (predicate-shape-table)** — still open.

### Carried from S3018 (STATUS PRESERVED)

- **S3018 Fold B (test-time advisory for decorator-chain-break)** — still open, future arc.
- **S3018 Fold D (Rigby response truncation)** — still at 1st trigger.
- **Method-decorator detection extension** — still open.

### Carried from S3017 / older — all preserved from S3020 close 00-START.

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008. No open ADR successor arcs.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (design-fork kickoff → A2 APPROVE + zoom-out adopt → ship → recycle-all post-merge → live smoke).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles (design-fork + A2 with tool-grounded diff).** Zero rubber-stamp. **13 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: Chris directive at session-open ("Please begin U5 auto-link") ratified S3021 primary directive; single merge-decision routing via Rigby with plain-English framing (do we lose anything / more work later / concrete ask).
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once — post-PR-3727 merge.
- **Fold classification (PLAYBOOK-6.10.8):** 1× `same_pr_actionable → resolved` (test tightening — parent_topic + FK pair). 1× `future_arc → deferred` (backfill scope). 1× `informational` (hivemind pattern).
- **Verify-before-build (Cycle 1A):** **6th consecutive trigger** — reused shared U2/U3 helper + hivemind direct-set pattern + test scaffolding.

## Chris directive transcript

**T1 (S3020 close):** Chris directive "Please begin U5 auto-link — post-create wire `initiative_signal_linker.auto_link_initiative_signals()` after cluster→initiative create. ~30 min, fresh engineering, breaks the substrate-hardening streak for balance." ratified S3021 primary directive.

**T2 (mid-session):** No further routing needed. Rigby+Claude converged on Option 2 (direct-set) with reasoning; Rigby A2 APPROVE with tool-grounded evidence; merge decision routed with plain-English framing; Rigby endorsed merge.

## Wrapper pin

Active PA conversation pin at S3021 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3021 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
