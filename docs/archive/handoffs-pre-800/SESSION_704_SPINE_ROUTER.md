# Session 704: SPINE - Central API Router

**Date:** January 6, 2026
**Focus:** Implementing the SPINE - Central API Router for request routing and health monitoring

---

## Overview

The SPINE is the backbone of the AI body - central request routing and coordination. It tracks API metrics, provides health-aware routing, and manages request flow integrated with HEART, LUNGS, and CIRCULATORY services.

### Human Body Metaphor

| Spine Concept | Technical Equivalent |
|---------------|---------------------|
| **Backbone** | Central routing infrastructure |
| **Vertebrae** | Individual route patterns |
| **Alignment** | Route health and availability |
| **Posture** | Overall routing efficiency |
| **Nerve Signals** | Request traces with correlation IDs |
| **Compression** | High load, degraded routing |
| **Injury** | Critical route failures |

---

## Files Created (5)

### 1. `core/models_spine.py` (~320 lines)

Database models for the SPINE router:

```python
class RoutePattern(models.Model):
    """Configuration for a monitored API route pattern."""
    CATEGORY_CHOICES = [
        ('agents', 'Agent Orchestration'),
        ('spiders', 'Spider Network'),
        ('content', 'Content & Media'),
        ('business', 'Business Logic'),
        ('creative', 'Creative Pipeline'),
        ('scifi', 'Sci-Fi Features'),
        ('monitoring', 'System Monitoring'),
        ('llm', 'LLM Routing'),
        ('admin', 'Admin & System'),
        ('websocket', 'WebSocket'),
        ('auth', 'Authentication'),
        ('other', 'Other'),
    ]
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('normal', 'Normal'),
        ('low', 'Low'),
    ]
    pattern = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    max_latency_ms = models.IntegerField(default=5000)
    max_error_rate = models.FloatField(default=0.05)
    requires_healthy_heart = models.BooleanField(default=False)
    requires_healthy_lungs = models.BooleanField(default=False)

class RouteMetrics(models.Model):
    """Time-series record of route performance metrics."""
    pattern = models.ForeignKey(RoutePattern, on_delete=models.CASCADE)
    total_requests = models.BigIntegerField(default=0)
    avg_latency_ms = models.FloatField(default=0)
    p95_latency_ms = models.FloatField(default=0)
    error_rate = models.FloatField(default=0)
    health_score = models.FloatField(default=100.0)

class SpineStatus(models.Model):
    """Current spine status - cached routing health."""
    STATUS_CHOICES = [
        ('aligned', 'Aligned'),      # All routes healthy
        ('strained', 'Strained'),    # Some routes degraded
        ('compressed', 'Compressed'), # High load, routing slowed
        ('injured', 'Injured'),       # Critical routes failing
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    health_score = models.FloatField(default=100.0)
    heart_status = models.CharField(max_length=20)
    lungs_status = models.CharField(max_length=20)
    circulatory_status = models.CharField(max_length=20)

class RequestTrace(models.Model):
    """Individual request trace for detailed analysis."""
    correlation_id = models.CharField(max_length=64, unique=True)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    duration_ms = models.FloatField(null=True)
    status_code = models.IntegerField(null=True)
```

### 2. `core/services/spine.py` (~700 lines)

SpineRouterService singleton:

```python
def get_spine_router() -> 'SpineRouterService':
    """Get the singleton SpineRouterService instance."""
    global _spine_instance
    if _spine_instance is None:
        _spine_instance = SpineRouterService()
    return _spine_instance

class SpineRouterService:
    """Central API Router - the backbone of the AI body."""

    def align(self) -> dict:
        """Run full spine alignment check - main health check."""

    def is_aligned(self) -> bool:
        """Quick check - is the spine healthy?"""

    def get_vitals(self) -> dict:
        """Get current spine vitals (cached)."""

    def can_route(self, path: str, method: str = 'GET') -> Tuple[bool, str]:
        """Check if a request can be routed to the given path."""

    def get_route_metrics(self, path: str, hours: int = 24) -> dict:
        """Get metrics for a specific route pattern."""

    def get_history(self, hours: int = 24, limit: int = 100) -> list:
        """Get spine alignment history."""

    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for request tracing."""

    def start_trace(self, method: str, path: str, ...) -> RequestTrace:
        """Start tracing a request."""

    def complete_trace(self, correlation_id: str, status_code: int, ...) -> RequestTrace:
        """Complete a request trace."""

    def get_patterns(self, category: str = None, active_only: bool = True) -> list:
        """Get all route patterns, optionally filtered by category."""
```

### 3. `core/views_spine.py` (~300 lines)

