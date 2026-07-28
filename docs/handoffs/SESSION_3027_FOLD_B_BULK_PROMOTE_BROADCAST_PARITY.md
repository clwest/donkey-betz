# Session 3027 — S3023 Fold B re-scope: bulk_promote_decisions broadcast parity

**Date:** 2026-07-28 · **HEAD at close:** `35c3ed0e5` (PR #3741 merged) + docs cascade

## What shipped

**PR #3741 (`35c3ed0e5`) — `feat(s3027): S3023 Fold B re-scope — bulk_promote_decisions emits canonical broadcast via shared helper`**

Continues S3026 Fold C fix. Post-S3026, single-promote emits a `canonical_policy_created` event on the `agent_learning` Redis channel; `bulk_promote_decisions` (Session 942) never did. That silent drift class is exactly what S3026 surfaced — two endpoints that "should" match diverged silently for ~5 years.

**Shape A per Rigby A1:** extract `_emit_canonical_promotion_broadcast(decision, *, request_id=None) -> bool` as the single source of truth for the event shape. Both endpoints call it after `decision.promote_to_canonical(...)`.

### Backend (`core/views_agent_learning.py`, +73/-57)

**New helper `_emit_canonical_promotion_broadcast(decision, *, request_id=None) -> bool`** at module level (near `_require_boardroom_staff`):
- Best-effort, non-fatal — catches all Redis exceptions internally, logs with `decision_id` + `request_id`, returns False.
- **Only place** in the module that sets `schema_version`, emits dual-key `participants` + `agents_involved` back-compat alias, performs `rationale/stance` accessor cascade, wraps `Redis.publish` in try/except.
- Verified via `repo_tool` search: sole `r.publish('agent_learning', ...)` call in the file.

**`promote_decision` (single endpoint):**
- Inline broadcast block (previously ~30 lines) REPLACED with helper call.
- `HTTP_X_REQUEST_ID` piped through for trace correlation.

**`bulk_promote_decisions` (bulk endpoint):**
- Helper called inside existing per-row loop after `promote_to_canonical` succeeds.
- Broadcast failure never fails promotion — helper returns bool, loop tracks `broadcasts_succeeded` / `broadcasts_failed` counters alongside `promoted`.
- Response payload additive-only per Rigby A1 REVISE #2: existing S942 `{success, count, message}` preserved; added `broadcasts_succeeded` + `broadcasts_failed`. No per-row `results[]` this iteration.

### Tests (`core/tests/test_s3027_bulk_promote_broadcast_parity.py`, +200 lines, 5 tests)

1. **`test_bulk_promote_emits_broadcast_per_row`** — 3 drafts → 3 `publish()` calls to `agent_learning`, each carrying correct `schema_version` + dual-key participants/agents_involved.
2. **`test_broadcast_failure_isolated_from_promotion_success`** — Redis `publish` raises `RuntimeError` → all 3 rows still flip to `canonical` + response reports `broadcasts_failed=3`.
3. **`test_bulk_and_single_emit_structurally_identical_events`** (Rigby A1 test tweak — deep-equal excluding fields expected to differ: `timestamp`, `decision_id`, `topic`) — regression guard against future drift.
4. **`test_bulk_promote_response_includes_broadcast_counts`** — additive contract preservation.
5. **`test_empty_queryset_still_returns_broadcast_counts`** — edge case.

### Results

| Metric | Actual |
|---|---|
| New suite (`test_s3027_bulk_promote_broadcast_parity.py`) | **5/5 pass in 0.504s** |
| Regression bundle (S3013 + S3014 + S3015 + S3023 + S3024 + S3026 + S3027) | **58/58 pass in 6.867s** |
| Post-merge `make recycle-all` | HEAD `35c3ed0e5`, `sha=35c3ed0e5a33` recorded in `logs/recycle_events.jsonl` |

## Cycle 1A verify-before-build wins

**12th consecutive session where reuse cut scope:**

- **Bulk endpoint already looped per-row.** Adding broadcast was a 1-line call inside the existing loop, not a refactor.
- **S3026 broadcast code was ready to extract.** ~30 inline lines → ~35-line helper + 3 call sites (single + bulk + future). Net LOC roughly neutral; drift-risk dropped to zero.
- **Test infrastructure reused.** New test file copies the `patch("redis.Redis")` pattern from `test_s3026_promote_decision_fold_c.py` — no new mock scaffolding needed.

## Rigby SIGN quality this session

**2 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** — matches S3010 → S3026 pattern (**13 sessions continuous**).

Cycle summary:

1. **A1 SIGN — APPROVE Shape A with 2 REVISE conditions:**
   - REVISE #1: Helper contract — must be the ONLY place that owns transport concerns (schema_version, dual-key, accessor cascade, Redis try/except).
   - REVISE #2: Response contract additive-only — no per-row `results[]` this iteration.
   - Test tweak: shape-parity test must exclude fields expected to differ (timestamp/decision_id/topic) rather than asserting full deep-equal.
   All applied same-PR.

2. **A2 SIGN — AGREE.** Verified via `repo_tool` (helper module-level + sole `r.publish` caller; inline broadcast block gone from single; additive response fields present in bulk; shape-parity test exists). Zoom-out: no new fold flags; `HTTP_X_REQUEST_ID` is acceptable canonical trace header; additive JSON fields unlikely to break consumers.

## Folds (pattern evidence, not automatic escalation)

**No new folds this session.** The session was a clean-execution of the S3023 Fold B re-scope; no zoom-out surprises surfaced.

Notable non-fold observations:
- **S3026 Fold A `2nd trigger` candidate:** the S3023 Fold B forward-carry was clearly described (both handoff + 00-START called out the re-scope precisely after S3026 Fold C removed the KT write). This is contrast evidence for S3026 Fold A ("fold descriptions should be backed by failing tests"). Not a 2nd trigger for codification — inverse evidence that well-authored forward-carries don't need the codified rule. Codification pressure on S3026 Fold A stays at 1st trigger.
- **Helper extraction moment:** this session justified the S3026 A2 REVISE decision to add `schema_version: 1` upfront. When bulk endpoint needed the same event, having `schema_version` already in the shape meant zero migration work.

## Forward carries

### New from S3027

- **None.** Session shipped 1 PR without new folds or non-MVP followups.
- **Substrate strengthened:** helper pattern for the promote/broadcast side-effect is now available for future decision-lifecycle endpoints (e.g., a hypothetical `bulk_reject_decisions` with a `canonical_decision_rejected` broadcast, or a `bulk_defer_decisions` variant).

### Carried from S3026 (STATUS PRESERVED)

- **S3026 Fold A `1st trigger`** — fold descriptions should be backed by minimal failing test or stacktrace. Watch for 2nd trigger.
- **S3026 Fold B `informational`** — 2 spec-invalidations in one session; watch for 3rd trigger in next 5 sessions. **S3027 clean-execution = counter-evidence** — session with well-scoped work had zero spec-invalidations.
- **S3026 Fold C `informational`** — `learning_reason` bare-string typing.
- **Design-arc candidate** — KnowledgeTransfer model realignment.

### Carried from S3025 (STATUS PRESERVED)

- **S3025 Fold A `informational`** — `chunks.indexOf(chunk)` inside loop.
- **S3025 Fold B `informational`** — cancelled rows revert to `pending` glyph.
- **S3025 Fold C `codification candidate`** — `BulkPromoteModal` complexity growth.

### Carried from S3024 (STATUS PRESERVED)

- **Fold A `1st trigger`** — cross-tier default-formatting shadowing.
- **Fold B `informational`** — silent-fallback vs strict-validate asymmetry.

### Carried from S3023 (STATUS UPDATED)

- **S3023 Fold A `informational`** — pressure-test 2-session-old forward-carry notes. S3027 supports "well-authored forward-carries execute cleanly" as counter-evidence.
- **S3023 Fold B** — **RESOLVED** by S3027 PR #3741.
- **S3023 Fold C** — RESOLVED by S3026 PR #3738.
- **S3023 Fold D `1st trigger`** — U4-H tests ratify current status/lifecycle contract.
- **Decision lifecycle parity (Rigby A1 zoom-out standing carry)** — HAI vs ADS lifecycle families still fragmented.

### Carried from S3022 / S3021 / S3020 / S3019 / S3018 / older — all preserved from S3026 close 00-START.

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** — discovery → A1 APPROVE-with-REVISE → implement → A2 AGREE → ship → recycle-all. Clean execution, zero abort-early invocations.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles. Zero rubber-stamp. 19 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive "start s3023 fold b" ratified S3027 primary; joint recommendation from S3026 close matched Chris directive exactly.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once post-merge (`sha=35c3ed0e5a33`).
- **Fold classification (PLAYBOOK-6.10.8):** 0 new folds. All Rigby A1 REVISE conditions classified `same_pr_mitigatable` (applied before implementation).
- **Verify-before-build (Cycle 1A):** **12th consecutive session** — helper extraction reused S3026 code + tests reused S3026 mock pattern.

## Wrapper pin note

Session-open pin was `pa-b2948ae4c2624583` (retired at S3026 close). Active during session: `pa-eaee6590fb9c43e1`. Close mints next pin; wrapper diff committed per `feedback_commit_wrapper_pin_bump_at_close`.
