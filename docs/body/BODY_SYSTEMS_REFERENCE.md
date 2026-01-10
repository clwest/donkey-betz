# Body Systems Reference - Complete Technical Documentation

**Created:** Session 708 (January 7, 2026)
**Purpose:** Detailed technical reference for all 7 body system implementations

---

## Table of Contents

1. [HEART System](#1-heart-system---component-health-monitoring)
2. [LUNGS System](#2-lungs-system---resource--budget-management)
3. [CIRCULATORY System](#3-circulatory-system---data-flow-monitoring)
4. [SPINE System](#4-spine-system---api-routing-health)
5. [IMMUNE System](#5-immune-system---security--threat-detection)
6. [DIGESTIVE System](#6-digestive-system---data-ingestion--processing)
7. [MUSCULAR System](#7-muscular-system---agent-work-execution)

---

## 1. HEART System - Component Health Monitoring

**Session:** 701
**Purpose:** Monitor health of 6 core platform components
**Metaphor:** Just as the heart pumps blood to check organ health, this service pings all components

### Files

| File | Purpose |
|------|---------|
| `core/services/heart.py` | HeartMonitorService singleton |
| `core/models_heart.py` | HeartBeat, ComponentStatus models |
| `core/views_heart.py` | 5 API endpoints |
| `core/management/commands/heart_check.py` | CLI command |

### Database Models

#### HeartBeat (Time-Series)
```python
class HeartBeat(models.Model):
    id = models.UUIDField(primary_key=True)

    # Overall metrics
    overall_status = models.CharField(max_length=20)  # healthy/degraded/critical/offline
    health_score = models.FloatField()  # 0-100%

    # Component breakdown
    components_checked = models.IntegerField()
    components_healthy = models.IntegerField()
    components_degraded = models.IntegerField()
    components_critical = models.IntegerField()

    # Details
    component_statuses = models.JSONField()  # Per-component status

    # Metadata
    pulse_duration_ms = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)
```

#### ComponentStatus (Cache)
```python
class ComponentStatus(models.Model):
    COMPONENT_CHOICES = [
        ('brain', 'Brain (ThinkingAgent)'),
        ('nervous_system', 'Nervous System (LLM/ML Routers)'),
        ('organs', 'Organs (72 Agents)'),
        ('sensory', 'Sensory (77 Spiders)'),
        ('skin', 'Skin (Workspace Manager)'),
        ('memory', 'Memory (Database & Redis)'),
    ]

    name = models.CharField(max_length=50, primary_key=True)
    status = models.CharField(max_length=20)  # healthy/degraded/critical/offline
    health_score = models.FloatField(default=100.0)

    # 24h metrics
    error_count_24h = models.IntegerField(default=0)
    uptime_percent_24h = models.FloatField(default=100.0)

    last_check = models.DateTimeField(auto_now=True)
    last_healthy = models.DateTimeField(null=True)
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/heart/pulse/` | GET | Run full health check |
| `/api/heart/status/` | GET | Get cached vitals |
| `/api/heart/history/` | GET | Get heartbeat history |
| `/api/heart/component/<name>/` | GET | Get specific component |
| `/api/heart/alive/` | GET | Quick alive check |

### Status Levels

| Score | Status | Emoji |
|-------|--------|-------|
| 80-100% | healthy | ❤️ |
| 60-79% | degraded | 💛 |
| 20-59% | critical | 🧡 |
| 0-19% | offline | 🖤 |

### Celery Schedule

```python
'heart-service-heartbeat': {
    'task': 'core.tasks.run_heartbeat',
    'schedule': 60.0,  # Every 60 seconds
}
```

### Response Format

```json
{
  "timestamp": "2026-01-07T05:00:00Z",
  "overall_status": "healthy",
  "health_score": 92.5,
  "is_alive": true,
  "components": {
    "brain": {"status": "healthy", "score": 95.0},
    "nervous_system": {"status": "healthy", "score": 90.0},
    "organs": {"status": "healthy", "score": 88.0},
    "sensory": {"status": "degraded", "score": 75.0},
    "skin": {"status": "healthy", "score": 100.0},
    "memory": {"status": "healthy", "score": 98.0}
  }
}
```

---

## 2. LUNGS System - Resource & Budget Management

**Session:** 702
**Purpose:** Track token consumption and budget allocation
**Metaphor:** Oxygen = Budget remaining; Breathing = Resource consumption rate

### Files

| File | Purpose |
|------|---------|
| `core/services/lungs.py` | LungsCapacityService singleton |
| `core/models_lungs.py` | Budget, BreathCycle, RespiratoryStatus models |
| `core/views_lungs.py` | 7 API endpoints |
| `core/management/commands/lungs_check.py` | CLI command |

### Database Models

#### Budget (Configuration)
```python
class Budget(models.Model):
    SCOPE_CHOICES = [
        ('system', 'System-wide'),
        ('provider', 'Per Provider'),
        ('agent', 'Per Agent'),
    ]

    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)

    # Limits
    token_limit = models.BigIntegerField()  # Max tokens per period
    cost_limit = models.DecimalField(max_digits=10, decimal_places=2)  # Max $ per period
    period_days = models.IntegerField(default=30)  # Budget period

    # Current usage
    tokens_used = models.BigIntegerField(default=0)
    cost_incurred = models.DecimalField(default=0)

    # Alerts
    warning_threshold = models.FloatField(default=0.8)  # 80%
    critical_threshold = models.FloatField(default=0.95)  # 95%
```

#### BreathCycle (Time-Series)
```python
class BreathCycle(models.Model):
    id = models.UUIDField(primary_key=True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)

    # Consumption this cycle
    tokens_used = models.BigIntegerField(default=0)
    cost_incurred = models.DecimalField(default=0)

    # Calculated metrics
    oxygen_level = models.FloatField()  # % budget remaining
    respiratory_rate = models.FloatField()  # calls per minute
    projected_end_usage = models.FloatField()  # Projected % at period end

    recorded_at = models.DateTimeField(auto_now_add=True)
```

#### RespiratoryStatus (Cache)
```python
class RespiratoryStatus(models.Model):
    STATUS_CHOICES = [
        ('normal', 'Normal'),
        ('elevated', 'Elevated'),
        ('hyperventilating', 'Hyperventilating'),
        ('holding', 'Holding Breath'),  # Rate limited
    ]

    budget = models.OneToOneField(Budget, primary_key=True)

    status = models.CharField(max_length=20)
    oxygen_level = models.FloatField()  # 0-100%
    respiratory_rate = models.FloatField()  # calls/min

    is_breathing = models.BooleanField(default=True)  # False = rate limited
    breath_held_until = models.DateTimeField(null=True)  # Rate limit expiry
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/lungs/breathe/` | GET | Full breathing check |
| `/api/lungs/status/` | GET | Cached respiratory status |
| `/api/lungs/oxygen/` | GET | Remaining budget % |
| `/api/lungs/budgets/` | GET | List all budgets |
| `/api/lungs/budgets/` | POST | Create new budget |
| `/api/lungs/forecast/` | GET | Spending forecast |
| `/api/lungs/can-breathe/` | GET | Check if LLM call allowed |

### Status Levels

| Oxygen Level | Status | Emoji |
|--------------|--------|-------|
| 50-100% | normal | 🫁 |
| 20-49% | elevated | 😤 |
| 5-19% | hyperventilating | 🥵 |
| 0-4% | holding | 🚫 |

### Celery Schedules

```python
'lungs-service-breathing': {
    'task': 'core.tasks.check_breathing',
    'schedule': 30.0,  # Every 30 seconds
},
'lungs-daily-forecast': {
    'task': 'core.tasks.forecast_spending',
    'schedule': crontab(hour=9, minute=0),  # Daily 9 AM
},
'lungs-daily-reset': {
    'task': 'core.tasks.reset_daily_counters',
    'schedule': crontab(hour=0, minute=0),  # Daily midnight
},
```

### Response Format

```json
{
  "timestamp": "2026-01-07T05:00:00Z",
  "overall_status": "normal",
  "is_breathing": true,
  "budgets": [
    {
      "name": "System Monthly",
      "oxygen_level": 72.5,
      "tokens_used": 1375000,
      "token_limit": 5000000,
      "cost_incurred": 45.23,
      "cost_limit": 150.00,
      "projected_end_usage": 85.2,
      "status": "normal"
    }
  ],
  "respiratory_rate": 12.5,
  "forecast": {
    "end_of_period": "2026-01-31",
    "projected_tokens": 4250000,
    "projected_cost": 127.50,
    "will_exceed": false
  }
}
```

---

## 3. CIRCULATORY System - Data Flow Monitoring

**Session:** 703
**Purpose:** Monitor data flow through Redis, Celery, WebSockets
**Metaphor:** Blood flow = Data flow; Arteries = Queues/Channels

### Files

| File | Purpose |
|------|---------|
| `core/services/circulatory.py` | CirculatorySystemService singleton |
| `core/models_circulatory.py` | FlowRoute, CirculationPulse, FlowStatus models |
| `core/views_circulatory.py` | 6 API endpoints |
| `core/management/commands/circulation_check.py` | CLI command |

### Database Models

#### FlowRoute (Configuration)
```python
class FlowRoute(models.Model):
    ROUTE_TYPES = [
        ('redis', 'Redis Queue'),
        ('celery', 'Celery Task Queue'),
        ('websocket', 'WebSocket Channel'),
        ('event_stream', 'Event Stream'),
    ]

    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    route_type = models.CharField(max_length=20, choices=ROUTE_TYPES)

    # Connection details
    endpoint = models.CharField(max_length=255)  # Queue name, channel, etc.

    # Thresholds
    max_depth = models.IntegerField(default=1000)  # Max queue depth
    max_latency_ms = models.IntegerField(default=5000)  # Max acceptable latency
    min_throughput = models.FloatField(default=1.0)  # Min items/second

    is_critical = models.BooleanField(default=False)
```

#### CirculationPulse (Time-Series)
```python
class CirculationPulse(models.Model):
    id = models.UUIDField(primary_key=True)

    # Overall flow status
    overall_status = models.CharField(max_length=20)  # flowing/slow/congested/blocked
    flow_score = models.FloatField()  # 0-100%

    # Aggregate metrics
    total_items_in_transit = models.IntegerField()
    total_throughput = models.FloatField()  # items/second
    avg_latency_ms = models.FloatField()

    # Route breakdown
    route_statuses = models.JSONField()
    bottlenecks = models.JSONField(default=list)

    recorded_at = models.DateTimeField(auto_now_add=True)
```

#### FlowStatus (Cache)
```python
class FlowStatus(models.Model):
    STATUS_CHOICES = [
        ('flowing', 'Flowing'),
        ('slow', 'Slow'),
        ('congested', 'Congested'),
        ('blocked', 'Blocked'),
    ]

    route = models.OneToOneField(FlowRoute, primary_key=True)

    status = models.CharField(max_length=20)
    current_depth = models.IntegerField(default=0)
    latency_ms = models.FloatField(default=0)
    throughput = models.FloatField(default=0)  # items/second

    # 24h metrics
    items_processed_24h = models.IntegerField(default=0)
    errors_24h = models.IntegerField(default=0)
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/circulatory/circulate/` | GET | Run full circulation check |
| `/api/circulatory/status/` | GET | Cached flow status |
| `/api/circulatory/routes/` | GET | List all monitored routes |
| `/api/circulatory/bottlenecks/` | GET | Detect bottlenecks |
| `/api/circulatory/velocity/` | GET | Flow velocity metrics |
| `/api/circulatory/is-flowing/` | GET | Quick alive check |

### Status Levels

| Score | Status | Emoji |
|-------|--------|-------|
| 80-100% | flowing | 🩸 |
| 60-79% | slow | 🐌 |
| 40-59% | congested | ⚠️ |
| 0-39% | blocked | 🚫 |

### Celery Schedule

```python
'circulatory-system-pulse': {
    'task': 'core.tasks.check_circulation',
    'schedule': 45.0,  # Every 45 seconds
}
```

---

## 4. SPINE System - API Routing Health

**Session:** 704
**Purpose:** Monitor API route health, latency, error rates
**Metaphor:** Spine = Central routing backbone; Alignment = Route health

### Files

| File | Purpose |
|------|---------|
| `core/services/spine.py` | SpineRouterService singleton |
| `core/models_spine.py` | RoutePattern, RouteMetrics, SpineStatus models |
| `core/views_spine.py` | 6 API endpoints |
| `core/management/commands/spine_check.py` | CLI command |

### Database Models

#### RoutePattern (Configuration)
```python
class RoutePattern(models.Model):
    CATEGORIES = [
        ('agents', 'Agent APIs'),
        ('spiders', 'Spider APIs'),
        ('content', 'Content APIs'),
        ('business', 'Business APIs'),
        ('creative', 'Creative APIs'),
        ('scifi', 'Sci-Fi Feature APIs'),
        ('monitoring', 'Monitoring APIs'),
        ('llm', 'LLM/ML APIs'),
        ('admin', 'Admin APIs'),
        ('websocket', 'WebSocket APIs'),
        ('auth', 'Authentication APIs'),
    ]

    id = models.UUIDField(primary_key=True)
    pattern = models.CharField(max_length=255)  # URL pattern
    category = models.CharField(max_length=30, choices=CATEGORIES)

    # Thresholds
    max_latency_p50_ms = models.IntegerField(default=500)
    max_latency_p95_ms = models.IntegerField(default=2000)
    max_error_rate = models.FloatField(default=0.05)  # 5%

    # Dependencies
    requires_heart_healthy = models.BooleanField(default=False)
    requires_lungs_healthy = models.BooleanField(default=False)

    is_critical = models.BooleanField(default=False)
```

#### RouteMetrics (Time-Series)
```python
class RouteMetrics(models.Model):
    id = models.UUIDField(primary_key=True)
    pattern = models.ForeignKey(RoutePattern, on_delete=models.CASCADE)

    # Request counts
    requests_total = models.IntegerField(default=0)
    requests_successful = models.IntegerField(default=0)
    requests_failed = models.IntegerField(default=0)

    # Latency percentiles
    latency_p50_ms = models.FloatField(default=0)
    latency_p95_ms = models.FloatField(default=0)
    latency_p99_ms = models.FloatField(default=0)

    # Calculated
    error_rate = models.FloatField(default=0)
    health_score = models.FloatField(default=100)

    recorded_at = models.DateTimeField(auto_now_add=True)
```

#### SpineStatus (Cache)
```python
class SpineStatus(models.Model):
    STATUS_CHOICES = [
        ('aligned', 'Aligned'),
        ('strained', 'Strained'),
        ('compressed', 'Compressed'),
        ('injured', 'Injured'),
    ]

    id = models.UUIDField(primary_key=True)

    status = models.CharField(max_length=20)
    alignment_score = models.FloatField()  # 0-100

    # Pattern counts
    healthy_patterns = models.IntegerField(default=0)
    degraded_patterns = models.IntegerField(default=0)
    failed_patterns = models.IntegerField(default=0)

    # Integration status (ONLY SYSTEM THAT CHECKS OTHERS)
    heart_status = models.CharField(max_length=20, null=True)
    lungs_status = models.CharField(max_length=20, null=True)
    circulatory_status = models.CharField(max_length=20, null=True)
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/spine/align/` | GET | Full alignment check |
| `/api/spine/status/` | GET | Cached routing status |
| `/api/spine/patterns/` | GET | List all route patterns |
| `/api/spine/metrics/` | GET | Route performance metrics |
| `/api/spine/can-route/` | GET | Check if route allowed |
| `/api/spine/is-aligned/` | GET | Quick health check |

### Status Levels

| Score | Status | Emoji |
|-------|--------|-------|
| 80-100% | aligned | 🦴 |
| 60-79% | strained | ⚡ |
| 40-59% | compressed | 🔧 |
| 0-39% | injured | 🚨 |

### Integration Code (ONLY CROSS-SYSTEM INTEGRATION)

```python
# core/services/spine.py lines 648-697
def _check_heart_status(self) -> dict:
    """Check heart service status for routing decisions."""
    try:
        from core.services.heart import get_heart_monitor
        heart = get_heart_monitor()
        vitals = heart.get_vitals()
        return {
            'status': vitals.get('overall_status', 'unknown'),
            'score': vitals.get('health_score', 0),
            'is_healthy': vitals.get('is_alive', False)
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def _check_lungs_status(self) -> dict:
    """Check lungs service status for budget-aware routing."""
    # Similar implementation...

def _check_circulatory_status(self) -> dict:
    """Check circulatory service status for flow-aware routing."""
    # Similar implementation...
```

### Celery Schedule

```python
'spine-alignment-check': {
    'task': 'core.tasks.check_spine_alignment',
    'schedule': 120.0,  # Every 2 minutes
}
```

---

## 5. IMMUNE System - Security & Threat Detection

**Session:** 705
**Purpose:** Detect and respond to security threats
**Metaphor:** Antibodies = Threat patterns; Quarantine = IP/User blocking

### Files

| File | Purpose |
|------|---------|
| `core/services/immune.py` | ImmuneSystemService singleton |
| `core/models_immune.py` | ThreatPattern, ThreatEvent, Quarantine, ImmuneStatus models |
| `core/views_immune.py` | 7 API endpoints |
| `core/management/commands/immune_check.py` | CLI command |

### Database Models

#### ThreatPattern (Configuration - like antibodies)
```python
class ThreatPattern(models.Model):
    THREAT_CATEGORIES = [
        ('rate_abuse', 'Rate Limit Abuse'),
        ('auth_attack', 'Authentication Attack'),
        ('injection', 'Injection Attempt'),
        ('scraping', 'Scraping/Crawling'),
        ('dos', 'Denial of Service'),
        ('enumeration', 'Enumeration Attack'),
        ('privilege', 'Privilege Escalation'),
        ('data_exfil', 'Data Exfiltration'),
        ('bot', 'Bot Activity'),
        ('anomaly', 'Behavioral Anomaly'),
    ]

    DETECTION_TYPES = [
        ('signature', 'Signature Match'),
        ('threshold', 'Threshold Breach'),
        ('anomaly', 'Anomaly Detection'),
        ('reputation', 'Reputation Based'),
        ('behavioral', 'Behavioral Pattern'),
    ]

    RESPONSE_ACTIONS = [
        ('log', 'Log Only'),
        ('rate_limit', 'Apply Rate Limit'),
        ('block_temp', 'Temporary Block'),
        ('block_perm', 'Permanent Block'),
        ('quarantine', 'Full Quarantine'),
        ('alert', 'Alert Admin'),
    ]

    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=THREAT_CATEGORIES)
    detection_type = models.CharField(max_length=20, choices=DETECTION_TYPES)

    # Detection rules
    pattern = models.TextField()  # Regex or threshold rule
    threshold = models.IntegerField(null=True)  # For threshold-based
    window_seconds = models.IntegerField(default=60)  # Detection window

    # Response
    response_action = models.CharField(max_length=20, choices=RESPONSE_ACTIONS)
    block_duration_minutes = models.IntegerField(default=60)

    severity = models.IntegerField(default=50)  # 1-100
    is_active = models.BooleanField(default=True)
```

#### ThreatEvent (Time-Series)
```python
class ThreatEvent(models.Model):
    STATUS_CHOICES = [
        ('detected', 'Detected'),
        ('analyzing', 'Analyzing'),
        ('responded', 'Responded'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
        ('escalated', 'Escalated'),
    ]

    id = models.UUIDField(primary_key=True)
    pattern = models.ForeignKey(ThreatPattern, on_delete=models.CASCADE)

    # Source info
    source_ip = models.GenericIPAddressField(null=True)
    user_id = models.IntegerField(null=True)
    request_path = models.CharField(max_length=500)
    request_method = models.CharField(max_length=10)

    # Detection info
    confidence_score = models.FloatField()  # 0-1
    evidence = models.JSONField()  # Detection evidence

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response_taken = models.CharField(max_length=20, null=True)

    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True)
```

#### Quarantine (Active blocks)
```python
class Quarantine(models.Model):
    QUARANTINE_TYPES = [
        ('ip', 'IP Address'),
        ('user', 'User Account'),
        ('path', 'Request Path'),
        ('pattern', 'URL Pattern'),
    ]

    id = models.UUIDField(primary_key=True)
    quarantine_type = models.CharField(max_length=10, choices=QUARANTINE_TYPES)
    target = models.CharField(max_length=255)  # IP, user_id, or path

    reason = models.TextField()
    threat_event = models.ForeignKey(ThreatEvent, null=True)

    is_permanent = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True)

    blocked_requests = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
```

#### ImmuneStatus (Cache)
```python
class ImmuneStatus(models.Model):
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('alert', 'Alert'),
        ('fighting', 'Fighting'),
        ('overwhelmed', 'Overwhelmed'),
        ('compromised', 'Compromised'),
    ]

    THREAT_LEVELS = [
        ('none', 'None'),
        ('low', 'Low'),
        ('elevated', 'Elevated'),
        ('high', 'High'),
        ('severe', 'Severe'),
    ]

    id = models.UUIDField(primary_key=True)

    status = models.CharField(max_length=20)
    threat_level = models.CharField(max_length=20)
    immune_score = models.FloatField()  # 0-100

    # 24h metrics
    threats_detected_24h = models.IntegerField(default=0)
    threats_blocked_24h = models.IntegerField(default=0)
    false_positives_24h = models.IntegerField(default=0)

    # Active quarantines
    active_ip_blocks = models.IntegerField(default=0)
    active_user_blocks = models.IntegerField(default=0)
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/immune/scan/` | GET | Run security scan |
| `/api/immune/status/` | GET | Current immune status |
| `/api/immune/patterns/` | GET | List threat patterns |
| `/api/immune/threats/` | GET | List detected threats |
| `/api/immune/quarantine/` | GET | List quarantined entities |
| `/api/immune/is-healthy/` | GET | Quick health check |
| `/api/immune/check-request/` | GET | Check if request allowed |

### Status Levels

| Score | Status | Emoji |
|-------|--------|-------|
| 80-100% | healthy | 🛡️ |
| 60-79% | alert | ⚠️ |
| 40-59% | fighting | ⚔️ |
| 20-39% | overwhelmed | 🔥 |
| 0-19% | compromised | 💀 |

### Celery Schedule

```python
'immune-system-scan': {
    'task': 'core.tasks.run_immune_scan',
    'schedule': 300.0,  # Every 5 minutes
}
```

---

## 6. DIGESTIVE System - Data Ingestion & Processing

**Session:** 706
**Purpose:** Process spider data through ingestion pipeline
**Metaphor:** Eating = Data ingestion; Digestion = Processing; Nutrients = Routed data

### Files

| File | Purpose |
|------|---------|
| `core/services/digestive.py` | DigestiveSystemService singleton |
| `core/models_digestive.py` | IngestionRoute, DigestivePulse, DigestionStatus models |
| `core/views_digestive.py` | 6 API endpoints |
| `core/management/commands/digestion_check.py` | CLI command |

### Database Models

#### IngestionRoute (Configuration)
```python
class IngestionRoute(models.Model):
    ROUTE_TYPES = [
        ('spider', 'Spider Data'),
        ('api', 'API Ingestion'),
        ('webhook', 'Webhook'),
        ('upload', 'File Upload'),
        ('stream', 'Data Stream'),
    ]

    STAGES = [
        ('intake', 'Intake'),
        ('processing', 'Processing'),
        ('enrichment', 'Enrichment'),
        ('routing', 'Routing'),
    ]

    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    route_type = models.CharField(max_length=20, choices=ROUTE_TYPES)
    stage = models.CharField(max_length=20, choices=STAGES)

    # Thresholds
    max_queue_depth = models.IntegerField(default=1000)
    target_throughput = models.FloatField(default=10.0)  # items/min
    max_latency_ms = models.IntegerField(default=30000)

    is_critical = models.BooleanField(default=False)
```

#### DigestivePulse (Time-Series)
```python
class DigestivePulse(models.Model):
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('sluggish', 'Sluggish'),
        ('bloated', 'Bloated'),
        ('blocked', 'Blocked'),
        ('starving', 'Starving'),
    ]

    id = models.UUIDField(primary_key=True)

    overall_status = models.CharField(max_length=20)
    digestion_score = models.FloatField()  # 0-100

    # Stage metrics
    intake_status = models.CharField(max_length=20)
    processing_status = models.CharField(max_length=20)
    enrichment_status = models.CharField(max_length=20)
    routing_status = models.CharField(max_length=20)

    # 24h metrics
    items_ingested_24h = models.IntegerField(default=0)
    items_processed_24h = models.IntegerField(default=0)
    items_routed_24h = models.IntegerField(default=0)
    items_filtered_24h = models.IntegerField(default=0)

    # Metabolism
    intake_rate = models.FloatField(default=0)  # items/min
    processing_rate = models.FloatField(default=0)
    output_rate = models.FloatField(default=0)

    # Queue status
    items_pending = models.IntegerField(default=0)

    # Bottlenecks
    bottlenecks = models.JSONField(default=list)

    # Integration flags (NOT IMPLEMENTED)
    heart_connected = models.BooleanField(default=False)
    circulatory_connected = models.BooleanField(default=False)

    recorded_at = models.DateTimeField(auto_now_add=True)
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/digestive/digest/` | GET | Run digestion check |
| `/api/digestive/status/` | GET | Digestion status |
| `/api/digestive/routes/` | GET | Ingestion routes |
| `/api/digestive/bottlenecks/` | GET | Detected bottlenecks |
| `/api/digestive/metabolism/` | GET | Processing rates |
| `/api/digestive/is-digesting/` | GET | Quick alive check |

### Status Levels

| Score | Status | Emoji |
|-------|--------|-------|
| 80-100% | healthy | 🍽️ |
| 60-79% | sluggish | 🐌 |
| 40-59% | bloated | 🎈 |
| 20-39% | blocked | 🚫 |
| 0-19% | starving | 💀 |

### Pipeline Stages

```
INTAKE → PROCESSING → ENRICHMENT → ROUTING
   ↓          ↓            ↓           ↓
Spiders   Normalize    Embeddings   To Agents
collect   Deduplicate  Scoring      Solutions
```

### Celery Schedule

```python
'digestive-system-check': {
    'task': 'core.tasks.check_digestion',
    'schedule': 180.0,  # Every 3 minutes
},
'process-spider-data': {
    'task': 'core.tasks.process_core_spider_data',
    'schedule': 120.0,  # Every 2 minutes
}
```

---

## 7. MUSCULAR System - Agent Work Execution

**Session:** 707
**Purpose:** Monitor agent execution success, fatigue, and strain
**Metaphor:** Muscles = Agent groups; Strength = Success rate; Fatigue = High load

### Files

| File | Purpose |
|------|---------|
| `core/services/muscular.py` | MuscularSystemService singleton |
| `core/models_muscular.py` | MuscleGroup, MuscularPulse, MuscleStatus models |
| `core/views_muscular.py` | 8 API endpoints |
| `core/management/commands/muscular_check.py` | CLI command |

### Database Models

#### MuscleGroup (Configuration)
```python
class MuscleGroup(models.Model):
    CATEGORY_CHOICES = [
        ('creation', 'Creation Agents'),
        ('research', 'Research Agents'),
        ('strategy', 'Strategy Agents'),
        ('development', 'Development Agents'),
        ('blockchain', 'Blockchain Agents'),
        ('stocks', 'Stock Analysis Agents'),
        ('executive', 'Executive Agents'),
        ('narrative', 'Narrative Agents'),
        ('orchestration', 'Orchestration Agents'),
        ('markets', 'Market Agents'),
    ]

    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    # Agent membership
    agent_names = models.JSONField(default=list)  # List of agent names

    # Thresholds
    target_success_rate = models.FloatField(default=90.0)  # %
    max_avg_execution_time_ms = models.IntegerField(default=30000)
    max_fatigue_level = models.FloatField(default=80.0)
    max_daily_executions = models.IntegerField(default=1000)

    is_critical = models.BooleanField(default=False)
```

#### MuscularPulse (Time-Series)
```python
class MuscularPulse(models.Model):
    STATUS_CHOICES = [
        ('strong', 'Strong'),
        ('fit', 'Fit'),
        ('fatigued', 'Fatigued'),
        ('strained', 'Strained'),
        ('paralyzed', 'Paralyzed'),
    ]

    id = models.UUIDField(primary_key=True)

    overall_status = models.CharField(max_length=20)
    strength_score = models.FloatField()  # 0-100

    # 24h execution metrics
    total_executions_24h = models.IntegerField(default=0)
    successful_executions_24h = models.IntegerField(default=0)
    failed_executions_24h = models.IntegerField(default=0)
    success_rate_24h = models.FloatField(default=0)

    # Performance
    avg_execution_time_ms = models.FloatField(default=0)
    total_tokens_used_24h = models.IntegerField(default=0)
    total_cost_24h = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    # Agent counts
    active_agents = models.IntegerField(default=0)
    fatigued_agents = models.IntegerField(default=0)
    strained_agents = models.IntegerField(default=0)

    # Group breakdown
    group_metrics = models.JSONField(default=dict)

    # Issues
    weak_muscles = models.JSONField(default=list)  # Low success rate
    overworked_muscles = models.JSONField(default=list)  # High execution count

    recorded_at = models.DateTimeField(auto_now_add=True)
```

#### MuscleStatus (Cache per group)
```python
class MuscleStatus(models.Model):
    group = models.OneToOneField(MuscleGroup, primary_key=True)

    status = models.CharField(max_length=20)  # strong/fit/fatigued/strained/paralyzed
    is_healthy = models.BooleanField(default=True)

    # Metrics
    strength_score = models.FloatField(default=100.0)
    fatigue_level = models.FloatField(default=0)  # 0-100 (higher = more tired)
    strain_level = models.FloatField(default=0)  # 0-100 (higher = more errors)

    # 24h rolling
    executions_24h = models.IntegerField(default=0)
    success_rate_24h = models.FloatField(default=100.0)
    avg_execution_time_ms = models.FloatField(default=0)
    tokens_used_24h = models.IntegerField(default=0)

    # Agent counts
    total_agents = models.IntegerField(default=0)
    active_agents = models.IntegerField(default=0)
    idle_agents = models.IntegerField(default=0)

    # Best/worst performers
    top_performer = models.CharField(max_length=100, null=True)
    worst_performer = models.CharField(max_length=100, null=True)
```

### Default Muscle Groups (10)

| Group Name | Category | Agents | Critical |
|------------|----------|--------|----------|
| Creation Muscles | creation | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent | No |
| Research Muscles | research | ResearchAgent | Yes |
| Strategy Muscles | strategy | ContentStrategyAgent, BrandIdentityAgent, SEOOptimizerAgent, SocialMediaAgent | No |
| Development Muscles | development | CodeGeneratorAgent, FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent | Yes |
| Blockchain Muscles | blockchain | BlockchainAuditCoordinator, SmartContractAuditorAgent, TransactionMonitorAgent, WhaleWatcherAgent, ExploitDetectorAgent | No |
| Stock Analysis Muscles | stocks | StockAuditCoordinator, StockAnalystAgent, MarketMovementMonitorAgent, BullCaseAgent, BearCaseAgent | Yes |
| Executive Muscles | executive | CTOAgent, COOAgent, CreativeDirectorAgent, MeetingCoordinatorAgent | No |
| Narrative Muscles | narrative | NarrativeDriftCoordinator, NarrativeHistorianAgent, TrendBreakDetectorAgent, CulturalImpactAgent | No |
| Orchestration Muscles | orchestration | WorkflowAgent, WorkflowOrchestrationAgent, OpportunityPipelineAgent, ContentExecutorAgent | Yes |
| Market Muscles | markets | PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector | No |

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/muscular/flex/` | GET | Run muscle check |
| `/api/muscular/status/` | GET | Muscle status |
| `/api/muscular/groups/` | GET | Agent muscle groups |
| `/api/muscular/groups/<id>/` | GET | Specific group status |
| `/api/muscular/weak/` | GET | Weak agents |
| `/api/muscular/overworked/` | GET | Overworked agents |
| `/api/muscular/history/` | GET | Muscular pulse history |
| `/api/muscular/is-strong/` | GET | Quick health check |

### Status Levels

| Score | Status | Emoji |
|-------|--------|-------|
| 80-100% | strong | 💪 |
| 60-79% | fit | 🏃 |
| 40-59% | fatigued | 😓 |
| 20-39% | strained | 🥵 |
| 0-19% | paralyzed | 🦽 |

### Celery Schedule

```python
'muscular-system-check': {
    'task': 'core.tasks.check_muscular',
    'schedule': 90.0,  # Every 90 seconds
}
```

---

## Summary Table

| System | Session | Service File | Model File | Endpoints | Schedule |
|--------|---------|--------------|------------|-----------|----------|
| HEART | 701 | `heart.py` | `models_heart.py` | 5 | 60s |
| LUNGS | 702 | `lungs.py` | `models_lungs.py` | 7 | 30s |
| CIRCULATORY | 703 | `circulatory.py` | `models_circulatory.py` | 6 | 45s |
| SPINE | 704 | `spine.py` | `models_spine.py` | 6 | 120s |
| IMMUNE | 705 | `immune.py` | `models_immune.py` | 7 | 300s |
| DIGESTIVE | 706 | `digestive.py` | `models_digestive.py` | 6 | 180s |
| MUSCULAR | 707 | `muscular.py` | `models_muscular.py` | 8 | 90s |

---

## Related Documentation

- [BODY_ARCHITECTURE.md](./BODY_ARCHITECTURE.md) - System overview and architecture diagram
- [BODY_INTEGRATION_GAPS.md](./BODY_INTEGRATION_GAPS.md) - Complete gap analysis
- [BODY_IMPLEMENTATION_ROADMAP.md](./BODY_IMPLEMENTATION_ROADMAP.md) - Phased implementation plan
