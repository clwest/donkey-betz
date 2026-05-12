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
| 1 | Phantom `ContentDistributionAgent` in `_NON_SPECIALIST` routing whitelist | low | open | Rigby-gated |
| 2 | Orphaned `distribution_agent` handler — unreachable from LLM | low | open | Rigby-gated |
| 3 | 7 broken beat task refs — silent autodiscover misses | medium | open | Chris/Rigby green-light |
| 4 | 5 `AdvisorDomain` enum values with no advisors | low | open | informational |
| 5 | CLAUDE.md said `144` Discord commands; actual is `96` (double-count) | medium | **✅ fixed Session 1115** | — |
| 6 | CLAUDE.md said `32` advisors; actual is `25` (drift on both subtotals) | medium | **✅ fixed Session 1115** | — |
| 7 | Phantom `ContentDistributionAgent` taxonomy miscount (73/9/1 → 74/8/1) | medium | **✅ fixed Session 1115** | — |
| 8 | `BACKEND_INVENTORY.md` says 63 management commands; actual is 164 | medium | open | doc refresh |
| 9 | Learning bridge naming inconsistency (`LearningLoop` × 7 vs `LearningBridge` × 1) | informational | open | cosmetic |

---

## 1. Phantom `ContentDistributionAgent` in `_NON_SPECIALIST`

**Status:** open · low severity · Rigby-gated (behavior change).

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

**Status:** open · low severity.

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

**Status:** open · medium severity · **Chris/Rigby green-light needed**.

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
