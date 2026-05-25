---
originating_session: 986
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 986 -- Nervous System 60% Health Fix

**Date:** February 10, 2026
**Previous Session:** 985 (PA Boardroom Response Improvement + Celery OOM Deep Fix)

---

## Problem: Nervous System Health 60% on Railway

The nervous system (WebSocket communication monitoring) reported 60% health on Railway but 100% locally. This was a measurement bug, not a real connectivity issue.

### Root Cause Analysis

**Issue 1: Redis URL parsing bug (-40 points)**

`_check_channel_layer()` in `core/services/nervous.py` assumed `CHANNEL_LAYERS.CONFIG.hosts` was always a list of `(host, port)` tuples. But `core/settings.py` provides URL strings:

```python
# settings.py
_redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CHANNEL_LAYERS = {
    'default': {
        'CONFIG': {
            'hosts': [_redis_url],  # <-- string, not tuple
        },
    },
}
```

The old code:
```python
host, port = redis_url[0] if isinstance(redis_url[0], tuple) else ('127.0.0.1', 6379)
```

When `hosts[0]` was a string (always), it fell back to `127.0.0.1:6379` which doesn't exist on Railway. Redis showed as "disconnected" -> -40 points.

**Issue 2: Message throughput hardcoded to 0**

`_get_message_stats()` returned zeros with a "not yet implemented" note. Activity level was permanently "dormant". Now that `CeleryTaskEvent` exists (Session 983), real data is available.

## Solution: 3 Changes (1 file)

### Change 1: Redis URL String Handling

**File:** `core/services/nervous.py` -- `_check_channel_layer()` (lines 237-275)

Replaced tuple-only parsing with type-aware handling:
- If `hosts[0]` is a string -> `redis.from_url(url, socket_timeout=2)`
- If `hosts[0]` is a tuple -> `redis.Redis(host, port, socket_timeout=2)` (existing behavior)
- Fallback: try `settings.REDIS_URL` or localhost

Credentials in URLs are masked for display output using a regex that replaces everything between `://` and `@` with `***`.

### Change 2: Wire Message Stats to CeleryTaskEvent

**File:** `core/services/nervous.py` -- `_get_message_stats()` (lines 413-436)

Replaced hardcoded zeros with:
```python
from core.models_celery_telemetry import CeleryTaskEvent
count_24h = CeleryTaskEvent.objects.filter(timestamp__gte=day_ago).count()
mps = round(count_24h / 86400, 4) if count_24h > 0 else 0
```

Graceful fallback if `CeleryTaskEvent` table doesn't exist (returns dict with `'note'` key).

### Change 3: Activity Penalty for Genuinely Zero Activity

**File:** `core/services/nervous.py` -- `_calculate_health_score()` (lines 474-477)

Added mild -10 penalty when:
- `messages_24h == 0` AND no `'note'` key in the dict

This distinguishes "system idle but tracking works" (-10) from "tracking unavailable" (no penalty, same as before).

---

## Expected Impact

| Environment | Before | After | Why |
|-------------|--------|-------|-----|
| Railway | 60% | ~90-100% | Redis reconnected (+40), real activity data flowing |
| Local | ~100% | ~100% | Redis already connected locally via tuple config |

## Files Changed

| File | Lines | Change |
|------|-------|--------|
| `core/services/nervous.py` | ~237-275 | URL string + tuple + fallback Redis handling |
| `core/services/nervous.py` | ~413-436 | CeleryTaskEvent query for real throughput |
| `core/services/nervous.py` | ~474-477 | Mild activity penalty for zero throughput |

No migrations. No frontend changes. No new dependencies.

---

## Patterns for Future Sessions

**Body system health score debugging:**
1. Check Railway logs for the specific health check method that's scoring low
2. Compare settings between local and Railway (especially Redis/DB URLs)
3. `CHANNEL_LAYERS.CONFIG.hosts` uses URL strings, not tuples -- any code parsing this must handle both formats
4. Use `CeleryTaskEvent` for task throughput metrics (populated via Celery signals in `core/celery_telemetry.py`)
