---
originating_session: 970
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 970 — Surgical Moves Verification + ToolCallRecord Activation + Attention Coverage

**Date:** February 8, 2026
**PRs:** #977 (Surgical Moves verification + visibility), #978 (ToolCallRecord activation + attention coverage)
**Status:** COMPLETE — Both PRs deployed to Railway, ToolCallRecord verified populating (6 rows in first 3 minutes)

---

## What Was Done

### Phase 5.1: Surgical Moves Verification + Visibility (PR #977)

Sessions 960-963 implemented Surgical Moves Phases 0-3 (doc tracking, contract persistence, decision enforcement, strategic memory, evidence packs, session traces). The code existed and tests passed, but there was no way to verify end-to-end without reading logs. This phase made it visible, testable, and demoable.

#### Deliverable A: Management Command `verify_surgical_moves`

**New file:** `core/management/commands/verify_surgical_moves.py` (~244 lines)

- `--mode=smoke` (default): Runs a real 4-turn debate via `ConversationOrchestrator.generate_conversation()`, then queries all artifacts and prints a structured pass/warn/fail verification report
- `--mode=report-only`: Queries the latest completed `DeliberationSession` without running LLM
- `--session-id=<uuid>`: Check a specific session
- Checks: contract serialization, decision enforcement, doc read tracking, session persistence, turn count, contract count, evidence pack, session trace, memory retrievals
- Local verification: 7 PASS, 2 WARN, 0 FAIL

#### Deliverable B: PA Tool `surgical_moves_status_tool`

**Modified:** `core/services/tool_dispatcher.py` (+104 lines), `core/services/unified_pa_entrypoint.py` (+28 lines)

- New handler queries `DeliberationSession`, `DeliberationTurn`, `ContractRecord` within configurable time window
- Returns structured dict with runs array containing session_id, objective, status, turn_count, contract_count, contracts, decision_verdict, evidence_stats
- Intent routing: "surgical moves", "deliberation status", "deliberation sessions", "verification report", "moves status", "what deliberations"
- Aliases: `deliberation_status`, `verification_status`, `moves_status` -> `surgical_moves_status`
- Payload builder: action (summary/detailed), hours extraction, UUID session_id extraction

#### Deliverable C: API Endpoint + Frontend Panel

**Modified:** `core/views_deliberation.py` (+172 lines), `core/urls.py` (+3 lines), `frontend/src/pages/workspace/tabs/OrchestrationTab.tsx` (+240 lines)

- `GET /api/deliberation/sessions/<uuid>/verification-report/` — enriched JSON with session, turns, contracts, evidence_stats, trace_stats, checks array
- `SurgicalMovesPanel` in Orchestration Monitor sub-tab — lists 5 most recent completed sessions with turn/contract badges
- `VerificationReportModal` — click a session to see full verification report with pass/warn/fail checks, contract details, evidence stats, raw JSON toggle

### Production System Review + Gap Analysis

Verified the SystemIntelligenceAgent report against Railway production database. Key findings:
- 549 stale suggestions (report said 548 — accurate)
- Celery running (48,543+ periodic task runs), results in Redis not DB (intentional config, not a bug)
- ToolCallRecord empty because `_execute_and_record_tool_call()` defined but never called by any agent
- 47 completed DeliberationSessions, 87 ContractRecords
- 18 SignalClusters (8 active, 8 detecting, 2 triggered)

### Gap C Fix: ToolCallRecord Activation (PR #978)

**Modified:** `core/agents/base_agent.py` (+27 lines)

**Problem:** `_execute_and_record_tool_call()` existed in base_agent.py since Session 861 but had **0 callers** — all 50+ agent subclasses called `_execute_tool_call()` directly, bypassing recording. ToolCallRecord table was permanently empty.

**Solution:** Added `__init_subclass__` hook to BaseAgent that automatically wraps every subclass's `_execute_tool_call` method with recording logic at class definition time. When any agent executes a tool call:

