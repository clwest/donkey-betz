# Session 589 - Execution Gap Infrastructure

**Date:** December 29, 2025
**Focus:** Address 82% execution gap identified in Session 588

---

## Summary

Session 589 implements the infrastructure to address the execution gap where 82% of Boardroom decisions sit in DRAFT status forever. Following ChatGPT's strategic guidance (governance-first posture, don't rush), we implemented:

1. **Decision Promotion Rules Service** - Tiered governance-respecting auto-promotion
2. **Execution Gap Monitoring** - Integrated into System State Aggregator
3. **Celery Tasks** - Scheduled auto-promotion and gap metrics reporting

---

## The Execution Gap (Session 588 Finding)

```
Decisions: 754 total
  Draft (not enacted): 623 (82%) ← THE GAP
  Canonical (enacted):  117 (15%)
```

ChatGPT's analysis: "The system is better at deciding what to do than doing it."

---

## New Components

### 1. Decision Promotion Rules Service

**File:** `core/services/decision_promotion_rules.py`

Implements a tiered governance-respecting auto-promotion system:

| Tier | Decision Type | Impact Area | Auto-Promote? |
|------|---------------|-------------|---------------|
| 1 | `guideline` | `prompting`, `product`, `workflow` | YES (after 24h) |
| 2 | `policy`, `architecture`, `pipeline` | Any | NO - Requires review |
| 3 | Any | `security`, `infrastructure`, `agents` | NEVER |

**Key Functions:**
- `can_auto_promote(decision)` - Check eligibility
- `get_promotable_decisions()` - Find all eligible decisions
- `run_auto_promotion(dry_run)` - Execute or preview promotion
- `get_execution_gap_metrics()` - Dashboard data

**Conservative Settings:**
- 24-hour minimum aging before auto-promotion
- Max 10 decisions per run (prevent runaway)
- Never auto-promote high-risk decisions

### 2. System State Aggregator Integration

**File:** `core/services/system_state_aggregator.py`

Added new attention items for execution gap:

| ID | Category | Priority | Trigger |
|----|----------|----------|---------|
| `execution_gap_critical` | `execution_gap` | 82 | Gap > 70% |
| `execution_gap_stale` | `stale_concern` | 65 | >50 stale decisions |
| `execution_gap_promotable` | `opportunity` | 55 | Auto-promotable available |

Now appears in PA context:
```
### URGENT (needs immediate attention):
- [AUTONOMOUS] Execution Gap: 83%: 624 decisions in DRAFT vs 117 canonical
```

### 3. Celery Tasks

**File:** `core/tasks.py` (lines 19780-19911)

| Task | Purpose | Schedule |
|------|---------|----------|
| `auto_promote_low_risk_decisions` | Promote Tier 1 decisions | Every 6 hours |
| `report_execution_gap_metrics` | Log gap metrics | Daily 9 AM |

**Beat Schedules Added:**
```python
'auto-promote-low-risk-decisions': {
    'schedule': crontab(hour='*/6'),  # Every 6 hours
    'kwargs': {'dry_run': False}
}
'report-execution-gap-metrics': {
    'schedule': crontab(hour=9, minute=0),  # Daily 9 AM
}
```

---

## Current Metrics

```
Total Decisions: 754
  Draft: 624 (82.6%)
  Canonical: 117 (15.5%)

Age Distribution of Drafts:
  under_24h: 93
  1_to_7_days: 14
  7_to_30_days: 516
  over_30_days: 0

Auto-Promotable: 10 (1.6% of drafts)
  - All are low-risk guidelines
  - All in product/workflow impact areas
  - All >24 hours old
```

---

## What This Does NOT Do

Following ChatGPT's guidance to not rush:

1. **Does NOT auto-promote high-risk decisions** - Security, architecture, infrastructure decisions always require human review
2. **Does NOT execute decisions automatically** - Promotion is just changing status, not triggering actions
3. **Does NOT bypass governance** - Human-in-the-loop remains for Tier 2/3 decisions

---

## Testing

```bash
# Test the promotion rules (dry run)
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.services.decision_promotion_rules import run_auto_promotion
result = run_auto_promotion(dry_run=True)
print(f'Would promote: {result[\"would_promote\"]} decisions')
"

# Test the Celery task
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.tasks import auto_promote_low_risk_decisions
result = auto_promote_low_risk_decisions(dry_run=True)
print(f'Success: {result[\"success\"]}, Would promote: {result.get(\"would_promote\", 0)}')"
```

---

## Future Work (Session 590+)

### ActionIntent Model (Deferred)

ChatGPT recommended designing an ActionIntent model that:
- Captures the intent to execute a decision
- Respects governance checkpoints
- Creates audit trail from decision → action

This was deferred to avoid rushing autonomous execution before trust is established.

### Execution Pipeline

Once auto-promotion has run for a few cycles and the gap is reduced:
1. Consider expanding Tier 1 criteria
2. Add Decision → Action mapping
3. Implement ActionIntent for complex decisions

---

## Files Created/Modified

| File | Change |
|------|--------|
| `core/services/decision_promotion_rules.py` | **NEW** - Promotion rules service |
| `core/services/system_state_aggregator.py` | Added execution gap monitoring |
| `core/tasks.py` | Added 2 new Celery tasks |
| `core/celery.py` | Added 2 beat schedules |

---

## Key Insight

The system now has **self-awareness about its execution gap**. The PA will proactively surface this concern:

```
## System Attention Required

### URGENT (needs immediate attention):
- [AUTONOMOUS] Execution Gap: 83%: 624 decisions in DRAFT vs 117 canonical

### Important:
- [autonomous] Stale Decisions: 516: Decisions over 7 days old awaiting action
- [autonomous] Auto-Promotable: 10: Low-risk guidelines ready for auto-promotion
```

This visibility is the first step to closing the gap.

---

---

## Spider Telemetry Unification (ChatGPT Review)

ChatGPT reviewed the Self Blog and System Insights and identified a **multi-source desync**:

```
Self Blog prose:     "72 spiders"      ❌ stale
Self Blog telemetry: "0 spider data"   ❌ wrong query
System Insights:     "77 active spiders" ✅ correct
```

### Root Causes Found

1. **HTML defaults**: `ai_image_studio.html` had hardcoded 72
2. **Agent prompts**: Business agents mentioned "74 data sources"
3. **WebSocket fallbacks**: `consumers.py` used 40 as default
4. **API fallbacks**: `views_project_intelligence.py` used 74

### Fixes Applied

All spider counts now use single source of truth:
- **Primary**: `spider_registry.get_spider_count()['total']` = 77
- **Fallback**: 77 (not stale values)

### Files Fixed

| File | Old Value | New Value |
|------|-----------|-----------|
| `ai_core/templates/ai_image_studio.html` | 72 | 77 |
| `core/agents/business/*.py` | 74 | 77 |
| `core/consumers.py` | 40 | 77 |
| `core/new_pages_consumer.py` | 40 | 77 |
| `core/views_project_intelligence.py` | 74 | 77 |

### Verification

```bash
python manage.py write_self_blog --dry-run
# Output: "Spiders: 77, Spider Data Points: 10,603" ✅
```

---

**Session 589: Execution gap infrastructure + Spider telemetry unification complete**
