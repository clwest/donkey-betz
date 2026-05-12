# Audit Findings — Open Items

> **Purpose:** central runbook for every real finding surfaced by the
> Session 1115 capability audits. Each entry tells future-you (or anyone
> coming back to fix things) exactly what's wrong, where to look, how to
> verify the finding is still real, what the fix is, and what the
> blast-radius is. **Update this file as findings get closed.**

> Last refreshed: Session 1115 (2026-05-12).

## How to use this file

1. Pick a finding below.
2. Re-run the suggested verifier claim — if it now passes, the finding is
   already closed. Mark `Status: ✅ fixed in Session XXXX`. Otherwise it's
   still open.
3. Read the `Fix` section. Apply.
4. Re-run the verifier claim — it should now pass.
5. Update `Status:` and append a Session note. Don't delete the entry;
   keep the history.

The verifier command form is always:

```bash
python manage.py verify_doc_claims --doc <doc-name> --only-drift
```

Substitute the doc name from each finding's `Verifier doc:` line.

---

## Index

| # | Finding | Severity | Status | Owner |
|---|---|:-:|:-:|---|
| 1 | Phantom `ContentDistributionAgent` in `_NON_SPECIALIST` routing whitelist | low | **✅ fixed Session 1115** | removed from all 4 mirror sets |
| 2 | Orphaned `distribution_agent` handler — unreachable from LLM | low | **✅ fixed Session 1115** | added to `run_agent.agent_name.enum` |
| 3 | 7 broken beat task refs — silent autodiscover misses | medium | **✅ fixed Session 1115** | `on_after_finalize` hook in `core/celery.py` |
| 4 | 5 `AdvisorDomain` enum values with no advisors | low | open | informational |
| 5 | CLAUDE.md said `144` Discord commands; actual is `96` (double-count) | medium | **✅ fixed Session 1115** | — |
| 6 | CLAUDE.md said `32` advisors; actual is `25` (drift on both subtotals) | medium | **✅ fixed Session 1115** | — |
| 7 | Phantom `ContentDistributionAgent` taxonomy miscount (73/9/1 → 74/8/1) | medium | **✅ fixed Session 1115** | — |
| 8 | `BACKEND_INVENTORY.md` says 63 management commands; actual is 164 | medium | open | doc refresh |
| 9 | Learning bridge naming inconsistency (`LearningLoop` × 7 vs `LearningBridge` × 1) | informational | open | cosmetic |
| 10 | `run_market_intelligence_desk` PeriodicTask absent — doc says it should be scheduled daily | medium | open | doc-or-schedule decision |
| 11 | `persona_agent_count` / `total_agent_count_claim` re-pegged from prod-stale `223/306` to seed-baseline `148/231` | medium | **✅ fixed Session 1115** | — |
| 12 | **245 orphan Celery tasks** (67% of 365) — defined but no caller and no beat-schedule entry | medium-high | open | dead-code review |
| 13 | Runtime telemetry framework added (`build_runtime_audit`) — surfaces "declared vs actually executed" once telemetry rows exist | informational | open | run against prod for real findings |
| 14 | **`run_heartbeat` takes 32s** and **`check_celery_health` takes 31s** — long for "every 10 min" infrastructure tasks (3× the interval) | medium | open | perf investigation |
| 15 | **`core_skin_status` + `core_skin_pulses` missing 15 columns from migration 0185's raw CREATE TABLE IF NOT EXISTS** | high | **✅ fixed Session 1115** | migrations 0338 + 0339 |
| 16 | **`muscular` reports "paralyzed"** (no agent execution telemetry) and **`digestive` reports "sluggish"** on fresh DB — body systems express their dependency on real activity | informational | open | known cold-start state |
| 17 | **`ToolCallRecord` only writes from PA entrypoint** — direct `ToolDispatcher.execute_sync()` calls don't log. Telemetry blind spot for non-PA tool invocations. | low-medium | open | observability gap |

---

## 1. Phantom `ContentDistributionAgent` in `_NON_SPECIALIST`

**Status:** ✅ fixed Session 1115 — removed from all 4 mirror sets.

