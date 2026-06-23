# Session 1221 — Tier 1 + Tier 2 from 7ae61cf7

**Status:** Both tiers from the Session 1220 P2 deliverable shipped same-session. PeriodicTask materialized, workers restarted, new task verified registered.
**Date:** 2026-06-23.
**Active conversation:** `pa-58737666f25741dc` (continued from Sessions 1217-1220).
**Prior session:** [`SESSION_1220_ZOMBIE_MONITOR_PLUS_HTTPX_INVESTIGATION.md`](./SESSION_1220_ZOMBIE_MONITOR_PLUS_HTTPX_INVESTIGATION.md).
**Next session entry point:** Session 1222 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1222".

## TL;DR

The Session 1220 P2 investigation (deliverable `7ae61cf7-…`) named two follow-on fixes: **Tier 1** (total-request bound at `BaseAgent._call_openai`) to stop new zombie LLM calls from forming, and **Tier 2** (`LLMCallEvent` cleanup watchdog) to catch any zombies that escape — including from non-`BaseAgent` paths. Both shipped same-session as small, surgical PRs. Together they close the `httpx.Timeout(read=90s)` per-chunk loophole at both layers.

## Session Manifest

### PRs merged

| # | Title | Tier |
|---|---|---|
| **#2519** | `feat(session-1221): total-request bound on OpenAI calls (Tier 1 from 7ae61cf7)` | 1 |
| **#2520** | `feat(session-1221): LLMCallEvent cleanup watchdog (Tier 2 from 7ae61cf7)` | 2 |
| **(this PR)** | `docs(session-1221): close — Tier 1 + Tier 2 from 7ae61cf7 + Session 1222 start-here` | — |

### Beat schedule + worker state

- PeriodicTask `cleanup-stuck-llm-calls` materialized via `python manage.py add_critical_celery_tasks` (1 row created, 83 skipped).
- Local workers restarted (`pkill -9 -f celery; rm -f .celery*.pid; make celery`) to load the new `@shared_task` and Tier 1 helper.
- Verified registration: `celery -A core inspect registered` returns `core.tasks.cleanup_stale_llm_calls` in all 4 worker processes.
- Schedule cadence: `crontab(minute='*/10')`, queue `broadcast` — same tick as the existing `cleanup-stuck-agent-executions`.

## Tier-by-tier close

### Tier 1 (PR #2519) — total-request bound on `BaseAgent._call_openai`

New helper `_run_openai_create_with_total_cap` at the top of `core/agents/base_agent.py`. Wraps the sync OpenAI SDK call in a `concurrent.futures.ThreadPoolExecutor` + `Future.result(timeout=...)`. `shutdown(wait=False)` to avoid blocking on the worker thread (Session 1075 precedent — the underlying httpx request remains alive in the worker thread, same Phase 3 zombie semantics, bounded by `--max-tasks-per-child` recycling).

**Call site change** in `BaseAgent._call_openai` at ~line 2589:

```python
total_request_cap_s = max(180.0, float(self.llm_timeout) * 2.5)
response = _run_openai_create_with_total_cap(
    self.client.chat.completions.create,
    create_kwargs,
    total_request_cap_s,
    agent_name=self.name,
)
```

**Cap-formula derivation:**

| Agent | `llm_timeout` | Cap (s) | Wall-clock budget (s) |
|---|---|---|---|
| AudioAgent | 60 | 180 | 300 — cap leaves 120s for cleanup |
| ContentWriterAgent | 60 | 180 | 600 — empirical max SUCCESS 102.7s, 90s headroom |
| CTOAgent | 180 | 450 | 1200 |
| ResearchAgent | 1500 | 3750 | matches heavy-research wall-clock budget |

Floor of 180s keeps the bound above the observed legitimate ContentWriterAgent 102.7s SUCCESS. Multiplier of 2.5× scales for reasoning-heavy agents while staying below per-agent wall-clock so cleanup has time.

**6 smoke tests** in `tests/services/test_openai_total_request_cap.py`:
- Returns value on success (transparent wrap)
- Forwards kwargs verbatim
- Raises `TimeoutError` when call exceeds cap
- Error message names the cap value
- Propagates non-timeout exceptions unchanged
- Empty agent_name → 'unknown'

### Tier 2 (PR #2520) — `LLMCallEvent` cleanup watchdog

Mirror of the existing `_impl_cleanup_stale_agent_executions`. New impl `_impl_cleanup_stale_llm_calls` in `core/tasks_agents.py`. Default threshold 10 min — well above Tier 1 cap floor of 180s and observed legitimate ContentWriterAgent SUCCESS max of 102.7s.

