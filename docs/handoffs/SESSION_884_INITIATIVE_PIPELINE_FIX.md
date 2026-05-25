---
originating_session: 884
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 884: Initiative Pipeline Fix & Circuit Breaker

**Date:** January 30, 2026
**Status:** Complete

## Problems Found

The Initiative Pipeline was completely broken due to multiple issues:

### 1. Worker Saturation
- 288 initiatives accumulated, none making progress
- Celery workers were blocked by 4 long-running `intelligence.tasks.scan_spider_opportunities` tasks
- All 4 concurrency slots on `celery-default` were occupied for 30+ minutes

### 2. No Rate Limiting
- Dream/thinking cycles kept creating initiatives even when backlog existed
- No mechanism to pause creation when overwhelmed

### 3. LLM Integration Broken (Critical)
- **Syntax error** in `agent_llm_integration.py` (broken indentation)
- Error: `expected 'except' or 'finally' block (agent_llm_integration.py, line 79)`
- This prevented ALL agents from making LLM calls

### 4. GPT-5 Parameter Mismatch
- Code used `max_tokens` but GPT-5 requires `max_completion_tokens`
- Code used `temperature` but GPT-5 reasoning models don't support it
- Token limit was too low (800) for reasoning - needs 6000+

## Solutions Implemented

### PR #596: Route Intelligence Tasks to Long-Running Queue
```python
CELERY_TASK_ROUTES = {
    'intelligence.*': {'queue': 'long_running'},  # Prevents blocking default queue
    ...
}
```

### PR #597: Initiative Circuit Breaker
New service `core/services/initiative_circuit_breaker.py`:
- Auto-pauses initiative creation when backlog exceeds threshold (default: 100)
- Manual pause/resume via API or environment variable
- Checks added to all 3 creation points:
  - `ConversationInitiativePipeline.process()`
  - `HiveMindExecutionPipeline._create_initiative_from_feature()`
  - `AgentDream.promote_to_initiative()`

**API:** `GET/POST /api/initiatives/circuit-breaker/`

### PR #598: Fix Circuit Breaker Pause Function
Changed from non-existent `SystemSetting` to `SystemConfiguration` model.

### PR #599: Initiative Cleanup Endpoint
New endpoint `POST /api/initiatives/cleanup/`:
- Archive or delete stuck initiatives
- Configurable completion threshold
- Dry-run/preview mode

### PR #601: Fix LLM Integration Syntax Error
Fixed broken indentation in `ai_core/agents/agent_llm_integration.py`:
```python
# BEFORE (broken - no indentation)
            content = await AsyncLLMAdapter().chat(
    messages,
    model=...,
)
return {  # <-- outside try block!

# AFTER (fixed)
            response = await AsyncLLMAdapter().chat(
                messages,
                model=...,
            )
            return {  # <-- inside try block
```

### PR #602: GPT-5 Parameter Fix
Fixed parameters for GPT-5 models:
```python
# GPT-5 uses max_completion_tokens, not max_tokens
# GPT-5 reasoning models don't support temperature
if is_gpt5:
    kwargs['max_completion_tokens'] = 6000  # Higher for reasoning
else:
    kwargs['max_tokens'] = 800
    kwargs['temperature'] = 0.2
```

## Actions Taken

1. **Restarted all Celery workers on Railway** - Cleared blocked tasks
2. **Kickstarted 15 stuck initiatives** - Dispatched Stage 1 tasks
3. **Archived 288 initiatives** - Clean slate for the system
4. **Fixed LLM integration** - Agents can now make LLM calls
5. **Fixed GPT-5 parameters** - Correct token settings for reasoning

## API Endpoints Added

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/initiatives/circuit-breaker/` | GET | Check circuit breaker status |
| `/api/initiatives/circuit-breaker/` | POST | Pause/resume initiative creation |
| `/api/initiatives/cleanup/` | GET | Preview initiatives to clean up |
| `/api/initiatives/cleanup/` | POST | Archive or delete initiatives |
| `/api/initiatives/kickstart/` | POST | Kickstart stuck initiatives |
| `/api/initiatives/retry-stuck/` | POST | Retry Stage 1 tasks |

## Configuration

```bash
# Environment variables
INITIATIVE_CREATION_PAUSED=true        # Pause all creation
INITIATIVE_BACKLOG_THRESHOLD=50        # Auto-pause threshold (default: 100)
```

## Verification

```bash
# Check circuit breaker status
curl -X GET "https://your-app.railway.app/api/initiatives/circuit-breaker/" \
  -H "Authorization: Token YOUR_TOKEN"

# Archive stuck initiatives
curl -X POST "https://your-app.railway.app/api/initiatives/cleanup/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "archive", "max_completion": 12}'
```

## Files Changed

| File | Changes |
|------|---------|
| `core/settings.py` | Added `intelligence.*` routing to `long_running` queue |
| `core/services/initiative_circuit_breaker.py` | NEW - Circuit breaker logic |
| `core/services/conversation_initiative_pipeline.py` | Added circuit breaker check |
| `core/services/hivemind_execution_pipeline.py` | Added circuit breaker check |
| `core/models_unified_system.py` | Added circuit breaker check to `promote_to_initiative()` |
| `core/views_initiative_kickstart.py` | Added circuit breaker + cleanup endpoints |
| `core/urls.py` | Added new endpoint routes |
| `ai_core/agents/agent_llm_integration.py` | Fixed syntax error + GPT-5 parameters |

## PRs in This Session

| PR | Description |
|----|-------------|
| #596 | Route intelligence tasks to long_running queue |
| #597 | Initiative Circuit Breaker |
| #598 | Fix circuit breaker to use SystemConfiguration |
| #599 | Initiative cleanup endpoint |
| #600 | Session handoff documentation |
| #601 | Fix LLM integration syntax error |
| #602 | Fix GPT-5 max_completion_tokens parameter |

## Result

- **Before:** 288 stuck initiatives, LLM integration broken, workers blocked
- **After:** 0 active initiatives, LLM fixed, circuit breaker in place, clean slate

## Next Steps

1. **Restart Celery workers** after deployment to pick up LLM fixes
2. Monitor initiative creation rate vs processing rate
3. Consider lowering `INITIATIVE_BACKLOG_THRESHOLD` if issues recur
4. Check Railway memory limits if workers keep crashing
