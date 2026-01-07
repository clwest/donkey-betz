# Session 701: HEART Service - System Health Monitoring

**Date:** January 6, 2026
**Focus:** Implementing the HEART (Health, Events, Activity, Real-time Telemetry) service
**Status:** COMPLETE

---

## Overview

The **HEART** service is the central heartbeat of the AI body. Following the human body metaphor used throughout the platform (Brain, Nervous System, Organs, Sensory, Skin, Memory), the HEART continuously monitors all system components every 60 seconds and provides health status through CLI, API, and Celery Beat.

---

## Human Body Architecture Complete

| Body Part | Technical Component | Purpose |
|-----------|---------------------|---------|
| **CONSCIOUSNESS** | Human Operator | Final decisions, approvals |
| **EYES/EARS** | HumanInterfaceLayer | Attention aggregation |
| **BRAIN** | ThinkingAgent | Autonomous reasoning |
| **HEART** | HeartMonitorService | **Health monitoring (NEW)** |
| **NERVOUS SYSTEM** | LLM/ML Routers | Signal routing |
| **ORGANS** | 72 Specialized Agents | Work execution |
| **SENSORY** | 77 Spiders | Data gathering |
| **SKIN** | WorkspaceManager | Interface with reality |
| **MEMORY** | Database & Redis | Persistence |

---

## Files Created (5)

| File | Lines | Purpose |
|------|-------|---------|
| `core/models_heart.py` | ~200 | HeartBeat + ComponentStatus models |
| `core/services/heart.py` | ~500 | HeartMonitorService class |
| `core/views_heart.py` | ~180 | 5 API endpoints |
| `core/management/commands/heart_check.py` | ~240 | CLI management command |
| `core/migrations/0147_session_701_heart_service.py` | ~130 | Database migration |

---

## Files Modified (4)

| File | Changes |
|------|---------|
| `core/urls.py` | Added 5 HEART API routes |
| `core/tasks.py` | Added `run_heartbeat` Celery task |
| `core/celery.py` | Added Beat schedule (every 60 seconds) |
| `core/admin.py` | Registered HeartBeat + ComponentStatus models |

---

## Components Monitored (6 Body Parts)

| Component | What It Checks | Healthy Threshold |
|-----------|----------------|-------------------|
| **Brain** | ThinkingAgent availability | Can import & instantiate |
| **Nervous System** | LLM Provider Registry | ≥1 provider active |
| **Organs** | 72 Agents in database | ≥50 agents registered |
| **Sensory** | 77 Spiders in registry | ≥50 spiders registered |
| **Skin** | Workspace Manager | Module importable |
| **Memory** | Database + Redis connectivity | Both respond to ping |

---

## Health Status Levels

| Status | Score Range | Action |
|--------|-------------|--------|
| **HEALTHY** | 80-100% | All systems operational |
| **DEGRADED** | 50-79% | Some components have issues |
| **CRITICAL** | 0-49% | Discord alert sent |

---

## Usage

### CLI Commands

```bash
# Full health check
python manage.py heart_check

# Check specific component
python manage.py heart_check brain
python manage.py heart_check nervous_system
python manage.py heart_check organs
python manage.py heart_check sensory
python manage.py heart_check skin
python manage.py heart_check memory

# Continuous monitoring (60s interval)
python manage.py heart_check --watch

# Show heartbeat history
python manage.py heart_check --history
python manage.py heart_check --history --hours 48

# JSON output
python manage.py heart_check --json
```

### API Endpoints

```bash
GET /api/heart/pulse/                     # Run full check now
GET /api/heart/status/                    # Get cached vitals
GET /api/heart/history/                   # Get heartbeat history
GET /api/heart/history/?hours=48&limit=50 # With parameters
GET /api/heart/component/brain/           # Component detail
GET /api/heart/alive/                     # Quick alive check (for load balancers)
```

### Python Usage

```python
from core.services.heart import get_heart_monitor

heart = get_heart_monitor()

# Run full health check
pulse = heart.pulse()
print(f"Health: {pulse['overall_status']} ({pulse['health_score']}%)")

# Check specific component
brain_status = heart.check_brain()

# Quick alive check
is_alive = heart.is_alive()

# Get cached vitals from DB
vitals = heart.get_vitals()

# Get heartbeat history
history = heart.get_history(hours=24, limit=100)

# Record heartbeat to database
heartbeat = heart.record_heartbeat(pulse)

# Alert if critical (sends Discord notification)
heart.alert_if_critical(pulse)
```

---

## Celery Integration

### Task
```python
# core/tasks.py
@shared_task(name='core.tasks.run_heartbeat')
def run_heartbeat():
    """Runs every 60 seconds via Celery Beat"""
    heart = get_heart_monitor()
    pulse = heart.pulse()
    heart.record_heartbeat(pulse)
    heart.alert_if_critical(pulse)
    # Publish to Redis for WebSocket consumers
    return pulse
```

### Beat Schedule
```python
# core/celery.py
'heart-service-heartbeat': {
    'task': 'core.tasks.run_heartbeat',
    'schedule': 60.0,  # Every 60 seconds
    'options': {
        'expires': 55,
        'queue': 'broadcast',
    }
},
```

---

## Database Models

### HeartBeat (Time-Series)
```python
class HeartBeat(models.Model):
    id = models.UUIDField(primary_key=True)
    health_score = models.FloatField()      # 0-100%
    overall_status = models.CharField()      # healthy/degraded/critical
    is_alive = models.BooleanField()
    components = models.JSONField()          # Detailed component data
    check_duration_ms = models.IntegerField()
    components_checked = models.IntegerField()
    components_healthy = models.IntegerField()
    alerts_sent = models.BooleanField()
    recorded_at = models.DateTimeField()
```

### ComponentStatus (Cache)
```python
class ComponentStatus(models.Model):
    component = models.CharField(primary_key=True)  # brain, organs, etc.
    display_name = models.CharField()
    status = models.CharField()              # healthy/degraded/critical
    is_healthy = models.BooleanField()
    last_check = models.DateTimeField()
    last_healthy = models.DateTimeField()
    response_time_ms = models.IntegerField()
    error_count_24h = models.IntegerField()
    uptime_percent_24h = models.FloatField()
    details = models.JSONField()
    last_error = models.TextField()
```

---

## Test Results

```
============================================================
  HEART SERVICE - System Health Check
============================================================
  Overall Status: HEALTHY (100.0%)
  Components: 6/6 healthy
  Check Duration: 324ms

  [OK] Brain (ThinkingAgent)        - claude-opus-4
  [OK] Nervous System (LLM Routers) - 5 providers, 8 models
  [OK] Organs (72 Agents)           - All active
  [OK] Sensory (77 Spiders)         - 38 categories
  [OK] Skin (Workspace Manager)     - 2 workspaces
  [OK] Memory (Database & Redis)    - Connected
============================================================
```

---

## Next Steps (Session 702)

### Missing Body Parts to Implement

1. **LUNGS** - Resource/capacity management
   - Token budget tracking across LLM providers
   - API rate limit management
   - Cost optimization

2. **CIRCULATORY SYSTEM** - Data flow infrastructure
   - Redis as bloodstream
   - WebSocket connections
   - Celery queue monitoring

3. **SPINE** - Central API routing layer

---

## Documentation Updated

- `CLAUDE.md` - Added HEART to System Stats and Recent Sessions
- `docs/CAPABILITIES.md` - Added HEART Service section and Human Body table entry
- `docs/SERVICES.md` - Added System Health category with HeartMonitorService
- `docs/handoffs/SESSION_701_HEART_SERVICE.md` - This document
