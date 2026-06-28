---
title: "Session 1250 PR 11 — Local Work Queue Exercise & Observation"
status: active
session: 1250
generated: 2026-06-28
companion_docs:
  - EVENT_SYSTEM_INVENTORY.md (§13 RigbyWorkItem, §16 harness, §18 exercise summary)
  - handoffs/SESSION_1250_PR10_LOCAL_INTAKE_EXERCISE.md (previous stage)
---

# Session 1250 PR 11 — Local Work Queue Exercise

**Mode:** Operator validation. No new platform code. Stage 2 of the
pipeline verified locally.

## TL;DR

- Flipped `RIGBY_EVENT_INTAKE_ENABLED=true` **and**
  `RIGBY_INTERNAL_WORK_QUEUE_ENABLED=true` locally.
- Triggered three Deliverable status transitions: forward / backward
  / terminal.
- **Exactly 3 MissionRuns + exactly 2 RigbyWorkItems created.**
  Forward (`ignore`) → 0 work items; backward (`monitor`) → 1 work
  item with priority=3; terminal (`notify`) → 1 work item with
  priority=5.
- Every Stage 3/4 gate held closed (no AgentExecution, no delegation
  lifecycle events, no notifications).
- **Stage 2 is safe to proceed.** Recommended next step:
  PR 12 — flip `RIGBY_WORK_QUEUE_REVIEW_ENABLED=true` locally and
  exercise the `rigby_work_item` PA tool review surface.

## Setup

Operator-side findings carried forward from PR 10:
- Flag must be set on **both** the signal-emitting process AND the
  `pa` worker.
- Cascade-delete on test User is blocked by pre-existing local-DB
  drift; clean up Deliverable + ProjectWorkspace + MissionRun
  directly.

### Process changes

```bash
# Stop existing pa worker
kill $(cat .celery-pa.pid)

# Start replacement with BOTH flags ON
PG_APPLICATION_NAME=dbz:celery-pa-pr11 SKIP_NLP_MODELS=1 \
  OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES TOKENIZERS_PARALLELISM=false \
  PA_USE_FUNCTION_CALLING=true \
  RIGBY_EVENT_INTAKE_ENABLED=true \
  RIGBY_INTERNAL_WORK_QUEUE_ENABLED=true \
  nohup .venv/bin/celery -A core worker --pool=solo --queues=pa \
    --hostname=pa-pr11@%h > celery-pa-pr11.log 2>&1 &
```

Baseline after PR 10 cleanup: 0 intake MissionRuns, 0 RigbyWorkItems.

## Exercise

Shell-side log (3 enqueues from the subscriber):

```text
[RIGBY_INTAKE_SUBSCRIBE] enqueued event_ref=deliverable_event:6ff05300-...  task_id=78745f25-...  dry_run=True  flag=ON
[RIGBY_INTAKE_SUBSCRIBE] enqueued event_ref=deliverable_event:ded72955-...  task_id=f381acca-...  dry_run=True  flag=ON
[RIGBY_INTAKE_SUBSCRIBE] enqueued event_ref=deliverable_event:0b59bf78-...  task_id=dab0f56d-...  dry_run=True  flag=ON
```

Result snapshot from the shell:

```text
[BASELINE] intake MissionRuns: 0; RigbyWorkItems: 0
[TRANS 1] forward (draft → ready)
[TRANS 2] backward (ready → draft)
[TRANS 3] terminal (draft → archived)
[RESULT] intake MissionRuns: 3 (delta 3)
[RESULT] RigbyWorkItems:     2 (delta 2)
```

## Expected vs actual

