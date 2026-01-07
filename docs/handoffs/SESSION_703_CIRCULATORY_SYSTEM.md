# Session 703: CIRCULATORY SYSTEM - Data Flow Monitoring

**Date:** January 6, 2026
**Focus:** Implementing the CIRCULATORY SYSTEM for monitoring data flow health

---

## Overview

The CIRCULATORY SYSTEM monitors data flow health - the "blood flow" of the AI body. It tracks Redis queues, Celery tasks, WebSocket channels, and event streams to detect bottlenecks and ensure smooth data movement.

### Human Body Metaphor

| Circulation Concept | Technical Equivalent |
|---------------------|---------------------|
| **Blood** | Data flowing through the system |
| **Arteries** | Outbound channels (Redis pub, Celery queues, WebSocket broadcasts) |
| **Veins** | Inbound channels (Spider data, API requests, event consumers) |
| **Heart Rate** | Flow rate / throughput (items/second) |
| **Blood Pressure** | Queue depth / backpressure |
| **Clot/Blockage** | Stuck queue, failed route, bottleneck |
| **Circulation Time** | End-to-end latency |
| **Blood Volume** | Total items in transit |

---

## Files Created

### 1. `core/models_circulatory.py` (~200 lines)

Database models for the CIRCULATORY system:

```python
# FlowRoute - Configuration for monitored routes
class FlowRoute(models.Model):
    ROUTE_TYPE_CHOICES = [
        ('redis_queue', 'Redis Queue'),
        ('celery_queue', 'Celery Queue'),
        ('websocket', 'WebSocket Channel'),
        ('event_stream', 'Event Stream'),
    ]
    name = models.CharField(max_length=100, unique=True)
    route_type = models.CharField(max_length=20, choices=ROUTE_TYPE_CHOICES)
    identifier = models.CharField(max_length=200)  # Queue name, channel, stream
    max_depth = models.IntegerField(default=1000)  # Threshold
    max_latency_ms = models.IntegerField(default=5000)  # Threshold
    is_critical = models.BooleanField(default=False)  # Alert on failure

# CirculationPulse - Time-series records
class CirculationPulse(models.Model):
    overall_status = models.CharField(max_length=20)  # flowing, slow, congested, blocked
    flow_score = models.FloatField()  # 0-100%
    total_routes_checked = models.IntegerField()
    routes_healthy = models.IntegerField()
    bottlenecks = models.JSONField(default=list)
    recorded_at = models.DateTimeField(auto_now_add=True)

# FlowStatus - Current state cache per route
class FlowStatus(models.Model):
    route = models.OneToOneField(FlowRoute, primary_key=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)  # flowing, slow, congested, blocked
    current_depth = models.IntegerField()
    current_throughput = models.FloatField()
    current_latency_ms = models.FloatField()
```

### 2. `core/services/circulatory.py` (~550 lines)

CirculatorySystemService singleton:

```python
def get_circulatory_system() -> 'CirculatorySystemService':
    """Get the singleton CirculatorySystemService instance."""
    global _circulatory_instance
    if _circulatory_instance is None:
        _circulatory_instance = CirculatorySystemService()
    return _circulatory_instance

class CirculatorySystemService:
    """Data flow monitoring - the circulation of the AI body."""

    def circulate(self) -> dict:
        """Run full circulation check - monitor all data flows."""

    def is_flowing(self) -> bool:
        """Quick check - is data flowing normally?"""

    def get_vitals(self) -> dict:
        """Get current flow vitals (cached)."""

    def get_history(self, hours: int = 24, limit: int = 100) -> list:
        """Get circulation pulse history."""

    def detect_bottlenecks(self) -> list:
        """Identify congestion points in data flow."""

    def get_flow_velocity(self, hours: int = 1) -> dict:
        """Calculate current flow rate metrics."""

    # Route-specific checks
    def _check_redis_route(self, route: FlowRoute) -> dict:
        """Check Redis queue depth and latency."""

    def _check_celery_route(self, route: FlowRoute) -> dict:
        """Check Celery queue status and workers."""

    def _check_websocket_route(self, route: FlowRoute) -> dict:
        """Check WebSocket channel layer health."""

    def _check_event_stream_route(self, route: FlowRoute) -> dict:
        """Check Redis event stream status."""
```

### 3. `core/views_circulatory.py` (~350 lines)

