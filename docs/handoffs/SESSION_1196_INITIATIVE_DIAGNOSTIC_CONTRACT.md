# Session 1196 — Initiative no-orphan contract (`initiative_create` write-path enforcement)

**Status:** Wrapped clean. **6 Plan C side-quest PRs merged** + post-apply local inventory verified + sweep readiness check green + 7-day watch queued for 2026-06-29.
**Date:** 2026-06-22
**Active conversation:** `pa-ea12236c83eb4826` (spun fresh at session open per Rigby's Session 1195 close-recommendation).
**Prior session:** [`SESSION_1195_PLAN_C_PHASE_1_COMPLETE.md`](./SESSION_1195_PLAN_C_PHASE_1_COMPLETE.md).

## TL;DR

Session 1195 close-out identified a structural hole in the no-orphan contract Plan C Phase 1 shipped: the deliverable factory could detect Initiative-alignment violations only when `initiative.target_workspace_id` was set, but Session 1195 recon found **68 DBZ deliverables linked to Initiatives with no `target_workspace_id`** — Plan C couldn't evaluate alignment for them. This session closed that hole end-to-end across 6 atomic PRs by extending the same Phase 1 pattern (diagnostic block + signal hooks + daily sweep + tests + backfill recon) to the Initiative write-path.

The contract is now sealed in both directions:
- **Deliverable side (Plan C Phase 1, Session 1195):** factory marks misaligned creates, update tool path auto-clears, daily 3:45 AM sweep retires expired ones, recon command quantifies.
- **Initiative side (Session 1196):** post-save signal marks creates with no `target_workspace_id`, model-level auto-clear handles ws-set transitions from any path (admin/UI/scripts/mgmt), daily 3:55 AM sweep retires expired ones, recon + apply mgmt cmd retroactively flags pre-existing orphans.

## PRs shipped

| PR | Branch | Theme | Merge commit |
|---|---|---|---|
| **#2409** | `feat/session-1196-initiative-diag-migration` | Migration — 5 diagnostic fields + 3-col composite index on Initiative | `bf17a049` |
| **#2410** | `feat/session-1196-initiative-diag-signal` | Post-save signal create-mark + `INITIATIVE_DIAGNOSTICS_ENABLED` kill switch + stable `[ORPHAN-INITIATIVE]` warn-log | `14a3ad18` |
| **#2411** | `feat/session-1196-initiative-diag-clear` | Pre-save snapshot + post-save auto-clear on `target_workspace_id` NULL→set transition (`.update()` to dodge recursion) | `76483f9f` |
| **#2412** | `feat/session-1196-initiative-diag-sweep` | Daily sweep beat task at 3:55 AM Denver + manual mgmt cmd `sweep_diagnostic_initiatives` | `c95625f6` |
| **#2413** | `feat/session-1196-initiative-diag-tests` | 15-case regression test suite (12 from design matrix + Rigby PR #5 additions 11/12/13) | `557c80dd` |
| **#2414** | `feat/session-1196-initiative-diag-backfill` | `backfill_initiative_workspace_links` recon mgmt cmd with idempotent `--apply` flag | `9d44012d` |

## Architecture diverged from Plan C — and why

Plan C wraps the deliverable factory directly (`create_deliverable` calls `_evaluate_initiative_alignment` explicitly inline). Session 1196 uses a **post-save signal** instead because Initiative has **8+ create callsites** with no single factory to wrap:

1. `core/services/initiative_integration_service.py:167` — `get_or_create_initiative` (PA path, 21/30 of orphans)
2. `core/services/conversation_initiative_pipeline.py:494`
3. `core/services/hivemind_execution_pipeline.py:476`
4. `core/services/td_handlers_core.py:2772`
5. `core/services/autonomous_action_executor.py:1120`
6. `core/models_unified_system.py:9656`
7. `core/views_research_demo.py:1921` — auto-populate path (9/30 of orphans)
8. `core/management/commands/extract_initiatives_from_survey.py:225`

Plus admin form saves and direct ORM scripts that no factory would catch.

Rigby ratified the signal-based approach in `pa-ea12236c83eb4826` with 5 guardrails:

1. **Narrow trigger** — `created=True` only on the mark path; `old None → new not None` only on the clear path. No double-fire.
2. **Kill switch** — `INITIATIVE_DIAGNOSTICS_ENABLED` setting (default `True`) gates the field mutation; warn-log fires regardless so visibility survives emergency disable.
3. **`.update()` not `.save()`** — auto-clear and sweep both bypass the post_save dispatch to dodge recursion (PR #3 + PR #4).
4. **No-op on nothing-to-clear** — `clear_initiative_diagnostic()` returns bool; handler short-circuits.
5. **Observability** — `[INITIATIVE-DIAGNOSTIC-CLEARED]` log at INFO; `[ORPHAN-INITIATIVE] code=ttl_auto_archive ...` at INFO during sweep.

## Post-apply inventory (local — production rollout pending)

After `python manage.py backfill_initiative_workspace_links --apply` on local DB:

| Metric | Value |
|---|---|
| Total Initiatives with `diagnostic_code='missing_target_workspace_id'` | **30** |
| By status — TRIAGE | 12 |
| By status — ARCHIVED | 9 |
| By status — COMPLETED | 7 |
| By status — ACTIVE | 2 |
| By creator — `PersonalAssistant` | 21 |
| By creator — `auto_populate` | 9 |
| `diagnostic_payload.backfilled=True` (mgmt cmd marks) | 30 |
| Create-time signal marks | 0 |

Note: ARCHIVED + COMPLETED (16 total) are terminal — sweep won't touch them per the filter. The 14 non-terminal rows (12 TRIAGE + 2 ACTIVE) are the actual sweep candidates.

## Sweep readiness check (green)

```
Beat schedule entry: sweep-diagnostic-initiatives
  Task: core.tasks.sweep_diagnostic_initiatives
  Schedule: <crontab: 55 3 * * * (m/h/dM/MY/d)>  # 3:55 AM Denver
  Options: {'queue': 'default', 'expires': 3600}
```

Mgmt cmd dry-run against live DB: `Would archive 0 of 0 candidates` — because no rows are expired yet (TTL 168h, marked at session-close = 2026-06-22). All 14 sweep candidates will expire 2026-06-29, exactly aligning with the planned 7-day watch start.

## Production rollout playbook

```bash
# Step 1 — capture baseline JSON
python manage.py backfill_initiative_workspace_links --sample 5 --json-only > /tmp/2026-06-22-baseline.json

# Step 2 — retroactively mark pre-existing orphans diagnostic
python manage.py backfill_initiative_workspace_links --apply

# Step 3 — ensure celery worker restart picks up new @shared_task
pkill -9 -f celery; rm -f .celery*.pid; make celery

# Step 4 — verify sweep is registered + reachable
.venv/bin/celery -A core inspect registered | grep sweep_diagnostic_initiatives
python manage.py sweep_diagnostic_initiatives --dry-run
```

## 7-day watch (starts 2026-06-29, queued for Session 1197+)

Re-run recon and compare against the 2026-06-22 baseline:

```bash
python manage.py backfill_initiative_workspace_links --json-only > /tmp/2026-06-29-snapshot.json
diff <(jq -S . /tmp/2026-06-22-baseline.json) <(jq -S . /tmp/2026-06-29-snapshot.json)
```

Expected: archived count goes up; candidate_for_flag stays at 0 (signal catches all new orphans); already_diagnostic for non-terminal rows decreases to 0 by sweep day.

If trend looks good, Plan C Phase 2 hard-reject decision (Session 1195 close-out item) can move forward. If unexpected drift, investigate before Phase 2.

## Drift workstream (parked per Rigby Option A)

`makemigrations` during PR #2409 prep surfaced pre-existing mechanism drift unrelated to Session 1196:

**Set A — 4 unmigrated Narrative* models** (defined in `core/models_narrative_drift.py` since Session 471, Sept 2024). Migrations 0103 + 0115 exist + applied per `django_migrations`, but no `core_narrative*` tables in DB. Suggests prior `--fake` apply or schema reset.

**Set B — ~16 AlterField operations** on `agentexecution`, `curatedsignalentry`, `finalappliedoverrides`, `fleetpachatauditrow` (mostly choices/help_text drift).

Per `feedback_corpus_walks_surface_mechanism_drift.md`: surface and route, don't bridge. Tracked as a P2/P3 follow-up — leave untouched until time allows a careful investigation. Workspace ticket TBD (Rigby to create as part of Session 1196 close).

## Live behavior on `main`

Effective after `9d44012d` (PR #6) merge:

1. **New orphan create** → post-save signal marks `diagnostic_status='diagnostic'`, `diagnostic_code='missing_target_workspace_id'`, TTL +7d, payload includes `created_by` + `callsite_hint` + `status_at_mark`. `[ORPHAN-INITIATIVE]` warn-log fires.
2. **Setting `target_workspace_id` via any path** (admin, UI, mgmt cmd, ORM, tool handlers) → pre-save snapshot detects the NULL→set transition, post-save clears all 5 fields via `.update()`. `[INITIATIVE-DIAGNOSTIC-CLEARED]` INFO-log fires.
3. **Daily 3:55 AM Denver sweep** → archives expired diagnostic Initiatives (non-terminal status only), augments `diagnostic_payload` with `archived_by`/`archived_reason='ttl_expired'`/`archived_at`/`status_was`. Non-destructive — all 5 diagnostic_* fields preserved.
4. **Operator backfill** → `--apply` retroactively flags pre-existing orphans diagnostic. Idempotent. Marks payload `backfilled=True` for attribution.
5. **Kill switch** — `INITIATIVE_DIAGNOSTICS_ENABLED=False` suppresses create-mark mutation; auto-clear and sweep still run (clearing a stale diagnostic is always safe).

## Rollback levers

| Switch | Effect |
|---|---|
| `INITIATIVE_DIAGNOSTICS_ENABLED=False` | New creates: no field mutation; warn-log still fires. Clear path + sweep unaffected (clearing is always safe). |
| Disable signal via `post_save.disconnect(..., dispatch_uid='session_1196_initiative_diagnostic_post_save')` | Hard-disable create-mark path; sweep + clear paths still functional. |
| Disable beat schedule via `PeriodicTask.objects.filter(name='sweep-diagnostic-initiatives').update(enabled=False)` | Stops daily sweep; signal create-mark + auto-clear still functional. Diagnostic Initiatives accumulate until re-enabled. |
| Revert migration 0361 | Nuclear option — removes all 5 diagnostic_* fields. Requires PR #6 backfill apply to be rolled back first (or `--apply` becomes a no-op when the fields don't exist). Not expected to be needed. |

## Files added (net)

- `core/migrations/0361_session_1196_initiative_diagnostic_fields.py`
- `core/services/initiative_diagnostics.py`
- `core/signals/initiative_diagnostic_signals.py`
- `core/tasks.py` — `sweep_diagnostic_initiatives` `@shared_task` (added)
- `core/celery.py` — `sweep-diagnostic-initiatives` beat schedule entry (added)
- `core/management/commands/sweep_diagnostic_initiatives.py`
- `core/management/commands/backfill_initiative_workspace_links.py`
- `core/tests/test_initiative_workspace_diagnostics.py`

## Files modified

- `core/models_document_registry.py` — 5 fields + composite index on Initiative
- `core/apps.py` — wire `connect_initiative_diagnostic_signals` in `_register_signals`
- `core/signals/__init__.py` — export + `__all__` entries

## Open items for Session 1197

1. **Operator runs `backfill_initiative_workspace_links --apply` in prod** — locks the baseline. Worker restart required for the new `@shared_task` to be visible.
2. **7-day watch starting 2026-06-29** — re-run recon, compare against baseline, confirm sweep is archiving non-terminal expired rows.
3. **Plan C Phase 2 hard-reject decision** (DEFERRED-7d from Session 1195 close) — still time-gated to 2026-06-29. Now data-informed by both the Plan C 7d watch AND Session 1196 baseline drift.
4. **Drift workstream** — workspace ticket creation + eventual cleanup.
5. **Local test DB infra** (still P2) — `DJANGO_TEST_DATABASE_URL` support not yet implemented. Plan C + Session 1196 test suites can't run locally. CI is authoritative.

## Active conversation pin

`pa-ea12236c83eb4826` — Session 1196 close. Healthy. Rigby will likely recommend spinning fresh for Session 1197 given the focus shifts to the 7-day watch + Phase 2 decision design.