The phantom name lived in four kept-in-sync `_NON_SPECIALIST` literals:

- `core/services/td_handlers_ops.py:3618` (the routing-layer source of truth) — plus its `_REROUTE_REASON` companion entry.
- `core/agent_router.py:916` (the override-check mirror).
- `core/services/platform_inventory.py:80` (the inventory autoblock counting mirror).
- `core/services/doc_claim_verification.py` (two copies: the taxonomy-counting claim + the phantom-detection claim — both kept in sync per their docstring comments).
- `core/management/commands/build_capability_audit.py:46` (the audit-doc generator).

All five were updated in the same PR. Zero behavior change — the
phantom never matched any real routing decision (no `ContentDistributionAgent`
class exists in the codebase). The fix removes the bookkeeping
confusion only.

**Verifier doc:** `core/epa_handlers/td_handlers_ops.py`
**Verifier claim:** `non_specialist_phantom_entries`

```bash
python manage.py verify_doc_claims --doc core/epa_handlers/td_handlers_ops.py
```

**What:** The hardcoded `_NON_SPECIALIST` set in
`core/epa_handlers/td_handlers_ops.py:3618` lists `ContentDistributionAgent`,
but no class with that name exists in the codebase and `AGENT_MAP` does
not reference it.

**Where to look:**
- `core/epa_handlers/td_handlers_ops.py:3618` — primary location (routing
  layer; behaviour-affecting).
- `core/services/platform_inventory.py:84` — counting layer (already
  fixed in Session 1115 by intersecting with AGENT_MAP).
- `core/services/doc_claim_verification.py::_claude_agent_taxonomy` —
  verifier (already fixed in Session 1115).

**Why it's still listed as a finding:** the counting layer is fixed but
the actual routing whitelist still contains the phantom. It's fail-soft
(the router never matches it, no behaviour issue today) so this is a
documented oddity, not a bug. Removing it is the cleanup; it just needs
sign-off because `_NON_SPECIALIST` lives in the routing layer.

**Fix:**

```python
# core/epa_handlers/td_handlers_ops.py:3618
_NON_SPECIALIST = {
    'WorkflowAgent', 'VideoAgent', 'CodeGeneratorAgent', 'DevOpsAgent',
    'FullStackDeveloperAgent', 'CodeReviewAgent',
    # 'ContentDistributionAgent',  # Removed Session XXXX — no class exists
    'COOAgent', 'CTOAgent', 'AudioAgent',
}
```

Same edit needs to land in `core/services/platform_inventory.py` and
`core/services/doc_claim_verification.py` (kept in sync per the
docstring comments in those modules).

**Risk:** zero behaviour change — phantom never matched anything.
Re-run `verify_doc_claims --doc core/epa_handlers/td_handlers_ops.py`
after the edit; expect `low → ok`.

---

## 2. Orphaned `distribution_agent` handler

**Status:** ✅ fixed Session 1115 — added to `run_agent.agent_name.enum`.

The `DistributionAgent` class (the engagement-optimization agent
defined at `core/agents/distribution_agent.py:70` and registered in
`AGENT_MAP`) had a corresponding `self.register("distribution_agent",
self._handle_agent_tool)` entry in `tool_dispatcher.py:332` — but no
PA schema and no membership in `run_agent.agent_name.enum`. The
runtime handler existed but the LLM had no way to invoke it.

Fix: added `"distribution_agent"` to the `agent_name` enum on
`run_agent` in `core/services/pa_tool_schemas.py` (the agent now
appears in the Content Studio group alongside `topic_miner_agent`,
`contrarian_agent`, etc.). The LLM can now route to it via
`run_agent(agent_name="distribution_agent")`.

Verifier `pa_handlers_reachable` now passes (the previously orphaned
handler is reachable through the meta-tool).

**Verifier doc:** `docs/PA_TOOL_AUDIT.md`
**Verifier claim:** `pa_handlers_reachable`

```bash
python manage.py verify_doc_claims --doc docs/PA_TOOL_AUDIT.md
```