**Sweep logic:**

```python
stale = LLMCallEvent.objects.filter(
    status='STARTED',
    started_at__lt=cutoff_time,
)
stale.update(
    status='FAILED',
    error_type='timeout',
    error_message='... watchdog_cleanup',
    finished_at=now,
    cancelled=True,
)
```

`error_type='timeout'` + `watchdog_cleanup` in the message → `ops_tool.failure_signatures` aggregates them naturally without dashboard work.

**7 smoke tests** in `tests/services/test_llm_call_event_watchdog.py`:
- Marks stale STARTED → FAILED with all metadata
- Skips fresh STARTED rows
- Skips already-completed (SUCCESS/FAILED) rows
- Handles multiple stale rows in one sweep
- No-op when no rows
- Respects `minutes_threshold` kwarg
- Error message names the threshold value

## Defense layers after merge (full stack)

| Concern | Layer | First shipped |
|---|---|---|
| Per-agent wall-clock timeout DB-row early-save | `tasks_agents.py` early-save | PR #2513 (Session 1219 Phase 2) |
| Celery `task_failure` / `SoftTimeLimitExceeded` row update | `task_failure` bridge in `celery_telemetry.py` | PR #2512 (Session 1219 Phase 1) |
| Zombie-thread observability | `zombie_thread_monitor.py` + `ops_tool.zombie_thread_rate` | PR #2515 (Session 1220 P1) |
| **Total OpenAI request budget** | **`_run_openai_create_with_total_cap` in `base_agent.py`** | **PR #2519 (Session 1221 P1 / Tier 1)** |
| **Stuck `LLMCallEvent.status='STARTED'` rows** | **`cleanup_stale_llm_calls` beat task** | **PR #2520 (Session 1221 P2 / Tier 2)** |
| Hard SIGKILL fallback | Cleanup watchdog | (existing) |

The full watchdog story is now end-to-end: Tier 1 stops the leak at source for ~80 agents, Tier 2 catches anything that escapes (non-BaseAgent paths, edge cases), early-save guarantees the AgentExecution row state lands, the bridge catches Celery failures, the monitor surfaces structural-hang spikes, and the original cleanup watchdog remains the SIGKILL safety net.

## What this session did NOT do (Session 1222 candidates)

1. **Tier 3 from P2 deliverable** — wrap the openai_client_factory clients at construction time. Heavier contract change; defer unless Tier 1 + Tier 2 leakage persists.
2. **B2 follow-on for OpenAIProvider** (deferred since Session 1217 PR #2507). Full class removal requires confirming `real_*` agent paths are no longer exercised in production.
3. **Trim remaining 9 zero-exec gateway-referenced classes** (deferred since Session 1218 P2). Per-site refactor of gateway dispatches.
4. **Promote `check-reasoning-contract.yml` to enforce mode** (P2 carryover from Session 1216).
5. **Production verification of Tier 1 + Tier 2** — Chris's `feedback_local_only_default` memory says local-only unless explicitly notified. Local restart + workers-registered verification done; production merges happen via PR queue.

## Memory updates worth carrying forward

No new feedback memories this session. Four existing rules dogfooded:
- `feedback_celery_pid_cache_blocks_restart.md` — `pkill -9 -f celery; rm -f .celery*.pid; make celery` to load new `@shared_task` Tier 2 + helper Tier 1.
- `feedback_new_shared_task_needs_worker_restart.md` — explicit restart between Tier 2 merge and verification.
- `feedback_observation_cadence_via_beat_not_cron.md` — beat entry in `core/celery.py:beat_schedule` + `add_critical_celery_tasks` materializer (1 created, 83 skipped).
- `feedback_rigby_collaboration.md` — sync-check ping at start of Session 1221 confirmed Rigby had full context (DB-persisted conversation survived the worker restart).

## Files touched this session

```
core/agents/base_agent.py                                                       (+90 helper at top, +14 call-site wrap)
core/tasks_agents.py                                                            (+95 _impl_cleanup_stale_llm_calls)
core/tasks.py                                                                   (+10 @shared_task wrapper)
core/celery.py                                                                  (+10 beat schedule entry)
tests/services/test_openai_total_request_cap.py                                 (NEW, 144 lines, 6 tests)
tests/services/test_llm_call_event_watchdog.py                                  (NEW, 135 lines, 7 tests)
docs/handoffs/SESSION_1221_TIER_1_PLUS_TIER_2_FROM_7AE61CF7.md                  (NEW, this file)
00-START-NEXT-SESSION.md                                                        (Session 1222 FIRST THING rewrite)
```
