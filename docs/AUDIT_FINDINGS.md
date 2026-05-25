<!-- DOC-POINTER-V1 (Session 1146) -->
> **Living runbook — refresh-in-place; do not move.**
> This file is the central runbook for findings surfaced by the capability audits. Entries are updated as findings close; do not delete closed entries (the history is the point — see "How to use this file" below).
> **Last reviewed for drift labeling:** Session 1146 (2026-05-25)
> **Note:** the original "Last refreshed: Session 1115" line below reflects the last full sweep; individual entries may have been updated since. Many entries already show `✅ fixed Session 1115` status. If a finding looks open but was closed in a later session, re-verify per the entry's `Verifier doc:` line before re-opening.
> **Related canon:** [`docs/canon/INDEX.md`](canon/INDEX.md) (canon registry) + [`docs/PLATFORM_INVENTORY.md`](PLATFORM_INVENTORY.md) (sole counts source per `DOC_LIFECYCLE.md` §2c) + the 8 DOC-AUTOGEN audit files in `docs/*_AUDIT.md` (per-subsystem runtime evidence).

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
| 4 | 5 `AdvisorDomain` enum values with no advisors — routing intent + spider tagging both expected them | low → high (reframed) | **✅ fixed Session 1115** | 5 new advisors added; routing now resolves end-to-end |
| 5 | CLAUDE.md said `144` Discord commands; actual is `96` (double-count) | medium | **✅ fixed Session 1115** | — |
| 6 | CLAUDE.md said `32` advisors; actual is `25` (drift on both subtotals) | medium | **✅ fixed Session 1115** | — |
| 7 | Phantom `ContentDistributionAgent` taxonomy miscount (73/9/1 → 74/8/1) | medium | **✅ fixed Session 1115** | — |
| 8 | `BACKEND_INVENTORY.md` says 63 management commands; actual is 167 | medium | **✅ fixed Session 1115** | new `build_management_command_audit` + inline refresh |
| 9 | Learning bridge naming inconsistency — symptom of an **unused ABC** (`LearningBridge`) that nobody inherits from | informational → low (reframed) | **✅ fixed Session 1115 batch-13** — all 9 bridges migrated; guard severity bumped low → medium | — |
| 10 | `run_market_intelligence_desk` PeriodicTask absent — doc said it should be scheduled daily | medium | **✅ fixed Session 1115** | doc-stale; updated topic doc to "all 4 desks on-demand only" |
| 11 | `persona_agent_count` / `total_agent_count_claim` re-pegged from prod-stale `223/306` to seed-baseline `148/231` | medium | **✅ fixed Session 1115** | — |
| 12 | **272 → 10 orphan Celery tasks** — batches 1-8: 4x detector upgrades, 32 tasks wired, dead stubs un-tasked, 3 signal/mgmt-cmd wirings, `propagate_new_policies` deleted | medium-high | partial · 96.3% reduction; remaining 10 are all constraint-deferred (LLM-cost, agent-dispatch, Session 1031, intentional) | none — wait for credits or green-light |
| 13 | Runtime telemetry framework added (`build_runtime_audit`) — surfaces "declared vs actually executed" once telemetry rows exist | informational | open | run against prod for real findings |
| 14 | **`run_heartbeat` 32s** + **`check_celery_health` 31s** — long for "every 10 min" infra tasks | medium | **✅ fixed Session 1115** | timeout cap + no-worker short-circuit (34s→1.5s, 31s→0.04s) |
| 15 | **`core_skin_status` + `core_skin_pulses` missing 15 columns from migration 0185's raw CREATE TABLE IF NOT EXISTS** | high | **✅ fixed Session 1115** | migrations 0338 + 0339 |
| 16 | **`muscular` reports "paralyzed"** (no agent execution telemetry) and **`digestive` reports "sluggish"** on fresh DB — body systems express their dependency on real activity | informational | open | known cold-start state |
| 17 | **`ToolCallRecord` only writes from PA entrypoint** — direct `ToolDispatcher.execute_sync()` calls don't log. Telemetry blind spot for non-PA tool invocations. | low-medium | **✅ fixed Session 1115** | dispatcher writes on all return paths |

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

## 4. 5 `AdvisorDomain` enum values with no advisors — **fixed**

**Status:** ✅ fixed Session 1115. Reframed from "informational" to "real
finding" after investigation showed routing intent + spider tagging
were both wired to these domains; only the advisor registrations were
missing.

**What investigation revealed:**

The 5 "unused" domains aren't dead — they're **referenced as routing
destinations** in `core/services/advisor_context_builder.py`'s
`TASK_TO_DOMAINS` map:

| Domain | Used in routing for | Side evidence |
|---|---|---|
| `operations_management` | `coo` tasks → fell back to David Kim | — |
| `data_strategy` | `research`, `trend_analysis` → fell back to Sam Altman | — |
| `intellectual_property` | `legal` tasks → fell back to legal_counsel only | Tagged by findlaw, courtlistener, justia spiders — data was flowing in for nobody |
| `leadership_development` | `career`, `personal` → fell back to career_coaching | Already declared as a specialization on Dr. Maria Gonzalez |
| `regulatory_compliance` | `legal` → fell back to legal_counsel only | — |

So the system was silently degrading across 5 capability domains — not
broken, just operating below its declared intent.