9 API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/spine/align/` | GET | Run full alignment check |
| `/api/spine/status/` | GET | Get cached spine status |
| `/api/spine/patterns/` | GET | List all route patterns |
| `/api/spine/patterns/<id>/` | GET | Get specific pattern details |
| `/api/spine/metrics/` | GET | Get metrics for a pattern |
| `/api/spine/history/` | GET | Get alignment history |
| `/api/spine/can-route/` | GET | Check if path can be routed |
| `/api/spine/is-aligned/` | GET | Quick health check |
| `/api/spine/categories/` | GET | Get category breakdown |

### 4. `core/management/commands/spine_check.py` (~380 lines)

CLI management command:

```bash
python manage.py spine_check                    # Full alignment check
python manage.py spine_check --json             # JSON output
python manage.py spine_check --patterns         # List all patterns
python manage.py spine_check --categories       # Show category breakdown
python manage.py spine_check --pattern /api/agents/  # Specific pattern
python manage.py spine_check --watch            # Continuous monitoring (60s)
python manage.py spine_check --history          # Show alignment history
python manage.py spine_check --can-route /api/foo  # Check if path can route
```

### 5. `core/migrations/0150_session_704_spine_router.py` (~300 lines)

Creates tables and 19 default route patterns:

```python
default_patterns = [
    # Auth - Critical
    {'pattern': '/api/v1/auth/', 'category': 'auth', 'priority': 'critical'},

    # Agent Orchestration - High priority
    {'pattern': '/api/agents/', 'category': 'agents', 'priority': 'high', 'requires_healthy_heart': True},
    {'pattern': '/api/agent-execution/', 'category': 'agents', 'priority': 'high', 'requires_healthy_heart': True, 'requires_healthy_lungs': True},

    # Monitoring - Critical
    {'pattern': '/api/heart/', 'category': 'monitoring', 'priority': 'critical'},
    {'pattern': '/api/lungs/', 'category': 'monitoring', 'priority': 'critical'},
    {'pattern': '/api/circulatory/', 'category': 'monitoring', 'priority': 'critical'},
    {'pattern': '/api/spine/', 'category': 'monitoring', 'priority': 'critical'},

    # ... more patterns for all 12 categories
]
```

---

## Files Modified (5)

### 1. `core/urls.py`
Added 9 SPINE API routes.

### 2. `core/tasks.py`
Added `check_spine_alignment` Celery task:

```python
@shared_task(name='core.tasks.check_spine_alignment')
def check_spine_alignment():
    """Session 704: SPINE - Check central API router health."""
    from core.services.spine import get_spine_router
    spine = get_spine_router()
    return spine.align()
```

### 3. `core/celery.py`
Added Beat schedule (every 60 seconds):

```python
'spine-alignment-check': {
    'task': 'core.tasks.check_spine_alignment',
    'schedule': 60.0,
    'options': {'expires': 55, 'queue': 'broadcast'}
},
```

### 4. `core/admin.py`
Registered 4 SPINE models:
- RoutePatternAdmin
- RouteMetricsAdmin
- SpineStatusAdmin
- RequestTraceAdmin

### 5. `core/auth_middleware.py`
Added 8 SPINE endpoints to PUBLIC_PATHS.

---

## Status Levels

| Health Score | Status | Emoji | Meaning |
|--------------|--------|-------|---------|
| 90-100% | `aligned` | `🦴` | All routes healthy |
| 70-89% | `strained` | `⚡` | Some routes degraded |
| 50-69% | `compressed` | `🔧` | High load, routing slowed |
| 0-49% | `injured` | `🚨` | Critical routes failing |

---

## Response Format

```json
{
  "timestamp": "2026-01-06T15:30:00Z",
  "overall_status": "aligned",
  "health_score": 95.5,
  "is_aligned": true,
  "check_duration_ms": 58,
  "total_patterns": 19,
  "healthy_patterns": 19,
  "degraded_patterns": 0,
  "failed_patterns": 0,
  "metrics": {
    "total_requests": 12345,
    "error_rate": 0.02,
    "avg_latency_ms": 125.5
  },
  "routing": {
    "routes_blocked": 0,
    "routes_rate_limited": 0,
    "fallbacks_active": 0
  },
  "integrations": {
    "heart": {"status": "healthy", "is_healthy": true},
    "lungs": {"status": "full_capacity", "is_healthy": true},
    "circulatory": {"status": "flowing", "is_flowing": true}
  },
  "category_health": {
    "agents": {"health_score": 98.5, "pattern_count": 2},
    "monitoring": {"health_score": 100.0, "pattern_count": 4},
    "content": {"health_score": 95.0, "pattern_count": 2}
  }
}
```

---

## Test Results

```
============================================================
  SPINE - Central API Router Health Check
  The Backbone of the AI Body