8 API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/circulatory/circulate/` | GET | Run full circulation check |
| `/api/circulatory/status/` | GET | Get cached flow status |
| `/api/circulatory/routes/` | GET | List all monitored routes |
| `/api/circulatory/routes/<id>/` | GET | Get specific route status |
| `/api/circulatory/bottlenecks/` | GET | Get current bottlenecks |
| `/api/circulatory/velocity/` | GET | Get flow velocity metrics |
| `/api/circulatory/history/` | GET | Get circulation pulse history |
| `/api/circulatory/is-flowing/` | GET | Quick alive check |

### 4. `core/management/commands/circulation_check.py` (~420 lines)

CLI management command with multiple modes:

```bash
python manage.py circulation_check              # Full circulation check
python manage.py circulation_check --json       # JSON output
python manage.py circulation_check --routes     # List all routes
python manage.py circulation_check --bottlenecks # Show bottlenecks only
python manage.py circulation_check --velocity   # Show flow velocity
python manage.py circulation_check --watch      # Continuous monitoring (30s)
python manage.py circulation_check --history    # Show pulse history
python manage.py circulation_check --route celery_default  # Specific route
```

### 5. `core/migrations/0149_session_703_circulatory_system.py` (~280 lines)

Creates tables and 9 default routes:

```python
default_routes = [
    # Redis Queues
    {'name': 'redis_cache', 'route_type': 'redis_queue', 'identifier': 'redis://localhost:6379/1', 'max_depth': 10000, 'is_critical': True},
    {'name': 'redis_celery_broker', 'route_type': 'redis_queue', 'identifier': 'redis://localhost:6379/2', 'max_depth': 5000, 'is_critical': True},
    {'name': 'redis_celery_results', 'route_type': 'redis_queue', 'identifier': 'redis://localhost:6379/3', 'max_depth': 10000, 'is_critical': False},

    # Celery Queues
    {'name': 'celery_default', 'route_type': 'celery_queue', 'identifier': 'celery', 'max_depth': 1000, 'is_critical': True},
    {'name': 'celery_long_running', 'route_type': 'celery_queue', 'identifier': 'long_running', 'max_depth': 100, 'is_critical': False},
    {'name': 'celery_broadcast', 'route_type': 'celery_queue', 'identifier': 'broadcast', 'max_depth': 500, 'is_critical': True},

    # WebSocket
    {'name': 'websocket_channels', 'route_type': 'websocket', 'identifier': 'channels_redis', 'max_depth': 1000, 'is_critical': False},

    # Event Streams
    {'name': 'event_spider_data', 'route_type': 'event_stream', 'identifier': 'mi:spider_data', 'max_depth': 500, 'is_critical': False},
    {'name': 'event_opportunity_scored', 'route_type': 'event_stream', 'identifier': 'mi:opportunity_scored', 'max_depth': 200, 'is_critical': True},
]
```

---

## Files Modified

### 1. `core/urls.py`

Added 8 CIRCULATORY API routes:

```python
# Session 703: CIRCULATORY System API (Data Flow Monitoring)
urlpatterns += [
    path('api/circulatory/circulate/', circulate_view, name='circulatory-circulate'),
    path('api/circulatory/status/', circulatory_status_view, name='circulatory-status'),
    path('api/circulatory/routes/', routes_list_view, name='circulatory-routes'),
    path('api/circulatory/routes/<uuid:route_id>/', route_detail_view, name='circulatory-route-detail'),
    path('api/circulatory/bottlenecks/', bottlenecks_view, name='circulatory-bottlenecks'),
    path('api/circulatory/velocity/', velocity_view, name='circulatory-velocity'),
    path('api/circulatory/history/', circulatory_history_view, name='circulatory-history'),
    path('api/circulatory/is-flowing/', is_flowing_view, name='circulatory-is-flowing'),
]
```

### 2. `core/tasks.py`

Added `check_circulation` Celery task:

```python
@shared_task(name='core.tasks.check_circulation')
def check_circulation():
    """Session 703: CIRCULATORY SYSTEM - Check data flow health"""
    from core.services.circulatory import get_circulatory_system
    circulatory = get_circulatory_system()
    return circulatory.circulate()
```

### 3. `core/celery.py`

Added Beat schedule (every 30 seconds):

```python
'circulatory-system-pulse': {
    'task': 'core.tasks.check_circulation',
    'schedule': 30.0,  # Every 30 seconds
    'options': {
        'expires': 25,
        'queue': 'broadcast',
    }
},
```

### 4. `core/admin.py`

Registered 3 CIRCULATORY models:

```python
@admin.register(FlowRoute)
class FlowRouteAdmin(admin.ModelAdmin): ...

@admin.register(CirculationPulse)
class CirculationPulseAdmin(admin.ModelAdmin): ...

