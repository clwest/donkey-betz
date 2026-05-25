# Session 724: NERVOUS Body System - WebSocket Communication Monitoring

**Date:** January 7, 2026
**Status:** Complete
**System:** NERVOUS (10th Body System)

---

## Overview

Built the NERVOUS system - the 10th body system that monitors WebSocket communication health. This system tracks real-time communication infrastructure including WebSocket connections, message throughput, channel layer (Redis) connectivity, and consumer activity.

---

## Human Body Metaphor

| Body Concept | Technical Equivalent |
|--------------|---------------------|
| **Nerves** | WebSocket connections |
| **Nerve signals** | WebSocket messages |
| **Synapses** | Redis channel layer |
| **Neural pathways** | Message routing |
| **Reflexes** | Fast real-time updates |
| **Numbness** | Connection failures |
| **Overload** | Too many messages |
| **Dormant** | No activity |

---

## Status Levels

| Health Score | Status | Emoji | Meaning |
|--------------|--------|-------|---------|
| 80-100% | `responsive` | ⚡ | Fully responsive, fast connections |
| 60-79% | `active` | 🔌 | Active but some latency |
| 40-59% | `sluggish` | 🐌 | Slow response times |
| 20-39% | `numb` | ❄️ | Connection issues |
| 0-19% | `damaged`/`dormant` | 💔/💤 | Critical or no activity |

---

## Files Created

### 1. `core/models_nervous.py` (~250 lines)

Database models for nervous system:

```python
class NervousPulse(models.Model):
    """Time-series record of nervous system health."""
    status  # responsive, active, sluggish, numb, etc.
    health_score  # 0-100%
    total_consumers
    active_connections
    messages_24h
    messages_per_second
    avg_latency_ms
    channel_layer_healthy
    # ... more fields

class NervousStatus(models.Model):
    """Singleton cache of current nervous state."""
    # Similar to NervousPulse but cached

class WebSocketConnectionLog(models.Model):
    """Log of WebSocket connection events."""
    consumer_name
    event_type  # connect, disconnect, error
    connection_id
    # ... timestamps, metadata
```

### 2. `core/services/nervous.py` (~400 lines)

NervousService singleton:

```python
class NervousService:
    def feel(force: bool = False) -> dict:
        """Run full nervous system check."""

    def get_status() -> dict:
        """Get cached status (fast)."""

    def is_responsive() -> bool:
        """Quick health check."""

    def get_vitals() -> dict:
        """Get vitals for body coordinator."""

    def get_history(hours, limit) -> list:
        """Get pulse history."""

    def get_consumers_summary() -> dict:
        """Get WebSocket consumers summary."""
```

### 3. `core/views_nervous.py` (~160 lines)

6 API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/nervous/status/` | GET | Cached status (fast) |
| `/api/nervous/feel/` | GET | Full health check |
| `/api/nervous/vitals/` | GET | Body coordinator vitals |
| `/api/nervous/history/` | GET | Pulse history |
| `/api/nervous/is-responsive/` | GET | Quick alive check |
| `/api/nervous/consumers/` | GET | WebSocket consumers summary |

### 4. `core/migrations/0156_session_724_nervous_system.py`

Migration creating:
- NervousPulse table
- NervousStatus table
- WebSocketConnectionLog table
- Initial NervousStatus singleton record

---

## Files Modified

### 1. `core/urls.py`

Added 6 nervous API routes:

```python
path('api/nervous/status/', NervousStatusView.as_view()),
path('api/nervous/feel/', NervousFeelView.as_view()),
path('api/nervous/vitals/', NervousVitalsView.as_view()),
path('api/nervous/history/', NervousHistoryView.as_view()),
path('api/nervous/is-responsive/', NervousIsResponsiveView.as_view()),
path('api/nervous/consumers/', NervousConsumersView.as_view()),
```

### 2. `core/auth_middleware.py`

Added nervous endpoints to PUBLIC_PATHS:

```python
'/api/nervous/status/',
'/api/nervous/feel/',
'/api/nervous/vitals/',
'/api/nervous/history/',
'/api/nervous/is-responsive/',
'/api/nervous/consumers/',
```

### 3. `core/tasks.py`

Added Celery task:

```python
@shared_task(name='core.tasks.check_nervous')
def check_nervous():
    """Session 724: NERVOUS SYSTEM - Check WebSocket health."""
    from core.services.nervous import get_nervous_service
    nervous = get_nervous_service()
    result = nervous.feel()
    logger.info(f"[NERVOUS] Check: {result.get('status')}, score: {result.get('health_score')}")
    return result
