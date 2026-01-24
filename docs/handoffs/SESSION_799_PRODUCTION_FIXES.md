# Session 799: Production Fixes & Seeding

**Date:** January 23, 2026
**Focus:** Production data investigation, bug fixes, and database seeding
**PRs Merged:** 6 (#38, #39, #40, #41, #42, #43)

---

## Summary

Session 799 investigated why production pages weren't showing data and fixed multiple Celery/runtime errors discovered during investigation. Created a production seeding command and fixed the Personal Assistant's overly aggressive system command detection.

---

## Bug Fixes

### 1. broadcast_evolution_status XPHistory Fields (PR #38)

**Error:** `Invalid field name(s) given in select_related: 'evolution'`

**Root Cause:** `XPHistory` model has a direct `agent` ForeignKey, not through `evolution`.

**File:** `core/tasks.py`

```python
# Before (wrong)
recent_xp = XPHistory.objects.select_related('evolution__agent')
xp.evolution.agent.name
xp.amount

# After (fixed)
recent_xp = XPHistory.objects.select_related('agent')
xp.agent.name
xp.xp_amount
```

### 2. scifi_integration AgentMemory Query (PR #39)

**Error:** `Cannot resolve keyword 'user' into field`

**Root Cause:** `AgentMemory` model doesn't have a `user` field - memories are per-agent.

**File:** `core/super_platform/scifi_integration.py`

```python
# Before (wrong)
memories = AgentMemory.objects.filter(agent__name=agent_name, user=user)

# After (fixed)
memories = AgentMemory.objects.filter(agent__name=agent_name)
```

### 3. PA System Command Detection (PR #42)

**Issue:** "Tell me about this system" took 3+ minutes and returned generic help message instead of AI response.

**Root Cause:** Word "system" triggered system command mode incorrectly.

**File:** `core/personal_ai_assistant_enhanced.py`

```python
# Before - keyword matching (too broad)
system_keywords = ['database', 'system', 'status', ...]
is_system_command = any(kw in message_lower for kw in system_keywords)

# After - specific command patterns (precise)
system_command_patterns = [
    'check database',
    'database status',
    'list agents',
    'execute agent',
    'run agent',
    ...
]
is_system_command = any(pattern in message_lower for pattern in system_command_patterns)
```

### 4. execute_action_plan Celery Beat (PR #43)

**Error:** `execute_action_plan() missing 1 required positional argument: 'action_plan_id'`

**Root Cause:** Celery Beat schedule called task directly without required argument.

**Files:** `intelligence/tasks.py`, `core/celery.py`

**Solution:** Created wrapper task that finds pending ActionPlans:

```python
@shared_task
def process_pending_action_plans():
    """Find ActionPlans with status='created' and queue execution."""
    pending_plans = ActionPlan.objects.filter(status='created')[:5]
    for plan in pending_plans:
        execute_action_plan.delay(str(plan.id))
    return {"status": "success", "plans_queued": len(pending_plans)}
```

---

## Production Seeding Command (PR #40, #41)

Created `core/management/commands/seed_production.py` to initialize production with essential infrastructure.

### Usage

```bash
# On Railway
railway run python manage.py seed_production

# Local
python manage.py seed_production

# Dry run (preview without changes)
python manage.py seed_production --dry-run
```

### What It Creates

**5 Content Channels:**
| Channel | Topic Domain | Frequency |
|---------|--------------|-----------|
| Tech & AI Insights | AI, ML, tech trends, software | daily |
| Market Intelligence | stocks, crypto, financial trends | daily |
| Sports Analytics | betting, odds, predictions | daily |
| Career & Jobs | job market, career advice | weekly |
| AI Podcast Studio | AI discussions, debates | weekly |

**7 System Configurations:**
- autonomous_content_enabled
- spider_network_enabled
- agent_learning_enabled
- dream_generation_enabled
- opportunity_scoring_enabled
- max_daily_content_items (50)
- spider_refresh_interval_minutes (30)

---

## Production Audit Script

Created `scripts/production_data_audit.sh` to compare production vs local data.

```bash
# Usage
PROD_URL=https://your-app.railway.app PROD_TOKEN=your_token ./scripts/production_data_audit.sh
```

### Local Baseline (Session 799)
| Model | Count |
|-------|-------|
| Agent | 213 |
| AgentExecution | 904 |
| ContentChannel | 9 |
| ChannelEpisode | 162 |
| ContentDebate | 82 |
| SelfBlog | 1012 |
| AgentMemory | 675 |
| Opportunity | 11283 |
| PilotReadinessGate | 489 |
| SpiderData | 22219 |

---

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | Fixed XPHistory field names in broadcast_evolution_status |
| `core/super_platform/scifi_integration.py` | Removed user field from AgentMemory queries |
| `core/personal_ai_assistant_enhanced.py` | Changed to specific command pattern matching |
| `intelligence/tasks.py` | Added process_pending_action_plans wrapper |
| `core/celery.py` | Updated beat schedule to use wrapper task |
| `core/management/commands/seed_production.py` | **NEW** - Production seeding command |
| `scripts/production_data_audit.sh` | **NEW** - Production audit script |

---

## Verification

After deployment, verify:

1. **Content Channels Page** - Should show 5 seeded channels
2. **PA Assistant** - "Tell me about this system" should give AI response (not generic help)
3. **Celery Beat Logs** - No more `execute_action_plan missing argument` errors
4. **System Configs** - 7 configs should be visible in admin

---

## Next Steps (Session 800)

1. Monitor production for any new Celery errors
2. Verify autonomous content generation starts (daily/weekly schedules)
3. Test spider data collection in production
4. Consider adding more seeding options (sample opportunities, pilots)
