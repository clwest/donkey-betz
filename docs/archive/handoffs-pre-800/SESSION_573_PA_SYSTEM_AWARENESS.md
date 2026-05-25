# Session 573: PA System Awareness + Celery Multi-Queue Architecture

**Date:** December 28, 2025
**Status:** Complete

## Overview

This session implemented two major enhancements:

1. **Celery Multi-Queue Architecture** - Fixed "cloggage" by separating long-running tasks from quick tasks
2. **PA System Awareness** - The Personal Assistant now knows what needs attention across all 3 main sections

---

## Part 1: Celery Multi-Queue Architecture

### Problem
- Single default queue handling 450+ task triggers/hour
- Only 4 threads for all tasks
- Long-running tasks (spider network, agent conversations, dreams) blocking quick tasks
- No queue routing for task segregation

### Solution: 3-Worker Architecture

| Worker | Queue | Concurrency | Tasks |
|--------|-------|-------------|-------|
| `default@` | default, agents, sports, content, ml | 4 threads | Quick tasks (<1 min) |
| `long_running@` | long_running | 2 threads | Spider network, agent dreams, conversations |
| `broadcast@` | broadcast | 2 threads | High-frequency status updates (60-180s) |

### Files Modified

**`core/settings.py`**
- Added comprehensive `CELERY_TASK_ROUTES` for multi-queue architecture
- Routes 15+ long-running tasks to `long_running` queue
- Routes 10 broadcast tasks to `broadcast` queue

**`Makefile`**
- Updated `celery` target to start 3 workers + beat
- Added variables for new log files and PIDs
- Updated `celery-stop`, `celery-status`, `celery-logs` targets

**`core/celery.py`**
- Updated comments to reference settings.py for routing configuration
- Documented multi-queue architecture

---

## Part 2: PA System Awareness (SystemStateAggregator)

### Problem
User must manually check 3 sections (Command Center, Autonomous, Research) to see what needs attention. The PA should aggregate all system state and proactively surface what requires action.

### Solution: SystemStateAggregator Service

New service that aggregates attention items from all 3 UI sections with priority scoring.

### Data Structure

```python
@dataclass
class AttentionItem:
    id: str
    section: str        # 'command_center', 'autonomous', 'research'
    category: str       # 'alert', 'health', 'overdue', 'stale', etc.
    priority: int       # 1-100 (higher = urgent)
    title: str
    summary: str
    action_url: str
```

### What Each Section Contributes

**Command Center:**
- Failed autonomous thinking cycles (24h)
- Recurring concerns (came back after being resolved)
- Stale concerns (active > 7 days)

**Autonomous:**
- Content channels overdue for content
- Unverified narrative shifts
- Critical trigger events
- Failed autonomous actions

**Research:**
- Stale spiders (no data in 24h)
- High-value pending dreams (score >= 0.75)
- Pending boardroom decisions

### Priority Scoring

| Category | Base Priority |
|----------|---------------|
| Critical alert | 90 |
| Security alert | 85 |
| Health failure | 80 |
| Execution failure | 75 |
| Overdue task | 70 |
| Recurring concern | 65 |
| Stale concern | 60 |
| Pending decision | 50 |
| Opportunity | 40 |

### Conditional Injection

System state is injected into PA context when:
1. User asks status-related questions ("what should I focus on?", "catch me up", "status", etc.)
2. There are urgent items (priority >= 80)

### Files Created

**`core/services/system_state_aggregator.py`** (NEW - 500 lines)
- `SystemStateAggregator` class
- `AttentionItem` dataclass
- Section-specific query methods
- Caching layer (60s TTL)
- PA context formatting

### Files Modified

**`core/services/pa_intelligence_enricher.py`**
- Added `include_system_state` config option
- Added `_query_system_state()` method
- Added system state keywords list
- Updated `_format_context()` to include system state
- Updated `_build_attribution()` for system state

**`core/agents/base_agent.py`**
- Updated total_sources calculation in `_build_prompt_with_attribution()` to include system_state_count

**`core/tasks.py`**
- Added `refresh_system_state_cache()` Celery task

**`core/celery.py`**
- Added `refresh-system-state-cache` schedule (every 60s)

**`core/settings.py`**
- Added `refresh_system_state_cache` to broadcast queue routing

---

## Testing

```bash
# Test SystemStateAggregator
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django
django.setup()
from core.services.system_state_aggregator import get_system_state_aggregator

aggregator = get_system_state_aggregator()
items = aggregator.get_attention_items()
print(f'Items: {len(items)}')
for item in items[:5]:
    print(f'  - [{item.section}] {item.title} (priority: {item.priority})')
"

# Test PA Intelligence Enricher
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django
django.setup()
from core.services.pa_intelligence_enricher import PAIntelligenceEnricher

enricher = PAIntelligenceEnricher()
result = enricher.enrich_context('What should I focus on?')
print(f'System state count: {result[\"metadata\"].get(\"system_state_count\", 0)}')
"
```

---

## Usage

### User Queries That Trigger System State

- "What should I focus on?"
- "Catch me up"
- "What needs attention?"
- "System status"
- "Give me an overview"
- "What's going on?"
- "Action items"

### PA Response Examples

When system state is injected, the PA will see context like:

```markdown
### URGENT - Needs Immediate Attention:
- [Command Center] Thinking Cycle Failed: Cycle from 14:32 failed: ...

### Important System Items:
- [Research] Stale Spiders (1): No data in 24h: coindesk
- [Research] Dream: Content Contracts for Safe Iteratio
```

---

## Architecture Diagram

```
User Query ("What should I focus on?")
        ↓
PersonalAssistantAgent
        ↓
PAIntelligenceEnricher
        ↓ (detects status keywords)
SystemStateAggregator
    ├── _get_command_center_items()
    ├── _get_autonomous_items()
    └── _get_research_items()
        ↓
AttentionItem[] (sorted by priority)
        ↓
format_for_pa_context()
        ↓
Injected into PA prompt
```

---

## Future Enhancements

1. **Discord Integration** - Surface urgent items in Discord bot responses
2. **Push Notifications** - Send alerts for critical items (priority >= 90)
3. **Historical Tracking** - Track how long items stay in attention list
4. **Custom Thresholds** - User-configurable priority thresholds
5. **Section Weights** - Allow users to weight sections differently

---

## Summary

Session 573 delivered:
- **Celery Multi-Queue Architecture**: 3 workers handling tasks by type
- **PA System Awareness**: PA now knows what needs attention across all sections
- **Conditional Context**: Only injects system state when relevant or urgent
- **Cached Performance**: 60s cache TTL with background refresh task