```

### 4. `core/celery.py`

Added Beat schedule (every 60 seconds):

```python
'nervous-system-check': {
    'task': 'core.tasks.check_nervous',
    'schedule': 60.0,
    'options': {'expires': 55, 'queue': 'broadcast'}
},
```

### 5. `core/services/body_vitals.py`

- Added 'nervous' to SYSTEM_GETTERS
- Added 'nervous' to STATUS_WEIGHTS
- Added nervous status emojis to EMOJI_MAP
- Added _get_nervous_vitals() method
- Updated docstring from "9 body systems" to "10 body systems"

### 6. `frontend/src/lib/api.ts`

Added nervousApi:

```typescript
export const nervousApi = {
  feel: (force = false) => api.get('/nervous/feel/', { params: { force } }),
  status: () => api.get('/nervous/status/'),
  vitals: () => api.get('/nervous/vitals/'),
  history: (hours = 24, limit = 100) => api.get('/nervous/history/', { params: { hours, limit } }),
  isResponsive: () => api.get('/nervous/is-responsive/'),
  consumers: () => api.get('/nervous/consumers/'),
}
```

### 7. `frontend/src/pages/BodyHealthPage.tsx`

- Added nervousApi import
- Added 'nervous' to SYSTEM_CONFIG with Zap icon and yellow color
- Added nervous-specific statuses to STATUS_CONFIG ('responsive', 'numb')
- Added `{systemName === 'nervous' && <NervousDetailView />}`
- Added NervousDetailView component (~240 lines) showing:
  - Health score with status emoji
  - Channel layer (Redis) status with ping latency
  - Consumer statistics (categorized)
  - Connection stats
  - Message stats
  - Activity level
  - Issues detected

---

## API Response Format

```json
{
  "timestamp": "2026-01-07T23:51:06.207989+00:00",
  "status": "responsive",
  "health_score": 100,
  "is_healthy": true,
  "check_duration_ms": 7,
  "channel_layer": {
    "connected": true,
    "redis_ping_ms": 1.06,
    "redis_clients": 72,
    "host": "localhost",
    "port": 6379
  },
  "consumers": {
    "total_routes": 111,
    "unique_consumers": 59,
    "categories": {
      "agent": 10,
      "dashboard": 4,
      "chat": 2,
      "sports": 3,
      "content": 2,
      "system": 6,
      "other": 32
    }
  },
  "connections": {
    "active_estimate": 0,
    "errors_24h": 0
  },
  "messages": {
    "messages_24h": 0,
    "messages_per_second": 0
  },
  "activity_level": "dormant",
  "issues": []
}
```

---

## System Statistics

| Metric | Value |
|--------|-------|
| WebSocket Routes | 111 |
| Unique Consumers | 59 |
| Agent Consumers | 10 |
| Dashboard Consumers | 4 |
| Chat Consumers | 2 |
| Sports Consumers | 3 |
| Content Consumers | 2 |
| System Consumers | 6 |
| Other Consumers | 32 |
| Redis Ping | ~1ms |

---

## Testing

All APIs tested and working:

```bash
# Full check
curl http://localhost:8000/api/nervous/feel/

# Cached status
curl http://localhost:8000/api/nervous/status/

# Quick check
curl http://localhost:8000/api/nervous/is-responsive/

# Consumer summary
curl http://localhost:8000/api/nervous/consumers/
```

---

## Body Systems Complete (10/10)

| System | Purpose | API |
|--------|---------|-----|
| HEART | Core platform health | `/api/heart/` |
| LUNGS | Resource/budget management | `/api/lungs/` |
| CIRCULATORY | Data flow monitoring | `/api/circulatory/` |
| SPINE | Central API routing | `/api/spine/` |
| IMMUNE | Security & threat detection | `/api/immune/` |
| DIGESTIVE | Data ingestion & processing | `/api/digestive/` |
| MUSCULAR | Agent work execution | `/api/muscular/` |
| BRAIN | Cognitive processing | `/api/brain/` |
| SKIN | Workspace outputs | `/api/skin/` |
| **NERVOUS** | **WebSocket monitoring** | `/api/nervous/` |

---

## Future Enhancements

1. **Message Tracking** - Implement actual message counting per consumer
2. **Connection Logging** - Track real connection/disconnect events
3. **Latency Monitoring** - Measure actual message round-trip times
4. **Consumer Health** - Monitor individual consumer health metrics
5. **WebSocket Alerts** - Trigger alerts on connection failures

---

**Session 724 Complete** - NERVOUS system monitoring WebSocket health with 111 routes and 59 unique consumers