**What:** `core/services/tool_dispatcher.py:332` registers a handler for
`distribution_agent`. There's no matching PA schema in
`core/services/pa_tool_schemas.py`, and `distribution_agent` is not
listed in the `run_agent.agent_name.enum` either. The handler runs at
startup but the LLM has no way to invoke it.

**Where to look:**
- `core/services/tool_dispatcher.py:332` — the orphan registration.
- `core/services/pa_tool_schemas.py` — where the matching schema would
  go (search for `run_agent` to find the agent-routing meta-tool).
- `docs/PA_TOOL_AUDIT.md` Findings section — same fact, in narrative.

**Decision:** pick one of:

a. **Remove the registration.** If `DistributionAgent` is dead code,
   delete the `self.register(...)` line. Lightweight, no behaviour
   change (handler currently never runs).

b. **Add it to `run_agent.agent_name.enum`.** If the agent is meant to
   be reachable via Rigby's `run_agent` meta-tool, add `"distribution_agent"`
   to the enum in `pa_tool_schemas.py`. Re-run
   `python manage.py refresh_doc_inventory_blocks` after.

c. **Give it its own schema.** If `DistributionAgent` deserves direct
   LLM access (e.g. Rigby should be able to call it without going
   through `run_agent`), write a schema in `pa_tool_schemas.py` matching
   the patterns of the other agent-tools.

**Risk:** (a) is zero-risk. (b) lets Rigby invoke an agent that's been
quietly dormant — sanity-check the underlying class's behaviour first.
(c) is the same plus a new tool slot in the LLM's function list.

---

## 3. 7 broken beat task references — autodiscover misses

**Status:** ✅ fixed Session 1115 — `on_after_finalize` hook in `core/celery.py`.

**Verifier doc:** `docs/BEAT_AUDIT.md`
**Verifier claim:** `beat_schedule_task_refs_resolve`

```bash
python manage.py verify_doc_claims --doc docs/BEAT_AUDIT.md
```

**What:** 7 entries in `app.conf.beat_schedule` (`core/celery.py`) point
at task paths that don't appear in the runtime Celery task registry. The
underlying `@shared_task` functions all exist — Celery's
`autodiscover_tasks()` simply isn't picking up those modules at worker
startup.

| Beat entry | Task path | Module location |
|---|---|---|
| `clean-stale-data` | `ai_core.tasks.clean_stale_data` | `ai_core/tasks.py:157` |
| `cleanup-old-model-files` | `ml.cleanup_old_model_files` | `ml/tasks.py:143` |
| `cleanup-old-predictions` | `sports.cleanup_old_predictions` | `sports/tasks.py:344` |
| `cleanup-opportunities-daily` | `intelligence.tasks.cleanup_old_opportunities` | `intelligence/tasks.py:1803` |
| `collect-real-opportunities` | `ai_core.tasks.collect_real_opportunities` | `ai_core/tasks.py:18` |
| `scan-spider-opportunities` | `intelligence.tasks.scan_spider_opportunities` | `intelligence/tasks.py:1564` |
| `warm-up-spiders` | `ai_core.tasks.warm_up_spider_network` | `ai_core/tasks.py:193` |

Direct probe (`importlib.import_module`) confirms all 4 task modules
(`ai_core.tasks`, `ml.tasks`, `sports.tasks`, `intelligence.tasks`)
import cleanly. The functions exist. Celery just doesn't know about them.

**Where to fix:** `core/celery.py:317` — extend `app.conf.imports` to
include the missing modules:

```python
app.conf.imports = (
    'core.tasks_agents',
    'ai_core.tasks',         # adds clean_stale_data, collect_real_opportunities, warm_up_spider_network
    'ml.tasks',              # adds cleanup_old_model_files
    'sports.tasks',          # adds cleanup_old_predictions
    'intelligence.tasks',    # adds cleanup_old_opportunities, scan_spider_opportunities
)
```

**Why Chris/Rigby need to green-light:** this re-enables 3 active-work
schedules that have been silently dormant:

- `collect-real-opportunities` runs every **15 minutes** — heavy spider
  burst on first re-enable.
