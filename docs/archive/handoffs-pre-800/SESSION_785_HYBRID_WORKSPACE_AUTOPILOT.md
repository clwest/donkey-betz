# Session 785: Hybrid Workspace Autopilot

**Date:** January 20, 2026
**Status:** COMPLETE

## Problem Statement

Agents weren't executing autonomous workspace operations despite having 14+ scheduled tasks defined in `celery.py`. Root cause: Celery Beat uses `DatabaseScheduler` which completely ignores static `beat_schedule` definitions in Python code - tasks must be registered in the database.

## Solution: Hybrid Event-Driven Architecture

Based on ChatGPT's recommendation, implemented a hybrid approach that combines:
1. **Event-driven trigger insertion** - WorkspaceTrigger records created on SpiderData save
2. **Single conductor task** - workspace_autopilot_tick drains the queue periodically
3. **Configurable rules** - WorkspaceTriggerConfig defines what triggers fire

### Architecture Flow

```
SpiderData.post_save
       |
       v
evaluate_workspace_triggers_for_spider_data()
       |
       v (checks all active WorkspaceTriggerConfigs)
       |
       v (if match)
WorkspaceTrigger.create_from_spider_data()
       |
       v (queued with TTL, priority, dedupe)
       |
       v (every 5 minutes)
workspace_autopilot_tick() conductor
       |
       v (up to budget_per_tick)
Route to agent → Execute → Update status
```

## New Models

### WorkspaceTriggerType (Enum)
- `spider_code_insight` - Code/Tech insights from spiders
- `spider_security_alert` - Security vulnerabilities
- `spider_market_signal` - Market/financial signals
- `spider_content_idea` - Content creation triggers
- `spider_trend_alert` - Trending topics
- `spider_dependency_update` - Dependency/version updates
- `spider_competitor_move` - Competitor intelligence
- `spider_research_finding` - Research discoveries

### WorkspaceTrigger
Event-driven work queue item:
- `trigger_type` - One of WorkspaceTriggerType
- `title` - Human-readable description
- `source_spider_data` - FK to triggering SpiderData
- `target_agent` - Optional specific agent
- `target_category` - Optional category for routing
- `priority` - P0 (critical) to P3 (low)
- `status` - pending/processing/completed/failed/expired/skipped
- `expires_at` - TTL expiration timestamp
- `dedupe_hash` - SHA256 hash for deduplication
- `context_data` - JSON payload for agent
- `result_data` - JSON result from agent execution

Class methods:
- `create_from_spider_data()` - Factory with automatic TTL and dedupe
- `get_pending_triggers()` - Query pending work with filters

### WorkspaceTriggerConfig
Rule configuration for when to create triggers:
- `name` - Unique rule name
- `trigger_type` - Type to create when matched
- `match_field` - Dot-notation path in SpiderData.raw_data
- `match_operator` - contains, regex, gt, lt
- `match_value` - Value/pattern to match
- `target_spiders` - Optional spider name filter
- `target_agent` - Agent to route to
- `target_category` - Category for routing
- `priority` - Default priority for triggers
- `ttl_hours` - Time-to-live for triggers
- `cooldown_minutes` - Rate limiting
- `trigger_title_template` - Dynamic title with variables

## Conductor Task

`workspace_autopilot_tick(budget_per_tick=5, min_priority=None, category=None, dry_run=False)`

1. Mark expired triggers as 'expired'
2. Get pending triggers (respects budget, priority, category)
3. For each trigger:
   - Mark as 'processing'
   - Route to appropriate agent
   - Execute via agent.process_request() or health_check()
   - Mark as 'completed' or 'failed'
   - Store result_data

### Agent Routing

Routing priority:
1. `trigger.target_agent` - Explicit agent name
2. `trigger.target_category` → category agent map
3. `trigger.trigger_type` → type agent map
4. Default: SystemIntelligenceAgent

## Default Trigger Configs

| Name | Match | Target | Priority |
|------|-------|--------|----------|
| Security Alert Scanner | title contains vulnerability\|exploit\|CVE\|security | SecuritySystemMonitor | P0 |
| Dependency Update Detector | title contains update\|upgrade\|version\|release | DependencyAnalyst | P1 |
| Code Best Practice Monitor | content regex (TODO\|FIXME\|HACK\|XXX) | CodeQualityReviewer | P2 |
| Bug Pattern Detector | title contains bug\|error\|crash\|fail | BugTriageAgent | P1 |

## Files Created/Modified

### New Files
- `core/management/commands/setup_workspace_autopilot.py` - Management command
- `core/migrations/0179_workspace_triggers_session_785.py` - Migration

### Modified Files
- `core/models_skin_layer.py` - Added 3 models + DEFAULT_WORKSPACE_TRIGGER_CONFIGS
- `core/signals/trigger_signals.py` - Added workspace trigger evaluation
- `core/tasks.py` - Added workspace_autopilot_tick
- `core/admin.py` - Added WorkspaceTriggerAdmin, WorkspaceTriggerConfigAdmin

## Setup Commands

```bash
# Create PeriodicTask in DB
python manage.py setup_workspace_autopilot

# With custom settings
python manage.py setup_workspace_autopilot --interval=300 --budget=5

# Also seed default configs
python manage.py setup_workspace_autopilot --seed-configs

# Preview without changes
python manage.py setup_workspace_autopilot --dry-run

# Disable autopilot
python manage.py setup_workspace_autopilot --disable
```

## Verification

```bash
# Check configs
python manage.py shell -c "from core.models_skin_layer import WorkspaceTriggerConfig; print(f'Active: {WorkspaceTriggerConfig.objects.filter(is_active=True).count()}')"

# Check PeriodicTask
python manage.py shell -c "from django_celery_beat.models import PeriodicTask; t=PeriodicTask.objects.filter(name='Workspace Autopilot Conductor').first(); print(f'{t.name}: enabled={t.enabled}, interval={t.interval}')"

# Check pending triggers
python manage.py shell -c "from core.models_skin_layer import WorkspaceTrigger; print(f'Pending: {WorkspaceTrigger.objects.filter(status=\"pending\").count()}')"

# Manual dry run
python manage.py shell -c "from core.tasks import workspace_autopilot_tick; workspace_autopilot_tick(dry_run=True)"
```

## Benefits

1. **Database-driven** - Works with Celery Beat's DatabaseScheduler
2. **Event-driven** - Triggers created immediately when spider data arrives
3. **Budget-controlled** - Prevents overload with budget_per_tick
4. **Deduplicated** - Hash-based deduplication prevents duplicate work
5. **TTL-expiring** - Stale triggers auto-expire
6. **Configurable** - Rules can be added/modified via admin
7. **Auditable** - Full history of trigger creation and execution
8. **Priority-aware** - Critical triggers processed first

## Future Enhancements

1. Frontend trigger dashboard in React
2. Trigger analytics and effectiveness metrics
3. Manual trigger creation UI
4. Webhook notifications for high-priority triggers
5. More sophisticated routing (load balancing, capability matching)
