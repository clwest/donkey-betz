# Session 702: LUNGS Service - Resource & Capacity Management

**Date:** January 6, 2026
**Status:** COMPLETE
**Duration:** 1 session

---

## Overview

Implemented the **LUNGS** (Limits, Usage, Notifications, Governance, Spending) service - the resource and capacity management system that controls "breathing" (token consumption) across all LLM providers.

---

## Human Body Metaphor

The LUNGS manage the system's "breathing" - taking in resources (API credits) and expelling them (token consumption):

| Breathing Concept | Technical Equivalent |
|-------------------|---------------------|
| **Inhale** | Budget allocation (credits available) |
| **Exhale** | Token consumption (usage) |
| **Breath Cycle** | Budget period (daily/weekly/monthly) |
| **Lung Capacity** | Total budget limit |
| **Oxygen Level** | Remaining budget % |
| **Hyperventilation** | Overspending alert |
| **Holding Breath** | Rate limit pause |
| **Respiratory Rate** | Calls per minute |

---

## Files Created (5)

| File | Lines | Purpose |
|------|-------|---------|
| `core/models_lungs.py` | ~250 | Budget, BreathCycle, RespiratoryStatus models |
| `core/services/lungs.py` | ~450 | LungsCapacityService singleton class |
| `core/views_lungs.py` | ~350 | 9 API endpoints |
| `core/management/commands/lungs_check.py` | ~443 | CLI command with 8 modes |
| `core/migrations/0148_session_702_lungs_service.py` | ~300 | Migration + 6 default budgets |

## Files Modified (4)

| File | Changes |
|------|---------|
| `core/urls.py` | Added 9 LUNGS API routes |
| `core/tasks.py` | Added 3 Celery tasks |
| `core/celery.py` | Added 3 Beat schedules |
| `core/admin.py` | Registered 3 LUNGS models |

---

## Database Models

### 1. Budget - Budget Configuration

```python
class Budget(models.Model):
    """Budget limits for token/cost consumption."""

    PERIOD_CHOICES = [('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')]
    SCOPE_CHOICES = [('system', 'System-wide'), ('provider', 'Per Provider'), ('agent', 'Per Agent')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    scope_identifier = models.CharField(max_length=100, blank=True)  # provider/agent name
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)

    token_limit = models.BigIntegerField(null=True, blank=True)  # Max tokens per period
    cost_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Max USD

    warning_threshold = models.FloatField(default=0.8)  # Alert at 80%
    critical_threshold = models.FloatField(default=0.95)  # Critical at 95%

    is_active = models.BooleanField(default=True)
    enforce_hard_limit = models.BooleanField(default=False)  # Alerts only, not blocking
```

### 2. BreathCycle - Period Tracking (Time-Series)

```python
class BreathCycle(models.Model):
    """Tracks resource consumption per budget period."""

    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    tokens_used = models.BigIntegerField(default=0)
    cost_incurred = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    call_count = models.IntegerField(default=0)

    utilization_percent = models.FloatField(default=0)  # 0-100%
    warning_sent = models.BooleanField(default=False)
    critical_sent = models.BooleanField(default=False)
    on_pace_to_exceed = models.BooleanField(default=False)
```

### 3. RespiratoryStatus - Current Breathing State (Cache)

```python
class RespiratoryStatus(models.Model):
    """Current breathing status - cached state."""

    STATUS_CHOICES = [
        ('normal', 'Normal Breathing'),
        ('elevated', 'Elevated Usage'),
        ('hyperventilating', 'Over Budget'),
        ('holding', 'Rate Limited'),
    ]

    component = models.CharField(primary_key=True, max_length=50)
    display_name = models.CharField(max_length=100)
    status = models.CharField(choices=STATUS_CHOICES, default='normal')
    oxygen_level = models.FloatField(default=100.0)  # Budget remaining %
    respiratory_rate = models.FloatField(default=0)  # Calls per minute
```

---

## LungsCapacityService

Singleton pattern following HEART service:

```python
_lungs_instance: Optional['LungsCapacityService'] = None

def get_lungs_monitor() -> 'LungsCapacityService':
    """Get the singleton LUNGS monitor instance."""
    global _lungs_instance
    if _lungs_instance is None:
        _lungs_instance = LungsCapacityService()
    return _lungs_instance
```

### Key Methods

| Method | Purpose |
|--------|---------|
| `breathe()` | Run full breathing check - aggregate all consumption |
| `can_breathe(provider, agent, estimated_tokens)` | Check if an LLM call is allowed within budget |
| `record_breath(provider, agent, tokens, cost)` | Record token consumption after call |
| `check_oxygen_level(scope, identifier)` | Get remaining budget percentage |
| `forecast_end_of_period(budget)` | Project end-of-period usage |
| `get_spending_velocity(hours)` | Calculate current spending rate |
| `get_current_cycle(budget)` | Get or create current period's breath cycle |
| `check_and_alert(cycle)` | Send Discord alerts if thresholds crossed |

---

