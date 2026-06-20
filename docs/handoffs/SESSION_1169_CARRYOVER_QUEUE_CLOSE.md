---
originating_session: 1169
provenance_confidence: HIGH
provenance_note: Hand-authored Session 1169 handoff. Five PRs merged closing the entire Session 1168 + 1167 carryover queue, plus one tracking deliverable for schema drift surfaced incidentally. Rigby ratified each design pre-implementation in conv pa-639751f029bc432f (same thread continued from Session 1168 — health 75/100 at session entry, 'continue' recommendation per session_tool.health_check). All five followed the Sessions 1165–1168 bypass-merge pattern with explicit per-PR Chris auth. Live PA-dispatch verification of Layer C Phase 1 reason_code propagation executed post-restart through Rigby.
---

# Session 1169 — Carryover queue close (B-C-E-A-D-1 stretch path)

**Date:** 2026-06-20 (UTC)
**Branch state at session close:** All work merged. Main is clean. Five PRs landed in the order Rigby set: 2 → 3 → F → D → 1.

---

## TL;DR

Session 1169 cleared the full Session 1168 + Session 1167 carryover queue plus one incidentally-surfaced tracking item:

- **Item 2 — Idempotent enforce-disabled in `add_critical_celery_tasks`** (Rigby's late add from Session 1168 close). PR #2314 prevented NEW denylisted rows from being added; this PR closes the loop by re-asserting `enabled=False` on any existing rows the materializer finds. Idempotent — rows already disabled aren't touched. Live smoke verified the toggle fires only on `enabled=True` denylist hits.
- **Item 3 — Symmetric attach-aware lookup for `detail` / `save` / `unsave` / `append` / `delete` / `export_pdf`** on orphans. Extends PR #2311 (Session 1168 Bug #2) from `update`-only to all id-based mutation actions. Proactive fix — same `_id_lookup_qs` helper applied across the 7 actions. `link_initiative` (in `td_handlers_content.py`) intentionally not touched per scope cap.
- **Item F — `agent_name` dim on `CeleryTaskEvent` + `top_consumers(group_by='agent')`.** Closes carryover F via a single migration + signal-handler tweak + service-level `group_by` arg. Surfaced an incidental schema drift (4 unrelated Narrative tables + a pile of AlterField ops) during `makemigrations` — quarantined out of the surgical migration and tracked separately.
- **Item D — `monitor_celery_health` decorator-side timeouts.** Adds `queue='broadcast', soft_time_limit=60, time_limit=90` to the `@shared_task` so direct `.delay()` / `.apply_async()` calls outside beat also get bounded. Critical finding documented: timeouts alone are NOT sufficient for monitor tasks that fan out to broker/Redis inspect comms — `capture_pa_acks_health_snapshot` has carried the same timeouts since Session 1161 and STILL measured p95=1880s on PR #2306. Probe decomposition is the real fix; queued as Session 1170+ work.
- **Item 1 — `DeliverableGatedError` + `raise_on_gated` kwarg (Layer C Phase 1).** Rigby's phased migration plan, scope-capped per her advice. Phase 1 ships the primitive (typed exception class + 3-tuple gate return + new kwarg with `False` default preserving legacy contract) plus 3 hot-path opt-in migrations: PA dispatcher, `base_agent`, PA research-and-create. Phase 2 = batched sweep of remaining 24 callers; Phase 3 = flip default OR add deprecation log.

| PR | Theme | Merge SHA |
|---|---|---|
| **#2316** | `feat` — **Item 2:** idempotent enforce-disabled for denylisted PeriodicTask rows on local | `d421d1de` |
| **#2317** | `fix` — **Item 3:** symmetric attach-aware lookup for id-based deliverable mutations | `93e4e436` |
| **#2318** | `feat` — **Item F:** `agent_name` dim on `CeleryTaskEvent` + `top_consumers(group_by='agent')` | `1bc96909` |
| **#2319** | `fix` — **Item D:** decorator-side timeouts on `monitor_celery_health` + probe-decomposition operator note | `362960db` |
| **#2320** | `feat` — **Item 1:** `DeliverableGatedError` + `raise_on_gated` kwarg (Layer C Phase 1) | `a71b5a3e` |

**51 new tests** total across 5 new test files; all pass green.

---

## Behavioral invariants post-merge (what's now true)

1. **Denylisted Celery beat tasks stay disabled on local DB.** `add_critical_celery_tasks` doesn't just prevent new denylisted rows from being added — on local-safe mode (RAILWAY_ENVIRONMENT unset/empty), it also toggles any existing `enabled=True` rows in the denylist back to `enabled=False`. Idempotent: rows already at False are not touched. `ENABLE_BEAT_TASKS=<csv>` override skips both the prevent-add and the toggle for opted-in tasks.
2. **All id-based deliverable mutation actions find orphans for owners.** `detail` / `save` / `unsave` / `update` / `append` / `delete` / `export_pdf` use the shared `_id_lookup_qs()` helper that respects user-ownership but ignores workspace scoping. Non-staff users still cannot touch other users' deliverables (security regression covered by tests).
3. **`CeleryTaskEvent.agent_name` field exists** and is populated by the `task_prerun` signal handler when task kwargs include any of `agent_name` / `agent_class` / `agent` (string only) / `agent_type`. Empty string for non-agent tasks + pre-Session-1169 rows (no backfill — gradual fill per Rigby's skip-joins-in-v1 stance). Indexed.
4. **`ops_tool.top_consumers` accepts `group_by='task'` (default, backwards compat) or `group_by='agent'`.** Agent dim filters out empty `agent_name` rows so non-agent tasks don't dominate. `compute_top_consumers` raises `ValueError` on unknown `group_by` (locked allowlist).
5. **`monitor_celery_health` has decorator-side timeouts.** `queue='broadcast', soft_time_limit=60, time_limit=90` on the `@shared_task` itself. Direct dispatches now bounded; was previously running with Celery defaults (no time limit) outside beat.
6. **`create_deliverable()` legacy `None`-return contract preserved** for the 27 production callers that haven't migrated. Three hot-path callers opted in to `raise_on_gated=True` and now receive `DeliverableGatedError` with `reason_code` (`gate_1_media_stub` / `gate_2_smoke_pattern` / `gate_3_min_length` / `unknown_gate`).
7. **PA dispatcher gated response carries the factory's actual reason_code** (verified live post-merge — `reason_code='gate_2_smoke_pattern'` end-to-end on a smoke-test-titled `deliverable_tool.create`). Pre-Session-1169 the response always returned the generic `'unknown_gate'` placeholder regardless of which gate fired.

---

## Rollback / disable levers per change

### PR #2316 (Item 2 — enforce-disabled)

- **Soften:** revert just the `_enforce_disabled_local()` wiring in `handle()` — keeps the helper definition but stops calling it. Denylisted rows will silently re-enable next time a session manually flips them.
- **Full revert:** `git revert d421d1de`. Filter from PR #2314 still holds (new rows still prevented); only the toggle of existing rows reverts.
- **Disable for a specific run:** `ENABLE_BEAT_TASKS=<all-denylist-names-csv>` skips both the filter and the toggle.

### PR #2317 (Item 3 — symmetric attach-aware lookup)

- **Soften:** remove the `_id_lookup_qs()` helper definition; the if-statements then fall back to `base_qs` lookup. Orphan find for non-staff users with workspace context breaks again (back to Session 1168 Bug #2 state for non-update actions). Update action still works because PR #2311's inline logic remains in the action body history — but it's been replaced with the helper call here, so this would need careful rebase.
- **Full revert:** `git revert 93e4e436`. Restores Bug #2 to non-update actions. PR #2311's update fix still in place.
- **Per-action override:** none. The helper is unconditionally used for the 7 id-based actions.

### PR #2318 (Item F — agent_name dim)

- **Soften (lookup only):** remove the `_extract_agent_name()` call from `on_task_prerun`. New rows write empty `agent_name`. Field stays in schema; existing data not affected.
- **Soften (surface only):** remove `group_by='agent'` from `_VALID_GROUP_BY` in `top_consumers.py`. Calls with `group_by='agent'` then raise `ValueError`. Existing rows + extraction unchanged.
- **Full revert:** `git revert 1bc96909` followed by `python manage.py migrate core 0354`. Drops the `agent_name` column.
- **Data note:** the migration is additive (new column, blank default); no risk of data loss on rollback.

### PR #2319 (Item D — monitor_celery_health timeouts)

- **Soften:** revert just the decorator change to restore the original `@shared_task(name='core.tasks.monitor_celery_health')`. Direct-dispatch path becomes unbounded again; beat-scheduled fires still have the implicit queue routing.
- **Full revert:** `git revert 362960db`. Includes the docs addendum which describes the probe-decomposition pattern — that wisdom would be lost on full revert.
- **Note:** doesn't touch `_impl_monitor_celery_health` body. If the timeout fires aggressively (60s soft), the impl just logs `SoftTimeLimitExceeded` and returns; no state corruption risk.

### PR #2320 (Item 1 — Layer C Phase 1)

- **Soften (typed dispatcher only):** in `td_handlers_agents.py:1876`, set `raise_on_gated=False` and restore the `if obj is None:` check from PR #2310. Dispatcher reverts to generic `'unknown_gate'` reason_code in the response. Factory + exception class + tests stay.
- **Soften (one caller at a time):** revert any individual migration by setting `raise_on_gated=False` in that call and restoring the pre-migration error-handling pattern. base_agent (`if deliverable is None: return None`) and td_handlers_core (`except Exception` only) are well-documented in the commit message.
- **Full revert:** `git revert a71b5a3e`. Restores Session 1168's PR #2310 dispatcher + Session 1094's base_agent guard. Phase 1 primitive lost; would need re-implementation for Phase 2.
- **Critical:** do NOT delete the `DeliverableGatedError` class without also reverting every caller migration — Phase 2 follow-ons will land that depend on it.

---

## 24h watch checklist

Concrete copy-paste commands per invariant. Same `date -u +%Y-%m-%d` UTC convention as Session 1167's playbook.

### Item 2 + Item 3 (deliverable surfaces)

```bash
# (1) Denylisted PeriodicTask rows stay disabled on local
.venv/bin/python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
from core.management.commands.add_critical_celery_tasks import LOCAL_DENY_TASKS
rows = list(PeriodicTask.objects.filter(name__in=LOCAL_DENY_TASKS).values('name', 'enabled'))
print('Denylist rows ({}/{}):'.format(len(rows), len(LOCAL_DENY_TASKS)))
for r in sorted(rows, key=lambda r: r['name']):
    flag = '✗' if r['enabled'] else '✓'
    print(f'  {flag} {r[\"name\"]} (enabled={r[\"enabled\"]})')
"
# Expect: all 6 with ✓ (enabled=False).

# (2) Orphan mutations work for non-staff users — through Rigby (live PA):
#       deliverable_tool.detail(id='<orphan>', workspace_id='<chris-personal>')   → ok
#       deliverable_tool.append(id='<orphan>', content='...')                     → ok
#       deliverable_tool.delete(id='<orphan>')                                    → ok (deletes)
```

### Item F (agent_name dim)

```bash
# (1) New CeleryTaskEvent rows have agent_name populated when the task
#     carries agent-named kwargs:
.venv/bin/python manage.py shell -c "
from core.models_celery_telemetry import CeleryTaskEvent
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=24)
agent_rows = CeleryTaskEvent.objects.filter(started_at__gte=since).exclude(agent_name='')
print(f'Rows with agent_name in last 24h: {agent_rows.count()}')
for r in agent_rows[:5]:
    print(f'  - {r.agent_name} via {r.task_name}')
"
# Expect: non-zero count if agent dispatches happened post-merge.

# (2) ops_tool.top_consumers(group_by='agent') through Rigby:
#       expect populated 'consumers' list with 'agent_name' keys
#       (or empty if no agent fires in window)
```

### Item D (monitor timeouts)

```bash
# (1) monitor_celery_health decorator carries expected timeouts:
.venv/bin/python manage.py shell -c "
from core.tasks import monitor_celery_health
print('queue:', monitor_celery_health.queue)
print('soft_time_limit:', monitor_celery_health.soft_time_limit)
print('time_limit:', monitor_celery_health.time_limit)
"
# Expect: broadcast / 60 / 90.

# (2) ops_tool.top_consumers(window='24h') through Rigby — does
#     monitor_celery_health p95 drop now that direct dispatches are
#     bounded? Pre-Session-1169 was p95=1048s. Compare 24h post-merge.
```

### Item 1 (Layer C Phase 1)

```bash
# (1) PA dispatcher gated response carries machine-parseable reason_code
#     through Rigby:
#       deliverable_tool.create(title="Smoke test verify", content="anything")
#     Expected: ok=false, reason_code='gate_2_smoke_pattern' (NOT 'unknown_gate'),
#               reason='smoke test pattern in title'.
#     VERIFIED post-merge by Rigby at session close (Session 1169).

# (2) Factory contract still backwards compatible — call without
#     raise_on_gated keyword:
.venv/bin/python manage.py shell -c "
from core.services.deliverable_factory import create_deliverable
# Smoke-test title + no raise_on_gated → should return None, not raise.
result = create_deliverable(
    title='Smoke test legacy contract',
    content='x' * 400,
    agent_name='SomeAgent',
    metadata={'trigger_source': 'pa_tool'},
)
print('legacy contract result:', result)
"
# Expect: None.
```

---

## Carryover to Session 1170

### From this session's work

1. **Layer C Phase 2 — sweep remaining 24 callers.** Batched by file category:
   - `services/*` (~10 sites: `td_handlers_newsletter`, `td_handlers_core` (remaining 2 of 3), `deliverable_envelope`, `mission_control_executor`, `conversation_deliverable_extractor`, `deliverable_append_service`, `workspace_pipeline_runner`, `conversation_initiative_pipeline`, `implementation_executor` x2)
   - `tasks_*.py` (~5 sites: `tasks_content`, `tasks_initiatives` x2, `tasks_conversations`, etc.)
   - `views_*.py` (~3 sites: `views_diagnostics` x2, `views_workspace_templates`, `views_demo_pipeline`)
   - `management/commands/*.py` (~6 sites: 5 external-repo commands + `import_patent_disclosures`)
   - Each batch small enough to review per-caller.
2. **Layer C Phase 3 — flip default OR add deprecation log.** Decision point: do we want the clean invariant (no silent None) by deleting the legacy contract, or measure remaining legacy callers before the flip? Should follow Phase 2.
3. **`capture_pa_acks_health_snapshot` probe decomposition.** Real fix for the p95=1880s. Split the body into 4 cadence tasks (queue depth, workers inspect, hang signature, inflight estimate), each with its own timeout. Per the Session 1169 PR #2319 doc addendum: monitor tasks that fan out to broker/Redis inspect comms can't be fixed by timeouts alone.
4. **Schema-drift reconciliation deliverable `b58b20b3`.** Tracking item Rigby created during Session 1169 for the unrelated drift surfaced by `makemigrations` (Narrative subsystem + 11 cosmetic AlterFields). Cluster A (Narrative) needs an explicit owner; Cluster B (CuratedSignalEntry `needs_regen`) needs intent confirmation + a migration; Cluster C (help_text-only drift) can be batched at any time or left forever — no schema impact.

### Standing aspirational items (still queued)

- **`pg_stat_statements` on staging/prod.** Installed locally Session 1165.

---

## Session-level patterns worth noting

These came up during Session 1169 and are general enough that future sessions will benefit. Captured here rather than in a separate memory feedback file because they're tightly scoped to the carryover pattern:

1. **`makemigrations` bundles every model-vs-state drift it finds, not just the change you asked for.** If you're shipping a surgical model change, audit the generated migration file BEFORE adding the dependency. Quarantine unrelated drift into a separate tracking item; don't ship it bundled. (Item F caught the Narrative subsystem + 11 AlterFields. Surgical migration `0355_session_1169_celerytaskevent_agent_name.py` ships only the field; drift tracked in deliverable `b58b20b3`.)
2. **Decorator-side options matter even when the beat-side options are correct.** Beat scheduling carries its own `options` block (queue, expires, etc.) but those only apply to scheduled fires. Direct `.delay()` / `.apply_async()` calls use the `@shared_task` decorator's options. If a task is called both ways (which most are), the decorator MUST carry the queue + timeouts independently of beat. Caught on Item D: `monitor_celery_health` was missing decorator-side `time_limit` entirely, so manual dispatches ran unbounded.
3. **Timeouts alone don't bound monitor tasks that block in C-level calls.** `soft_time_limit` raises `SoftTimeLimitExceeded` only between Python bytecode operations. A blocking broker `inspect()`, Redis `BLPOP`, or filesystem scan doesn't yield. Evidence: `capture_pa_acks_health_snapshot` has had `soft_time_limit=60, time_limit=90` since Session 1161 yet still measures p95=1880s. Probe decomposition (split into per-check cadence tasks) is the real fix.
4. **Phased migrations beat single-PR sweeps when caller count is high.** Item 1's Layer C had 27 callers. Rigby's instinct (Option C in the design pass) — ship the primitive + 3-5 hot-path opt-ins in Phase 1, sweep batches in Phase 2, flip default in Phase 3 — is much safer than trying to audit 27 sites in one PR. Reduces regression risk; lets ops measure the new contract working in production before the migration completes.

---

## Conversation state at session close

- **Active PA conversation:** `pa-639751f029bc432f` (continued from Session 1168; Rigby's `session_tool.health_check` at Session 1169 entry returned `75/100, continue`).
- **Health at close:** not re-measured; thread carried 6 design passes + 5 verification rounds + 1 schema-drift triage + 1 close ping. Likely now in `recommend_fresh` territory. Plan to mint a new thread at Session 1170 entry.
- **`tools/pa_local.sh`:** still points at `pa-639751f029bc432f`. Will be updated at Session 1170 entry if a fresh thread is created.

---

## What didn't happen (intentional)

- **Layer C Phases 2 and 3:** scope-capped per Rigby's phased migration design call. The 24-caller sweep + default flip are queued, not ignored.
- **`capture_pa_acks_health_snapshot` probe decomposition:** the simple timeout add isn't sufficient for this task (the existing timeouts from Session 1161 didn't help). Real fix is its own design pass and PR. Documented + queued.
- **Schema-drift Cluster A (Narrative subsystem) cleanup:** tracked in deliverable `b58b20b3` for an owner to claim. Not Session 1169's scope to design/migrate that subsystem.
- **Phase 1 grep CI check:** Rigby suggested an optional repo-wide check to flag new blind-`.id` access after `create_deliverable(...)`. Skipped to keep PR #2320 tight; can be added in Phase 2.
- **Operator playbook cross-refs into `docs/topics/agent-system.md` for Layer C:** the factory contract is well-documented inline (docstring on `create_deliverable`, attributes on `DeliverableGatedError`, commit message, PR description). A standalone doc section can land alongside Phase 2.

---

## File touchpoints summary

- `core/management/commands/add_critical_celery_tasks.py` (Item 2: enforce-disabled helper + handle() wiring)
- `core/services/td_handlers_agents.py` (Item 3: `_id_lookup_qs` helper across 7 actions; Item 1: PA dispatcher Layer C migration)
- `core/models_celery_telemetry.py` (Item F: `agent_name` field)
- `core/migrations/0355_session_1169_celerytaskevent_agent_name.py` (Item F: surgical migration)
- `core/celery_telemetry.py` (Item F: `_extract_agent_name` helper + `on_task_prerun` wiring)
- `core/services/top_consumers.py` (Item F: `group_by` arg + agent-dim SQL)
- `core/services/td_handlers_ops.py` (Item F: dispatcher group_by threading)
- `core/tasks.py` (Item D: decorator timeouts on monitor_celery_health)
- `core/services/deliverable_factory.py` (Item 1: `DeliverableGatedError` class + 3-tuple gate + `raise_on_gated` kwarg)
- `core/agents/base_agent.py` (Item 1: hot-path opt-in)
- `core/services/td_handlers_core.py` (Item 1: PA research-and-create opt-in)
- `docs/topics/celery-workers.md` (Items D + F: operator playbook addenda)
- `core/tests/test_enforce_disabled_local.py` (Item 2: 7 tests)
- `core/tests/test_deliverable_orphan_mutations_symmetric.py` (Item 3: 9 tests)
- `core/tests/test_celery_telemetry_agent_extract.py` (Item F: 13 tests)
- `core/tests/test_top_consumers.py` (Item F: 6 new tests on `group_by='agent'`)
- `core/tests/test_monitor_celery_health_timeouts.py` (Item D: 4 tests)
- `core/tests/test_deliverable_factory_gated_exception.py` (Item 1: 13 tests)
- `core/tests/test_deliverable_create_gated.py` (Item 1: 2 tests updated for typed exception)
- `tools/pa_local.sh` (still points at `pa-639751f029bc432f`; session bookkeeping, not in any PR)

**5 PRs / 18 files touched / +1,540 / -150 / 51 new tests, all passing. Plus 1 tracking deliverable `b58b20b3` for schema drift.**