**Fix landed (Option A from the runbook):** added 5 new advisors,
filling every previously-orphan domain.

| Domain | Advisor added | Type |
|---|---|---|
| `operations_management` | **Tim Cook (AI Model)** | named figure |
| `data_strategy` | **Andrew Ng (AI Model)** | named figure |
| `intellectual_property` | Priya Raman, Senior IP Counsel | domain specialist |
| `leadership_development` | Marcus Whitfield, Executive Leadership Coach | domain specialist |
| `regulatory_compliance` | Eleanor Park, Regulatory & Compliance Strategist | domain specialist |

**Forward guard:** new verifier claim `task_domain_routing_resolves` —
checks that every `TASK_TO_DOMAINS` key has at least one matching
advisor in the registry. Currently passes for all task kinds. Future
"declared but not filled" drift surfaces here automatically.

**Headcount drift:**

| Doc | Before | After |
|---|---:|---:|
| Total advisors | 25 | 30 |
| Named figures | 14 | 16 (added Tim Cook + Andrew Ng) |
| Domain specialists | 11 | 14 (added Priya Raman, Marcus Whitfield, Eleanor Park) |
| Domains covered | 21 / 26 | 26 / 26 |

CLAUDE.md Advisor row + ADVISOR_AUDIT.md regenerated to reflect.

---

## 8. `BACKEND_INVENTORY.md` undercounts management commands

**Status:** ✅ fixed Session 1115 — new audit doc + inline refresh.

**Verifier claim:** `backend_inventory_mgmt_cmds_count`

**What:** `docs/BACKEND_INVENTORY.md` had claimed 63 / 153 (across three
inconsistent inline places) while the filesystem had 167. The
Session-1115 audit-doc additions made the drift more visible but the
underlying doc had been stale for many sessions before.

**Fix landed (sustainable):**

1. **New audit doc** at `docs/MANAGEMENT_COMMAND_AUDIT.md` — auto-regenerates
   from the filesystem via `python manage.py build_management_command_audit`.
   Pulls each Command class's `help=` text, AST-parses `add_arguments`,
   buckets by heuristic category. Same DOC-AUTOGEN pattern as the 11
   other audits.
2. **`BACKEND_INVENTORY.md` inline numbers** updated (three places) and
   pointed at the new audit doc as the runtime-derived source.
3. **Verifier claim** renamed from `backend_inventory_mgmt_cmds_63` to
   `backend_inventory_mgmt_cmds_count`, expected baseline bumped from
   153 → 167, drift bands tightened. Future filesystem additions /
   removals surface here as `low` (≤30 drift) or `medium` (>30).
4. **`scripts/verify_repo_guardrails.py`** protected-file list extended
   so hand-edits to the new audit doc fail strict mode.

**Risk:** zero — pure doc-and-tooling change.

---

## 9. Unused `LearningBridge` ABC — naming inconsistency is the symptom

**Status:** ✅ fixed Session 1115 batch-13 — all 9 concrete bridges
now inherit from the `LearningBridge` ABC. Verifier baseline dropped
9 → 0; severity bumped from `low` to `medium` so the forward-drift
guard is teeth-on (any new bridge that doesn't inherit fails the
check). Migration spanned five PRs:

- batch-9 PR #2086 — `RevenueAttributionLearningLoop`
- batch-10 PR #2087 — `Collaboration` + `AgentExecution`
- batch-11 PR #2088 — `ApplicationOutcome` + `SpiderData`
- batch-12 PR #2089 — `AdvisorFeedback` + `AutoConsultation`
- batch-13 — `PersonalizationFeedback` + `SportsBetting`

Migration pattern (documented in batch-9 commit, reused in batches
10-13):
1. Subclass `LearningBridge` with `bridge_name='...'`
2. Implement 4 abstract methods (`process_event`, `_extract_patterns`,
   `_update_learning`, `_generate_insights`)
3. Thread the ORM/event instance through `patterns['_X']` so the
   1-argument `_update_learning(patterns)` contract works
4. Keep original entry methods as back-compat shims
5. Get observability helpers (`log_event`, `log_success`, `log_error`,
   `event_count`, `success_count`, `get_statistics`) for free

Two bridges needed slight pattern adaptations:
- `PersonalizationFeedbackLoop` handles TWO event types; `process_event`
  dispatches by `hasattr(event_data, 'message')` vs
  `hasattr(event_data, 'interaction_type')`.
- `SportsBettingLearningBridge` is invocation-driven (sync utility),
  not signal-driven; `process_event(user)` triggers a full sync.

**Verifier doc:** `docs/LEARNING_BRIDGE_AUDIT.md`
**Verifier claim:** `learning_bridges_inherit_base` (added Session 1115).

**Reframed finding** (after closer investigation):

The visible symptom is naming: 7 classes use `*LearningLoop` suffix,
1 uses `*LearningBridge`. But the deeper issue is that **nobody
inherits from the abstract base class `LearningBridge`** at
`core/learning_bridges/base.py:13`.

The original design intent was clear:

- Directory name: `core/learning_bridges/`
- AppConfig class: `LearningBridgesConfig`
- Abstract base: `LearningBridge(ABC)` — declares 4 abstract methods
  (`process_event`, `_extract_patterns`, `_update_learning`,
  `_generate_insights`) and provides observability helpers
  (`event_count`, `success_count`, `log_event`, `log_success`,
  `log_error`, `get_statistics`).

