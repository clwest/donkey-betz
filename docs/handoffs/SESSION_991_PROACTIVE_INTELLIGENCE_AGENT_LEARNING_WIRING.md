---
originating_session: 991
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 991 - Wire ProactiveIntelligenceService + AgentLearningService

**Date:** February 12, 2026
**Previous Session:** 990 (PA-to-Agent Content Feedback Loop)
**Focus:** Connect two fully-built but uncalled services into the main execution paths

---

## Problem

Two substantial services (~1,300 lines combined) existed with zero callers from the main execution paths:

1. **ProactiveIntelligenceService** (`core/services/proactive_intelligence.py`, 545 lines) — fetches domain-specific intelligence (financial alerts, job opportunities, content trends, legal updates) from SpiderData, TriggerEvent, BlockchainSecurityAlert, Opportunity, MarketIntelligenceBrief. Had `format_for_prompt()` ready but was never called from the unified PA enrichment pipeline.

2. **AgentLearningService** (`core/services/agent_learning_service.py`, 778 lines) — Redis-based preference learning (styles, themes, models, quality, moods). Tracks positive/negative signals, builds adaptive context strings via `get_adaptive_context()`. `record_interaction()` was never called after agent execution; preferences were never injected into agent context.

## Changes Made

### 1. ProactiveIntelligenceService → PA Enrichment Pipeline (unified_pa_entrypoint.py)

**INTENT_ENRICHMENT_MAP** — Added `'proactive_intelligence'` to 4 intents:
- `opportunities` — surfaces matching jobs/gigs
- `stock_intelligence` — surfaces market/blockchain alerts
- `content_review` — surfaces trending content topics
- `system_overview` — surfaces cross-domain intelligence

**ENRICHMENT_CAPS** — Added `'proactive_intelligence': 500`

**Lazy property** — `proactive_intelligence_service` follows existing pattern (try/except ImportError, cached on instance)

**Enrichment handler** — New `elif` after `strategic_memory`:
- Calls `get_relevant_intelligence(message, None, 3, 24)` via `asyncio.to_thread`
- Formats with `format_for_prompt()`
- Respects relevance gate for non-direct intents

**Analytical prompt** — Added `'proactive_intelligence': 'PROACTIVE INTELLIGENCE'` to section_labels

### 2. AgentLearningService → Agent Router (agent_router.py)

**Record interaction** — After every `route()` execution (success or failure), calls:
```python
get_learning_service().record_interaction(
    user_id, agent_name, InteractionType.CREATED,
    input_data={'task': task[:500]},
    output_data={'success': ..., 'execution_time_ms': ..., 'message_preview': ...}
)
```

**Inject adaptive context** — In `_get_user_context()`, after `_apply_agent_learning`:
```python
adaptive_text = self._get_agent_learning_adaptive_context(agent_name)
if adaptive_text:
    user_context['agent_learned_preferences'] = adaptive_text
```

**Surface in gather_context()** — Propagates `agent_learned_preferences` from `user_context` into `spider_context` so agents see it.

Both new methods are fully wrapped in try/except — never break execution.

## Data Flow

```
ProactiveIntelligenceService:
  PA receives message with intent in {opportunities, stock_intelligence, content_review, system_overview}
      |
      v
  _enrich_tool_result() fires 'proactive_intelligence' service key
      |
      v
  get_relevant_intelligence(message, None, 3, 24)  [queries SpiderData, TriggerEvent, etc.]
      |
      v
  format_for_prompt()  [builds text block]
      |
      v
  _build_analytical_prompt() includes === PROACTIVE INTELLIGENCE === section
      |
      v
  LLM receives real-time domain intelligence alongside tool data

AgentLearningService:
  AgentRouter.route() executes agent
      |
      v
  _record_agent_learning_interaction()  [Redis: record usage pattern]
      |
      v
  Next execution: _get_user_context() calls _get_agent_learning_adaptive_context()
      |
      v
  get_adaptive_context(user_id, agent_name)  [Redis: build preference string]
      |
      v
  user_context['agent_learned_preferences'] -> spider_context['agent_learned_preferences']
      |
      v
  Agent prompt includes learned preferences
```

## Files Changed

| File | Change |
|------|--------|
| `core/services/unified_pa_entrypoint.py` | 6 edits: INTENT_ENRICHMENT_MAP, ENRICHMENT_CAPS, __init__, lazy property, enrichment handler, section_labels |
| `core/agent_router.py` | 4 edits: record call after execution, 2 new methods, adaptive context injection, gather_context surfacing |

## What We Did NOT Change

- No new models — ProactiveIntelligence queries existing models, AgentLearningService uses Redis
- No new Celery tasks — both run synchronously (via `asyncio.to_thread` in PA)
- No frontend changes, no migration
- Not touching AgentFeedbackService — already wired via `_apply_agent_learning`, separate system

## Verification

1. `py_compile` passes for both changed files
2. PA query "show me job opportunities" → enrichment includes `proactive_intelligence` section
3. PA query "what's trending in crypto" → proactive intelligence surfaces blockchain/market alerts
4. Agent execution via `route()` → no errors, `record_interaction()` logged to Redis
5. After multiple executions → `spider_context['agent_learned_preferences']` contains preference string