============================================================
  Overall Status: STRAINED     ⚡
  Health Score: 73.3%
  Is Aligned: No
  Check Duration: 58ms

  Pattern Summary:
  ----------------------------------------
  Total Patterns:   19
  Healthy:          19
  Degraded:         0
  Failed:           0

  Routing Status:
  ----------------------------------------
  Routes Blocked:   3
  Rate Limited:     0
  Fallbacks Active: 0

  Category Health:
  ----------------------------------------
  admin           100.0% (1 patterns)
  agents          100.0% (2 patterns)
  auth            100.0% (1 patterns)
  business        100.0% (2 patterns)
  content         100.0% (2 patterns)
  creative        100.0% (2 patterns)
  llm             100.0% (1 patterns)
  monitoring      100.0% (4 patterns)
  scifi           100.0% (2 patterns)
  spiders         100.0% (1 patterns)
  websocket       100.0% (1 patterns)
============================================================
```

---

## Human Body Architecture (Updated)

| Body Part | Component | Purpose | Session |
|-----------|-----------|---------|---------|
| **CONSCIOUSNESS** | Human Operator | Final decisions | - |
| **EYES/EARS** | HumanInterfaceLayer | Attention aggregation | - |
| **BRAIN** | ThinkingAgent | Reasoning | - |
| **HEART** | HeartMonitorService | Health monitoring | 701 |
| **LUNGS** | LungsCapacityService | Resource management | 702 |
| **CIRCULATORY** | CirculatorySystemService | Data flow monitoring | 703 |
| **SPINE** | **SpineRouterService** | **Central API routing** | **704** |
| NERVOUS SYSTEM | LLM/ML Routers | Signal routing | - |
| ORGANS | 72 Agents | Work execution | - |
| SENSORY | 77 Spiders | Data gathering | - |
| SKIN | WorkspaceManager | Reality interface | 695 |
| MEMORY | Database & Redis | Persistence | - |

---

## API Endpoint Usage

```bash
# Run full alignment check
curl http://localhost:8000/api/spine/align/

# Get cached status
curl http://localhost:8000/api/spine/status/

# List all patterns
curl http://localhost:8000/api/spine/patterns/

# Filter by category
curl "http://localhost:8000/api/spine/patterns/?category=agents"

# Get metrics for a path
curl "http://localhost:8000/api/spine/metrics/?path=/api/agents/"

# Check if path can be routed
curl "http://localhost:8000/api/spine/can-route/?path=/api/agents/"

# Quick health check
curl http://localhost:8000/api/spine/is-aligned/

# Get category breakdown
curl http://localhost:8000/api/spine/categories/
```

---

## CLI Command Usage

```bash
# Full alignment check
python manage.py spine_check

# Watch mode (continuous 60s)
python manage.py spine_check --watch

# List all patterns
python manage.py spine_check --patterns

# Category breakdown
python manage.py spine_check --categories

# Check specific pattern
python manage.py spine_check --pattern /api/agents/

# Check routing
python manage.py spine_check --can-route /api/foo
```

---

## Next Steps (Session 705)

1. **IMMUNE SYSTEM** - Security & Threat Detection
   - Rate limit abuse detection
   - Suspicious pattern recognition
   - Active defense layer

2. **DIGESTIVE SYSTEM** - Data Ingestion Pipeline
   - Spider data parsing
   - Data normalization
   - Enrichment pipeline

3. **Frontend Integration** - Add SPINE widget to React dashboard
   - Real-time health display
   - Pattern browser
   - Routing status visualization

---

---

## Session 704 Updates (Integration Fix)

**Issue Found:** SPINE showed 3 blocked routes and 0% for all integrations (HEART/LUNGS/CIRCULATORY).

**Root Cause:** The `_check_*_status()` methods in `spine.py` were looking for field names that didn't exist in each service's `get_vitals()` response:

| Service | Expected Fields | Actual Fields |
|---------|----------------|---------------|
| HEART | `status`, `health_score`, `is_healthy` | Dict of components with individual statuses |
| LUNGS | `status`, `capacity_score` | `system_status`, `system_oxygen` |
| CIRCULATORY | `overall_status`, `flow_score`, `is_flowing` | `routes` dict with route statuses |

**Fix Applied:** Updated all three integration methods in `core/services/spine.py:648-727`:
1. **HEART**: Calculate overall health from component statuses
2. **LUNGS**: Map `system_status` → `status`, `system_oxygen` → `capacity_score`
3. **CIRCULATORY**: Calculate overall status from routes dict

**Results After Fix:**
- Routes blocked: 3 → **0**
- Overall status: "strained" → **"aligned"**
- Health score: 73.3% → **100%**
- All 11 route categories now show 100% health

---

**Session 704 Complete** - SPINE (19 Route Patterns, 12 Categories, Integrated with HEART/LUNGS/CIRCULATORY)