## API Endpoints (9)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/lungs/breathe/` | GET | Run full breathing check |
| `/api/lungs/status/` | GET | Get cached respiratory status |
| `/api/lungs/oxygen/` | GET | Get remaining budget % |
| `/api/lungs/budgets/` | GET/POST | List or create budgets |
| `/api/lungs/budgets/<id>/` | PUT/DELETE | Update or delete budget |
| `/api/lungs/forecast/` | GET | Get spending forecast |
| `/api/lungs/history/` | GET | Get breath cycle history |
| `/api/lungs/can-breathe/` | GET | Check if call allowed |
| `/api/lungs/alive/` | GET | Quick alive check |

---

## CLI Command

```bash
# Usage examples:
python manage.py lungs_check                    # Full breathing status
python manage.py lungs_check --json             # JSON output
python manage.py lungs_check --oxygen           # Just oxygen levels
python manage.py lungs_check --forecast         # Show spending forecast
python manage.py lungs_check --velocity         # Show spending velocity
python manage.py lungs_check --watch            # Continuous monitoring (15 min)
python manage.py lungs_check --history          # Show breath cycle history
python manage.py lungs_check --budgets          # List all budgets
python manage.py lungs_check --provider openai  # Check specific provider
python manage.py lungs_check --agent ResearchAgent  # Check specific agent
```

---

## Celery Integration

### Tasks (3)

| Task | Purpose |
|------|---------|
| `check_breathing` | Run breathing check, update cycles, send alerts |
| `daily_cost_forecast` | Generate daily forecast, send to Discord |
| `reset_daily_respiratory_stats` | Reset daily stats at midnight |

### Beat Schedules (3)

| Schedule | Frequency | Task |
|----------|-----------|------|
| `lungs-service-breathing` | Every 15 minutes | `check_breathing` |
| `lungs-daily-forecast` | Daily at 8 AM | `daily_cost_forecast` |
| `lungs-daily-reset` | Daily at 00:01 | `reset_daily_respiratory_stats` |

---

## Default Budgets (6)

Created by migration:

| Budget | Scope | Period | Cost Limit |
|--------|-------|--------|------------|
| System Daily | system | daily | $50.00 |
| System Monthly | system | monthly | $500.00 |
| OpenAI Daily | provider/openai | daily | $30.00 |
| Anthropic Daily | provider/anthropic | daily | $20.00 |
| Together AI Daily | provider/together_ai | daily | $10.00 |
| DeepSeek Daily | provider/deepseek | daily | $10.00 |

---

## Status Levels

| Oxygen Level | Status | Visual |
|--------------|--------|--------|
| 80-100% | `normal` | Green bar |
| 50-79% | `elevated` | Yellow bar |
| 20-49% | `hyperventilating` | Red bar |
| 0-19% | `holding` | Critical alert |

---

## Test Results

```
============================================================
  LUNGS SERVICE - Resource & Capacity Check
  The Breathing of the AI Body
============================================================

  Overall Status: NORMAL (O2: 100.0%)
  Respiratory Rate: 0.0 calls/min
  Budgets Checked: 6
  Can Breathe: Yes
  Check Duration: 22ms

  System Budget:
  --------------------------------------------------------
    O2 Level: 100.0%
    Status: NORMAL
    Cost Today: $0.0000
    Tokens Used: 0
    Calls: 0
    Limit: $50.00
    Remaining: $50.00

  Provider Budgets:
  --------------------------------------------------------
  OPENAI:
      O2 Level: 100.0%
      Status: NORMAL
  ANTHROPIC:
      O2 Level: 100.0%
      Status: NORMAL
  TOGETHER_AI:
      O2 Level: 100.0%
      Status: NORMAL
  DEEPSEEK:
      O2 Level: 100.0%
      Status: NORMAL

============================================================
```

---

## Integration with Existing Systems

LUNGS integrates with existing infrastructure:

1. **LLMCallLog** - Aggregates cost/token data from existing call logs
2. **AgentLLMConfig** - Tracks per-agent cumulative costs
3. **LLMProviderRegistry** - Uses provider cost calculations
4. **Discord** - Sends alerts when thresholds crossed

---

## Human Body Architecture (Updated)

| Body Part | Technical Component | Purpose |
|-----------|---------------------|---------|
| **CONSCIOUSNESS** | Human Operator | Final decisions, approvals |
| **EYES/EARS** | HumanInterfaceLayer | Attention aggregation |
| **BRAIN** | ThinkingAgent | Complex reasoning and evaluation |
| **HEART** | HeartMonitorService | Health monitoring (Session 701) |
| **LUNGS** | LungsCapacityService | **Resource & capacity management (NEW)** |
| **NERVOUS SYSTEM** | LLM/ML Routers | Signal routing |
| **ORGANS** | 72 Specialized Agents | Work execution |
| **SENSORY** | 77 Spiders | Data gathering |
| **SKIN** | WorkspaceManager | Interface with reality |
| **MEMORY** | Database & Redis | Persistence |

---

## Next Body Parts to Consider

1. **CIRCULATORY SYSTEM** - Data flow infrastructure (Redis as bloodstream)
2. **SPINE** - Central API routing backbone
3. **IMMUNE SYSTEM** - Security and threat detection

---

## Session 702 Complete

- 5 new files created (~1,800 lines)
- 4 files modified
- 3 database models
- 9 API endpoints
- 3 Celery tasks + schedules
- 6 default budgets
- Full CLI management command
