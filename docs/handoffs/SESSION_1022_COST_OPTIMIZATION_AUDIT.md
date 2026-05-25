---
originating_session: 1022
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1022 - Cost Optimization Audit

**Date:** February 16, 2026
**PRs:** #1253, #1254, #1255, #1256, #1257, #1258

## Problems

### 1. Agent Execution Detail 500 Error (PR #1255)
`GET /api/v1/agents/execution/<uuid>/` returned 500 in production. Root cause: `views_agent_execution.py:506` accessed `execution.agent.display_name` but `core.models_unified_system.Agent` only has `name` — a different `Agent` model in `core/models/agents_registry/models.py` has `display_name`. Same bug in `views_analytics.py:2333`.

### 2. Deliverable Spam — 1,500+/day (PR #1256)
`_save_to_deliverable()` in `base_agent.py` always called `Deliverable.objects.create()` with no dedup. Intelligence desk agents (ArbitrageDetector, StockAnalystAgent, MarketMovementMonitorAgent, etc.) run every 5-15 min with identical task strings, creating identical deliverables. Audit: 9,577 deliverables, top duplicates: StockAnalystAgent (709x), ResearchAgent (639x), ArbitrageDetector (592x).

### 3. CodeGeneratorAgent Wasting $7/day (PR #1257)
Audit Remediation System (Sessions 820-823) dispatched 86 tasks to CodeGeneratorAgent, which operates in an empty sandbox with no access to the real codebase. Tasks never complete — just generate useless reports. Dream pipeline was also a complete no-op (zero DreamImplementations, zero approved dreams in 7 days) but only $0.54/day.

### 4. Conversation Duplication — 59% Duplicate Rate (PR #1258)
`run_agent_conversation` and `run_multi_agent_conversation` had zero dedup. Same `AgentKnowledgeSource` items were randomly selected every 30-60 min, producing identical conversations. Audit: 293 conversations/24h, only 121 unique (59% duplicates), wasting ~$7/day.

## Solutions

### Fix 1: display_name → name (PR #1255)
Changed `display_name` to `name` in 3 locations:
- `views_agent_execution.py:506` — execution detail endpoint
- `views_agent_execution.py:896` — monitoring_agent_detail view
- `views_analytics.py:2333` — analytics agent list

### Fix 2: Deliverable Dedup (PR #1256)
Added 4-hour dedup window to `_save_to_deliverable()`. If same `title` + `agent_name` exists within 4 hours, updates existing row instead of creating new. Cleaned up 5,850 duplicate rows on Railway (9,577 → 3,737).

### Fix 3: Pause Remediation System (PR #1257)
- Cancelled 26 stuck tasks on Railway (`assigned`/`in_progress` status)
- Commented out all 5 remediation Celery Beat schedules in `core/celery.py`
- Schedules paused: `discover-and-import-audits`, `assign-open-findings-to-agents`, `execute-remediation-tasks`, `verify-completed-fixes`, `run-autonomous-remediation-cycle`

### Fix 4: Conversation Dedup (PR #1258)
Added 6-hour dedup window to both `run_agent_conversation` and `run_multi_agent_conversation`. Before creating a conversation, checks if the same `related_knowledge` FK or same topic string was used in the last 6 hours. Skips with log message.

### Session Docs (PR #1253)
Updated session handoff documentation.

### PA Initiative Stage Visibility (PR #1254)
Fixed PA `initiative_tool` to show initiative stage information.

## Files Modified

| File | Changes |
|------|---------|
| `core/views_agent_execution.py` | PR #1255: `display_name` → `name` (2 locations) |
| `core/views_analytics.py` | PR #1255: `display_name` → `name` (1 location) |
| `core/agents/base_agent.py` | PR #1256: Deliverable dedup (4-hour window) |
| `core/celery.py` | PR #1257: Paused 5 remediation schedules |
| `core/tasks.py` | PR #1258: Conversation dedup (6-hour window, both functions) |

## Cost Impact Summary

| Issue | Daily Cost | Status |
|-------|-----------|--------|
| CodeGeneratorAgent remediation | ~$7.10/day | **FIXED** (PR #1257) |
| Conversation duplicates | ~$7/day | **FIXED** (PR #1258) |
| Deliverable duplicates | Indirect (DB bloat) | **FIXED** (PR #1256) |
| **Total daily savings** | **~$14/day (~$420/month)** | |

## 24-Hour Agent Audit Findings

| Metric | Value |
|--------|-------|
| Total executions (24h) | 439 |
| Completed | 411 (93.6%) |
| Failed | 27 (6.1%) |
| Unique agents active | 29 |
| Daily LLM cost | $13.08 |
| Weekly LLM cost | $126.38 |
| Top cost: CodeGeneratorAgent | $7.10/day (54% of total) |
| Deliverables created (24h) | 1,515 (mostly duplicates) |
| Conversations (24h) | 293 (59% duplicates) |

## Initiative Cleanup

- Deleted 32 ARCHIVED initiatives (all had zero activity)
- Promoted 4 TRIAGE initiatives to ACTIVE
- Current state: 3 ACTIVE (Stage 2, IN_REVIEW), 1 TRIAGE

## Remediation System Audit Findings

86 total remediation tasks analyzed. Valuable findings (for future reference):
- `_calculate_error_rate()` always returns 0.0 (division logic bug)
- Multiple `AgentExecution` models across different modules
- `core/tasks.py` is 12,000+ lines (needs modular decomposition)
- 1,200+ API endpoints without documentation
- External service health not monitored

These findings are preserved in `AuditRemediationTask` records and can be surfaced via HumanAttentionItem/Boardroom when remediation agents gain real codebase access.

## Key Discoveries

### Agent Model Confusion
Two `Agent` models exist:
- `core.models_unified_system.Agent` — has `name`, used by `AgentExecution` FK
- `core.models.agents_registry.Agent` — has `display_name`, used by agent registry

`AgentExecution.agent` FK points to the first one. Always use `.name` not `.display_name`.

### Dream Pipeline is a No-Op
- `score_and_promote_dreams`: processes but nothing qualifies
- `process_approved_dreams`: zero approved dreams in 7 days
- `execute_dream_implementations`: zero DreamImplementations exist
- Only $0.54/day — not worth fixing now but worth knowing

### Remediation System Can't Succeed
CodeGeneratorAgent has no access to the real codebase (runs in empty sandbox workspace). All 86 remediation attempts just generated reports or fake patches that couldn't be applied. Re-enable when agents have real workspace access.
