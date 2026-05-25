---
originating_session: 994
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 994B: Initiative Pipeline Fixes

**Date:** February 12, 2026
**Focus:** Stop initiative bleeding — enforce circuit breaker, add quality gate, TRIAGE status, activity tracking

## Problem

Production PA report showed 158 active initiatives, ALL with `last_activity_at=None`, 64 created in last 24 hours despite the circuit breaker being tripped (158 >= 50 threshold). The circuit breaker existed but `InitiativeIntegrationService` bypassed it entirely. Initiatives were created from every conversation regardless of whether they contained actionable content.

## Changes

### 1. Circuit Breaker Enforcement (initiative_integration_service.py)
- Split `get_or_create_initiative()` into: check existing (always allowed) + circuit breaker + create
- Added `InitiativeCreationBlocked` exception class
- Updated `DecisionExtractor` to catch the new exception
- Updated `link_action_to_initiative()` to catch the new exception

### 2. Quality Gate (conversation_initiative_pipeline.py)
- Added `_quality_gate()` method to `ConversationInitiativePipeline`
- `EXPLORE_PATTERNS`: 20 patterns that indicate exploratory/non-actionable conversations
- `ACTION_VERBS`: 22 verbs that indicate initiative-worthy objectives
- Gate checks: explore pattern count, action verb presence, content substance (1000+ chars), topic prefix

### 3. QUEUED_FOR_TRIAGE Status (models_document_registry.py)
- Added `TRIAGE = 'TRIAGE', 'Queued for Triage'` to Initiative.Status choices
- ALL auto-creation paths now use TRIAGE instead of ACTIVE:
  - `InitiativeIntegrationService.get_or_create_initiative()`
  - `ConversationInitiativePipeline.process()`
  - `HiveMindExecutionPipeline` initiative creation
  - `AgentDream.promote_to_initiative()`
- Circuit breaker counts TRIAGE in backlog
- PA `update_status` action now includes TRIAGE as valid status
- Migration: `0238_session_994_initiative_triage_status`

### 4. Intent-Aware Spawning
- Implemented as part of quality gate — exploratory topics (explore, trending, brainstorm, etc.) are filtered out before initiative creation

### 5. Stage 1 Activity Tracking (last_activity_at)
- Added `initiative.update_activity()` calls in 4 key places:
  - `InitiativeStage.approve()` — on every stage approval
  - `generate_initiative_stage_document` task — when stage docs are created
  - `handle_stage_task_completion()` — when any stage work completes
  - `process_initiative_auto_progression` task — when stages auto-progress
- Previously only called from 2 conversation-related places, causing ALL initiatives to show `last_activity_at=None`

### 6. PA Flow Metrics (tool_dispatcher.py)
- Added `triage` count to `stats` action return
- New `flow_metrics` action with: creation rate (24h/7d), backlog (triage/active/no-activity), stage distribution, circuit breaker status, completions
- Updated `update_status` valid statuses to include TRIAGE
- Updated error message to list all valid actions

## Files Changed

| File | Changes |
|------|---------|
| `core/services/initiative_integration_service.py` | Circuit breaker enforcement, TRIAGE status, InitiativeCreationBlocked exception |
| `core/services/decision_extractor.py` | Catch InitiativeCreationBlocked |
| `core/services/conversation_initiative_pipeline.py` | Quality gate, TRIAGE status, update_activity() call |
| `core/services/hivemind_execution_pipeline.py` | TRIAGE status |
| `core/services/initiative_circuit_breaker.py` | Count TRIAGE in backlog |
| `core/services/tool_dispatcher.py` | flow_metrics action, triage in stats, TRIAGE in valid_statuses |
| `core/models_document_registry.py` | TRIAGE status choice, update_activity() in approve() |
| `core/models_unified_system.py` | TRIAGE status in promote_to_initiative() |
| `core/tasks.py` | update_activity() in stage doc gen + auto-progression |
| `core/migrations/0238_session_994_initiative_triage_status.py` | Add TRIAGE to status choices |

## Expected Impact

- **Circuit breaker actually works**: No more bypassing via InitiativeIntegrationService
- **Fewer junk initiatives**: Quality gate filters exploratory conversations
- **Visibility**: TRIAGE status distinguishes auto-created from human-reviewed
- **Activity tracking**: `last_activity_at` actually reflects work, enabling proper staleness detection
- **PA metrics**: `flow_metrics` action gives real-time pipeline health