What actually happened: **every concrete bridge reinvents its own
structure independently.** None inherit from the ABC. None get the
unified observability for free. Two naming conventions emerged
because there was no contract to anchor on.

| Class | Suffix | Inherits `LearningBridge`? |
|---|---|---|
| `AgentExecutionLearningLoop` | LearningLoop | ✗ |
| `AdvisorFeedbackLearningLoop` | LearningLoop | ✗ |
| `AutoConsultationLearningLoop` | LearningLoop | ✗ |
| `ApplicationOutcomeLearningLoop` | LearningLoop | ✗ |
| `CollaborationLearningLoop` | LearningLoop | ✗ |
| `PersonalizationFeedbackLoop` | FeedbackLoop | ✗ |
| `RevenueAttributionLearningLoop` | LearningLoop | ✗ |
| `SpiderDataLearningLoop` | LearningLoop | ✗ |
| `SportsBettingLearningBridge` | LearningBridge | ✗ |

Renaming `SportsBettingLearningBridge` → `*LearningLoop` would lock
in the *deviation* from intent rather than fix it. The real fix is a
multi-PR refactor to make all 9 inherit from the ABC and unify the
process-event shape.

**Session 1115 partial fix (low-risk):**

1. Added verifier claim `learning_bridges_inherit_base` that walks
   every learning-loop class under `core/learning_bridges/` and flags
   any that don't inherit from `LearningBridge`. Currently surfaces
   all 9 as drift — but at `low` severity, since none have inherited
   historically (zero regression). The claim is the watchpoint: any
   NEW bridge added without inheriting now fails the check.
2. Updated `docs/LEARNING_BRIDGE_AUDIT.md` Findings section to
   highlight the ABC-orphan-pattern.

**Deferred to follow-up session:**

- Multi-PR refactor: make each of the 9 concrete classes inherit
  from `LearningBridge`, implement the 4 abstract methods, drop
  any private re-implementations of the observability helpers
  (`event_count` / `success_count` / `log_*`).
- Once all 9 inherit, bump the verifier severity from `low` to
  `medium` so the guard is teeth-on.

**Risk of the deferred refactor:** medium. Each bridge has slightly
different `process_event` signatures and pattern-extraction shapes.
The refactor is mechanical-ish but needs care to preserve existing
signal-emission behavior. Best done one bridge at a time with the
verifier confirming each step.

---

## 10. `run_market_intelligence_desk` no longer scheduled

**Status:** ✅ fixed Session 1115 — doc-stale, updated to reflect reality.

**Verifier claim:** `intelligence_desks_on_demand_only` (was
`intelligence_desks_partial_schedule`).

**What:** `docs/topics/agent-system.md` said "only stocks is currently
scheduled" but the verifier found no PeriodicTask matching
`run_market_intelligence_desk` after the local DB was bootstrapped.

**Investigation:** `git log -S "run_market_intelligence_desk"` showed
the schedule was deliberately removed in commit `a88fb8e7` ("minimal
beat schedule" cleanup), but the topic doc was never updated to match.
A Session 1100 "doc-drift purge" updated the doc, but the schedule was
already gone — so the Session 1100 update was incorrect too.

**Decision: doc is stale, schedule was intentionally removed.** All 4
intelligence desks (stocks, sports, blockchain, narrative) are now
on-demand only via `POST /api/home/trigger-desks/`. The underlying
task function `run_market_intelligence_desk` still exists at
`core/tasks.py:4356` and can be re-scheduled later if needed.

**Fix landed:**

1. `docs/topics/agent-system.md` updated — header narrative, schedule
   table, and inline note all say "on-demand only" with reference to
   commit `a88fb8e7`.
2. Verifier claim rewritten as `intelligence_desks_on_demand_only`
   that confirms no desk task has an enabled PeriodicTask.

**Risk:** zero — doc-only change reflecting existing system state.

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

## 12. 272 → 10 orphan Celery tasks — batches 1-8 closed

### Batch 8 outcome (Session 1115) — deprecated stub deletion

Deleted `propagate_new_policies` (Session 363, deprecated Session 659).
The task referenced a non-existent `propagated_at` field and returned a
deprecation notice immediately — `PolicyContextService` has handled
canonical policy injection at runtime since Session 659. Zero callers
anywhere in the codebase. Cleaned removal with a comment block in
`core/tasks.py` documenting the supersession path for future readers.

Registry shrank 398 → 397. Orphan count 11 → **10**.
Cumulative across batches 1-8: **272 → 10 (96.3% reduction).**

### Batch 7 outcome (Session 1115) — signal/CLI wire-ups for the last 3

Closed all three remaining "truly forgotten" tasks by wiring them to
their real triggers:

**1) `process_document_async`** → wired to `Document.post_save` signal.
New handler in `core/signals/document_processing_signals.py`. Fires
when `created=True` AND `file_path` is set AND `status in (pending, '')`.
Uses `transaction.on_commit` so dispatch waits for the row to commit
(mirrors existing trigger_signals pattern).

