# Session 1184 PR-B — BaseAgent → execution_id root-cause fix + 5 agent integration tests + §1 enumeration

**Status:** Ready. 1 PR open (stacked on PR #2362). 7/7 new tests pass. WARN log now includes caller fingerprint for fast PR-C triage.
**Date:** 2026-06-20
**Pinned conversation:** `pa-a60842917d36`
**Driving deliverable:** Phase 2 of [`e4f4e12f-bd77-4611-a3d6-1a50fd3b9412`](#) — caller sweep + strict enforcement.
**Prior handoff:** [SESSION_1184_DELIVERABLE_PROVENANCE_LINKAGE.md](./SESSION_1184_DELIVERABLE_PROVENANCE_LINKAGE.md) — Stage 1 (PR #2362) factory synthesis + read helper + first tests.

## TL;DR

Recon for the "31 caller sweep" surfaced a one-line root-cause bug: `core/agents/base_agent.py:_save_to_deliverable` was reading `getattr(self, '_current_execution_id', None)` — an attribute name nothing in production ever sets. Meanwhile `core/agent_router.py:1442` was writing the running execution id to `agent._execution_context['execution_id']`. Wrong attribute name → every BaseAgent dispatch dropped `parent_execution_id`. **One fix covers all ~80 routable agents at once**, far smaller than the 31-callsite migration we initially planned.

Also fixed: `agent_router._run_agent_execute` was setting `agent._execution_context = context` *inside* the standard `execute()` branch only. The `execute_with_workspace()` branch (Session 908) never got the assignment, leaving workspace-routed agents broken even after the BaseAgent fix. Hoisted the assignment above the branch so both paths land it.

Per Rigby's PR-A close-out: added a caller-fingerprint to the soft-enforce WARN so PR-C sweep work has fast triage signal. Format: `caller=<short_filename>:<lineno>:<funcname>` — walks the stack past factory + base_agent plumbing.

Produced the §1 enumeration table per Rigby's Q3 recommendation: `docs/specs/deliverable_creation_paths.md` — coverage summary + per-callsite buckets (wired / synthesized / WARN) + sweep notes for each remaining row.

| Change | Status |
|---|---|
| `base_agent.py:4266` — read `_execution_context['execution_id']` with dict-guard fallback to legacy attr | ✅ |
| `agent_router.py:1433` — hoist `agent._execution_context = context` so both execute paths set it | ✅ |
| `deliverable_factory.py` — WARN now includes `caller=<file>:<line>:<func>` fingerprint via stack walk | ✅ |
| `test_base_agent_provenance_wiring.py` — 7 tests covering ContentWriter, BlogWriter, Editor, ContentStrategy, Distribution + legacy attr fallback + missing-context bucket | ✅ 7/7 pass |
| `docs/specs/deliverable_creation_paths.md` — §1 enumeration artifact | ✅ |

## Design Qs ratified by Rigby (PR-B card on `pa-a60842917d36`)

- **Q1 PR-A scope** = root-cause fix + router hoist + 5 named integration tests + §1 enumeration table. **Ratified as written.** Explicit dict-guard pattern preferred over compact one-liner (`isinstance(ctx, dict)`). Don't skip the workspace-path hoist (would leave 20% broken). Don't skip the tests (the contract has to be real).
- **Q2 Top-5 agents:** ContentWriter / BlogWriter / Editor confirmed mandatory. Rigby's choice for the other 2: DistributionAgent + ContentStrategyAgent (distinct paths, high frequency). Swap to SocialMediaAgent only if recent volume shows it dominates.
- **Q3 PR-B sequencing:** Defer to next session. Ship this PR, watch WARN log for 24h, then targeted per-caller decisions in PR-C.
- **Extra guardrail:** caller fingerprint in WARN. Implemented via `_resolve_caller_fingerprint()` helper in `deliverable_factory.py`.

## What ships

### `core/agents/base_agent.py` (lines 4266-4280)

Changed the lookup from the wrong attribute to the right one:

```python
# Was: parent_exec_id = getattr(self, '_current_execution_id', None)
_exec_ctx = getattr(self, '_execution_context', None)
parent_exec_id = (
    _exec_ctx.get('execution_id')
    if isinstance(_exec_ctx, dict)
    else None
) or getattr(self, '_current_execution_id', None)
```

Legacy fallback preserved for `core/tests/test_carryforward_fixes.py` — the only place that sets `_current_execution_id`. Slated for removal once that test migrates.

### `core/agent_router.py` (lines 1425-1454)

Hoisted `agent._execution_context = context` to the top of `_run_agent_execute` so both `execute_with_workspace()` and `execute()` paths receive it.

### `core/services/deliverable_factory.py` (new helper + WARN)

- New `_CALLER_SKIP_FILES` constant + `_resolve_caller_fingerprint()` helper. Walks `sys._getframe` upward until it exits factory + base_agent + append-service files; returns `<short_filename>:<lineno>:<funcname>` or `'unknown'`.
- WARN log now includes `caller=<fingerprint>` field. Confirmed live in test run: `caller=core/tests/test_base_agent_provenance_wiring.py:183:test_missing_execution_context_falls_through_to_warn`.

### `core/tests/test_base_agent_provenance_wiring.py` (new file)

7 tests via a thin `_FakeAgent` subclass that bypasses BaseAgent's LLM/spider plumbing:

1. `test_content_writer_agent_wires_provenance`
2. `test_blog_writer_agent_wires_provenance`
3. `test_editor_agent_wires_provenance`
4. `test_content_strategy_agent_wires_provenance`
5. `test_distribution_agent_wires_provenance`
6. `test_legacy_current_execution_id_attr_still_works` — backward-compat for test-only callers
7. `test_missing_execution_context_falls_through_to_warn` — proves the soft-enforce path is reachable + WARN fires

Each named agent test asserts:
- `d.parent_object_type == 'agent_execution'`
- `d.parent_object_id == execution.id` (real, not synthesized)
- `provenance.origin_execution_id == execution.id`
- `provenance.synthesized == false`
- `provenance.legacy_no_provenance == false`

### `docs/specs/deliverable_creation_paths.md` (new file)

§1 enumeration artifact per Rigby's recommended table format. Buckets all production callsites into:
- ✅ wired (BaseAgent path — one row covers all ~80 agents)
- 🟡 synthesized (5 PA-direct callsites, factory handles automatically)
- ⚠️ WARN bucket (20+ rows: management commands, web views, Celery tasks, service helpers, other tools — the PR-C sweep targets)

Each WARN row has a "Notes for sweep" column with proposed approach (opt into synthesis vs. thread execution context from caller).

## Acceptance impact

PR-A's AC1 was "every newly-created deliverable record includes a non-null `origin_execution_id`" — strictly met only for PA-direct creates. PR-B closes that for all BaseAgent dispatches as a side effect of fixing the root cause:

| Caller class | AC1 status pre-PR-B | AC1 status post-PR-B |
|---|---|---|
| PA-direct (deliverable_tool, content_tool, etc.) | ✅ via PA-direct synthesis | unchanged |
| BaseAgent agents (~80) | ❌ all dropping `parent_execution_id` due to wrong attr name | ✅ wired via `_execution_context` |
| Non-agent callers (mgmt commands, web views, tasks, services) | ⚠️ WARN with no caller info | ⚠️ WARN **with caller fingerprint** for PR-C triage |

## Operational levers

- **Revert BaseAgent fix:** restore `parent_exec_id = getattr(self, '_current_execution_id', None)` at line 4266. Reverts to pre-PR-B WARN bucket for all agents.
- **Revert router hoist:** move `agent._execution_context = context` back inside the standard execute branch (post the `if has_workspace` check). Workspace agents will silently drop execution_id again.
- **Quiet WARN fingerprint:** the fingerprint computation is one `sys._getframe` walk per WARN. Cheap (<1ms), but if profiling shows hot-path cost, swap to a plain `''` literal.
- **Per-agent override:** any agent subclass can set `self._current_execution_id` directly (the legacy attr) to override `_execution_context['execution_id']`. Or pass `parent_execution_id` explicitly to `_save_to_deliverable` — that overrides everything.

## 24h watch (per Rigby)

After PR-B merges:
- `grep "No parent_execution_id" /tmp/celery-*.log | awk -F'caller=' '{print $2}' | awk -F' ' '{print $1}' | sort | uniq -c | sort -rn` — top-N WARN callers, grouped by fingerprint. Expect WARN volume to drop ~80-90% as the BaseAgent path stops contributing, leaving only the genuine PR-C sweep targets.
- The grouped output IS the PR-C work queue.

Once WARN volume reaches steady state (low + stable across 24h), PR-C can flip the factory contract from `logger.warning(...)` to `raise DeliverableProvenanceMissingError(...)` for non-PA contexts.

## Phase 3 (PR-C — deferred)

1. **Sweep the WARN bucket** — work through the ⚠️ rows in `docs/specs/deliverable_creation_paths.md`. Pick per row: opt into PA synthesis (`trigger_source='direct'` in metadata) or thread real execution context from caller.
2. **Flip factory to hard-require** — once WARN reaches zero, change `logger.warning(...)` → `raise DeliverableProvenanceMissingError(...)` in the non-PA branch.
3. **Drop legacy attr fallback** — remove `or getattr(self, '_current_execution_id', None)` after migrating `core/tests/test_carryforward_fixes.py`.

## Files touched

```
core/agents/base_agent.py                          (~14 lines added at 4266)
core/agent_router.py                               (~8 lines moved, _execution_context hoist)
core/services/deliverable_factory.py               (+40 helper + WARN enhancement)
core/tests/test_base_agent_provenance_wiring.py    (+205, new — 7 tests)
docs/specs/deliverable_creation_paths.md           (+158, new)
docs/INDEX.md, docs/_index.json                    (regenerated)
```

Stacked on PR #2362 (PR-A — factory synthesis + read helper). Branch: `feat/session-1184-pr-b-baseagent-provenance-wiring`.
