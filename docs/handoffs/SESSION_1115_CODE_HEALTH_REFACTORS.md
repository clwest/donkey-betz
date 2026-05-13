---
title: "Session 1115 — code-health refactors (orphan Celery + LearningBridge ABC)"
date: 2026-05-12
status: active
session: 1115
previous_handoff: SESSION_1115_CONTEXT_KIT_DRIFT_CLEANUP.md
companion_handoff: SESSION_1115_CONTEXT_KIT_DRIFT_CLEANUP.md
---

# Session 1115 — code-health refactors

> **Read this if** you're trying to understand the May 2026 Celery
> task wiring + learning-bridge ABC work. Session 1115 ran in two
> phases on the same day. Phase 1 (the earlier handoff) was docs +
> verifier-only cleanup. Phase 2 (this handoff) turned into a 13-PR
> code-health arc that closed AUDIT_FINDINGS finding #9 entirely and
> took finding #12 from 272 → 10 orphans (96.3%).

## TL;DR

Two findings got worked end-to-end without OpenAI credits:

| Finding | Before | After | PRs |
|---|---|---|---|
| **#12 orphan Celery tasks** | 272 orphans (74% of registry) | **10 orphans (3% of registry)** | 8 PRs: #2079, #2080, #2081, #2082, #2083, #2084, #2085, #2086 |
| **#9 unused LearningBridge ABC** | 0 of 9 bridges inherit | **9 of 9 bridges inherit** (CLOSED) | 5 PRs: #2086, #2087, #2088, #2089, #2090 |

Both findings have forward-drift guards in `core/services/doc_claim_verification.py` at locked baselines:

- `_celery_orphan_count_baseline` → 10
- `_learning_bridges_inherit_base` → 0 (severity bumped `low` → `medium`)

## The arc, by batch

### Finding #12 — orphan Celery tasks

The detector itself was the biggest fix in the early batches. Most
"orphans" weren't dead — they were invoked through dispatch paths the
original detector didn't see.

| Batch | PR | Reduction | What changed |
|---|---|---|---|
| 1 | #2079 | 272 → 188 | Detector caught 3 indirect caller paths: `add_critical_celery_tasks.py` task dict, `ops_autopilot/budget.py` budget dict, same-name management commands |
| 2 | #2080 | 188 → 58 | Generic string-literal scan — dispatch patterns in `tasks_ops.py`, `discord_bot.py`, `views_autonomous_dashboard.py` pass task names as plain strings to dynamic dispatchers (`current_app.send_task(name)`). BSD-grep wrinkle: needed `[[:alnum:]_]` not `\w` |
| 3 | #2081 | 58 → 41 | Wired 14 safe DB-hygiene + metrics tasks (expire_old_*, cleanup_*, claim_stale_events, send_pending_notifications, check_*_slo, aggregate_roi_metrics_daily, calculate_daily_revenue_metrics) |
| 4 | #2082 | 41 → 24 | Wired 17 behavior-changing DB-only tasks (auto_approve_boardroom_items, auto_promote_low_risk_decisions, verify_completed_fixes, promote_to_shared_knowledge, hitl_escalations, lifecycle, etc.). Each verified by inspection: no LLM, no agent dispatch |
| 5 | #2083 | 24 → 19 | Detector bug fix — `_inspect()` was excluding **all** callers in the task's own definition file (intended to filter the `@shared_task` decorator line). Dropped legitimate intra-file parent→child chains in `intelligence/tasks.py` (proposal/response workflow). Fix: filter only the exact `file_path:line_no` of the task's definition |
| 6 | #2084 | 19 → 14 | Removed `@shared_task` from 4 dead stubs (`get_live_opportunities`, `get_live_predictions`, `trigger_market_scan`, `start_intelligence_engine` — zero callers anywhere). Wired `scan_income_spider_orchestrator` hourly (docstring said "Should run every hour") |
| 7 | #2085 | 14 → 11 | Final 3 forgotten wirings: `process_document_async` → Document.post_save signal, `trigger_content_from_shift` → NarrativeShift.post_save signal (via `current_app.send_task('narrative_drift.trigger_content_from_shift', ...)` to bypass function-vs-task-name mismatch), `start_resolve_render` → same-name `manage.py start_resolve_render` |
| 8 | #2086 | 11 → 10 | Deleted deprecated `propagate_new_policies` (Session 659 supersession — `PolicyContextService` handles policy injection automatically) |

**Remaining 10** are all constraint-deferred or intentional:

| Category | Count | Why |
|---|---:|---|
| LLM-cost scheduled | 5 | OpenAI credits depleted: `rag_retrieval_canary` (embeddings), `send_weekly_kpi_summary` (Discord), `run_ops_autopilot` (takes actions), `post_ops_digest`, `maintain_knowledge_freshness` |
| Agent-dispatch chains | 2 | Same green-light gate as finding #3: `check_blocked_research_for_unblock` (→ retry_blocked_research), `process_pending_action_plans` (→ execute_action_plan) |
| Session 1031 hard-blocked | 3 | `discover_and_import_audits`, `assign_open_findings_to_agents`, `execute_remediation_tasks` — all `return {'blocked': True}` immediately |
| Intentionally orphan | 1 | `debug_task` |

