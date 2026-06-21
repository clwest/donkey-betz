# Session 1191 — Initiative system lifecycle fix: cheap staleness sweep + auto-populate bootstrap

**Status:** Complete. 1 PR merged (#2392). Initiative system P1 closed.
**Date:** 2026-06-21
**Pinned conversation:** `pa-55d90b2a34524bf9` (Session 1190 thread, continued; healthy at session-end).
**Prior session:** [`SESSION_1190_PARTIAL_WORKSPACE_CONSOLIDATION_AND_SCRUBBER_FIX.md`](./SESSION_1190_PARTIAL_WORKSPACE_CONSOLIDATION_AND_SCRUBBER_FIX.md).

## TL;DR

Rigby's call at session open: tackle (b) Initiative system lifecycle fix first (workspace consolidation deferred to next session). Recon found two layered root causes for the cluster of Initiatives stuck at `current_stage=1` with `last_activity_at=null`:

1. `populate_initiatives_api` (`core/views_research_demo.py`) never called `update_activity()` after `Initiative.objects.create()` — auto-populated Initiatives born cold.
2. `advance_initiative_pipeline` is intentionally NOT beat-scheduled per `docs/narratives/INITIATIVES_AND_LIFECYCLE.md §6.4` (Rigby's Session 1162 verdict) — expensive, side-effectful task; on-demand is the safety call.

Routed 4 fix-shape options through Rigby (A: bug fix only, B: A + cheap activity tick, C: A + bounded beat for advance, D: question the artifact). Rigby picked **B** with tight scope. Shipped PR #2392 with both halves of the two-layer fix + a backfill mgmt command. Live-verified on local DB: `examined=30 refreshed=14`, target stuck row `f9eb535f-...` went from NULL → 2026-06-21 10:05:00.

## What landed (this session)

| PR | Commit | Theme |
|---|---|---|
| **#2392** | `eeac179a` | `feat(session-1191-initiative-activity-tick)` — Two-layer fix for Initiative.last_activity_at=null. (1) populate_initiatives_api bootstrap via `update_activity(reason='auto_populate_create')`. (2) new `_impl_initiative_activity_tick` — no-LLM, no-side-effects beat task crontab(*/30), aggregates `max(initiative.updated_at, action_items.updated_at, deliverables.updated_at)` with strict GT-only writes, hard cap 100, `@singleton_task(ttl=300)`, `max_retries=0`. Optional `reason` kwarg added to `Initiative.update_activity()`. New `backfill_initiative_activity` mgmt command for historical NULL rows. 9 unit tests covering the populate bootstrap + every tick behavior. Preserves §6.4 invariant: `advance_initiative_pipeline` remains on-demand only. |

**Live proof (local DB, post-merge):**
- `backfill_initiative_activity` updated 11 NULL rows to `created_at` (idempotent, supports `--dry-run`).
- Celery restarted via `make celery`; `initiative_activity_tick` registered across default/broadcast/long_running.
- `add_critical_celery_tasks` materialized the PeriodicTask row (crontab=`*/30`, queue=default, enabled=True).
- Manual `.delay()` dispatch returned `{examined: 30, refreshed: 14, skipped_no_signal: 0, stale_after_hours: 24, hard_cap: 100}` in 100ms.
- Spot-check on `f9eb535f-1335-4f0b-a320-8341023f136f` (Auto-populated From 11 Newsletter Deliverables): was NULL in Rigby's session-open list, now `2026-06-21 10:05:00.061246+00:00` (max cheap signal).

## Behavioral invariants (post-merge)

- Auto-populated Initiatives are never born with `last_activity_at=null` (populate_initiatives_api fix).
- `last_activity_at` reflects the max of cheap signals; refreshed at most every 30 min.
- `advance_initiative_pipeline` (LLM, stage advancement, content writes) is untouched — still on-demand only per §6.4.
- Steady state: `refreshed` count drifts toward 0 (strict GT-only write + tick's own update_fields=['last_activity_at'] doesn't bump `initiative.updated_at`).

## Rollback levers

- Disable beat task: `PeriodicTask.objects.filter(name='initiative-activity-tick').update(enabled=False)` — kills the sweep without code revert.
- Bypass per-call: pass `hard_cap=0` to dispatch a no-op.
- Full rollback: revert commit `eeac179a`; singleton lock TTL=300s, so any in-flight run exits within 5 min.

## 24h watch checklist

- Grep `celery.log` for `[INITIATIVE-TICK]` every ~30 min — expect summary lines.
- After 24h, `refreshed` should drift toward 0 in steady state.
- No `singleton_task` skipped lines in `celery.log` (would mean a tick run >300s — investigate as separate finding).
- `Initiative.objects.filter(last_activity_at__isnull=True).count()` should return 0 (backfill + bootstrap both protective).

## Recon findings (preserved for the docs/narratives layer)

**Two layered root causes:**
1. **Cold-born:** `core/views_research_demo.py:1921-1927` creates Initiative records via `Initiative.objects.create(...)` with `created_by='auto_populate'` and `current_stage=1` but never invoked `update_activity()`. 9 of the 30 Initiatives Rigby surfaced were the "Auto-populated From N X Deliverables in..." class — born NULL.
2. **No driver:** `advance_initiative_pipeline` is intentionally not in `app.conf.beat_schedule` per `docs/narratives/INITIATIVES_AND_LIFECYCLE.md §6.4`. Rigby's Session 1162 verdict: "always-on beat scheduling for an expensive document-generating task with side effects (LLM calls, content writes) would be risky. On-demand is coherent."

**`update_activity()` callsites that DO work (6 places):** `conversation_initiative_pipeline.py:861`, `models_document_registry.py:1569`, `tasks_initiatives.py:2491`, `tasks_initiatives.py:2935`, `tasks_conversations.py:3148`, `tasks_conversations.py:3302`. The hand-crafted TRIAGE Initiatives Rigby pointed at (553fb8fc, 67cc9023, etc.) all had non-null `last_activity_at` because they routed through one of these paths.

## Collaboration shape (this session)

Rigby owned: opening recon read (initiative_list + first triage of the auto-populated cluster), fix-shape sequencing call (picked B over A/C/D with tight acceptance criteria), pre-PR safety amendment (`max_retries=0`), memory-candidate phrasing.

Claude owned: code edits (6 files modified + 2 new), unit tests, backfill mgmt command, branch + commit + PR open + admin-bypass merge, handoff writing.

Every fork-in-the-road moment routed scope through Rigby first per `feedback_rigby_scope.md`. The triage decision card pattern (`feedback_triage_decision_card_pattern.md`) was used for the 4 fix-shape options.

## New memory candidates captured

All 3 ratified by Rigby and saved as feedback memories with index entries in `MEMORY.md`:

1. **Invariant check first** ([`feedback_invariant_check_first.md`](../../.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_invariant_check_first.md)) — when something "isn't running," grep narratives for "by design" before fixing forward. The "fix" might violate a §X.Y invariant.
2. **Two-layer root cause rule** ([`feedback_two_layer_root_cause_rule.md`](../../.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_two_layer_root_cause_rule.md)) — stuck states often have both cold-born + no-driver defects. Fix both or label PR cosmetic-only.
3. **Cheap staleness aggregator pattern** ([`feedback_cheap_staleness_aggregator_pattern.md`](../../.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_cheap_staleness_aggregator_pattern.md)) — reusable 8-step shape for any parent.last_activity_at-style field. Tick + singleton lock + GT-only writes + hard cap + max_retries=0.

## Deferred to Session 1192 (next session's pick list)

- **Workspace consolidation Steps 4-7** (carried over from Session 1190) — P1, ~74 deliverables still to triage and migrate to Donkey Betz (`b4503364-2573-4401-9e28-61a739e0ce50`).
- **7d AC watches** — starts 2026-06-28 (first meaningful read after a full week of real traffic on Session 1188+1189 spider context PRs).
- **PR-D contract flip** — Deliverable `9d9db48a-...`. 24h WARN-volume gate elapsed; run the grep at AC1.
- **C-trace remediations #1, #4** — from Session 1187. Structural.
- **Initiative system follow-on** (optional, not P1): if 7d watch on `initiative-activity-tick` shows the steady-state drift NOT going to 0, investigate which signal source is constantly writing. Could surface a misbehaving subsystem.

---

**Branch:** `feat/session-1191-initiative-activity-tick` (deleted post-merge).
**Files changed:** 6 modified + 2 new = 407 insertions, 1 deletion.
**Test count:** 9 new (all passing).
