# Session 1246 — S1245 bonus findings closed + audit_celery_zero_fire 5th axis + content/ char-training Celery surface retired + fleet caller verification

**Session window:** 2026-06-27 Saturday afternoon CDT/MDT (continuous from S1245 close).

**Theme:** Execute the S1245 P3/P4 carryover punch list (telemetry repr bug + ghost-task trace + zero-fire 5th axis) + the S1246 P2 content/ char-training retirement product-Q. Mid-session pivot to fleet-caller verification before merging deletion PRs, surfaced by Chris's "we might be deleting things we need because we didn't document the fleet apps properly" prompt. All 3 PRs cleared safe via Rigby runtime + Claude cross-repo ORM evidence and admin-merged at 22:53 UTC.

---

## TL;DR

- **3 PRs shipped + admin-merged** (#2692 + #2693 + #2694, all `session-1246-` subject-tagged).
- **S1245 P3.1 closed** — `task_name=str(sender)` repr bug in 3 Celery signal handlers fixed with shared `_extract_task_name(task, sender)` helper.
- **S1245 P3.2 closed** — `core.tasks.check_system_health` ghost task removed from PA's `ALLOWED_TASKS` whitelist (was never defined; zero hits via `git log -S "def check_system_health" -- core/tasks.py`).
- **S1246 P2 partial** — surgical deletion of the 3 dormant Celery tasks in `content/tasks.py`; bigger CharacterModel + 16-file chain retirement queued in deliverable `c5ea2f61-…` (Donkey Betz, status=ready) for S1247.
- **S1246 P4 closed** — `--include-direct-calls` 5th axis added to `audit_celery_zero_fire`; smoke-validated 3/3 incl. the exact S1245 blind-spot case (1 hit in `core/celery.py:629` for `intelligence.tasks.process_pending_action_plans`).
- **Fleet caller verification** — pre-merge sweep: 0 callers in any of 7 fleet repos + character-os + infra; 0 FleetServiceKey rows ever locally; 0 authenticated FleetPAChatAuditRow matches ever; 0 FleetArtifact mentions of any of the 4 task names.
- **2 deliverables produced by Rigby in Donkey Betz workspace** (post-correction from `cf708a2e-…` leak shape):
  - `421eeaca-fab8-4753-bd11-33a9b831ee96` — S1246 P1 morning_brief verification runbook (3,479 chars, status=ready)
  - `c5ea2f61-be21-4211-abd5-30d7c99983f7` — S1247 content/ char-training full retirement reachability map (7,067 chars after addendum, status=ready)
- **1 memory rule queued** for the close cascade (see §Memory).

### Net stats

- **3 PRs** admin-merged via `gh pr merge --admin --merge --delete-branch`
- **2 deliverables** advanced (P1 runbook + S1247 reachability map)
- **3 tasks deleted** (the 3 dormant Celery `@shared_task`s in `content/tasks.py`)
- **1 task_routes entry removed** from `core/settings.py`
- **1 ghost whitelist entry removed** from `td_handlers_gateway.py`
- **210 deletions + 5 insertions** in PR #2693
- **163 insertions + 1 deletion** in PR #2694
- **20 insertions + 5 deletions** in PR #2692

### Active conversation at close

- `pa-2bb73c969fd24802` — Session 1246 thread Rigby created at S1245 close.
- Mid-session topic spread: 1 (deliverable, plus the fleet verification thread within).
- Health at S1246 mid-session check: 100/continue/1 turn (very early in session).
- After the multi-ask + content sweep + fleet verification round: should be re-pulled at S1247 open. Likely fine to continue.

---

## What shipped — PRs

| PR | SHA | Subject | Net | Stage |
|---|---|---|---|---|
| [#2692](https://github.com/clwest/donkey-betz-platform/pull/2692) | `fbc77b81` | celery telemetry task_name + remove ghost task whitelist | +20/-5 | merge `57071592` |
| [#2693](https://github.com/clwest/donkey-betz-platform/pull/2693) | `cc9ab2c1` | delete dormant content/ char-training Celery tasks | +5/-211 | merge `1f1edabe` |
| [#2694](https://github.com/clwest/donkey-betz-platform/pull/2694) | `48e135e9` | audit_celery_zero_fire --include-direct-calls axis | +163/-1 | merge `660c6b5e` |

---

## P3.1 close — `task_name=str(sender)` repr bug

S1245 close found a CeleryTaskEvent row with `task_name='<@task: core.tasks.cleanup_stale_agent_executions of unified_donkey_betz_core at 0x10b8d91d0>'` — the bad-repr shape that comes from `str(task_obj)` instead of `task.name`.

Root cause located at 3 sites in `core/celery_telemetry.py`:
- `on_task_prerun:87` — `task.name if task else str(sender)` (partial — falls through to bad repr when `task` is None and `sender` is the Task instance, which IS the normal case Celery sends)
- `on_task_postrun:133` — same partial pattern
- `on_task_failure:197` — JUST `str(sender)` (no fallback chain at all; this was the worst of the 3 and the most likely emitter of the bad-shape row)

Fix: shared `_extract_task_name(task, sender)` helper that pulls `.name` off whichever object the signal carried in priority order:

```python
def _extract_task_name(task, sender):
    name = getattr(task, 'name', None) or getattr(sender, 'name', None)
    if isinstance(name, str) and name:
        return name
    return str(sender) if sender is not None else ''
```

Applied to all 3 signal handlers. Smoke test (6/6) covers:
- task object with `.name` → uses it
- only sender has `.name` (real Celery scenario) → uses it
- task wins over sender when both have `.name`
- neither has `.name` (degenerate) → falls back to `str(sender)`
- both None → empty string (not a bad-shape row)
- **Task instance whose `__repr__` returns `<@task: ...>` → returns `.name`, NOT the repr** (the exact S1245 bug repro)

---

## P3.2 close — ghost task `core.tasks.check_system_health`

S1245 close found telemetry rows for `core.tasks.check_system_health` despite the task not appearing in `current_app.tasks`. Traced via:

- `git log -S "def check_system_health" -- core/tasks.py` → **zero hits, ever**
- Repo-wide grep → only matches are the private method `_check_system_health` in `core/services/metadata_tracking.py` (unrelated) and the whitelist string itself
- Frontend → zero references

Stuck-QUEUED rows came from `td_handlers_gateway.py:982` writing CeleryTaskEvent eagerly with `status='QUEUED'` when PA dispatched, then worker rejecting the unregistered task with no postrun/failure signal to update the row.

Fix: removed `'core.tasks.check_system_health'` from `ALLOWED_TASKS`. Stale QUEUED rows for the task name will age out via `CELERY_TASK_EVENT_RETENTION_DAYS` (30d default).

---

## P2 (S1246) close — content/ char-training Celery surface retired

Chris green-lit content/ retirement at S1246 mid-session. Rigby's verify-before-delete sweep classified it `has-live-callers` for the model + view + agent surface (16 files importing `CharacterModel`), so the deletion was scoped to Option C:

**Surgical scope (this PR):**
- Whole-file delete of `content/tasks.py` (only contained the 3 tasks; nothing else in the module)
- Removed `'content.tasks.poll_pending_trainings'` from `core/settings.py` `task_routes`

**Deferred to S1247:**
- `content/models.py CharacterModel` + the 16-file dependency chain
- `content/character_training.py` + migration 0014
- `core/views_character_training.py` (URL-registered — Rigby confirmed live in `core/urls.py:2920+`)
- `core/views_image_helpers.py` + `core/epa_handlers_tools.py` imports
- 2 training agents (`CharacterTrainingAgent`, `TrainedCreationAgent`) + `ai_core/agents/brand_style_agent.py`
- 5 `tests/one-off/*` files

**Why safe (S1246 evidence):**
- 0 PeriodicTask rows for any of the 3 task names
- 0 CeleryTaskEvent telemetry events ever (per S1245 audit_celery_zero_fire 14d window)
- 0 live Python imports of `content.tasks.*` anywhere in `core/`, `agents/`, `ai_core/`, `frontend/`
- Smoke test: `current_app.tasks` deregisters all 3 names + `task_routes` parses to 278 entries with removed route absent

---

## P4 close — `audit_celery_zero_fire --include-direct-calls` 5th axis

S1245 probe blind-spot: a task that was (registered) AND (zero-fire in telemetry window) AND (not in AUDIT_FINDINGS.md #12 KNOWN_DEFERRED) could still have a direct Python caller in a mgmt command and look deletable. Existing command's line 223 already said "Verify direct-Python-call references with `rg "\b<short>\s*\("` before any cleanup PR" — a manual step now automated.

**Implementation:**
- `_resolve_task_defsite(task_name)` — best-effort def-site lookup via `inspect.getsourcefile(current_app.tasks[name].run)`. None on failure (non-fatal).
- `_count_direct_callers(task_name, repo_root)` — subprocess call to `rg` with `--type py`, 10s timeout. Excludes def-site file + this audit cmd + `build_celery_audit` cmd (both enumerate task names as data) + any `def <short>(` line (defensive defsite-resolution backup).
- Wired into JSON output (new `direct_call_report` + `direct_call_skipped_reason` keys) and human output (per-task `direct=N` suffix when flag set).
- Skips gracefully if `rg` not on PATH.

**Validation:** 3 known cases hit expected results:
- `core.tasks.run_all_spiders` → `hits=0` (beat-driven; no direct Python callers — correct)
- `core.tasks.generate_morning_brief_daily` → `hits=7` all in `core/tests/test_morning_brief_sub_step_c.py` (test callers)
- `intelligence.tasks.process_pending_action_plans` → **`hits=1` in `core/celery.py:629`** — exactly the S1245 blind-spot case the axis was built for

---

## Fleet caller verification — mid-session pivot

Chris flagged the risk surface ("we might be deleting things we need because we didn't document the fleet apps properly") before merging #2692 + #2693. Three-axis sweep:

### Cross-repo grep (Claude)

| Repo | Refs to `poll_pending_trainings` / `check_single_training` / `cleanup_stale_trainings` / `check_system_health` / `CharacterModel` / `content.tasks` |
|---|---|
| signal-studio | 0 |
| mentorforge | 0 |
| pitchdeckforge | 0 |
| contract-concierge | 0 |
| sellerpilot | 0 |
| dealflowtracker | 0 |
| compliancesentinel | 0 |
| character-os | 0 |
| infra | 0 |
| 24-7-ai-global | 0 |
| ai-content-studio | Different `content/tasks.py` (generate_text_content, generate_image_content, etc.) — independent Django app, not relevant |
| dbao-studio | Same as ai-content-studio — different `content/tasks.py` namespace, independent app |

### Runtime tools (Rigby)

- `ops_tool.celery_task_history` 30d window: 0 events for all 3 content/training tasks; 1 stuck QUEUED row for `core.tasks.check_system_health` on 2026-06-22T19:50:02Z
- `db_health_tool` confirmed fleet table schemas
- Initial risk read: PR #2693 LOW; PR #2692 MED (ambiguous source of the QUEUED row)

### Direct ORM (Claude)

- `FleetServiceKey.objects.count() == 0` — no fleet keys ever provisioned in this local DB
- `FleetServiceIdentity.objects.filter(is_active=True).count() == 0`
- `FleetPAChatAuditRow.objects.filter(match=True).count() == 0` — zero authenticated fleet calls ever recorded
- `FleetArtifact` ORM probe with `payload::text ILIKE ... OR caller_metadata::text ILIKE ...` for all 4 task names → 0 hits
- The 4 PAChatAuditRow rows in the ±10 min window around the QUEUED `check_system_health` event all have `verified_app_slug=''`/`match=None` (unauthenticated local PA traffic)
- QUEUED event itself has `agent_name=''` `queue='default'` — looks like a local PA dispatch from a prior session

### Verdict — all 3 PRs cleared safe; both Claude and Rigby signed off

**Caveat for S1247:** Local DB has 0 FleetServiceKey rows ever + 0 authenticated calls. Possible explanations: (a) fleet keys live only in prod, (b) fleet integration has gone dormant locally, (c) keys were never provisioned here. Filed in the S1247 reachability map addendum (1865 chars appended to deliverable `c5ea2f61-…`): "Fleet caller verification (S1246 sweep): zero local evidence; verify prod before any model-layer deletion in S1247."

---

## Workspace leak watch — cf708a2e still active

`workspace_tool` status check showed active workspace was still **`cf708a2e-…` (Session 1231 E2E sandbox)** — the meeting-context leak shape on the watch list since S1230 F2. Rigby was instructed to explicitly pass `workspace_id=b4503364-…` (Donkey Betz) on both deliverable creates; both verified post-create with `workspace.id` starts `b4503364`. ORM cross-check (Claude verifies): both deliverables on Donkey Betz, status=ready, content_length 3479 + 5200 (later 7067 with addendum).

Filed as S1246 F-bonus in the runbook deliverable: rotation rule isn't auto-firing — `cf708a2e-…` has been active since 2026-06-24 despite S1245 having flagged it.

---

## Subfindings — character training agents are smoke-only

Rigby's `ops_tool.execution_search` showed the only AgentExecution rows for `CharacterTrainingAgent` + `TrainedCreationAgent` are **fleet-smoke no-op receipts** ("Fleet smoke: return one-sentence receipt of capability. No deliverables. No code review. No file writes."). Last real-looking ones:

- CharacterTrainingAgent: most recent 2026-06-24T23:41:05Z = fleet smoke receipt
- TrainedCreationAgent: most recent 2026-06-24T23:52:44Z = fleet smoke receipt
- BrandStyleAgent: not registered in agent_introspection_tool at all (suggestions point to `BrandIdentityAgent`/`BrandStrategyAgent`)

So those two training agents are "reachable via dispatch" only because fleet smoke tests ping every agent. Strengthens the S1247 full-retirement case.

---

## Memory rules

One memory rule queued for the close-cascade per Chris's "we might be deleting things we need" prompt:

**`feedback_fleet_caller_verification_before_celery_deletes.md`** — Before merging any Celery task deletion PR, do a 3-axis fleet caller sweep: (1) cross-repo grep all 7 fleet apps + character-os + infra for task name refs, (2) Rigby runtime check via `ops_tool.celery_task_history` + `FleetPAChatAuditRow` queries, (3) direct ORM probe of `FleetServiceKey` rows + `FleetArtifact` payload/caller_metadata ILIKE. Local-DB-only verdict has a known blind spot (fleet keys may live only in prod) — flag it explicitly in close docs. Verdict pattern: surface as a Rigby risk read ("LOW provisional based on N=...") + a Claude verification ("CONFIRMED: 0 hits across X, Y, Z") + a caveat for prod. Reason: S1246 mid-session pivot caught a documentation-gap risk before merging #2692/#2693, validating Chris's "verify-before-delete" rule extends to cross-repo concerns. How to apply: any session that touches `task_routes`, `core/celery.py` registration, `core/services/td_handlers_gateway.py:trigger_task` whitelist, or task `@shared_task` deletes needs this sweep before merge.

---

## Chris-side carryover into S1247

- Anthropic credit refill at https://console.anthropic.com/billing — still failing CI billing
- All 3 S1246 PRs admin-merged
- **06-28 morning_brief CUMULATIVE verification time-bound to ~13:00 UTC Sunday (= 07:00 MDT)** — uses Rigby's runbook deliverable `421eeaca-fab8-4753-bd11-33a9b831ee96`
- Local fleet integration appears dormant (0 active FleetServiceKey) — worth a clarifying question about prod state
- The 5 tests/one-off/* files in the character-training chain don't need deletion-first; they're detachable along with the model when the S1247 retirement plan ships
