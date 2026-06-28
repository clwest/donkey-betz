---
title: "Session 1250 PR 10 — Local Intake Exercise & Observation"
status: active
session: 1250
generated: 2026-06-28
companion_docs:
  - EVENT_SYSTEM_INVENTORY.md (§16 harness, §17 exercise summary)
---

# Session 1250 PR 10 — Local Intake Exercise

**Mode:** Operator validation. No new platform code. One finding documented.

## TL;DR

- Locally enabled `RIGBY_EVENT_INTAKE_ENABLED=true` against the live DB.
- Triggered three Deliverable status transitions: forward / backward / terminal.
- Stage 1 of the pipeline behaved exactly as specified — three MissionRuns
  created, three correct decisions (ignore / monitor / notify), every
  side-effect gate held closed.
- One operator-facing gotcha surfaced: the flag must be set on **both**
  the signal-emitting process AND the worker, not just the worker.
- **Stage 1 is safe to proceed.** Recommended next step: flip
  `RIGBY_INTERNAL_WORK_QUEUE_ENABLED=true` locally and re-exercise.

## Setup

```text
Before: all 4 Rigby flags OFF; 0 intake MissionRuns; 0 RigbyWorkItem rows.
Worker stack: `make celery` stack from earlier in the session (5 workers).
```

### Operator gotcha — set the flag on BOTH processes

First attempt: stopped the existing `pa` worker (PID 78013) and started a
replacement with `RIGBY_EVENT_INTAKE_ENABLED=true` baked into the env.
Triggered three transitions via `python manage.py shell`. **Result: 3
DeliverableEvent rows written, 0 MissionRuns created.**

Diagnosis: the signal handler in
`core/signals/deliverable_status_signals.py:_enqueue_rigby_intake`
reads `settings.RIGBY_EVENT_INTAKE_ENABLED` in the **same process that
saves the Deliverable** — i.e., the shell — not the worker. With the
flag set only on the worker, the shell saw it as `False` and never
called `apply_async`. The worker's flag is irrelevant for the gate
check; it's only relevant for what the task body does (and the task
body never ran because the message was never enqueued).

Worker log showed zero "Task received" entries despite three saves.
The `[RIGBY_INTAKE_SUBSCRIBE]` log line was also absent from the shell
output — the gate check was returning early.

**Fix:** invoke the shell with the env var explicitly:

```bash
RIGBY_EVENT_INTAKE_ENABLED=true .venv/bin/python manage.py shell <<'EOF'
...
EOF
```

This is **correct platform behavior** — the gate is per-process, which
is what the design intended. It's worth a sentence in
`docs/EVENT_SYSTEM_INVENTORY.md` §12.7 ("Current operational state")
or §16.1 ("Local-only rollout shape") since operators may set the env
on `make celery` but forget the shell.

## Exercise — three transitions, three decisions

After fixing the operator setup, ran:

```python
deliverable = Deliverable.objects.create(status='draft', ...)
deliverable.status = 'ready';    deliverable.save()  # forward
deliverable.status = 'draft';    deliverable.save()  # backward
deliverable.status = 'archived'; deliverable.save()  # terminal
```

Each save took ~6ms; each intake task completed before the next save
fired. Signal-side log (3 subscriber enqueues):

```
[RIGBY_INTAKE_SUBSCRIBE] enqueued event_ref=deliverable_event:369dc6b6-...  task_id=3045f89c-...  deliverable_id=79e1e720-...  dry_run=True  flag=ON
[RIGBY_INTAKE_SUBSCRIBE] enqueued event_ref=deliverable_event:fb1d75ad-...  task_id=48d64851-...  deliverable_id=79e1e720-...  dry_run=True  flag=ON
[RIGBY_INTAKE_SUBSCRIBE] enqueued event_ref=deliverable_event:50c39efe-...  task_id=15ad4a61-...  deliverable_id=79e1e720-...  dry_run=True  flag=ON
```

## Status command output (after exercise)