**2) `trigger_content_from_shift`** → wired to `NarrativeShift.post_save`
signal. The task's registered name is `narrative_drift.trigger_content_from_shift`
but the Python function is `trigger_content_from_narrative_shift` —
a function-name-vs-task-name mismatch. The signal dispatches via
`current_app.send_task('narrative_drift.trigger_content_from_shift', ...)`
which:
- Uses the canonical task name (won't break if function gets renamed)
- Gets picked up by the audit's `send_task('...')` string-literal scan
- Avoids the import-cycle risk of `from core.tasks import ...` in a signal

The NarrativeShift model lives in `core/models_narrative_drift.py` which
isn't auto-imported during Django startup (the `core/models/` package
directory shadows `core/models.py`'s catch-all `from .models_narrative_drift import *`).
Solution: explicit class import in `connect_document_processing_signals()`
+ `post_save.connect()` with the imported class as sender, instead of
the `@receiver(sender='core.NarrativeShift')` lazy-string form.

**3) `start_resolve_render`** → wrapped in same-name management command
`core/management/commands/start_resolve_render.py`. Operators can now
dispatch a Resolve render via:

    python manage.py start_resolve_render --job-id <uuid> --video-ids id1,id2 \
        --template default --color-grade neutral

The same-name CLI detector picks this up as a real caller automatically.

**Orphan count drop in batch 7:** 14 → **11** (3 wirings).
Cumulative across batches 1-7: **272 → 11 (96% reduction).**
No "forgotten" wirings remain.

### Remaining 11 — all constraint-deferred or intentional

| Category | Count | Examples |
|---|---:|---|
| **LLM-cost scheduled** (deferred until OpenAI credits) | 5 | `rag_retrieval_canary` (embeddings), `send_weekly_kpi_summary` (Discord), `run_ops_autopilot` (takes actions), `post_ops_digest`, `maintain_knowledge_freshness` |
| **Agent-dispatch chain** (deferred for green-light) | 2 | `check_blocked_research_for_unblock` (→ retry_blocked_research), `process_pending_action_plans` (→ execute_action_plan) |
| **Session 1031 hard-blocked** (return immediately) | 3 | `discover_and_import_audits`, `assign_open_findings_to_agents`, + 1 |
| **Deprecated** | 1 | `propagate_new_policies` — Session 659 |
| **Intentionally orphan** | 1 | `debug_task` |

Verifier baseline locked at **11**. Future regressions surface immediately.

### Batch 6 outcome (Session 1115) — dead stubs + 1 wiring

Two targeted cleanups:

**Removed `@shared_task`** from 4 intelligence-engine stubs that had
**zero callers** anywhere in the codebase:

- `start_intelligence_engine` — uses `asyncio.run` to drive
  `intelligence_engine.start_intelligence_stream()`. Now plain function;
  invoke from a management command if needed.
- `get_live_opportunities` — 1-liner pass-through to
  `intelligence_engine.get_current_opportunities()`. URL handler
  `core/views_ecosystem_activation.py:95` is the real `get_live_opportunities`.
- `get_live_predictions` — same pattern.
- `trigger_market_scan` — returns a hardcoded dict.

The functions are kept (still importable) but removed from the Celery
task registry. Registry shrank 402 → 398.

**Scheduled `scan_income_spider_orchestrator`** hourly. Its docstring
already said *"Should run every hour to gather opportunities from
multiple sources."* No LLM cost (uses spiders + income_spider_orchestrator).

**Orphan count drop in batch 6:** 19 → **14** (4 dead-stub removals
+ 1 wiring). Cumulative across batches 1-6: **272 → 14 (95% reduction).**

### Remaining 14 — final final triage

| Category | Count | Examples |
|---|---:|---|
| **LLM-cost scheduled** (deferred until credits) | 5 | `rag_retrieval_canary` (embeddings), `send_weekly_kpi_summary` (Discord), `run_ops_autopilot` (takes actions), `post_ops_digest`, `maintain_knowledge_freshness` |
| **Agent-dispatch chain** (deferred for green-light) | 2 | `check_blocked_research_for_unblock` (→ retry_blocked_research), `process_pending_action_plans` (→ execute_action_plan) |
| **Session 1031 hard-blocked** | 3 | `discover_and_import_audits`, `assign_open_findings_to_agents`, + 1 — all `return {'blocked': True}` immediately |
| **Needs signal/webhook wire-up** | 3 | `process_document_async` (Document post_save signal), `trigger_content_from_shift` (SignalCluster post_save signal), `start_resolve_render` (video-render webhook or mgmt command) |
| **Deprecated** | 1 | `propagate_new_policies` — Session 659 supersession |
| **Intentionally orphan** | 1 | `debug_task` |

Verifier baseline locked at **14**.

### Batch 5 outcome (Session 1115) — intra-file dispatch bug

Found a long-standing detector bug in `_inspect()`: the audit's caller
cross-reference excluded **all** callers in the task's own definition
file, not just the definition line. The intent was to filter out the
`@shared_task` decorator line itself (which can look like a self-match),
but the effect was to drop legitimate intra-file parent→child task chains.