@admin.register(FlowStatus)
class FlowStatusAdmin(admin.ModelAdmin): ...
```

### 5. `core/auth_middleware.py`

Added 7 CIRCULATORY endpoints to PUBLIC_PATHS:

```python
# Session 703: CIRCULATORY System APIs
'/api/circulatory/circulate/',
'/api/circulatory/status/',
'/api/circulatory/routes/',
'/api/circulatory/bottlenecks/',
'/api/circulatory/velocity/',
'/api/circulatory/history/',
'/api/circulatory/is-flowing/',
```

---

## Status Levels

| Flow Score | Status | Emoji | Meaning |
|------------|--------|-------|---------|
| 80-100% | `flowing` | `🩸` | All routes healthy |
| 50-79% | `slow` | `🐌` | Some latency issues |
| 20-49% | `congested` | `⚠️` | Queue depth warnings |
| 0-19% | `blocked` | `🚫` | Critical flow issues |

---

## Response Format

```json
{
  "timestamp": "2026-01-06T15:30:00Z",
  "overall_status": "flowing",
  "flow_score": 88.9,
  "is_flowing": true,
  "check_duration_ms": 11985,
  "routes_checked": 9,
  "routes_healthy": 7,
  "routes_congested": 2,
  "routes_blocked": 0,
  "flow_metrics": {
    "total_items_in_transit": 93460,
    "total_throughput": 0.00,
    "avg_latency_ms": 1,
    "max_latency_ms": 1
  },
  "routes": {
    "celery_default": {
      "status": "flowing",
      "is_healthy": true,
      "current_depth": 0,
      "throughput": 0.0,
      "latency_ms": 0
    },
    "celery_broadcast": {
      "status": "congested",
      "is_healthy": false,
      "current_depth": 2719,
      "throughput": 0.0,
      "latency_ms": 0
    }
  },
  "bottlenecks": [
    {
      "route": "celery_broadcast",
      "issue": "High queue depth: 2719/500",
      "severity": "critical"
    }
  ]
}
```

---

## Test Results

```
============================================================
  CIRCULATORY SYSTEM - Data Flow Health Check
  The Blood Flow of the AI Body
============================================================
  Overall Status: FLOWING
  Flow Score: 88.9%
  Is Flowing: Yes
  Check Duration: 11985ms

  Route Summary:
  ----------------------------------------
  Total Routes:   9
  Healthy:        7
  Slow:           0
  Congested:      2
  Blocked:        0

  Flow Metrics:
  ----------------------------------------
  Items in Transit:  93,460
  Total Throughput:  0.00 items/sec
  Avg Latency:       1ms
  Max Latency:       1ms

  Bottlenecks Detected:
  - celery_broadcast: High queue depth: 2719/500
  - celery_long_running: High queue depth: 1044/100
============================================================
```

---

## Human Body Architecture (Updated)

| Body Part | Component | Purpose | Session |
|-----------|-----------|---------|---------|
| CONSCIOUSNESS | Human Operator | Final decisions | - |
| EYES/EARS | HumanInterfaceLayer | Attention aggregation | - |
| BRAIN | ThinkingAgent | Reasoning | - |
| **HEART** | HeartMonitorService | Health monitoring | **701** |
| **LUNGS** | LungsCapacityService | Resource management | **702** |
| **CIRCULATORY** | CirculatorySystemService | **Data flow monitoring** | **703** |
| NERVOUS SYSTEM | LLM/ML Routers | Signal routing | - |
| ORGANS | 72 Agents | Work execution | - |
| SENSORY | 77 Spiders | Data gathering | - |
| SKIN | WorkspaceManager | Reality interface | 695 |
| MEMORY | Database & Redis | Persistence | - |

---

## Usage Examples

### CLI Commands

```bash
# Full circulation check
python manage.py circulation_check

# Watch mode (continuous monitoring)
python manage.py circulation_check --watch

# Show bottlenecks only
python manage.py circulation_check --bottlenecks

# Check specific route
python manage.py circulation_check --route celery_default
```

### Python Usage

```python
from core.services.circulatory import get_circulatory_system

circulatory = get_circulatory_system()

# Run full check
result = circulatory.circulate()
print(f"Flow Score: {result['flow_score']}%")

# Quick check
if circulatory.is_flowing():
    print("Data is flowing normally")

# Get bottlenecks
bottlenecks = circulatory.detect_bottlenecks()
for b in bottlenecks:
    print(f"Bottleneck: {b['route']} - {b['issue']}")

# Get flow velocity
velocity = circulatory.get_flow_velocity(hours=1)
print(f"Throughput: {velocity['total_throughput']} items/sec")
```

### API Usage

```bash
# Run full check
curl http://localhost:8000/api/circulatory/circulate/

# Get cached status
curl http://localhost:8000/api/circulatory/status/

# List routes
curl http://localhost:8000/api/circulatory/routes/

# Get bottlenecks
curl http://localhost:8000/api/circulatory/bottlenecks/

# Quick alive check
curl http://localhost:8000/api/circulatory/is-flowing/
```

---

## Next Steps (Session 704)

1. **SPINE** - Central API Router (request routing, load distribution)
2. **IMMUNE SYSTEM** - Security & Threat Detection
3. **DIGESTIVE SYSTEM** - Data Ingestion Pipeline
4. **Frontend Integration** - Add CIRCULATORY widget to React dashboard

---

**Session 703 Complete** - CIRCULATORY SYSTEM (9 Routes, 88.9% Flow Score)