When OpenAI credits come back, the 5 LLM-cost tasks become tractable. When green-lit, the 2 agent-dispatch chains can be wired (same caution as finding #3). The Session 1031 set needs the underlying audit-tracker regex parsing to be fixed first.

### Finding #9 — LearningBridge ABC migration

All 9 concrete learning bridges migrated to inherit from `LearningBridge`. Each PR was a small, focused refactor of 1-2 bridges:

| Batch | PR | Bridges migrated | Baseline |
|---|---|---|---|
| 9 | #2086 | RevenueAttribution | 9 → 8 |
| 10 | #2087 | Collaboration + AgentExecution | 8 → 6 |
| 11 | #2088 | ApplicationOutcome + SpiderData | 6 → 4 |
| 12 | #2089 | AdvisorFeedback + AutoConsultation | 4 → 2 |
| 13 | #2090 | PersonalizationFeedback + SportsBetting | 2 → 0 ✅ |

After batch-13 the forward-drift guard severity was bumped from `low` → `medium` — any new bridge that doesn't inherit fails the verifier check at medium severity.

## Migration pattern (reusable)

For each bridge:

1. **Subclass `LearningBridge`** with descriptive `bridge_name`
2. **Implement 4 abstract methods**:
   - `process_event(event_data) -> Dict` — main entry, returns result dict
   - `_extract_patterns(event_data) -> Dict` — pull metrics + features
   - `_update_learning(patterns) -> None` — write the learning rows
   - `_generate_insights(patterns) -> List[str]` — human-readable strings
3. **Thread the ORM/event instance** through `patterns['_X']` so the
   1-argument `_update_learning(patterns)` contract works without
   losing access to the underlying model object
4. **Keep original entry methods as back-compat shims** — existing
   signal handlers (`on_revenue_saved`, `on_collaboration_completed`,
   etc.) keep working unchanged. Example:
   ```python
   def process_revenue_event(self, revenue: Revenue) -> Dict:
       """Back-compat shim — delegates to `process_event`."""
       return self.process_event(revenue)
   ```
5. **Free observability**: `log_event`, `log_success`, `log_error`,
   `event_count`, `success_count`, `get_statistics()`

## Pattern wrinkles (read these before adding a new bridge)

Each documented in detail in `docs/REFACTOR_GOTCHAS.md`:

1. **Multi-event dispatch** (PersonalizationFeedback batch-13): a single
   bridge handling two row types. Use `hasattr(event_data, 'X')` checks
   in `process_event` to route to type-specific helpers.

2. **Invocation-driven** (SportsBetting batch-13): not signal-driven.
   `process_event(user)` triggers a full sync. Original sync method
   stays as a back-compat method.

3. **Dict-driven** (AutoConsultation batch-12): `event_data` is a Dict,
   not a Django row. Optional `user` flows through as
   `event_data['_user']`. Original method returned `bool` — back-compat
   shim wraps `process_event` result and returns
   `result.get('status') == 'ok'`.

## Drift surfaces (where to check)

Every detector/wiring change has a verifier claim that catches future regressions:

```bash
# Quick green check
python manage.py verify_doc_claims --only-drift

# Targeted checks
python manage.py verify_doc_claims --doc docs/CELERY_AUDIT.md
python manage.py verify_doc_claims --doc core/learning_bridges/base.py
```

Both currently return `ok`:
- `celery_orphan_count_baseline` → 10 (was 245 pre-Session-1115)
- `learning_bridges_inherit_base` → 0 of 9 don't inherit (was 9 of 9)

## Files touched

### New files

- `core/signals/document_processing_signals.py` — Document + NarrativeShift signal handlers (batch 7)
- `core/management/commands/start_resolve_render.py` — same-name CLI wrapper (batch 7)
- `docs/REFACTOR_GOTCHAS.md` — central wrinkles doc (this handoff's companion)

### Modified

| File | Why |
|---|---|
| `core/celery.py` | Wired 32 new beat-schedule entries across batches 3-6 |
| `core/tasks.py` | Deleted `propagate_new_policies` (batch 8) |
| `intelligence/tasks.py` | Removed `@shared_task` from 4 dead stubs (batch 6); registered baseline still 14 fewer |
| `core/learning_bridges/*_bridge.py` | All 9 bridges refactored to inherit from `LearningBridge` |
| `core/learning_bridges/__init__.py` | Exported new document_processing_signals connector |
| `core/apps.py` | Wired `connect_document_processing_signals` into `ready()` |
| `core/management/commands/build_celery_audit.py` | Detector upgrades: 4 new caller-path scans + intra-file fix |
| `core/services/doc_claim_verification.py` | Verifier mirror of detector logic + baseline bumps |
| `docs/AUDIT_FINDINGS.md` | Per-batch outcome sections + closing entries for #9 and #12 |
| `docs/CELERY_AUDIT.md` | Auto-regenerated after every detector/wiring change |

## What's NOT in this work

- **Tests for the new signal handlers.** `process_document_async` and
  `trigger_content_from_shift` are now wired through Django signals but
  have no unit tests. If someone breaks the signal handler silently, the
  verifier won't catch it — the orphan detector sees the dispatch
  pattern, not the handler's correctness.
- **The 7 broken beat refs from finding #3** that need green-light to
  re-enable. Same gate as finding #12's behavior-changing tail.
- **Naming inconsistency cleanup** (the surface symptom of finding #9).
  All 9 bridges inherit now, but the suffix mix remains:
  `*LearningLoop` x7, `*LearningBridge` x1, `*FeedbackLoop` x1. Pure
  cosmetic — could be a future rename-only refactor if desired.

## Next session candidates (no OpenAI needed)

- Add unit tests for the 2 new signal handlers
- Address the cosmetic naming inconsistency (all 9 bridges to `*LearningLoop` suffix)
- Investigate Session 1031 audit-tracker regex parsing (the gate for
  unblocking 3 remaining orphans + the autonomous remediation pipeline)
- Tests for the back-compat shim layer on all 9 bridges