Example: `intelligence/tasks.py:1192` has `submit_proposal_automatically.delay(...)`
chaining into the task defined at `intelligence/tasks.py:1209`. Both lines
live in the same file but the dispatch is real — `process_pending_action_plans`
(line 67) chains to `execute_action_plan` chains to `submit_proposal_automatically`
chains to `check_proposal_responses` chains to `handle_client_response`
chains to `submit_follow_up` and `update_ml_model_with_feedback`. This
proposal/response workflow lives entirely inside `intelligence/tasks.py`.

Fix: filter only the exact `file_path:line_no` of the task's definition
instead of the whole file. **5 fewer false orphans** —
`submit_proposal_automatically`, `submit_follow_up`, `handle_client_response`,
`check_proposal_responses`, `update_ml_model_with_feedback` now correctly
attributed to their intra-file chains.

The verifier's `celery_orphan_count_baseline` was always using simple
set-membership without the own-file filter, so its logic was correct —
the baseline of 24 just tracked the audit's miscount. Updated to 19.

**Orphan count drop in batch 5:** 24 → **19** (detector fix, no new
wiring). Cumulative across batches 1-5: **272 → 19 (93% reduction).**

### Remaining 19 — final triage

| Category | Count | Examples |
|---|---:|---|
| **LLM-cost scheduled** (deferred until credits) | ~5 | `rag_retrieval_canary` (embeddings), `send_weekly_kpi_summary` (Discord), `run_ops_autopilot` (takes actions), `post_ops_digest`, `maintain_knowledge_freshness` |
| **Agent-dispatch chain** (deferred for green-light) | ~2 | `check_blocked_research_for_unblock` (→ retry_blocked_research), `process_pending_action_plans` (→ execute_action_plan) |
| **Session 1031 hard-blocked** | ~3 | `discover_and_import_audits`, `assign_open_findings_to_agents`, execute_remediation_tasks — all `return {'blocked': True}` immediately |
| **Truly forgotten — needs wire-up decision** | ~7 | `start_resolve_render` (video render trigger), `scan_income_spider_orchestrator`, `start_intelligence_engine`, `trigger_market_scan`, `trigger_content_from_shift` (signal wiring needed), `process_document_async` (Document save signal needed), `get_live_opportunities`, `get_live_predictions` (API-only — could remove `@shared_task` decorator) |
| **Deprecated** | 1 | `propagate_new_policies` — Session 659; PolicyContextService handles injection automatically |
| **Intentionally orphan** | 1 | `debug_task` |

The "truly forgotten" 7 are the most interesting set. Most likely fixes:

- `trigger_content_from_shift` — wire to a Django signal on
  `SignalCluster` save when `pattern_type='narrative_shift'`
- `process_document_async` — wire to a `post_save` signal on `Document`
  when `status='pending'` and a file_path exists
- `get_live_opportunities`, `get_live_predictions` — these are simple
  read functions that don't need to be Celery tasks; remove the
  `@shared_task` decorator (they're already called by URL handlers
  in `core/urls.py`)
- `start_resolve_render`, `scan_income_spider_orchestrator`,
  `start_intelligence_engine`, `trigger_market_scan` — manual-trigger
  tasks that should be wrapped in management commands

Verifier baseline locked at **19**.

### Batch 4 outcome (Session 1115)

Wired 17 more **behavior-changing DB-only** tasks into `app.conf.beat_schedule`.
Each was verified by inspection to make no LLM calls, dispatch no agents, and
perform only DB queryset updates / file reads / in-app state changes.
These are "behavior-changing" only in that they update DB state (auto-approve,
auto-promote, archive, etc.) — same lens as Chris's "should this do something
and got forgotten about" reframe.

| Task | Cadence | What it does |
|---|---|---|
| `auto_approve_boardroom_items` | every 30 min | DB-only HumanAttentionItem aging-based auto-approve |
| `auto_promote_low_risk_decisions` | every 2 hours | Tier-1 AgentDecisionSummary aging promotion (governance-respecting) |
| `verify_completed_fixes` | every 6 hours | AuditFinding verification (file reads + regex, no subprocess) |
| `promote_to_shared_knowledge` | Mon 04:00 | High-confidence AgentKnowledgeSource → SharedKnowledge |
| `update_distribution_analytics` | daily 04:00 | ContentDistribution daily aggregation |
| `monitor_isolation_progress` | daily 04:30 | Document namespace tagging snapshot |
| `update_mythology_pattern_statistics` | daily 04:00 | MythPattern frequency rollup |
| `sync_pipeline_insights_to_collective` | every 6 hours | Style/voice insights → collective intelligence |
| `process_hitl_escalations` | every 15 min | HITL priority bumps + deadline extensions (no LLM) |
| `scan_concerns_for_human_action` | hourly :30 | TrackedConcern → ProactiveNotification |
| `maintain_dream_backlog` | daily 04:30 | Archive low-score AgentDreams (composite_score-based) |
| `report_pending_review_metrics` | daily 09:00 | Pending-review metrics log (read-only) |
| `process_human_attention_lifecycle` | every 10 min | DB lifecycle state machine — expire/dismiss/escalate/approve |
| `poll_pending_3d_models` | every 5 min | Replicate poll (no-op when no pending) |
| `detect_duplicate_initiatives` | daily 04:15 | Similarity-based dedup (no LLM) |
| `check_operating_rhythm_status` | daily 09:15 | Operating rhythm health (read-only) |
| `rescan_active_workspaces` | every 4 hours | WorkspaceContext refresh (no LLM) |