- `scan-spider-opportunities` — daily/periodic, also actual work.
- `warm-up-spiders` — full spider warmup, hits external endpoints.

The 4 cleanup tasks (`clean-stale-data`, `cleanup-old-model-files`,
`cleanup-old-predictions`, `cleanup-opportunities-daily`) are low-risk
DB cleanup work that has been silently building up while not running.

**Suggested rollout:**

1. Add the 4 cleanup imports first (`ai_core`, `ml`, `sports` minus the
   active-work tasks) — but Celery imports a *module*, not a specific
   function. So you'd have to either:
   - Add all 4 modules at once and accept the active-work resumption.
   - Move the cleanup tasks to a separate `_cleanup.py` module that
     can be imported independently of the active-work tasks.
2. Watch logs for the first 24h after the change. The 3 active-work
   schedules will fire; verify they're behaving.
3. Re-run the verifier — `beat_schedule_task_refs_resolve` should drop
   from `medium → ok`.

**Risk:** behaviour-changing. Three active-work schedules resume.
Memory + outbound API risk if they've drifted from when they last ran.

---

**Fix landed (Session 1115):**

Two-part fix in `core/celery.py`:

1. Added `ai_core.tasks`, `ml.tasks`, `sports.tasks`, `intelligence.tasks`
   to `app.conf.imports` (canonical worker-boot mechanism).
2. Added an `@app.on_after_finalize.connect` hook that eagerly imports
   the same four modules. This is necessary because `app.conf.imports`
   only fires at worker boot — verifier / audit code reads `app.tasks`
   at finalize time, before any worker runs. The hook ensures the
   registry is correct at both audit-time and worker-time.

Eager-import-at-module-level was attempted first but failed
(`AppRegistryNotReady` — Django apps not loaded when celery.py runs at
module-load). The `on_after_finalize` signal fires AFTER Django apps
are ready, which is the right hook.

**Verified post-fix:**
- `beat_schedule_task_refs_resolve` → ok (0 broken refs)
- Task registry: 365 → 402 (the 4 modules contribute 37 tasks)
- 27 of those 37 new tasks are orphans → orphan baseline bumped 245 → 272
- All other claims still pass; no regressions introduced

**Behavior change documented in CHANGELOG / handoff:**
The seven previously-silent schedules now actually fire. The 3 active-
work tasks (`collect-real-opportunities`, `scan-spider-opportunities`,
`warm-up-spiders`) will start producing real spider activity once a
worker boots with this version. Watch logs for the first 24h.

---

## 4. 5 `AdvisorDomain` enum values with no registered advisor

**Status:** open · informational (no verifier severity).

**Verifier doc:** `docs/ADVISOR_AUDIT.md` (Findings section)

**What:** `advisors/registry.py:25` declares 26 `AdvisorDomain` enum
values, but `_initialize_advisor_network` only registers advisors in 21
of them. The unused 5:

- `data_strategy`
- `intellectual_property`
- `leadership_development`
- `operations_management`
- `regulatory_compliance`

**Why it might matter:** `find_best_advisor(topic, domain=X)` requires
an existing advisor in that domain — calling it with one of these
returns nothing. Could be a future-state stub (these domains were
planned but never staffed) or an oversight.

**Fix path:**

a. **Add advisors.** Drop 1-5 new entries into `_initialize_advisor_network`
   for the missing domains. Each needs a name, title, expertise level,
   specializations, background, achievements, certifications. See
   `advisors/registry.py:160+` for the pattern.

b. **Remove the enum values.** If these domains were aspirational and
   nothing in the rest of the codebase references them, delete them
   from the `AdvisorDomain` enum.

c. **Leave them.** If they're known future work and other code branches
   on the enum, leave them and document that.

**Risk:** (a) and (c) are zero-risk. (b) only safe if no calling code
mentions them by name — grep first.

---

## 8. `BACKEND_INVENTORY.md` undercounts management commands (63 → 164)

**Status:** open · medium severity · doc refresh.

**Verifier doc:** `docs/BACKEND_INVENTORY.md`
**Verifier claim:** `backend_inventory_mgmt_commands_63`

