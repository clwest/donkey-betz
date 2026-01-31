# Session 884: Initiative Pipeline Fix & Circuit Breaker

**Date:** January 30, 2026
**Status:** Complete

## Problem

The Initiative Pipeline was completely broken:
- 288 initiatives accumulated, none making progress
- Celery workers were blocked by 4 long-running `intelligence.tasks.scan_spider_opportunities` tasks
- All 4 concurrency slots on `celery-default` were occupied for 30+ minutes
- New initiatives kept being created faster than they could be processed

## Root Cause

1. **Worker Saturation:** Intelligence tasks (~30 min each) blocked the default queue
2. **No Rate Limiting:** Dream/thinking cycles kept creating initiatives even when backlog existed
3. **No Cleanup Mechanism:** Stuck initiatives had no way to be archived or deleted

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

## Actions Taken

1. **Restarted all Celery workers on Railway** - Cleared blocked tasks
2. **Kickstarted 15 stuck initiatives** - Dispatched Stage 1 tasks
3. **Archived 288 initiatives** - Clean slate for the system

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

## Result

- **Before:** 288 stuck initiatives, 0% processing, workers blocked
- **After:** 0 active initiatives, clean slate, circuit breaker in place

## Next Steps

1. Monitor initiative creation rate vs processing rate
2. Consider lowering `INITIATIVE_BACKLOG_THRESHOLD` if issues recur
3. May need to tune dream/thinking cycle frequency to match processing capacity
