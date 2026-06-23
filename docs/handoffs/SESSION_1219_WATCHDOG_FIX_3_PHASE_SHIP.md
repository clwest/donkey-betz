# Session 1219 — Watchdog Fix 3-Phase Ship

**Status:** Chris's 3-phase watchdog fix plan shipped end-to-end. 2 code PRs + 1 investigation deliverable + this docs PR.
**Date:** 2026-06-23.
**Active conversation:** `pa-58737666f25741dc` (continued from Sessions 1217 / 1218).
**Prior session:** [`SESSION_1218_WATCHDOG_INVESTIGATION_AND_DEAD_WEIGHT_TRIM.md`](./SESSION_1218_WATCHDOG_INVESTIGATION_AND_DEAD_WEIGHT_TRIM.md).
**Next session entry point:** Session 1220 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1220".

## TL;DR

Chris greenlit the watchdog fix as a 3-phase plan: (1) Celery failure bridge, (2) wall-clock-timeout evidence + early save, (3) investigate why the agent thread keeps running. All three shipped same-day. Phases 1 + 2 are merged code; Phase 3 is an investigation deliverable that recommends Option D (monitor + status quo) over heavier per-task-subprocess / signal-based / cooperative-cancellation alternatives. The 3-phase ship leaves the platform with three distinct timeout-source attributions (`agent_wall_clock` / `router_wall_clock` / `watchdog_cleanup`), a `task_failure` → `AgentExecution` bridge that catches `SoftTimeLimitExceeded` / generic exception cases, and a clear documented mechanic for the zombie threads that remain (bounded by `--max-tasks-per-child` worker recycling).

## Session Manifest

### PRs merged

| # | Title | Phase |
|---|---|---|
| **#2512** | `fix(session-1219): bridge Celery task_failure → AgentExecution failed status` | 1 |
| **#2513** | `fix(session-1219): make wall-clock-timeout path explicit + early-save the failed status` | 2 |
| **(this PR)** | `docs(session-1219): close — 3-phase watchdog fix ship + Session 1220 start-here` | — |

### Deliverables populated

| ID | Title | Final size | Status |
|---|---|---|---|
| `cf80d413-1f35-44a9-9763-6bc5f3a93916` | Session 1219 P3 — Zombie agent thread investigation | **7,289 chars** | populated via Rigby `deliverable_tool.append` of Claude's findings |

Cross-link: parent investigation `6b00c112-…` (Session 1218 P3 "Watchdog 3600s timeout root-cause investigation"). Session 1219 P3 is the follow-on that documents the underlying thread mechanic.

## Phase-by-phase close

### Phase 1 (PR #2512) — Celery failure bridge

New `on_agent_task_failure_bridge` signal handler in `core/celery_telemetry.py`. Matches `AgentExecution` rows via `input_data->>'celery_task_id'` (set at row creation in `tasks_agents.py:2179`) and flips them to `status='failed'` with explicit `error_message` carrying exception class + repr.

**Closes:** the gap where `SoftTimeLimitExceeded` / generic `task_failure` propagates past the `_FuturesTimeout` cleanup, leaving the row stuck in 'in_progress'.

**Caveats:**
- Hard SIGKILL cases (Celery `time_limit=3900`) cannot be handled — worker dies, signal never fires. Watchdog remains the safety net for that class.
- Idempotent: scope filters by `status IN ('running','in_progress')`. Re-fire / watchdog race is a no-op.

**5 smoke tests** in `tests/services/test_celery_failure_agentexecution_bridge.py`:
- Bridges `SoftTimeLimitExceeded`
- Bridges generic `RuntimeError`
- Skips already-completed rows
- No-op when no row matches
- Truncates long error messages to fit 2000-char column

### Phase 2 (PR #2513) — Wall-clock evidence + early save

Two changes per handler (Celery-task path + direct router path):

1. **Renamed `timeout_source` for attribution clarity.** `core/tasks_agents.py` now emits `timeout_source='agent_wall_clock'` (was bare `'wall_clock'`). Three distinct values now cover the timeout-source space: `agent_wall_clock`, `router_wall_clock`, `watchdog_cleanup`.

2. **Explicit early save inside both `_FuturesTimeout` handlers.** Right after building `AgentResult(success=False, ...)`, save `status='failed' + error_message + completed_at` with `update_fields=[...]` and emit `"early-saved failed status"` log marker. Defensive insurance — the downstream save() at ~line 2569 in `tasks_agents.py` still runs with full enrichment; one redundant UPDATE is acceptable.

**3 lock-in tests** in `tests/services/test_wall_clock_timeout_source_naming.py`:
- `tasks_agents.py` emits `'agent_wall_clock'` (catches reverts)
- `tasks_agents.py` does NOT still emit the legacy bare `'wall_clock'`
- Both handlers contain the `early-saved failed status` log marker