**What:** `docs/BACKEND_INVENTORY.md` claims 63 Django management commands;
the filesystem has 164 under `core/management/commands/`. Session 1115
added 9 new audit-builder commands which made the drift more visible, but
the underlying doc has been stale for many sessions before.

**Fix:** refresh `docs/BACKEND_INVENTORY.md`'s management-commands line to
say 164 (or whatever the count is at fix time), or — better — regenerate
the doc from runtime as part of a future `build_backend_inventory` audit.
Worth noting the same kind of pattern as the Session 1115 audits: build a
DOC-AUTOGEN command that walks `core/management/commands/`, pulls each
command's `help` and arg signatures, writes a runtime-derived
`docs/MANAGEMENT_COMMAND_AUDIT.md`.

**Risk:** zero — pure doc change.

---

## 9. Learning bridge naming inconsistency

**Status:** open · informational · cosmetic.

**Verifier doc:** `docs/LEARNING_BRIDGE_AUDIT.md` (Findings section)

**What:** Seven of the 9 learning-loop classes under `core/learning_bridges/`
end in the suffix `LearningLoop` (`AgentExecutionLearningLoop`,
`ApplicationOutcomeLearningLoop`, etc.). One ends in `LearningBridge`
(`SportsBettingLearningBridge`). Same concept, two naming conventions.

**Fix:** rename `SportsBettingLearningBridge` → `SportsBettingLearningLoop`
(or rename the rest the other way) in `core/learning_bridges/sports_betting_bridge.py`,
update the corresponding `core/learning_bridges/__init__.py` export, and
grep the codebase for any references.

**Risk:** small — has a public export in `core/learning_bridges/__init__.py`,
so callers that imported the old name would break. `git grep
SportsBettingLearningBridge` before renaming.

---

## 10. `run_market_intelligence_desk` no longer scheduled

**Status:** open · medium severity · doc-or-schedule decision needed.

**Verifier doc:** `docs/topics/agent-system.md`
**Verifier claim:** `intelligence_desks_partial_schedule`

```bash
DATABASE_URL="postgresql://unified_user:secure_password@localhost:5432/ai_unified_platform" \
  python manage.py verify_doc_claims --doc docs/topics/agent-system.md
```

**What:** `docs/topics/agent-system.md` says (per Session 1100): "only
`run_market_intelligence_desk` (stocks) is scheduled daily; 3 of 4 desks
are on-demand only." But:

- `run_market_intelligence_desk` no longer appears in
  `app.conf.beat_schedule` in `core/celery.py`.
- After `python manage.py sync_celery_beat --apply`, no PeriodicTask
  with that task path exists.

So the stocks desk is neither in the static schedule nor in the DB
periodic-task list. Either it was intentionally removed (and the doc is
stale) or it was dropped by accident (and the schedule needs restoring).

**Decision points:**

a. **Doc is stale.** If `run_market_intelligence_desk` is genuinely
   on-demand-only now (like the other 3 desks), update
   `docs/topics/agent-system.md` to say so. Lowest-risk fix.

b. **Schedule should be restored.** If the stocks desk *should* run
   daily, add an entry back to `app.conf.beat_schedule` in
   `core/celery.py` (likely a crontab pattern matching the previous
   schedule before removal). Then re-run `sync_celery_beat --apply`.

**Risk:** (a) is zero-risk. (b) re-enables a scheduled job that runs the
stocks intelligence pipeline daily — make sure the underlying task is
still healthy and budgeted appropriately first.

This finding only became visible after Session 1115's local-Postgres
bootstrap, which let the `db_required=True` claim actually evaluate.

---

## 11. CLAUDE.md persona/total agent counts re-pegged from `223/306` to seed baseline

**Status:** ✅ fixed Session 1115.

The verifier had hardcoded `expected = 223` for persona agents and
`expected = 306` for total agent count, both labelled "refreshed Session
1100 — matches current CLAUDE.md". But:

- Current CLAUDE.md doesn't actually contain `223` or `306` anywhere
  (those values would have been from an earlier doc version).
