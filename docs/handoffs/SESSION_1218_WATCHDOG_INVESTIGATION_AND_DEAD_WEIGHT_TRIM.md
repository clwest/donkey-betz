# Session 1218 — Watchdog 3600s Investigation + Dead-Weight Trim

**Status:** Session 1217 PRs merged (#2506/#2507/#2508). Session 1218 priorities reordered by Chris (P3 → P2). Both shipped. 1 deliverable populated.
**Date:** 2026-06-23.
**Active conversation:** `pa-58737666f25741dc` (continued from Sessions 1217-prep / 1217-execution).
**Prior session:** [`SESSION_1217_BOUNDED_AUDIT_EXECUTION.md`](./SESSION_1217_BOUNDED_AUDIT_EXECUTION.md).
**Next session entry point:** Session 1219 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1219".

## TL;DR

Chris greenlit the Session 1217 PRs and asked to reorder Session 1218 priorities — **investigate watchdog first, then dead-weight cleanup**. Both items shipped in one session. The watchdog investigation surfaced that "3600s" isn't a single timeout but the cleanup-watchdog beat tick (~30 min) interacting with the staleness threshold (60 min). Wall-clock + Celery soft-limit defenses are in place but leak `AgentExecution` rows when `SoftTimeLimitExceeded` / `SIGKILL` bypass the normal cleanup path. The recommended fix (`task_failure.connect` → mark AgentExecution failed) is documented in the deliverable; Chris should decide whether to ship.

The dead-weight cleanup trimmed 22 zero-execution agent classes from the PA dispatcher (originally identified as 31, but 9 are still referenced by gateway code paths). Zero functional impact.

## Session Manifest

### PRs merged

| # | Title | Purpose |
|---|---|---|
| **#2506** | `fix(session-1217): drop dead validated_result guard…` | Session 1217 Item 1 Bug A merged into main |
| **#2507** | `fix(session-1217): replace broken OpenAIProvider.generate…` | Session 1217 Item 1 Bug B + smoke test merged |
| **#2508** | `docs(session-1217): close — bounded-audit execution handoff…` | Session 1217 close + 1218 start-here merged |
| **#2509** | `docs(session-1218): regenerate INDEX.md after Session 1217 PR merges` | Routine post-merge INDEX regen |
| **#2510** | `chore(session-1218): trim 22 zero-execution agents from PA dispatcher` | Session 1218 P2 — dead-weight cleanup |
| **(this PR)** | `docs(session-1218): close — watchdog investigation + dead-weight trim handoff` | This handoff + Session 1219 start-here |

### Deliverables populated

| ID | Title | Final size | Status |
|---|---|---|---|
| `6b00c112-5fa9-4414-acf2-6d1b05cd9a1f` | Session 1218 P3 — Watchdog 3600s timeout root-cause investigation | **7,325 chars** | populated via Rigby `deliverable_tool.append` of Claude's findings |

## P3 — Watchdog investigation (no code shipped)

**Headline finding: "3600s watchdog timeout" is not a single timeout — it's the cleanup-watchdog beat tick (~30 min) catching `AgentExecution` rows whose 60-min staleness threshold has been exceeded.** Wall-clock per-agent timeouts (`core/services/agent_timeouts.py`, range 300-1500s) and Celery soft-limit (3600s) / hard-limit (3900s) on `execute_agent_task` exist as primary defenses but leak rows in 'in_progress' when:

1. **`SoftTimeLimitExceeded` propagates past the `_FuturesTimeout` handler** at `tasks_agents.py:2425`. The Celery `task_failure` signal updates `CeleryTaskEvent` but does NOT touch `AgentExecution`.
2. **Hard `time_limit=3900` SIGKILLs the worker mid-update.** The DB row stays orphaned in 'in_progress' until the next 30-min watchdog sweep catches it — potentially hours later.

Empirical data (last 7d): 15 watchdog-killed rows. Distribution dominated by CTOAgent/COOAgent (47%). Per-agent elapsed times exceed each agent's wall-clock timeout by 6-13× (e.g., AudioAgent `_wall_timeout=300s` ran 4006s before catch). All 15 rows have `cost=0, tokens_used=0, output_data={}` — the agent body never reported metrics.

**Recommended fix** (documented in deliverable `6b00c112`, not shipped this session — defer to Chris):

```python
@task_failure.connect
def on_agent_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    """Mark AgentExecution rows associated with the failed Celery task as failed."""
    rows = AgentExecution.objects.filter(
        status__in=('running', 'in_progress'),
        input_data__celery_task_id=str(task_id),
    )
    rows.update(
        status='failed',
        error_message=f'Celery task failed: {type(exception).__name__}: {str(exception)[:200]}',
        completed_at=timezone.now(),
    )
```

Closes the 0-30 min gap between Celery task death and watchdog cleanup. Hooks into `core/celery_telemetry.py`. ~30 line PR + smoke test.

**Open question deferred:** *why* wall-clock per-agent timeouts (`_future.result(timeout=300s)` for AudioAgent) don't fire when the agent runs 4000s. The `ThreadPoolExecutor` + `_future.result(timeout=...)` should raise `_FuturesTimeout` at 300s. The Celery `SoftTimeLimitExceeded`/`SIGKILL` interaction with that timeout is the suspected mechanism but needs separate investigation.

## P2 — Dead-weight cleanup (PR #2510)

Session 1217 Item 2 surfaced 31 zero-execution agent classes. Pre-flight grep this session found 9 are still referenced by gateway code paths (`td_handlers_content.py`, `td_handlers_ops.py`, `td_handlers_core.py`) — kept those in. **Remaining 22 truly safe to remove:**

`bookmaker_agent`, `bull_case_agent`, `content_executor_agent`, `cultural_impact_agent`, `debate_advocate_agent`, `debate_skeptic_agent`, `decision_enforcer_agent`, `distribution_agent`, `exploit_detector_agent`, `institutional_watcher_agent`, `market_anomaly_detector_agent`, `market_intelligence_agent`, `market_movement_monitor_agent`, `moderator_agent`, `narrative_drift_coordinator`, `narrative_historian_agent`, `prompt_engineering_agent`, `signal_scanner_agent`, `smart_contract_auditor_agent`, `technical_document_agent`, `transaction_monitor_agent`, `trend_break_detector_agent`

**Files touched:**
- `core/services/pa_tool_schemas.py` — `run_agent` enum: 80 → 58 entries. Description string updated.
- `core/services/tool_dispatcher.py` — register lines: 174 → 152 handlers.
- `core/services/td_handlers_agents.py` — `_tool_to_agent_name` map: 21 entries removed (the 22nd, `distribution_agent`, was already missing and relied on fallback).

**Confirmed safe even for the 4 trimmed tool names with external `grep` hits** (`content_executor_agent`, `market_intelligence_agent`, `narrative_drift_coordinator`, `prompt_engineering_agent`): all external refs use the CLASS name in independent code paths (separate dispatchers, mapping tables, source-name identifiers) — not the tool name. Removing the `run_agent` enum entry + `tool_dispatcher.register` + `_tool_to_agent_name` mapping doesn't affect those paths.

## Operational invariants (post-merge)

- `_handle_agent_tool` still routes `run_agent(agent_name="X")` for the 58 remaining enum entries.
- The 9 zero-exec classes that stayed in (`ContentDiversityOrchestrator`, `ContrarianAgent`, `LineMovementAnalyzer`, `PerformanceAnalystAgent`, `ResolveAgent`, `SharpActionDetector`, `TalkingCharacterAgent`, `VoiceCriticAgent`, `WhaleWatcherAgent`) are still in the run_agent enum, dispatcher register, and `_tool_to_agent_name` map. Gateway dispatches (`td_handlers_content.py:4160` etc.) keep working.
- The 22 trimmed classes' Python files in `core/agents/...` were NOT deleted. Only the dispatch surface area shrank. If anyone wants them back, restore the 3 dispatcher entries — files stay untouched.

## Memory updates worth carrying forward

No new feedback memories. Two existing rules dogfooded:
- `feedback_corpus_walks_surface_mechanism_drift.md` — the watchdog investigation found the original audit's "59 schemaless handlers" count was double-checked + corrected to "66 → 22 truly-safe to trim." Drift surfaced and routed back into the audit via the cleanup PR.
- `feedback_deliverable_tool_use_append_for_large_payloads.md` — 9.4 KB P3 findings shipped via Rigby `deliverable_tool` create + append (one initial create call failed silently because the payload was too large; Rigby split it). Reinforces the rule.

## What Session 1218 did NOT do (Session 1219 candidates)

1. **Ship the `task_failure.connect` watchdog fix.** Recommended in deliverable `6b00c112`, ~30 line PR + smoke test. Defer to Chris's go/no-go.
2. **B2 follow-on for OpenAIProvider** (deferred from Session 1217 PR #2507). Full class removal requires confirming `real_*` agent paths are no longer exercised in production.
3. **Trim the remaining 9 zero-exec gateway-referenced classes.** Requires refactoring the gateway dispatch sites — bigger scope than P2.
4. **Investigate why wall-clock per-agent timeouts (`_future.result(timeout=...)`) don't fire.** Open question from P3 investigation. Needs threading + Celery signal interaction analysis.

## Files touched this session

```
core/services/pa_tool_schemas.py                                                  (-22 enum + description update)
core/services/tool_dispatcher.py                                                  (-22 register lines)
core/services/td_handlers_agents.py                                               (-21 mapping entries)
docs/INDEX.md                                                                     (auto-regen)
docs/handoffs/SESSION_1218_WATCHDOG_INVESTIGATION_AND_DEAD_WEIGHT_TRIM.md         (NEW, this file)
00-START-NEXT-SESSION.md                                                          (Session 1219 FIRST THING rewrite)
```