**Orphan count drop in batch 4:** 41 → **24** (17 tasks wired).
Cumulative across batches 1-4: **272 → 24 (91% reduction).**

### Remaining 24 — final triage

| Category | Count | Action |
|---|---:|---|
| **LLM-cost scheduled** (deferred until credits) | ~5 | `rag_retrieval_canary`, `send_weekly_kpi_summary` (Discord), `run_ops_autopilot` (takes actions), `post_ops_digest`, `maintain_knowledge_freshness` |
| **Agent-dispatch chains** (deferred) | ~4 | `check_blocked_research_for_unblock` (→ retry_blocked_research), `process_pending_action_plans` (→ execute_action_plan), `trigger_market_scan`, `update_ml_model_with_feedback` |
| **Session 1031 hard-blocked** | ~3 | `discover_and_import_audits`, `assign_open_findings_to_agents`, `execute_remediation_tasks` — all `return {'blocked': True}` immediately |
| **Event-triggered** (no action needed) | ~10 | `start_intelligence_engine`, `start_resolve_render`, `submit_proposal_automatically`, `submit_follow_up`, `handle_client_response`, `check_proposal_responses`, `trigger_content_from_shift`, `get_live_opportunities`, `get_live_predictions`, `process_document_async` |
| **Deprecated** | 1 | `propagate_new_policies` — Session 659 deprecation; PolicyContextService handles injection automatically |
| **Intentionally orphan** | 1 | `debug_task` |

Verifier baseline locked at **24**.

### Batch 3 outcome (Session 1115)

Two parallel improvements:

**1) Detector now catches importlib-style `'module.path:func'` dispatch.**
The `scheduled_diagnostic_runner` and similar dispatchers resolve target
tasks at runtime from a path string like `'core.tasks:post_cto_daily_diagnostic'`.
The batch-2 quoted-token scan used `[[:alnum:]_.]+` for the token character
class which excludes `:`, so these paths weren't matched. Added a second
grep pass with `[[:alnum:]_.]+:[[:alnum:]_]+` plus a Python regex that
parses the module/func separator. **3 fewer false orphans** —
`post_coo_daily_diagnostic`, `post_cto_daily_diagnostic`,
`post_trend_daily_diagnostic` are now correctly attributed to the
`diagnostics/*.py` config files that reference them.

**2) Wired 14 safe DB-hygiene + metrics tasks** into `app.conf.beat_schedule`.
Every entry below was verified to (a) make no LLM/embedding calls,
(b) dispatch no agents, (c) perform only DB queryset filters or in-app
state changes. These are the kinds of tasks Chris meant by "should this
do something and got forgotten about" — they were defined with explicit
schedule hints in docstrings (e.g. *"Every hour"*, *"daily at midnight"*)
but never added to the schedule.

| Task | Cadence | What it does |
|---|---|---|
| `expire_old_opportunities` | daily 02:30 Denver | Mark expired opps |
| `expire_old_suggestions` | daily 02:45 Denver | Mark expired SmartSuggestions |
| `expire_overdue_validations` | hourly :00 | HITL deadline expiry |
| `claim_stale_events` | every 5 min | Reclaim stuck Redis-stream events |
| `cleanup_automated_conversation_artifacts` | daily 03:00 | Discussion-prefix conversation cleanup |
| `cleanup_expired_boardroom_items` | daily 03:15 | Boardroom retention |
| `cleanup_halted_experiments` | daily 03:30 | Experiment retention |
| `cleanup_stale_scoring_requests` | every 30 min | Scoring queue hygiene |
| `reap_zombie_work` | hourly :15 | Stuck deliberation + pilot work |
| `send_pending_notifications` | every 5 min | In-app notification delivery |
| `check_learning_loop_slo` | daily 09:00 | 24h usage_rate SLO check |
| `check_llm_cost_spike` | hourly :05 | LLM spend rate aggregate |
| `aggregate_roi_metrics_daily` | daily 02:00 | ROI metric rollup |
| `calculate_daily_revenue_metrics` | daily 00:15 | RevenueMetrics row |

**Orphan count drop in batch 3:** 58 → **41** (3 detector + 14 wired).
Cumulative across batches 1+2+3: **272 → 41 (85% reduction).**

### Remaining 41 — explicit triage

| Category | Approx count | Action needed |
|---|---:|---|
| **Intentionally orphan** (`debug_task`) | 1 | None — by design |
| **Behavior-changing scheduled** | ~10 | Needs Chris green-light — `auto_approve_boardroom_items`, `auto_promote_low_risk_decisions`, `propagate_new_policies`, `promote_to_shared_knowledge`, `verify_completed_fixes`, `assign_open_findings_to_agents`, `discover_and_import_audits`, `update_distribution_analytics`, `update_mythology_pattern_statistics`, `rescan_active_workspaces` |
| **LLM-cost scheduled** | ~5 | Deferred until OpenAI credits replenished — `rag_retrieval_canary` (embeddings), `send_weekly_kpi_summary` (Discord post), `post_ops_digest`, `run_ops_autopilot` (takes actions), `maintain_knowledge_freshness` (LLM scoring) |
| **Triggered by external events** | ~15 | None — fire on webhook/escalation/HITL events that the detector can't grep for |
| **Dormant utilities** | ~9 | Per-task — mgmt-command wrap or leave with comment |