- `load_all_agents_advisors` is the canonical seed for Agent rows; it
  creates 148 (its docstring claims 149 but the actual loaded count is
  148).
- After running the seed: `AGENT_MAP(83) + Agent rows(148) = 231 total`.

Verifier rewritten to:
- Reference the seed script as the source of truth (the claim's `doc`
  field now points at `core/management/commands/load_all_agents_advisors.py`,
  not `CLAUDE.md`).
- Expected baselines: `persona_agent_count = 148`,
  `total_agent_count_claim = 231`.
- Note tells future-you the seed command + how to bump the baseline if
  the canonical count changes.

Production may have additional Agent rows loaded by other paths (older
sessions referenced `223 persona agents` which suggests a prod-time
snapshot). When the verifier runs against prod, prod-side drift surfaces
as a normal `medium` finding — that's the right behavior.

---

## 12. 245 orphan Celery tasks (67% of registry)

**Status:** open · medium-high severity · dead-code review.

**Verifier doc:** `docs/CELERY_AUDIT.md`
**Verifier claim:** `celery_orphan_count_baseline`

```bash
python manage.py verify_doc_claims --doc docs/CELERY_AUDIT.md
```

**What:** the new Celery audit walked the full task registry (365 tasks
post-autodiscover) and cross-referenced each name against:

- `app.conf.beat_schedule` (cron-scheduled callers)
- A codebase-wide grep for `task.delay(...)` / `task.apply_async(...)` /
  `task.s(...)` / `task.si(...)` (static method-style callers)
- A grep for `send_task('module.path.task')` (dynamic-dispatch callers)

**245 of 365 tasks have NONE of those.** They exist as `@shared_task`
or `@app.task` decorated functions but nothing fires them. The full
list is the "Orphan tasks" section of `docs/CELERY_AUDIT.md`.

**Caveats:**

- Some orphans may be invoked through more exotic paths (`signature()`
  composition, `chord`/`chain` constructors, name-based dispatch via
  `current_app.tasks[name]`). The audit doesn't catch those.
- Some are intentionally kept warm for future use (`debug_task` is one).

**Suggested next step:** the orphan list is too long for a single
sweeping fix. The Celery audit prints orphans in a per-module rollup
under "Tasks by module" — start with the modules where the orphan
rate is highest (most likely candidates: `core/tasks.py` subsections
related to deprecated features). For each:

1. Confirm the task is truly unused (`git grep <task_name>` for unusual
   call patterns).
2. If unused: delete the function, or `git log` it to see when the last
   caller was removed and why.
3. If used via dynamic dispatch: leave it but add an explicit comment
   in the docstring noting the call site so future audits don't flag.

**Risk:** medium-high — these tasks may be loaded into production
workers' memory at boot for no reason. Removing them frees memory and
reduces audit noise. Deleting one that's actually called dynamically
breaks production.

---

## 13. Runtime telemetry audit framework added

**Status:** open (informational) · run against prod for real findings.

**Audit doc:** `docs/RUNTIME_AUDIT.md`
**Command:** `python manage.py build_runtime_audit`

**What:** new audit that cross-references the three telemetry tables
(`AgentExecution`, `CeleryTaskEvent`, `ToolCallRecord`) against the
three primary registries (`AGENT_MAP` + DB Agent rows, `app.tasks`,
`PA_TOOL_SCHEMAS`). For each registry it reports:

- Total registered
- Total with ≥1 execution in last 30 days (window configurable)
- Total executed ever
- **Never executed** — the headline finding

**Why it's informational, not a drift finding yet:** the local DB used
for Session 1115 has 0 telemetry rows (fresh seed). On a
production-mirror DB the audit will surface "agents declared but never
invoked," "tools declared but never called," etc. — combined with the
Celery audit's static orphan list, this gives you two angles on
"declared but not connected."

**Suggested next step:** run against production (or a recent prod-dump
in a sandbox) and treat the never-executed sets as evidence-based dead
code candidates. The intersection of Celery orphans (static) +
never-executed Celery tasks (runtime) is the highest-confidence dead
code; same applies for agents and tools.

