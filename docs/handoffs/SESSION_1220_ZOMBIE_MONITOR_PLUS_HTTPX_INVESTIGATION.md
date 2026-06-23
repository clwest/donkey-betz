# Session 1220 — Zombie Monitor (P1) + Two Detector Fixes + OpenAI httpx Investigation (P2)

**Status:** All planned items shipped. 4 PRs merged + 1 investigation deliverable.
**Date:** 2026-06-23.
**Active conversation:** `pa-58737666f25741dc` (continued from Sessions 1217-1219).
**Prior session:** [`SESSION_1219_WATCHDOG_FIX_3_PHASE_SHIP.md`](./SESSION_1219_WATCHDOG_FIX_3_PHASE_SHIP.md).
**Next session entry point:** Session 1221 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1221".

## TL;DR

Session 1220 P1 (zombie-thread monitor — Option D from Session 1219 P3) shipped clean. The live test surfaced two false-positive bugs in the PA scrubber/detector stack — fixed both same-session. P2 then answered the open question from Session 1219 P3 ("why doesn't the OpenAI httpx 90s read timeout catch the zombie before the 300s wall-clock?") with runtime evidence: the timeout is per-chunk, not total request, and the SDK has no aggregate. Recommended Tier 1 + Tier 2 fixes captured in deliverable `7ae61cf7-…` for Session 1221+.

## Session Manifest

### PRs merged

| # | Title | What |
|---|---|---|
| **#2515** | `feat(session-1220): zombie-thread monitor (P1 — Option D from cf80d413 deliverable)` | New `core/services/zombie_thread_monitor.py` (214 LoC). Wired into both `_FuturesTimeout` catch sites. New `ops_tool.zombie_thread_rate` action with hours / agent_name params. 11 smoke tests. |
| **#2516** | `fix(session-1220): tighten phone redactor so YYYYMMDDHH timestamps don't trip` | Phone regex required no separators — 10-digit hour buckets like `2026062315` were being scrubbed as phone numbers. Tightened to require at least one separator (parens, hyphen, dot, whitespace). Lookbehind/lookahead instead of `\b` so `(555) 123-4567` parens form still matches. 4 new regression tests. |
| **#2517** | `fix(session-1220): guard silent-fallback detector against legit tool-result echoes` | Session 1199's detector flagged any text containing `{"action": "..."}` JSON. Rigby's echoes of legitimate tool results (including `ops_tool.zombie_thread_rate`'s own return shape) were tripping it. New `_should_trigger_silent_fallback(text, tool_runs)` helper keeps the bare detector but only fires the alarm when no tool succeeded in this turn. 7 new unit tests. |
| **(this PR)** | `docs(session-1220): close — zombie monitor + httpx investigation + Session 1221 start-here` | This handoff + Session 1221 start-here. |

### Investigation deliverable

| ID | Title | Final size |
|---|---|---|
| `7ae61cf7-84aa-4837-8343-75c5011773c9` | Session 1220 P2 — OpenAI httpx read-timeout bypass investigation | **7,499 chars** |

Cross-link: parent investigation `cf80d413-…` (Session 1219 P3 "Zombie agent thread investigation"). P2 closes the open question that P3 left.

## Item-by-item close

### P1 — Zombie-thread monitor (PR #2515)

**Design:** Option D from the Session 1219 P3 deliverable (`cf80d413-…`). Per-agent, per-hour counter at `zombie_threads:{agent}:{YYYYMMDDHH}` with 24h TTL. Per-day registry of agents seen (30d TTL) so the query path can enumerate without backend-specific key scanning. Both backends supported (Redis + LocMem).

**Wired into:**
- `core/tasks_agents.py:2425` (Celery task wall-clock catch)
- `core/agent_router.py:1551` (direct router wall-clock catch)

Lazy imports keep worker startup cost zero.

**Surfaced via:** new `ops_tool.zombie_thread_rate` action. Params: `hours` (1..168, default 24), `agent_name` (optional filter). Returns `{action, window_hours, from_hour, to_hour, by_agent, top_offenders}`. Schema entry added to `pa_tool_schemas.py`.

**Suggested alert threshold:** >5/hour for any single agent. Signals a structural hang (upstream LLM provider degraded, spider source down, etc.), not a one-off timeout.

**Live test result:** Rigby called `ops_tool action=zombie_thread_rate hours=24` against the freshly-restarted local PA worker. Returned the expected empty `by_agent: {}` shape — no zombies post-merge.

### Redactor fix (PR #2516) — surfaced by P1 live test

The live test's response showed `from_hour: [REDACTED_PHONE]` instead of the YYYYMMDDHH timestamp. Root cause: `core/services/data_scrubber.py:41` matched bare 10-digit strings because the regex allowed both area-code/exchange separators to be optional.

