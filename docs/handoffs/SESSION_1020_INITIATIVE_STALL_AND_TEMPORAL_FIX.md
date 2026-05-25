---
originating_session: 1020
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1020 - Initiative Stage 2 Stall, Dedup, and Temporal Awareness

**Date:** February 16, 2026
**PRs:** #1247, #1248

## Problems

### 1. Initiative Stage 2 Stall (19/21 stuck)
All `balanced`-speed initiatives were stuck at Stage 2. Stage 1 gets a SelfBlog document at initialization (line 529-537 in `conversation_initiative_pipeline.py`), but `handle_stage_task_completion()` only saved task output to `stage.notes` — never creating a document for Stage 2+. The hard invariant from Session 916/943 (`if stage.document:`) correctly prevents approval without documents, causing a permanent stall.

### 2. Initiative Duplicates (4 "audit integrity" variants)
Of 6 initiative creation paths, only `InitiativeIntegrationService` had exact-name dedup. `AgentDream.promote_to_initiative()` and `HiveMindExecutionPipeline` had zero duplicate protection. `ConversationInitiativePipeline` lacked the circuit breaker entirely.

### 3. Conversation Date Hallucination
Agents citing "Oct 10, 2023" as current data in conversations. Individual agent execution gets date context via `build_intelligent_prompt()` and `_build_system_prompt()`, but conversation system prompts in `tasks.py` were built from scratch WITHOUT any date injection.

## Solutions

### Fix 1: Stage 2+ Document Creation (PR #1247)
In `handle_stage_task_completion()`, when a stage completes successfully and has no document, create a SelfBlog from the task output:
- Title: `"{initiative.name} - Stage {N}: {stage_label}"`
- Content: task output text
- Category: `initiative_stage`, status: `draft`
- Links to initiative and stage via FK

### Fix 2: Dedup + Circuit Breaker (PR #1247)
- **`AgentDream.promote_to_initiative()`**: Added `find_similar_initiative()` check — reuses existing initiative instead of creating duplicate
- **`InitiativeIntegrationService`**: Added similarity dedup before circuit breaker (had exact name match only)
- **`HiveMindExecutionPipeline`**: Added `can_create_initiative()` circuit breaker (was completely missing)
- **`ConversationInitiativePipeline`**: Added circuit breaker (was missing)
- **Manually archived** 5 duplicate initiatives on Railway (21 → 16)

### Fix 3: Timeout Tuning (PR #1247)
- OpenAI client timeout: 120s → 60s (prevents agent tool loop compounding)
- Cleanup threshold: 120min → 45min (just past 30min hard limit)
- Cleanup frequency: every 30min → every 15min

### Fix 4: Temporal Awareness for Conversations (PR #1248)
Added `_conversation_temporal_context()` helper in `tasks.py`:
```
TEMPORAL AWARENESS:
- Today's date: February 16, 2026
- Current year: 2026
- All analysis must be current and relevant to February 2026
- DO NOT treat data from 2024 or 2025 as "current" — note its age
```
Injected into all 4 conversation system prompt types:
1. `run_agent_conversation` 2-agent prompt
2. `run_multi_agent_conversation` panel prompt
3. Spider-triggered conversation prompt
4. Project-focused conversation prompt

## Files Modified

| File | Changes |
|------|---------|
| `core/services/conversation_initiative_pipeline.py` | Stage 2+ document creation, circuit breaker |
| `core/models_unified_system.py` | Dedup in `promote_to_initiative()` |
| `core/services/initiative_integration_service.py` | Similarity dedup |
| `core/services/hivemind_execution_pipeline.py` | Circuit breaker |
| `core/agents/base_agent.py` | OpenAI timeout 120→60s |
| `core/celery.py` | Cleanup threshold 120→45min, frequency 30→15min |
| `core/tasks.py` | `_conversation_temporal_context()`, injected into 4 prompt types |

## Verification on Railway

- PR #1248 deployed: `_conversation_temporal_context` function importable
- PR #1247 deployed: all code merged to main, auto-deployed
- 15 conversations in last hour, 41 executions, 0 failures
- Initiatives: 16 total (14 at Stage 2, 2 at Stage 1) — Stage 2 fix needs new stage tasks to trigger
- Agent failures: 25/day (7 AudioAgent quota, rest scattered), 0 timeout-related, 0 stuck

## Key Gotchas

- **Stage field**: Use `stage` (NOT `stage_number`) when querying `InitiativeStage`
- **Initiative dedup**: Uses Jaccard keyword similarity at 0.6 threshold via `find_similar_initiative()` in `initiative_circuit_breaker.py`
- **6 initiative creation paths**: InitiativeIntegrationService, AgentDream.promote_to_initiative(), HiveMindExecutionPipeline, ConversationInitiativePipeline, AutonomousActionExecutor, create_initiative_from_deliverables()