| Verification | Expected | Actual | ✓/✗ |
|---|---|---|---|
| `RIGBY_EVENT_INTAKE_ENABLED` ON | ON | ON | ✓ |
| `RIGBY_INTERNAL_WORK_QUEUE_ENABLED` ON | ON | ON | ✓ |
| `RIGBY_WORK_QUEUE_REVIEW_ENABLED` OFF | OFF | OFF | ✓ |
| `RIGBY_DELEGATION_ENABLED` OFF | OFF | OFF | ✓ |
| MissionRun count delta | +3 | +3 | ✓ |
| RigbyWorkItem count delta | +2 | +2 | ✓ |
| forward → 0 work items | 0 | 0 | ✓ |
| backward → 1 work item, decision='monitor', priority=3, status='open' | matched | `decision=monitor severity=warn mission_impact=low priority=3 status=open` | ✓ |
| terminal → 1 work item, decision='notify', priority=5, status='open' | matched | `decision=notify severity=notice mission_impact=medium priority=5 status=open` | ✓ |
| Each work item → correct source MissionRun (event_ref match) | matched | both items pass `wi.source_event_ref == mission_run.summary['event_ref']` | ✓ |
| 0 AgentExecution rows linked to RigbyWorkItem | 0 | 0 | ✓ |
| 0 delegation lifecycle OpsRunEvents | 0 | 0 | ✓ |
| Lag check reports OK | OK | OK | ✓ |

## RigbyWorkItem detail (ORM dump)

```text
RigbyWorkItem 8d8cbf19-38e5-4663-95c8-ab686211e40a
  decision=monitor  severity=warn  mission_impact=low  priority=3
  status=open  resolved_at=None
  source_event_ref=deliverable_event:ded72955-81af-4a65-9685-8c219b27cecf
  source_mission_run_id=481396bf-c1ac-4987-b7ba-2eb84f1de671
  title=Monitor: Deliverable rework signal

RigbyWorkItem d0d8d2e9-fd5e-45d3-80cb-1de48e748a5a
  decision=notify  severity=notice  mission_impact=medium  priority=5
  status=open  resolved_at=None
  source_event_ref=deliverable_event:0b59bf78-1c80-4d9e-a802-34407732ed88
  source_mission_run_id=4912a559-a09b-4596-80ba-1a1f64a9f95c
  title=Notify: Deliverable reached terminal state
```

Both items are `status='open'` with `resolved_at=NULL`. Titles are
the v0 templates from `_compose_work_item_fields` in
`core/services/rigby_event_intake.py`. Priority ladder matches §13.6
of the inventory (low=3, medium=5).

## Status command output (after exercise, both flags ON in shell)

```text
Rigby Intake Status
  generated: 2026-06-28T19:57:44.225018+00:00

Flags:
  [ON ]  RIGBY_EVENT_INTAKE_ENABLED
  [ON ]  RIGBY_INTERNAL_WORK_QUEUE_ENABLED
  [off]  RIGBY_WORK_QUEUE_REVIEW_ENABLED
  [off]  RIGBY_DELEGATION_ENABLED

Totals:
  all-time intake runs : 3
  last 24h             : 3
  last 7d              : 3
  currently running    : 0

Decision breakdown (7d):
  ignore                        1
  monitor                       1
  notify                        1

Recent intake runs (latest 3):
  4912a559-a09.. status=passed   decision=notify     impact=medium   events=3   work_item=✓ event_ref=deliverable_event:0b59bf78-...
  481396bf-c1a.. status=passed   decision=monitor    impact=low      events=3   work_item=✓ event_ref=deliverable_event:ded72955-...
  9b0273e8-db2.. status=passed   decision=ignore     impact=unknown  events=3   work_item=· event_ref=deliverable_event:6ff05300-...
```

**`work_item` column:** ✓ for the monitor + notify rows, · for the
ignore row. The PR 9 status command's `has_work_item` join works
exactly as designed — `True` for actionable decisions, `False` for
`ignore`.

## Lag check output

```text
Rigby Intake Lag Check — OK (threshold 5m)
  generated: 2026-06-28T19:57:50.124661+00:00
  No stuck intake MissionRuns.
```

## Side-effect gates verified independently

```text
AgentExecution rows linked to RigbyWorkItem: 0
Delegation lifecycle OpsRunEvents (any kind): 0
```

Plus the per-`ignore`-MissionRun check confirming no work item:

```text
MissionRun 9b0273e8-db2b-4fb3-8873-07afacdca246 (decision=ignore, event_ref=deliverable_event:6ff05300-...)
  associated RigbyWorkItems: 0
```

