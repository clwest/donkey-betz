# Session 1206 — Layer 1 telemetry fix + Wakeup Week cascade (5 PRs)

**Status:** Closed clean. **5 PRs merged.** All live-verified in local before merge.
**Date:** 2026-06-22
**Active conversation:** `pa-234a75abfe374695` — Session 1206 Layer 1 Telemetry Fix arc (also carries Wakeup Week mid-session expansion). Prior thread `pa-76aa5b61d0764d11` (Session 1205 evidence-card pipeline) retired.
**Prior session:** [`SESSION_1205_EVIDENCE_PIPELINE_PLUS_CAPABILITY_AUDIT.md`](./SESSION_1205_EVIDENCE_PIPELINE_PLUS_CAPABILITY_AUDIT.md).
**Next session entry point:** Session 1207 — pick from carryover queue. Time-gated: Phase B.1 24h watch fires `2026-06-23 ~14:48 UTC`, Session 1206 24h watch fires `2026-06-23 ~23:35 UTC`. Natural follow-ups from this session: lint-rule (`180f4e9f-…`) and workspace_id hallucination root-cause trace (`96b6a72a-…`, P0).

## TL;DR

Single-arc session that closed Session 1205 audit finding `65f1299f-…` (Telemetry blind spot — direct-constructor agent paths bypass `AgentExecution`).

**Recon surprise that changed the fix shape:** the START doc sketched the fix as "add row creation to `BaseAgent.execute()` with idempotency guard." But `execute()` at `core/agents/base_agent.py:1089` is `@abstractmethod` — a body cannot live there. Re-routed through Rigby for the architectural call: A (rename abstract to `_execute_impl`, 83 subclass renames) vs B (new concrete `run()` wrapper, migrate 7 known bypass callsites) vs C (wrap bypass callsites with existing `AgentExecutionTracker`, no `BaseAgent` change). **Rigby picked B** + follow-up lint rule to prevent future drift.