### Phase 3 (deliverable `cf80d413-…`) — Zombie thread investigation

**Question:** Why does the agent thread keep running after `_future.result(timeout=...)` raises?

**Answer:** `ThreadPoolExecutor.shutdown(wait=False)` doesn't kill the thread — Python has no API to kill threads. The agent body keeps running inside the Celery child process until it returns naturally (typically when the OpenAI httpx call's 90s read timeout fires, the spider HTTP request times out, etc.). The thread is "zombie" only in the sense that nobody is waiting for its result — it still consumes resources until either it returns or the child process exits via `--max-tasks-per-child` recycling.

**Per-worker zombie-thread accumulation cap:**

| Worker | max-tasks-per-child | Zombie cap per child process |
|---|---|---|
| celery-pa | 10 | up to 9 |
| celery-worker | 5 | up to 4 |
| celery-content | 2 | up to 1 |
| celery-long-running(-2) | 2 | up to 1 |
| code-worker | 1 | **0 (fresh process per task)** |

**Empirical rate (last 7d pre-fix):** ~2 zombies/day across all workers. Each holds ~25 MB Python frame state + 1 socket fd + 1 DB connection. Combined with `--max-memory-per-child=200000` (200 MB) safety net, child gets recycled before memory accumulation matters.

**Recommendation: Option D (status quo + monitor).** Phases 1 + 2 close the visible symptom (orphaned DB rows). Heavier alternatives (per-task subprocess, signal-based kill, cooperative cancellation) all have non-trivial tradeoffs. Defer until measurable production impact.

**Open question deferred to Session 1220+:** Why doesn't the OpenAI httpx 90s read timeout catch the zombie BEFORE the 300s+ wall-clock fires for short-budget agents like AudioAgent? If the OpenAI call legitimately respected its 90s read timeout, the agent body would have already raised cleanly. Worth focused investigation — would shrink the wall-clock incidence at the root.

## Defense layers (post-merge)

| Failure mode | Caught by |
|---|---|
| Per-agent wall-clock timeout in Celery task | Phase 2 early-save (`tasks_agents.py`) |
| Per-agent wall-clock timeout in direct router | Phase 2 early-save (`agent_router.py`) |
| Celery `SoftTimeLimitExceeded` | Phase 1 `task_failure` bridge (`celery_telemetry.py`) |
| Generic uncaught exception during agent execution | Phase 1 bridge |
| Hard SIGKILL (Celery `time_limit=3900`) | Cleanup watchdog (`tasks_agents.py:_impl_cleanup_stale_agent_executions`) |
| Race / re-fire | All bridges scope-filter by `status IN ('running','in_progress')` — idempotent |

## What this session did NOT do (Session 1220 candidates)

1. **Ship the zombie-thread monitor** (Option D from Phase 3 deliverable). Small ~10 LoC + ops_tool integration. Alert on >5 zombies/hour for any single agent.
2. **Investigate OpenAI httpx timeout bypass.** The open question from Phase 3 — why does AudioAgent run 4000s+ when its OpenAI client should httpx-timeout at 90s read.
3. **B2 follow-on for OpenAIProvider** (deferred since Session 1217 PR #2507). Full class removal — requires confirming `real_*` agent paths are no longer exercised in production.
4. **Trim the remaining 9 zero-exec gateway-referenced classes** (deferred since Session 1218 P2). Requires per-site refactor of the gateway dispatches.
5. **Promote `check-reasoning-contract.yml` to enforce mode** (P2 carryover from Session 1216).

## Memory updates worth carrying forward

No new feedback memories. Two existing rules dogfooded:
- `feedback_rigby_collaboration.md` — Chris gave a clear 3-phase spec ("ship the bridge, add evidence, then investigate"); execution matched the spec exactly; no scope creep.
- `feedback_deliverable_tool_use_append_for_large_payloads.md` — Phase 3 findings (7.9 KB) shipped via Rigby's `deliverable_tool` create+append. Multi-append pattern verified again.

## Files touched this session

```
core/celery_telemetry.py                                                        (+49 lines)
core/tasks_agents.py                                                            (Phase 2 early-save + rename)
core/agent_router.py                                                            (Phase 2 early-save)
tests/services/test_celery_failure_agentexecution_bridge.py                     (NEW, 143 lines)
tests/services/test_wall_clock_timeout_source_naming.py                         (NEW, 63 lines)
docs/handoffs/SESSION_1219_WATCHDOG_FIX_3_PHASE_SHIP.md                         (NEW, this file)
00-START-NEXT-SESSION.md                                                        (Session 1220 FIRST THING rewrite)
```