Every Stage 3/4 gate (PR 7 review tools, PR 8 delegation) held closed
exactly as designed.

## Anomalies

**None.** Stage 2 fired cleanly. Both PR 10 anomalies (flag-per-process
gotcha, local-DB cascade drift) were already known and applied
preventively — they did not surface again in PR 11.

## Cleanup state

| Item | Status |
|---|---|
| `pa` worker | restored to normal config (no exercise env vars), PID 87730 |
| Test Deliverables | deleted (4 cascade rows) |
| Test ProjectWorkspaces | deleted (1) |
| Test Users | left in DB (1 user; cascade still blocked by PR 10 anomaly A2; harmless) |
| Test MissionRuns + OpsRunEvents + RigbyWorkItems | **deleted** (14 cascade rows total: 3 MissionRuns + 9 OpsRunEvents + 2 RigbyWorkItems) |
| Final ORM counts | `OpsRun.objects.filter(domain='mission', run_kind='intake').count() == 0`; `RigbyWorkItem.objects.count() == 0` |

Local DB is back to baseline. The next operator exercise (PR 12)
starts from a clean state.

## Conclusion

**Stage 2 of the Rigby Event Intake → Work Queue pipeline is safe to
proceed.**

The full chain Deliverable.save → signal → intake task → MissionRun +
RigbyWorkItem (for actionable decisions only) fires correctly. The
`ACTIONABLE_DECISIONS = {monitor, notify}` filter in
`_maybe_create_work_item` works as designed — `ignore` decisions
produce zero work items, the other two produce exactly one each.
Priority ladder matches the spec. Status defaults to `open`. Both
items link back to their source MissionRun via `source_mission_run`
FK and to their source event via `source_event_ref`. The
`unique_together = ('source_event_ref', 'decision')` constraint isn't
exercised here (no re-runs), but the idempotency test suite
(`test_rigby_work_item.py`) covers that path.

## Recommendation — next stage (PR 12)

**PR 12: locally flip `RIGBY_WORK_QUEUE_REVIEW_ENABLED=true`**, keep
PR 8 flag OFF, exercise the `rigby_work_item` PA tool surface.

Suggested PR 12 exercise:

1. Re-run PR 11's exercise to produce 2 RigbyWorkItems (1 monitor, 1
   notify).
2. Via the PA tool dispatcher (or direct handler call):
   - `rigby_work_item action=list` — confirm both items returned,
     ordered by `-priority, -created_at` (notify first since
     priority=5 > monitor's 3), filtered by `status='open'`.
   - `rigby_work_item action=acknowledge work_item_id=<monitor>` —
     confirm status transitions `open → acknowledged` AND an
     `OpsRunEvent` with `label='work_item_acknowledged'` lands on
     the parent MissionRun.
   - `rigby_work_item action=resolve work_item_id=<notify> outcome=acted note='fixed'` —
     confirm `status → resolved`, `resolved_at` populated, and
     `work_item_resolved` event appended to MissionRun.
3. Run `rigby_intake_status` — `has_work_item` should still show ✓
   for both rows (the row exists; its status changed).
4. Verify no AgentExecution rows created, no delegation lifecycle
   events (PR 8 flag still OFF).
5. ORM-probe the parent MissionRun timelines — each acknowledged /
   resolved item should add one `OpsRunEvent` row with the matching
   label + `detail.work_item_id`.

If PR 12 is clean, PR 13 flips
`RIGBY_DELEGATION_ENABLED=true` and exercises the `delegate` action
end-to-end (which actually invokes `execute_agent_task.apply_async` —
this is the first stage that fires real agent work).

## Files changed in PR 11

Documentation only:

- `docs/handoffs/SESSION_1250_PR11_LOCAL_WORK_QUEUE_EXERCISE.md`
  (this file).
- `docs/EVENT_SYSTEM_INVENTORY.md` §18 — short exercise summary +
  link to this handoff.
- `docs/INDEX.md` — regenerated.

No code changes. No flag flips persisted. Production defaults
remain `False` for all four Rigby flags.