```text
Rigby Intake Status
  generated: 2026-06-28T19:48:03+00:00

Flags:
  [ON ]  RIGBY_EVENT_INTAKE_ENABLED
  [off]  RIGBY_INTERNAL_WORK_QUEUE_ENABLED
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
  12bbd443-d02.. status=passed   decision=notify     impact=medium   events=3   work_item=· event_ref=deliverable_event:50c39efe-...
  6d9451b7-ef4.. status=passed   decision=monitor    impact=low      events=3   work_item=· event_ref=deliverable_event:fb1d75ad-...
  98c5be14-93d.. status=passed   decision=ignore     impact=unknown  events=3   work_item=· event_ref=deliverable_event:369dc6b6-...
```

**Operator note:** the `Flags` block reflects the state of the
process **running the status command**, not the state when the
MissionRuns were created. Running `rigby_intake_status` without the
env var shows the flag as `[off]` even though the runs above were
clearly produced with it on. This is consistent (status is a snapshot
of "right now") but slightly counter-intuitive. The decision breakdown
+ row count are the real evidence that the intake ran.

## Lag check output

```text
Rigby Intake Lag Check — OK (threshold 5m)
  generated: 2026-06-28T19:47:57+00:00
  No stuck intake MissionRuns.
```

## Expected vs actual

| Expectation | Actual | ✓/✗ |
|---|---|---|
| Only `RIGBY_EVENT_INTAKE_ENABLED` ON; other 3 OFF | confirmed by status command flag block | ✓ |
| MissionRun count increments by 1 per transition | baseline=0 → after=3 | ✓ |
| `running_count` returns to 0 after each | 0 throughout (intake is millisecond-scale) | ✓ |
| forward → decision='ignore' (impact=unknown) | matched on row 1 (19:47:11) | ✓ |
| backward → decision='monitor' (impact=low) | matched on row 2 (19:47:13) | ✓ |
| terminal → decision='notify' (impact=medium) | matched on row 3 (19:47:15) | ✓ |
| Each MissionRun has exactly 3 timeline events | `timeline_event_count: 3` for all three; ORM probe confirms (`intake_started`, `impact_assessed`, `decision_made`) | ✓ |
| `has_work_item: false` for every row | `work_item=·` for all three | ✓ |
| 0 RigbyWorkItem rows created | ORM probe = 0 | ✓ |
| 0 AgentExecution rows linked to RigbyWorkItem | ORM probe = 0 | ✓ |
| No delegation occurs | no `delegation_started` / `agent_assigned` / etc. events on any MissionRun | ✓ |
| Lag check reports OK | confirmed | ✓ |

## MissionRun timeline shape verified

```text
MissionRun 98c5be14-... status=passed decision=ignore
  intake_started   event_type=info  detail_keys=['dry_run', 'event_ref', 'source', 'source_id']
  impact_assessed  event_type=info  detail_keys=['mission_impact', 'reason', 'rules_fired', 'severity']
  decision_made    event_type=info  detail_keys=['decision', 'dry_run', 'mission_impact', 'reason', 'rules_fired']

MissionRun 6d9451b7-... status=passed decision=monitor
  intake_started   event_type=info       (same keys)
  impact_assessed  event_type=info       (same keys)
  decision_made    event_type=step_pass  detail_keys=['decision', 'dry_run', 'mission_impact', 'reason', 'rules_fired']

MissionRun 12bbd443-... status=passed decision=notify
  intake_started   event_type=info       (same keys)
  impact_assessed  event_type=info       (same keys)
  decision_made    event_type=step_pass  detail_keys=['decision', 'dry_run', 'mission_impact', 'reason', 'rules_fired']
```

Notes on `event_type`:
- `decision_made` uses `event_type='info'` when decision is `ignore`
  and `event_type='step_pass'` when decision is anything else.
  This matches PR 4 §11.7's intent: `step_pass` for "we did something",
  `info` for "we chose to do nothing."
- `intake_started` + `impact_assessed` are always `info` — they're
  process events, not outcomes.

## Anomalies

### A1 — flag must be set on both signal-emitting AND worker process

Documented above. Not a platform bug; operator setup gotcha.

**Recommendation:** add a sentence to `EVENT_SYSTEM_INVENTORY.md`
§12.7 noting that the flag check runs in the signal-emitting process,
not the worker, so `export RIGBY_EVENT_INTAKE_ENABLED=true` must be
visible to whichever process saves the Deliverable (Django shell,
runserver, the `default` worker, etc.) — not just the `pa` worker.