1. Times the execution
2. Calls the original method normally
3. In a `finally` block, records to ToolCallRecord via `_record_tool_call()`
4. Recording failures silently caught — can never break agent execution

**Zero agent files touched.** All 50+ agents now have audit trail automatically.

**Production verification:** 6 ToolCallRecord rows appeared within 3 minutes of deploy:
- ResearchAgent: `web_search` (864ms), `spider_query` (272ms), `analyze_trends` (201ms), `reddit_search` (636ms)
- SystemIntelligenceAgent: `get_system_attention` (234-238ms)

### Scoped Gap A: Expanded Attention Coverage (PR #978)

**Modified:** `core/services/system_state_aggregator.py` (+~150 lines)

Added 2 new attention sections to `SystemStateAggregator.get_attention_items()`:

1. **`_get_deliberation_items()`** — Surfaces:
   - Stuck deliberation sessions (in_progress/pending for >1 hour)
   - Completed sessions with no contracts (decision enforcement gap)

2. **`_get_signal_cluster_items()`** — Surfaces:
   - Stale active clusters (not detected in 48h)
   - High-strength untriggered clusters (strength >= 0.7, status=detecting, count >= 3)

Both wired with try/except for graceful degradation. Import: `SignalCluster` is in `core.models_signal_intelligence` (not `models_unified_system`). Field: use `detected_at` (not `updated_at`).

---

## Files Modified

| # | File | Action | Lines |
|---|------|--------|-------|
| 1 | `core/management/commands/verify_surgical_moves.py` | NEW | ~244 |
| 2 | `core/services/tool_dispatcher.py` | EDIT | +104 (register + handler) |
| 3 | `core/services/unified_pa_entrypoint.py` | EDIT | +28 (intent + aliases + detect + payload) |
| 4 | `core/views_deliberation.py` | EDIT | +172 (verification-report endpoint) |
| 5 | `core/urls.py` | EDIT | +3 (import + URL pattern) |
| 6 | `frontend/src/pages/workspace/tabs/OrchestrationTab.tsx` | EDIT | +240 (panel + modal) |
| 7 | `core/agents/base_agent.py` | EDIT | +27 (__init_subclass__ wrapper) |
| 8 | `core/services/system_state_aggregator.py` | EDIT | +150 (2 new attention sections) |

**Total: 1 new file, 7 edits, ~970 lines**

## Key Decisions

- **`__init_subclass__` over rename-swap**: Wrapping at class definition time avoids touching 50+ agent files. The `_orig` default arg captures the original method per-class, avoiding closure bugs.
- **Recording in `finally` with bare `except: pass`**: Recording must never break agent execution. If ToolCallRecord model has issues, agents continue working.
- **`SignalCluster.detected_at`** not `updated_at`: Model has no `updated_at` field. Discovered via FieldError on first test.
- **Untriggered signal threshold >= 3**: Only surface as opportunity when multiple high-strength clusters accumulate, not for a single one.
- **Deliberation stuck threshold = 1 hour**: Conversations typically complete in minutes. 1h is generous enough to avoid false positives.

---

## What Could Come Next

1. **ToolCallRecord Analytics** — Now that data is flowing, build dashboards: tool usage by agent, latency percentiles, error rates, most-used tools
2. **Celery Result Backend Switch** — Consider switching from Redis to `django-db` backend if Celery task result visibility is needed (currently intentionally Redis)
3. **Attention Health Metric** — Derived `attention_pressure_score = f(stale_count, pending_actions, failure_rate)` as a single dashboard number
4. **Initiative Staleness Check** — Add `_get_initiative_items()` to SystemStateAggregator for initiatives with no activity in 7+ days
5. **FailureSignature Wiring** — The diagnostic pipeline (Session 856) has FailureSignature table but 0 records in production — may need activation similar to ToolCallRecord