Implemented B. Live-verified in local: dispatched `_impl_market_intelligence_scan` → 3 new `AgentExecution` rows with `input_source='BaseAgent.run'`, statuses reflecting real agent outcomes (2 failed with the agents' actual error messages, 1 completed). **Layer 4 cascade confirmed** — `agent_execution_bridge` fired on the new `PredictionMarketAnalyst` row (`20b939f4-…`), triggering the learning orchestrator. Idempotency guard verified separately: `_execution_record_id` preset → delta=0 rows.

Plus minor: pa_local.sh thread pin updated to the new Session 1206 conversation; audit deliverable `65f1299f-…` flipped to `completed` with resolution evidence appended; Layer 1 dashboard `7d221aa4-…` annotated "pending next beat cycle for live confirmation"; follow-up deliverable `180f4e9f-…` filed for the CI lint rule.

## Session Manifest

### PRs merged

| # | Arc | Title | Files | Verified |
|---|---|---|---|---|
| **#2461** | Arc A: Telemetry fix | fix(session-1206): BaseAgent.run() closes Layer 1 telemetry blind spot | 7 (1 base_agent.py + 5 callsites + 1 pa_local.sh) | ✅ live (3 new AgentExecution rows, Layer 4 cascade confirmed, idempotency guard verified) |
| **#2462** | Arc B: TheOdds loud-fail | fix(session-1206): TheOddsSpider loud-failure pattern — no more lying api_status rows | 1 | ✅ live (returns 1 fetch_failure row with circuit_breaker_engaged=True under dead key) |
| **#2463** | Arc C: Finding B1 | fix(session-1206): tasks_agents writes canonical+legacy output_data shapes additively | 1 | ✅ live (PredictionMarketAnalyst execution `9be19cef-…` has all 7 keys) |
| **#2464** | Arc C: Finding B3 | fix(session-1206): BLOCKED detector requires structural markers, not inline prose | 1 | ✅ 7-case test matrix (3 false-positives rejected, 4 true-positives extracted) |
| **#2465** | Arc C: Finding B2 | fix(session-1206): workspace_id validation guardrail at deliverable_factory entry | 1 | ✅ live (fake UUID → WARN + fallback to real DBZ workspace, deliverable `71a2b6bf-…` created without FK violation) |

**Arc A** was the planned session work. **Arc B** + **Arc C** emerged mid-session from a Rigby check-in — she'd kicked off Wakeup Week (manual agent dispatches) using the new BaseAgent.run() telemetry and found a cluster of downstream bugs that were previously invisible because no AgentExecution rows existed. **The telemetry fix is what made these visible.**

### Deliverables touched on Initiative `29154d73-06a5-4630-abb4-3412cbdca5c5` (Platform Capability Audit)

| ID | Action | Note |
|---|---|---|
| `65f1299f-…` | **Resolution evidence appended + status flipped completed** | PR #2461 link + 3 verification row IDs + Layer 4 cascade confirmation; `content_tool action=content_complete` per Session 1184 status-flip pattern |
| `180f4e9f-…` | **NEW (filed)** | "Lint rule: block .execute( outside core/agents/". Tagged `session-1206-followup`. Workspace=DBZ. |
| `7d221aa4-…` | Annotated | Layer 1 dashboard appended Session 1206 note: sports agents flip "pending next beat cycle for live confirmation". |
| `96b6a72a-…` | **NEW (filed)** | **P0** — "Workspace_id hallucination source — root cause trace". Mitigated by PR #2465; root cause open. Tagged `session-1206-followup`, `workspace-integrity`, `P0`, `root-cause-open`. |

Initiative is now at **12 deliverables** (was 10 end-of-Session-1205; +1 lint rule + +1 workspace hallucination trace).

## Arc B: TheOdds loud-failure (PR #2462)

**Trigger.** During Rigby check-in, the new telemetry surfaced GamePredictor failing with `"TheOddsSpider returned no events"` against a spider that the `spider_status_tool` reported as `active` with 86 runs in 7d. Investigation: the API key (Chris's billing-lapsed account) returns HTTP 401; Session 1083 circuit breaker engages correctly; but `fetch_data` was then falling back to the requested-sports list and persisting `api_status` rows claiming `sports_fetched: 48, futures_fetched: 11` — **materially lying about work having happened.**

**Fix.** On `_get_active_sports()` empty (auth or upstream failure), emit `data_type='fetch_failure'` row with `reason`, `error_summary`, `events_fetched=0`, `circuit_breaker_engaged`. No fallback to requested-sports list. Healthy `api_status` rows now include explicit `events_fetched` count. New `_build_failure_row()` helper. Downstream `tasks_financial.py:2175` already guards with `if not game_id` — `fetch_failure` rows (no event_id) filtered correctly. No consumer change needed.

**Chris-owned action item:** renew `THE_ODDS_API_KEY` when billing permits. Independent of this PR — the spider now signals honest outage either way.

**Related:** closes Session 1205 finding `2de3d8d6-…` ("theodds spider returns 0 events"). Root cause confirmed as billing-lapse, not seasonal/code.

## Arc C: Finding B (output_data shape + BLOCKED detector + workspace_id validation)

**Trigger.** Same Rigby check-in. Wakeup Week dispatches showed `ContentWriterAgent` and `MarketIntelligenceCoordinator` completing successfully with `_full_size_bytes: 11124` / `418992` output_data blobs but Rigby's `execution_history_tool` reported `message: "", result_preview: "", data: {}, deliverables: []`.

Deep dive surfaced **three distinct root causes**, each shipped as a separate PR:

### B1 — Non-canonical output_data shape (PR #2463)

`core/tasks_agents.py:2405` (the celery task path) overwrote `agent_router._complete_execution`'s canonical `{result_preview, data, message, error, tool_calls}` shape with non-canonical `{content, metadata}`. Downstream readers (execution_history_tool, deliverable_factory, frontend renderers) expected canonical, saw empty.

**Fix.** Write BOTH shapes additively. Old readers (Session 1181 PR5 artifact_pointers, `views_platform_command:532`) keep working; new canonical keys land alongside.

### B3 — BLOCKED detector matches inline prose (PR #2464)

Session 1088 `_detect_blocked_content` used a permissive regex (`BLOCKED\s*(?:ON)?[:\s]*(.{10,150})` case-insensitive) that matched the literal word "BLOCKED" in legitimate prose — including ContentWriterAgent's wakeup document containing `"NOT-ROUTABLE/REROUTED/BLOCKED, producing a practical readiness map..."` (BLOCKED as one enum value in a classification rubric).

**Fix.** Strict structural markers only: `**BLOCKED ON:**`, `[BLOCKED: reason]`, or line-anchored `^BLOCKED ON:` / `^BLOCKED:`. Case-SENSITIVE.

### B2 — Hallucinated workspace_id kills deliverable saves (PR #2465)

ContentWriterAgent's deliverable save died on FK constraint with `workspace_id=b4503364-9323-4e3e-b600-b7a5aa85fa5d` — a UUID that doesn't exist. Real DBZ is `b4503364-2573-4401-9e28-61a739e0ce50`. Same prefix, different suffix: classic LLM hallucination pattern (model matched first 8 chars of a remembered UUID then fabricated the rest).

**Defensive guardrail.** Validate `workspace_id` existence at `create_deliverable` entry. If invalid: emit `WARNING` with structured fields (`workspace_id_invalid`, `workspace_id_received`, `workspace_id_fallback_used`), set `workspace_id=None`, let existing fallback machinery resolve to user.active_workspace or Unassigned bucket. Fail-OPEN on validation hiccups.

**Out of scope:** root cause trace (which LLM/dispatcher is fabricating UUIDs). Filed as P0 deliverable `96b6a72a-…` with suspected call chain + grep targets + verification metric (WARN volume → zero in 24h post-fix). The guardrail stops artifact loss now; root cause stays open.

## Behavioral invariants — what's now true post-merge

1. **`BaseAgent.run()` is the canonical entry for direct-constructor agent paths.** Writes `AgentExecution` row at `core_agentexecution` (the canonical table per Session 1084 lines 993-1005 — the deprecation docstring at `core/models_unified_system.py:884` was already debunked there). Status transitions: `in_progress` → `completed`/`failed`. `execution_time_ms`, `error_message`, `completed_at` all populated.
2. **Idempotency is opt-out, not opt-in.** `context['_execution_record_id']` set → `run()` short-circuits the row write and just delegates to `execute()`. Wrappers that already manage their own record (router, `AgentExecutionTracker`, `SyncAgentExecutor`) must set this key before calling `.run()` to avoid double-writes. Today they don't call `.run()` at all (they call `.execute()`) so the guard is forward-compatible insurance.
3. **Telemetry is fail-open.** Missing `Agent` DB row → `WARNING` log + `execute()` still runs. DB hiccup on row create → `WARNING` log + `execute()` still runs. Failure on status update → `logger.exception` + return value still returned. Telemetry never blocks agent work.
4. **7 known bypass callsites migrated.** `core/tasks_financial.py` `_impl_market_intelligence_scan` (×3), `core/services/sports_betting_coordinator.py`, `core/views_odds_sports.py`, `core/services/discord_bot.py` `/arb` cog, `core/tasks_misc.py` arb-notify task. All `.execute(...)` → `.run(...)`. No other behavioral change.
5. **Layer 4 cascade now fires on these paths.** `agent_execution_bridge.AgentExecutionLearningLoop` triggers on `AgentExecution` row create signal. Pre-fix: 0 signals from sports agents. Post-fix: 1 signal per agent execution (verified on `20b939f4-…`).

## Rollback levers (per change)

| Lever | Action | Effect |
|---|---|---|
| **Soften: skip row write at one callsite** | Revert that specific `.run(` → `.execute(` line | Restores the bypass for that one callsite; other 6 still write rows. |
| **Soften: skip ALL telemetry without revert** | `git checkout main -- core/tasks_financial.py core/services/sports_betting_coordinator.py core/views_odds_sports.py core/services/discord_bot.py core/tasks_misc.py` | Keeps `BaseAgent.run()` available for future callers but reverts all 7 callsite migrations. |
| **Full revert** | `git revert e7613392` (the fix commit; the chore commit `9563c195` is a config change, leave it) | Removes `BaseAgent.run()` and all callsite migrations. Layer 1 telemetry blind spot returns. |
| **Disable telemetry write per-call** | Caller sets `context['_execution_record_id'] = 'noop-' + uuid` | `run()` skips the row write and just delegates to `execute()`. Useful if a specific path is producing noisy/spurious telemetry. |

## 24h watch checklist (fires 2026-06-23 ~23:35 UTC)

**Invariants to verify:**

1. **Sports agents land rows on every `_impl_market_intelligence_scan` beat fire.**
   ```bash
   # Beat fires every 2h; should see 3 new rows per cycle (1 per sports agent)
   USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
   from core.models_unified_system import AgentExecution
   from datetime import timedelta
   from django.utils import timezone
   cutoff = timezone.now() - timedelta(hours=24)
   for n in ['SportsOddsAnalyst', 'ArbitrageDetector', 'PredictionMarketAnalyst']:
       c = AgentExecution.objects.filter(agent__name=n, created_at__gte=cutoff).count()
       print(f'{n}: {c} rows in last 24h (expect 12 if beat fires every 2h)')
   "
   ```
2. **No double-writes.** No callsite should produce >1 row per dispatch.
   ```bash
   # Per-task duplicate check (group by task text + created_at minute bucket)
   USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
   from core.models_unified_system import AgentExecution
   from datetime import timedelta
   from django.utils import timezone
   from django.db.models import Count
   cutoff = timezone.now() - timedelta(hours=24)
   dupes = (AgentExecution.objects
       .filter(agent__name__in=['SportsOddsAnalyst','ArbitrageDetector','PredictionMarketAnalyst'],
               created_at__gte=cutoff)
       .values('agent__name', 'task')
       .annotate(c=Count('id'))
       .filter(c__gt=1))
   for d in dupes:
       print(f'POSSIBLE DUPE: {d}')
   print('(no output above = no duplicates)')
   "
   ```
3. **No telemetry-write failures degrading agent work.** Grep workers for the new WARN logs.
   ```bash
   grep "BaseAgent.run: failed" celery*.log
   grep "BaseAgent.run: no Agent DB row" celery*.log
   ```

**Rollback trigger conditions:**
- Sports agents stop returning results post-merge (telemetry blocking work)
- Duplicate rows per dispatch (idempotency guard misfire)
- Agent table `total_executions` metric drift (out of scope for this PR — the existing `AgentExecutionTracker` updates that field; `BaseAgent.run()` intentionally does NOT, to keep scope minimal. If it matters, file as follow-up.)

## Open / followup

- **PR #2461** — verify CI, merge when green. Workers will need a restart post-merge for the imported code change to propagate (`pkill -9 -f celery; rm -f .celery*.pid; make celery`) — `tasks_financial.py` is celery-task-imported per `feedback_new_shared_task_needs_worker_restart.md` case 2.
- **Lint rule follow-up (`180f4e9f-…`)** — block `\.execute\(` outside `core/agents/`. Implementation options: pre-commit hook scanning staged diffs / ruff custom rule / `scripts/verify_repo_guardrails.py` extension / dedicated `manage.py` command run in CI. Allowlist: `core/agents/`, tests, `core/agent_execution_wrapper.py`, `ai_core/agents/sync_executor.py`.
- **`AgentExecution` model "DEPRECATED" docstring at `core/models_unified_system.py:884`** — already debunked by Session 1084 (lines 993-1005). Should be removed in a docs PR, but no functional change. Out of scope for this fix.
- **Agent metrics update** (`total_executions`, `successful_executions`) — `AgentExecutionTracker` updates these post-execution; `BaseAgent.run()` intentionally does not. If parity matters, follow-up to add it (would also benefit from `F()` expressions to fix the existing race condition in the tracker — same code, different concern).

## Worker freshness note

Local workers started Mon Jun 22 17:22; this fix sits in the working tree but workers are still on pre-PR code. The local verification path (`_impl_market_intelligence_scan` dispatched via `manage.py shell`) loaded the new code via fresh Python process, NOT via worker. Post-merge, workers MUST be restarted to pick up the `tasks_financial.py` change. Daphne does not need restart (no HTTP path touched).

## Architecture note for future readers

The "direct-constructor bypass" pattern this PR closes is one of three known wiring gaps for `AgentExecution` telemetry:
1. **Direct constructor + `.execute()`** — closed by this PR via `.run()` wrapper + 7 callsite migrations.
2. **PA tool dispatch via `tool_dispatcher.execute()`** — uses a different path (`tool_dispatcher` doesn't go through `BaseAgent`); writes happen via the `ToolCallRecord` machinery separately. NOT addressed here.
3. **Workflow execution** — `workflows/views.py:325` creates mock execution records; out of scope for this fix.

Future audit pass: confirm Layer 1 dashboard `7d221aa4-…` shows the sports agents transition from UNTESTED → CONFIRMED WORKING after the next beat cycle, AND confirm Layer 2 PA tools dashboard `bb1e0a98-…` numbers reconcile with whatever `ToolCallRecord`-based telemetry exists.