**Fix:** require at least one separator. Use lookbehind/lookahead instead of `\b` so the `(555) 123-4567` parens form (which the original `\b` couldn't match before `(`) still scrubs.

**Coverage loss:** continuous `15551234567`-style entries no longer match. Acceptable — unformatted 10-digit runs are far more often IDs/timestamps in unstructured text than real phone numbers.

### Detector guard (PR #2517) — surfaced by P1 live test

Worker logs from the live test showed `llm_iterations=1 tool_calls=1 silent_fallback=true` — Rigby used only 2/12 of her iteration budget AND the ops_tool call succeeded, but the user got the canned "I hit my iteration cap" message. Root cause: Session 1199's `_detect_silent_tool_call_fallback` regex matched the JSON in Rigby's echo of the tool result (which legitimately starts with `{"action": "zombie_thread_rate", ...}`).

**Fix:** new `_should_trigger_silent_fallback(text, tool_runs)` helper. Bare detector unchanged (so Session 1199 tests still pass). Helper adds: if any successful tool ran in the cumulative `tool_runs`, treat the JSON shape as a legitimate echo and skip the alarm. Logs `[PA_SILENT_FALLBACK_SKIPPED]` at INFO for auditability.

### P2 — OpenAI httpx read-timeout bypass investigation

**Question:** Session 1219 P3 deliverable noted that AudioAgent (`_wall_timeout=300s`) ran 4006s before the watchdog caught it. The OpenAI client factory sets `read=90s` — that should have raised `APITimeoutError` at ~90s. Why didn't it?

**Answer (deliverable `7ae61cf7-…`):** `httpx.Timeout(read=90s)` is a **per-chunk** timeout, not a **total request** timeout. As long as the OpenAI server emits any response bytes within 90s of the previous bytes, the connection stays open indefinitely. GPT-5.x reasoning models stream thinking + output slowly enough to never trip it.

**Empirical evidence (last 7d, `LLMCallEvent` table):**
- 36 LLM call rows. 34 SUCCESS, 2 stuck STARTED.
- Top successful call durations: 102.7s, 90.9s, 80.3s, … all `retry_count=0`. If `read=90` were total, the 102.7s and 90.9s rows would have raised — they didn't.
- 2 stuck STARTED rows held open 16h and 96h. One has `execution_id` matching a Session 1219 P3 watchdog-killed AgentExecution → proof the LLM call kept running for hours after the ThreadPoolExecutor wall-clock raised at the agent layer.
- Zero `error_type='timeout'` rows. The SDK didn't time out; the wrapper above it bailed.

**Secondary finding:** factory-cached clients share one httpx connection pool per `(api_key, base_url)` per worker process. One stuck call holding a connection starves sibling agents at the `pool=60s` queue.

**Recommendations (for Session 1221+):**
- **Tier 1** — wrap `base_agent._call_openai` in `asyncio.wait_for` / `concurrent.futures.Future.result` with a total cap (suggested `max(180, llm_timeout * 2.5)`). Single call site, ~80 agents covered.
- **Tier 2** — add a cleanup watchdog for stuck `LLMCallEvent.status='STARTED'` rows. Mirror of the `AgentExecution` cleanup pattern. Surfaces leakage via existing `ops_tool.failure_signatures`.
- **Tier 3** (defer) — wrap the openai_client_factory itself with the total-request bound. Heavier contract change.

## Defense layers after merge

| Concern | Layer |
|---|---|
| DB-row staleness on wall-clock-timeout | Session 1219 Phase 2 early-save (PR #2513) |
| DB-row staleness on Celery failure | Session 1219 Phase 1 task_failure bridge (PR #2512) |
| Observability of zombie thread spawn rate | Session 1220 P1 monitor (**PR #2515**) |
| Phone redactor false-positive on 10-digit IDs | Session 1220 redactor fix (**PR #2516**) |
| Silent-fallback false-positive on legit tool-result echo | Session 1220 detector guard (**PR #2517**) |
| OpenAI HTTP total-request bound | **Not yet** — see P2 deliverable Tier 1/2 |

## What this session did NOT do (Session 1221 candidates)

1. **Ship Tier 1** from P2 deliverable — `asyncio.wait_for` wrap in `base_agent._call_openai` with total-request cap. ~30 LoC + a smoke test.
2. **Ship Tier 2** from P2 deliverable — `LLMCallEvent` cleanup watchdog for stuck STARTED rows. ~50 LoC + tests.
3. **B2 follow-on for OpenAIProvider** (deferred since Session 1217 PR #2507). Full class removal requires confirming `real_*` agent paths are no longer exercised in production.
4. **Trim remaining 9 zero-exec gateway-referenced classes** (deferred since Session 1218 P2). Per-site refactor of gateway dispatches.
5. **Promote `check-reasoning-contract.yml` to enforce mode** (P2 carryover from Session 1216).

## Memory updates worth carrying forward

No new feedback memories. Three existing rules dogfooded:
- `feedback_celery_pid_cache_blocks_restart.md` — local PA worker restart needed `pkill -9 -f celery; rm -f .celery*.pid; make celery` to pick up the new `pa_tool_schemas.py`.
- `feedback_deliverable_tool_use_append_for_large_payloads.md` — P2 findings (9.5 KB source → 7.5 KB after Rigby's multi-append; some content elided at split boundaries). Reinforces the "verify content_length matches expected" rule.
- `feedback_rigby_collaboration.md` — Chris's two interrupt corrections this session (redactor + detector) both produced live tests with empirical evidence (worker logs showing `silent_fallback=true` on 2/12 iterations) before I shipped fixes.

## Files touched this session

```
core/services/zombie_thread_monitor.py                                          (NEW, 214 lines)
core/services/td_handlers_ops.py                                                (+15 lines, zombie_thread_rate action)
core/services/pa_tool_schemas.py                                                (+11, ops_tool enum + description)
core/services/data_scrubber.py                                                  (+16, -2, phone regex tighten)
core/services/unified_pa_entrypoint.py                                          (+50, _should_trigger_silent_fallback + call-site guard)
core/tasks_agents.py                                                            (+12, record_zombie_thread wire)
core/agent_router.py                                                            (+13, record_zombie_thread wire)
core/tests/test_data_scrubber.py                                                (+26 lines, 4 new regressions)
core/tests/test_pa_silent_fallback_detector.py                                  (+67 lines, 7 new guard tests)
tests/services/test_zombie_thread_monitor.py                                    (NEW, 156 lines, 11 tests)
docs/handoffs/SESSION_1220_ZOMBIE_MONITOR_PLUS_HTTPX_INVESTIGATION.md           (NEW, this file)
00-START-NEXT-SESSION.md                                                        (Session 1221 FIRST THING rewrite)
```
