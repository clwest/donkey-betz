# Session 3031 — did_promote idempotency

**Date:** 2026-07-28 · **HEAD at close:** `d7bb28b4f` (PR #3751 merged) + docs cascade

## What shipped

**1 feature PR merged this session** — shipped in the same terminal as S3030 (Chris ratified continuation after S3030 close for the "small clean lean" option).

### PR #3751 (`d7bb28b4f`) — `feat(s3031): did_promote idempotency`

Closes S3030 Fold D / S3029 Fold B (carried) — the duplicate-broadcast race across all 6 canonical-promotion paths. If two paths race on the same row (AI service + Rules service, or human + Celery auto-approve, etc.), both would emit `canonical_decision_promoted` — 2 duplicate events. Low today (paths implicitly gate on `is_canonical=False` at query time) but easy to close cleanly.

**Shape:**

- **`AgentDecisionSummary.promote_to_canonical`** (`core/models_unified_system.py:18199`):
  - Now returns `bool`: True if this call performed the state transition, False if the row was already canonical (no-op — callers treat False as success via idempotent no-op, not error).
  - Early exit if `self.is_canonical`: no save at all, `updated_at` not bumped.
  - `save(update_fields=['status', 'is_canonical', 'promoted_at', 'promoted_by', 'updated_at'])` containment: only touches the 5 fields it owns; unrelated in-memory mutations won't be accidentally persisted. `updated_at` is explicitly listed so Django still fires `auto_now` on the write path.

- **6 caller sites** (all now wrap `emit_canonical_promotion_broadcast` in `if did_promote:`):
  - `core/services/ai_decision_promoter.py`
  - `core/services/decision_promotion_rules.py`
  - `core/services/td_handlers_agents.py` (PA tool handler)
  - `core/tasks_ops.py` (Celery auto-approve — `did_promote` also gates both `promoted_count` increment AND the `promoted_ids.append(...)` that feeds the outside-atomic broadcast loop)
  - `core/views_agent_learning.py:promote_decision` (single view)
  - `core/views_agent_learning.py:bulk_promote_decisions` (bulk view — added explicit `if not did_promote: continue` between promote counter and broadcast counter so `broadcasts_succeeded/broadcasts_failed` stay accurate)

- **NEW** `core/tests/test_s3031_did_promote_idempotency.py` (+99, 3 tests):
  - `test_first_call_returns_true_and_mutates_all_fields`
  - `test_second_call_returns_false_and_is_noop` — asserts `promoted_at`, `promoted_by`, AND `updated_at` all unchanged after the 2nd (no-op) call. Codifies "no-op ≠ updated_at bump" as an invariant per Rigby A2 recommendation.
  - `test_ai_promoter_service_fires_broadcast_exactly_once_when_called_twice` — end-to-end via `AIDecisionPromoterService` with spy on `emit_canonical_promotion_broadcast`; proves 2 service calls on the same row = 1 broadcast.

## Results

| Metric | Actual |
|---|---|
| PR #3751 diff | +170/-30 (7 files: 1 model + 5 caller files + 1 new test) |
| S3031 suite | **3/3 pass in 0.027s** |
| Regression bundle (S3013 + S3014 + S3015 + S3023 + S3024 + S3026 + S3027 + S3028 + S3029 [both] + S3030 + S3031) | **77/77 pass in 7.166s** (baseline 74/74 at S3030 close; +3 new = 77) |
| Post-merge `make recycle-all` | clean, `sha=d7bb28b4f91f` recorded in `logs/recycle_events.jsonl` |

## Cycle 1A verify-before-build wins

**16th consecutive session.** Verify pass at T1: read `promote_to_canonical` model method + all 6 caller sites + grep for other `emit_canonical_promotion_broadcast(` callers (confirmed only 5 files with 6 sites + definition + S3030 backfill docstring reference — no missing site) + grep for direct `is_canonical=True` / `status='canonical'` writes (3 non-test production hits, all READS not writes). Grounded T1 spec in reality before dispatching to Rigby.

## Rigby SIGN quality this session

**2 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** — matches S3010 → S3030 pattern (**17 sessions continuous**).

Cycle summary:

1. **T1 SIGN — AGREE + minor REVISE nits.** Rigby endorsed the bool + early-exit + gated-broadcast shape as "the right T1 hardening". REVISE nits folded: `save(update_fields=[...])` containment (with `updated_at` explicit so auto_now still fires on writes), variable name `did_promote` everywhere (not `success`) so future engineers don't misinterpret False as "failed" instead of "idempotent no-op success", tasks_ops collects only did_promote decisions into `promoted_ids`. Skipped `select_for_update` lock (agreed overkill for T1).
2. **A2 SIGN (post-code) — AGREE + tool-grounded zoom-out sweep.** Rigby ran 8 `repo_tool` searches confirming:
   - No other production callers of `promote_to_canonical` beyond the 6 known sites + backfill + tests.
   - No `emit_canonical_promotion_broadcast` callers not already gated in the diff.
   - Only one test sets `is_canonical=True` directly (`test_s3029_tasks_ops_auto_approve_promotion_convergence.py:97`) — asserts SKIP behavior, not broadcast. No test relies on duplicate broadcast.
   - No downstream consumer relies on `updated_at` bump for no-op promote. S3031 test now codifies this as an invariant.

## Folds (pattern evidence, not automatic escalation)

### Fold A `2nd trigger` — Boolean-return semantics discipline (carried and refined from S3030)

Reinforced by S3031's rename to `did_promote` across 6 caller sites. Rigby A2 flagged coupling risk: "future code might treat `False` as 'failed' instead of 'idempotent no-op success'." Mitigated in-PR via variable naming discipline; note as a broader "boolean-return-value contract" pattern that may apply to other model methods (`did_reject`, `did_deprecate`, etc.). Watch for a 2nd similar bool-return method to codify.

### Fold B `informational` (carried from S3029 Fold A / S3030 Fold B) — spy `side_effect=lambda` signature fragility

Unchanged. The S3029 spy pattern happens to work here because Python lambdas implicitly return the inner call's value, so True/False forwards through the spy without explicit `return original(...)`. Fold is still recorded because a future signature change (e.g. adding a required kwarg) would still silently mis-forward.

### Fold C `3rd cycle, no discovery` — A2 zoom-out sweep for drift/hardening class

- S3029: 1st cycle — **discovered** tasks_ops silent site
- S3030: 2nd cycle — no discovery (drift class already closed at source)
- S3031: 3rd cycle — no discovery (idempotency change didn't introduce new drift or miss any caller)

Three cycles of the pattern; two clean sweeps confirming the drift-class + idempotency-class closures hold. Codification pressure remains "watch for genuine 2nd discovery to codify" but with strong evidence the pattern is useful even when it finds nothing. This is arguably ready to codify with the "clean-sweep-confirms-closure" framing rather than the original "catches adjacent silent bugs" framing.

### Fold D `informational` (carried from S3030 Fold A) — Rigby ORM allowlist gap

Unchanged. `AgentDecisionSummary` still not in `orm_inspect_tool` allowlist. Not blocking this arc; ledger candidate for future substrate slate.

## Forward carries

### New from S3031

- **Fold A `2nd trigger`** — boolean-return semantics discipline. Watch for 2nd bool-return method in a similar mutation-with-side-effect shape (`did_X` pattern) to codify.
- **Fold C `3rd cycle, no discovery`** — A2 zoom-out sweep pattern applied cleanly again. Ready-to-codify pressure elevated but not automatic.

### Carried from S3030 (STATUS UPDATED)

- **S3030 Fold A** — carried as new Fold D (Rigby ORM allowlist gap, still ledger candidate).
- **S3030 Fold B `informational` (spy fragility)** — carried unchanged as new Fold B.
- **S3030 Fold C `2nd cycle`** — advanced to `3rd cycle, no-discovery` as new Fold C.
- **S3030 Fold D `informational` (dup-broadcast race)** — **RESOLVED** by S3031 PR #3751.
- **S3030 prod deploy carry** — still open: run `python manage.py backfill_canonical_drift --apply` against Railway prod when convenient.

### Carried from S3026 → S3029 (STATUS PRESERVED)

- **S3028 Fold A** — FULLY RESOLVED at S3029.
- **S3029 PR #3747 deferred item** — RESOLVED by S3030 PR #3749.
- **S3029 Fold C** — advanced to S3031 Fold C 3rd cycle.
- **S3026 Fold A `1st trigger`** — S3030 + S3031 A2 sweeps = additional supporting evidence (both tool-grounded `repo_tool` sweeps). Codification pressure stays at 1st trigger.
- **S3026 Fold B `informational`** — spec-invalidation watch.
- **S3026 Fold C `informational`** — `learning_reason` bare-string typing.
- **Design-arc candidate** — KnowledgeTransfer model realignment.

### Carried from S3025 / S3024 / older — all preserved from S3030 close 00-START.

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (PR #3751 planned end-to-end from S3030 forward-carry).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles. Zero rubber-stamp. 23 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris directive at S3030 close: "If you have the context can you knock out the did_promote in this terminal session?" — ratified the small clean lean per S3030 recommendation.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once post-PR-3751, clean at `sha=d7bb28b4f91f`.
- **Fold classification (PLAYBOOK-6.10.8):** 4 folds. A 2nd trigger. B/D informational carried. C 3rd cycle no-discovery.
- **Verify-before-build (Cycle 1A):** **16th consecutive session** — read method + 6 caller sites + grep for missing callers + grep for adjacent silent writes before spec.

## Wrapper pin note

Session-open pin was `pa-fea126fc09314e51` (minted at S3030 close). Close mints next pin; wrapper diff committed per `feedback_commit_wrapper_pin_bump_at_close`.

## Multi-session-in-one-terminal note

S3030 + S3031 both shipped in the same terminal session per Chris directive. S3030 was the primary directive (backfill for existing drift rows deferred from PR #3747); S3031 was the S3030 close recommendation ("small clean lean, closes the last known race in the arc"). Total shipped: 4 PRs across 2 sessions in one terminal (PR #3749 S3030 code, PR #3750 S3030 docs cascade, PR #3751 S3031 code, this docs cascade S3031 close).