Verifier baseline locked at **41**.

### Batch 2 outcome (Session 1115)

After batch 1 brought orphans from 272 → 188 by catching 3 missed
caller paths (CLI / `add_critical_celery_tasks` / autopilot budget),
batch 2 added one more: **string-literal task names anywhere in the
codebase.** Examples surfaced when walking the `run_*` family:

- `core/services/tasks_ops.py` maps situation slugs to task names
  via dict-value strings.
- `core/services/discord_bot.py` references task names in slash-command
  handlers.
- `core/views_autonomous_dashboard.py::run_situation_now` dispatches
  situations by task name from URL kwargs.

These dispatch patterns pass task names as plain strings to dynamic
dispatchers (`current_app.send_task(name)`, etc.). The original
detector didn't grep for the strings themselves; it only looked for
`.delay()` / `send_task(...)` patterns directly.

Implementation note: the BSD `grep -E` regex didn't accept `\w`
shorthand — using `[[:alnum:]_]` instead made the difference. The
"first commit didn't change the count" mystery in this branch's
history was that regex problem (the grep returned 0 matches under
the original `\w`-using version).

**Orphan count drop in batch 2:** 188 → **58**. 130 more false-orphans
reclaimed. Cumulative across batches 1 + 2: **272 → 58 (79% reduction).**

### Final triage of the remaining 58

The 58 split into categories that need different handling:

| Category | Approx count | Action needed |
|---|---:|---|
| **Intentionally orphan** (debug-only) | 1 | None — `debug_task` is by design |
| **Should-be-scheduled but never wired** | ~20 | **Wire schedules** — these have docstrings like "Every 10 min" or "daily" but no entry in `app.conf.beat_schedule` or `add_critical_celery_tasks` |
| **Triggered by external events** | ~15 | None — these fire on webhook/escalation/HITL events that the detector can't grep for (e.g. `handle_client_response`, `submit_proposal_automatically`) |
| **Dormant utilities** | ~20 | Per-task — could wrap in mgmt commands or leave with `dormant utility` comment |

The biggest category of "real find" is **~20 tasks that were
designed for a schedule but the schedule entry was never added.**
The most explicit examples:

- `run_ops_autopilot` — docstring: *"Every 10 min: evaluate ops policies and take allowed automatic actions."* No schedule.
- `post_coo_daily_diagnostic`, `post_cto_daily_diagnostic`, `post_trend_daily_diagnostic` — 3 daily diagnostics, no schedule.
- `aggregate_roi_metrics_daily`, `calculate_daily_revenue_metrics`, `send_weekly_kpi_summary` — metrics rollups, no schedule.
- `check_learning_loop_slo`, `rag_retrieval_canary` — SLO/quality checks, no schedule.
- `claim_stale_events`, `expire_old_opportunities`, `expire_old_suggestions`, `expire_overdue_validations`, `maintain_dream_backlog`, `maintain_knowledge_freshness` — maintenance tasks, no schedule.

**Deferred:** wiring these schedules. Same caution as finding #3's
broken beat refs — this is behavior-changing (re-enabling tasks
that have been dormant). Best done in a focused follow-up session
where each task gets a green-light decision: does it actually need
to fire? at what cadence? what queue?

The verifier baseline is now **58** so this drop is locked in;
future regressions surface immediately.

### Batch 1 outcome (kept for history)
### 12-batch-1. Detection upgrade (272 → 188 orphans)

**Batch 1 outcome (Session 1115):** the detection itself was the
biggest fix. Walking the `backfill_*` family (6 tasks) showed most
"orphans" weren't dead — they were invoked through paths the original
detector didn't see:

| Task | Real caller path |
|---|---|
| `backfill_voice_scores` | Same-name CLI: `python manage.py backfill_voice_scores` |
| `backfill_deliverable_workspaces` | PA dynamic dispatch via `cockpit_tool.trigger_task` + same-name CLI |
| `backfill_conversation_embeddings` | `add_critical_celery_tasks.py` second-scheduler dict + ops_autopilot budget |
| `backfill_memory_embeddings` | `add_critical_celery_tasks.py` + ops_autopilot budget |
| `backfill_stage_documents` | `add_critical_celery_tasks.py` second-scheduler dict |
| `backfill_signal_scores` | **Genuinely orphan** — Session 1025 one-shot scorer, only ref is queue routing in settings.py |

Detection upgraded in `build_celery_audit.py` + verifier
`celery_orphan_count_baseline` to recognize three new caller patterns:

1. **`add_critical_celery_tasks.py` task dict** — a separate scheduler
   source that creates `PeriodicTask` rows distinct from
   `app.conf.beat_schedule`.
2. **`ops_autopilot/budget.py` budget dict** — autopilot dispatches
   these within daily budgets.
3. **Same-name management commands** — when `core/management/commands/<short>.py`
   matches a task's short name, the CLI is a real public caller.

Verifier baseline bumped: **272 → 188 orphans.** Three claim values
documented in the verifier comments + AUDIT_FINDINGS entry below.

**The one genuine orphan in batch 1** (`backfill_signal_scores`) is a
dormant utility — fine to keep, since it's a manual-recovery tool for
re-scoring SignalClusters if scoring gets disabled then re-enabled.
Could be wrapped in a management command in a follow-up batch so the
audit shows it as wired.