---

## 14. `run_heartbeat` and `check_celery_health` take >30 seconds each

**Status:** open · medium severity · perf investigation.

**Verifier doc:** `docs/RUNTIME_AUDIT.md` (telemetry-driven)

**What:** During the Session 1115 local full-stack run (12 min of
Celery worker + beat), 19 `CeleryTaskEvent` rows were captured. Two
infrastructure tasks stood out:

- `core.tasks.run_heartbeat`: 32.36s (scheduled every 10 min)
- `core.tasks.check_celery_health`: 31.58s (scheduled every 10 min)

Every other task in the sample ran in 0.02–0.50s. A 32-second
heartbeat that fires every 10 minutes is 5% of wall-clock spent on
the heartbeat alone. Both tasks may be sequentially polling all
body-system services + each Celery worker for vitals — the slow
path is probably the introspection.

**Fix path:**

1. Profile `run_heartbeat` and `check_celery_health` to find the slow
   step. Likely candidate: synchronous calls to each `*Service.get_vitals()`
   over network sockets (Redis / DB connection pool).
2. Add an `inspect.ping` timeout cap, or parallelize the vital fetches.
3. Consider degrading to a 5-minute interval if the heartbeat is meant to
   be quick.

**Risk:** medium — the heartbeat tasks themselves are infrastructure
and may have established SLO expectations elsewhere. Don't change
intervals without checking what reads from `HeartBeat` model.

---

## 15. `core_skin_status` + `core_skin_pulses` schema drift — ✅ fixed Session 1115

**Status:** ✅ fixed Session 1115 (migrations 0338 + 0339).

**Root cause:** migration `0185_fix_body_system_tables.py:141` used raw
`CREATE TABLE IF NOT EXISTS` with an inline column list that predated
several model additions. On long-lived DBs the prior CREATE+ALTER
history had already added those columns, so `IF NOT EXISTS` was a no-op
and they survived. On freshly-bootstrapped DBs (like this session's
local Postgres) the table got re-created without them, and any read
that selects those columns fails with
`ProgrammingError: column ... does not exist`.

**Diff revealed 15 missing columns** when a comprehensive model-vs-DB
comparison was run during the fix:

`core_skin_status` (6 missing — added in 0338 + 0339):
- `total_files_tracked` (IntegerField default=0) — first to fail
- `total_operations_all_time` (IntegerField default=0)
- `avg_operation_time_ms` (FloatField default=0)
- `error_rate_24h` (FloatField default=0)
- `last_error_at` (DateTimeField null=True)
- `last_successful_operation_at` (DateTimeField null=True)
- `operations_per_hour` (FloatField default=0)
- `pending_reviews` (IntegerField default=0)

`core_skin_pulses` (9 missing — added in 0339):
- `agent_operation_counts` (JSONField default=`{}`)
- `avg_operation_time_ms` (FloatField default=0)
- `commands_executed_24h` (IntegerField default=0)
- `git_operations_24h` (IntegerField default=0)
- `lines_changed_24h` (IntegerField default=0)
- `most_active_agent` (CharField max_length=100, default=`''`)
- `pending_reviews` (IntegerField default=0)
- `permission_denials` (IntegerField default=0)
- `rollbacks_performed_24h` (IntegerField default=0)

**Fix landed:**

- `core/migrations/0338_skin_status_missing_columns.py` — addresses the
  two initially-failing columns.
- `core/migrations/0339_skin_body_columns_comprehensive.py` — addresses
  the remaining 13.

Both use `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` so they're
idempotent — safe on any prior DB state (no-op on DBs where the
columns already exist).

**Verified post-fix:** `get_skin_service().get_vitals()` returns
`status=healthy, score=100.0` on fresh local DB. All 9 body systems
respond cleanly.

**Forward guard:** the audit's body-system schema drift catcher (the
script that lives at `/tmp/check_body_columns3.py` during the session)
should be promoted to a recurring verifier claim — `body_system_schema_drift`
that walks every body-system model and compares its `_meta.get_fields()`
column set against `information_schema.columns`. **TODO Session 1116.**