### A2 — pre-existing local DB cascade-delete drift (unrelated to PR 10)

Cleaning up the test User cascade-deleted into
`learning_bridges_advisorconsultationfeedback` which doesn't exist
on Chris's local DB (unapplied migration). Worked around by
deleting Deliverable + ProjectWorkspace directly; test users left
in the DB (3 rows, harmless). Not a PR 10 issue — pre-existing
local-DB drift between migrations and ORM relations.

### A3 — status command flag block reflects current process, not historical state

When running `rigby_intake_status` without the env var set, the
`Flags` block shows `[off]` for `RIGBY_EVENT_INTAKE_ENABLED` even
when the listed MissionRuns were clearly produced with it on.
Operators interpreting "is the pipeline live right now?" → fine;
operators interpreting "were these runs produced under this flag
config?" → misleading. Worth a docstring or §16 note. Not a bug —
the status command is a snapshot, not a history.

## Side-effect gate verification (independent ORM check)

```text
RigbyWorkItem rows for the exercise deliverable: 0  (queue flag off → none expected)
RigbyWorkItem rows actually found:                0
AgentExecution rows linked to RigbyWorkItem:      0
```

Stage 1 produces no Stage 2/3/4 side effects. The pipeline gates work
as designed.

## Cleanup state

| Item | Status |
|---|---|
| `pa` worker | restarted to normal config (no exercise env var) |
| Test Deliverables | deleted (8 cascade rows total — 2 deliverables × 4 child rows including the 3 DeliverableEvents) |
| Test ProjectWorkspaces | deleted (2) |
| Test Users | **left in DB** (cascade blocked by A2; safe — 3 rows, no FK weight) |
| Test MissionRuns + OpsRunEvents | **left in DB as exercise evidence** (3 MissionRuns + 9 OpsRunEvents — tiny, harmless, can be deleted later) |

To remove the exercise evidence from the local DB:

```python
from core.models_ops_runs import OpsRun
OpsRun.objects.filter(
    domain='mission', run_kind='intake',
    summary__event_ref__startswith='deliverable_event:',
    title__startswith='intake: deliverable_event:',
    started_at__gte='2026-06-28T19:47:00+00:00',
    started_at__lt='2026-06-28T19:48:00+00:00',
).delete()
```

## Conclusion

**Stage 1 of the Rigby Event Intake pipeline is safe to proceed.**

The full chain DeliverableEvent → signal → enqueue → intake task →
MissionRun + 3 OpsRunEvents fires correctly. Decision rules match
the spec for all three transition directions. Every downstream gate
held closed. The lag check correctly reports OK under normal load.

## Recommendation — next stage

**PR 11: locally flip `RIGBY_INTERNAL_WORK_QUEUE_ENABLED=true`**, keep
the other two flags OFF, re-exercise with the same three transitions.

Expected new behavior:
- The `monitor` transition (backward) should produce **1 RigbyWorkItem**
  row with `decision='monitor'`, `mission_impact='low'`, `priority=3`,
  `status='open'`.
- The `notify` transition (terminal) should produce **1 RigbyWorkItem**
  row with `decision='notify'`, `mission_impact='medium'`, `priority=5`,
  `status='open'`.
- The `ignore` transition (forward) should produce **0 RigbyWorkItems**
  (ignore decisions never make work items).
- All three MissionRun timelines still have exactly 3 OpsRunEvents
  (PR 6 doesn't add new ones).
- `rigby_intake_status` `has_work_item` column should show `True` for
  rows 1 and 2, `False` for row 3.

If PR 11 looks clean, PR 12 could flip
`RIGBY_WORK_QUEUE_REVIEW_ENABLED=true` and exercise the
`rigby_work_item.list / acknowledge / resolve / ignore` PA tools.

## Files changed in PR 10

Documentation only:

- `docs/handoffs/SESSION_1250_PR10_LOCAL_INTAKE_EXERCISE.md` (this file).
- `docs/EVENT_SYSTEM_INVENTORY.md` §17 — short exercise summary +
  link to this handoff.
- `docs/INDEX.md` — regenerated via `build_docs_index`.

No code changes. No flag flips persisted. The exercise was local-only
and operator-driven; production defaults remain `False` for all four
flags.