**Remaining 188 orphans:** still need per-batch walking. Next batches
should pick families with highest payoff (likely `run_*` at 49
orphans, `check_*` at 22, `process_*` at 16). Each batch will likely
follow the same pattern: surface another caller path the detector
missed, then identify a small set of truly-dormant tasks for
case-by-case decision (delete / mgmt-command-wrap / leave with
comment).

---

### Original framing — pre-batch-1 (kept for history)
### 12-orig. 245 orphan Celery tasks (67% of registry)

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

## 14. `run_heartbeat` and `check_celery_health` take >30 seconds — ✅ fixed

**Status:** ✅ fixed Session 1115 — timeout cap + no-worker short-circuit.

**Verifier doc:** `docs/RUNTIME_AUDIT.md` (telemetry-driven)

**Before / after wall times** (measured locally with `cProfile`):

| Task | Before | After | Speedup |
|---|---:|---:|---:|
| `run_heartbeat` | 34.01s | **1.50s** | **22×** |
| `check_celery_health` | 31.39s | **0.04s** | **800×** |

### Root cause

`cProfile` showed both tasks spent 30+ of their 31-34 seconds inside
`core/services/celery_health.py::_check_workers`, which calls three
worker-introspection methods sequentially:

```python
inspect = self._app.control.inspect(timeout=10.0)
active = inspect.active() or {}
stats = inspect.stats() or {}
ping_response = inspect.ping() or {}
```

Each call uses Celery's `broadcast` mechanism: send a control message
to all workers, poll for replies until timeout. With the inspector
configured for a 10-second timeout, three sequential broadcasts ate
~30 seconds when no workers responded (local DB, no live workers).

### Fix landed

Two changes in `core/services/celery_health.py::_check_workers`:

1. **Drop per-call timeout from 10.0s → 1.0s.** Responsive workers
   reply in <100ms; non-responsive ones aren't going to answer at 10s
   either, so the extra wait is pure dead time.
2. **Short-circuit when zero worker processes exist on the host.**
   `_check_worker_processes()` (a cheap `ps`-grep) tells us
   immediately when there's nobody to broadcast to. Skip the three
   broadcasts entirely in that case.

### Cost when workers ARE running

Worst case after the fix is 3 × 1.0s = 3s in `_check_workers`,
plus the ~1.5s spent in body-system vital fetches. Total per
heartbeat: ~4.5s. Down from ~34s. Easily within the 600s (10-min)
schedule budget.

### Risk

Low. The heartbeat tasks still produce the same data; they just
stop blocking on broadcasts to workers that won't reply. Any caller
relying on the longer timeout was already getting timeout-default
data (empty dict) anyway.

### Verifier impact

No new claim registered for this fix — speed is operational, not
something the static-verifier framework tracks. Future runs of
`build_runtime_audit` will show the lower task durations in
`CeleryTaskEvent` aggregations.

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

## 17. `ToolCallRecord` blind spot for non-PA dispatch — ✅ fixed

**Status:** ✅ fixed Session 1115 — dispatcher writes on all return paths.

**Fix landed in `core/services/tool_dispatcher.py`:**

`execute()` gained 3 new kwargs:
- `agent_name: str = 'Direct'` — caller identity recorded on the row
- `conversation_id: Optional[Any] = None` — chat-session linkage
- `record_telemetry: bool = True` — escape hatch for callers that want
  exclusive write control

Two helpers added on `ToolDispatcher`:
- `_record_tool_call_async()` — async wrapper that schedules the ORM
  write on a worker thread via `asyncio.to_thread`. Fire-and-forget;
  failures logged at WARNING and swallowed.
- `_record_tool_call_sync()` — the actual `ToolCallRecord.objects.create(...)`
  write. Single INSERT.

The helper is called from **all five `execute()` return paths**:
1. Permission denied (`AssistantProfile` blocks the tool).
2. Tool not found (`tool_name not in self._tool_handlers`).
3. Success (handler returns a result).
4. Timeout (`asyncio.TimeoutError`).
5. Exception (anything else from the handler).

So every dispatch — PA, direct `execute_sync`, agent-to-tool delegation,
internal composition — produces a `ToolCallRecord` row.

**PA side:**
- All 3 PA-loop `execute(...)` call sites now pass
  `agent_name='PersonalAssistant'` and `conversation_id=self.conversation_id`
  so the dispatcher's row reflects PA context.
- The manual `_record_tool_call` block in the PA loop was **removed**
  (the dispatcher now handles it).
- `_record_tool_call` method on `UnifiedPersonalAssistant` is marked
  **deprecated** in its docstring; kept for external callers that
  imported it directly. Safe to delete once a grep confirms zero
  external uses.

**Verified live (Session 1115 local):**

```
Before: 0 ToolCallRecord rows
3 direct execute_sync calls (analytics_tool, audit_tool, nonexistent_tool)
After: 3 rows · agent=Direct · including the TOOL_NOT_FOUND failure path
```

**Risk:** small — adds 1 DB write per tool call, on a thread (no
blocking on the async loop). Schema already exists. PA pipeline's row
count stays at exactly 1 per dispatch (the dispatcher now owns it, PA
no longer double-writes).

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
