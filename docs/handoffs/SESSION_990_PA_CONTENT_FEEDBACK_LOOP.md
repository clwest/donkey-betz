---
originating_session: 990
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 990 - PA-to-Agent Content Feedback Loop

**Date:** February 12, 2026
**Previous Session:** 989 (Production Verification & Field Name Fixes)
**Focus:** Close the feedback loop between PA content review decisions and originating agents

---

## Problem

When the PA publishes, archives, or revises agent-created content, that decision vanished -- the originating agent never learned what the PA thought. The infrastructure existed (AgentMemory, UserAgentLearning, FeedbackLoopEngine, context injection) but the wiring to close the loop was missing.

## Changes Made

### 1. `_record_content_feedback()` Method (tool_dispatcher.py)

New method on ToolDispatcher (~50 lines) that records PA review outcomes:

- Creates `AgentMemory` record: `memory_type='feedback'`, `tags=['pa_review', 'action_{action}']`, `safety_class='approved'`
- Valence: publish=positive, archive=negative, revise=neutral
- Outcome: publish=success, archive=failure, revise=partial
- Updates `UserAgentLearning` for per-user personalization (publish→`record_success()`, archive→`record_failure()`)
- Fully wrapped in try/except -- never breaks PA response

### 2. Wired to 3 Existing Action Handlers (tool_dispatcher.py)

- **Publish** (~line 1790): Records feedback for `deliverable.agent_name` with "quality met standards" summary
- **Archive** (~line 1830): Records feedback with archive reason in summary
- **Revise** (~line 2300): Records feedback for `ContentWriterAgent` with before/after quality/structure scores and focus areas

### 3. PA Review Feedback Query (feedback_loop_engine.py)

Added step 2b in `get_feedback_for_agent()` (~20 lines):

- Queries `AgentMemory` for agent's `pa_review`-tagged feedback (last N days, max 5 records)
- Adds `feedback['pa_review_feedback']` = list of `{title, content, valence, created_at}`
- Adds `feedback['pa_review_summary']` = e.g., "5 PA reviews: 3 published, 1 archived, 1 revised"

### 4. Context Extraction (agent_router.py)

Added 3 lines after existing `feedback_context` extraction:

- `spider_context['pa_content_feedback']` = PA review history
- `spider_context['pa_review_summary']` = one-liner summary

## Data Flow

```
PA reviews content (publish / archive / revise)
        |
        v
_record_content_feedback()
        |
        +-> AgentMemory (type='feedback', tags=['pa_review'])
        |       |
        |   conversation_orchestrator._get_agent_knowledge()  [existing]
        |       |
        |   Agent sees PA feedback in multi-agent conversations
        |
        +-> UserAgentLearning.record_success() / record_failure()
        |       |
        |   Per-user personalization improves  [existing]
        |
        +-> feedback_loop_engine.get_feedback_for_agent()
                |
            agent_router.gather_context()  [existing]
                |
            spider_context['pa_content_feedback']
                |
            Agent sees PA review history in EVERY execution
```

## Files Changed

| File | Change |
|------|--------|
| `core/services/tool_dispatcher.py` | New `_record_content_feedback()` method + 3 call sites |
| `core/services/feedback_loop_engine.py` | PA review query in `get_feedback_for_agent()` |
| `core/agent_router.py` | Extract PA feedback into `spider_context` |
| `docs/topics/content-pipeline.md` | Documented PA-to-Agent feedback loop |
| `docs/topics/agent-system.md` | Updated context injection description |
| `docs/topics/personal-assistant.md` | Updated content_review_tool actions |

## Models Used (all existing, no migration needed)

- `AgentMemory` (`core/models_unified_system.py`) -- stores PA feedback as agent memory
- `UserAgentLearning` (`core/models_unified_system.py`) -- per-user learning signal
- `Agent` (`core/models_unified_system.py`) -- FK lookup by name

## Verification

1. All 3 files compile without errors
2. PA publishes Deliverable -> AgentMemory created with valence='positive'
3. PA archives Deliverable -> AgentMemory created with valence='negative' + archive reason
4. PA revises blog -> AgentMemory created with valence='neutral' + before/after scores
5. Agent execution -> `spider_context` includes `pa_content_feedback` and `pa_review_summary`