---

## 16. Body systems express cold-start state

**Status:** open · informational · known cold-start state.

**What:** On the freshly-seeded Session 1115 local DB:

- `muscular` reports `overall_status: paralyzed` (no agent execution rows)
- `digestive` reports `overall_status: sluggish` (low ingestion activity)

These aren't bugs — the body systems are correctly reflecting that the
platform hasn't been doing work. But it does mean:

1. A fresh prod-mirror bootstrap will show the same "paralyzed/sluggish"
   states until traffic flows.
2. Any health-check alert that bins these as "unhealthy" will fire on
   sandbox/test instances.

**Suggested action:** none required. Just worth documenting that these
specific states are expected on cold-start.

---

## 17. `ToolCallRecord` blind spot for non-PA dispatch

**Status:** open · low-medium severity · observability gap.

**What:** `ToolCallRecord` rows are only written by
`core/services/unified_pa_entrypoint.py:1849`. When `ToolDispatcher`
gets invoked by any other path (direct `execute_sync()` calls,
agent-to-tool delegation, internal tool composition), nothing logs
the call.

This was surfaced when Session 1115's local test invoked 20 PA tools
via `td.execute_sync(...)` and `ToolCallRecord.count() == 0` afterward.

**Implication:** the runtime audit's `tools never executed` set is an
under-count of "tools that fired"; specifically, any tool fired
outside a PA chat conversation is invisible to the audit.

**Fix path:** add the same `ToolCallRecord.objects.create(...)` block
inside `ToolDispatcher.execute()` so EVERY dispatch logs telemetry,
regardless of caller. PA entrypoint would either keep its own log or
defer to the dispatcher's.

**Risk:** small — adds 1 DB write per tool call. Match the existing
column schema; the PA path already does this.

---

## 5–7. Closed in Session 1115

### 5. Discord command double-count (`144 → 96`)

**Status:** ✅ fixed Session 1115.

The `discord_total_commands` claim used to count
`@\w+\.command(...)` and `@app_commands\.command(...)` regex matches
separately and add them — but `@\w+\.command` already matches
`@app_commands.command`, so the 48 slash commands got counted twice.
Verifier rewritten to AST-parse in Session 1115. CLAUDE.md and the
DISCORD_AUDIT.md headline both reflect `96` (48 slash + 48 prefix).

### 6. Advisor count drift (`32 → 25`)

**Status:** ✅ fixed Session 1115.

CLAUDE.md claimed `32 advisors (10 named + 22 specialists)` for a long
time. Registry materializes `25 (14 named + 11 specialists)`. The
narrative drifted in opposite directions — over-counted specialists by
11, under-counted named figures by 4. The 4 missing named figures
(Dr. Peter Attia, Grant Cardone, Kevin Mitnick, Sal Khan) now appear in
the CLAUDE.md row. Verifier guard `advisor_count_matches_doc` catches
future drift.

### 7. Agent taxonomy phantom (`73/9/1 → 74/8/1`)

**Status:** ✅ fixed Session 1115.

`platform_inventory.py` and `doc_claim_verification.py` both counted
`ContentDistributionAgent` as "rerouted" even though it isn't in
AGENT_MAP. Counting layer now intersects `_NON_SPECIALIST` with
AGENT_MAP keys, taxonomy reads `74/8/1` and the math actually adds up.
CLAUDE.md + autoblock fixed. The phantom still exists in the routing
layer (`td_handlers_ops.py:3618`) and is tracked as finding #1.

---

## When you close a finding

1. Set `Status: ✅ fixed Session XXXX`.
2. Move the entry to the bottom under "Closed in Session XXXX".
3. Update the Index table.
4. Re-run `python manage.py verify_doc_claims --only-drift` and paste
   the new totals into the relevant session handoff.

## When the audits surface a new finding

1. Run the relevant `build_*_audit` command — its findings section is
   the canonical first capture.
2. Add an entry here under a fresh number.
3. Register a verifier claim if there isn't one already.
4. Cross-link from the handoff that surfaced it.
