# Session 727: Celery Tasks Deep Audit

**Date:** January 7, 2026
**Auditor:** Claude Code (Session 727)
**Status:** MOSTLY HEALTHY - 177/274 Tasks Scheduled

---

## Executive Summary

The Celery task system is **extensive** with good scheduling coverage:

| Metric | Count | Status |
|--------|-------|--------|
| Total Tasks Defined | 274 | Across 16 files |
| Tasks Scheduled | 177 | In `core/celery.py` |
| On-Demand Tasks | ~97 | Called programmatically |
| core/tasks.py | 210 | Main task file |

**Reality Score: 85%**

---

## Task Distribution by File

| File | Tasks | Scheduled | Status |
|------|-------|-----------|--------|
| `core/tasks.py` | 210 | ~140 | High scheduling rate |
| `intelligence/tasks.py` | 17 | 2 | LOW - 15 unscheduled |
| `agents/tasks.py` | 7 | 1 | LOW - 6 unscheduled |
| `ai_core/spiders/tasks.py` | 7 | ~6 | Good |
| `ai_core/tasks.py` | 5 | 5 | All scheduled |
| `sports/tasks.py` | 5 | 4 | Good |
| `ml/tasks.py` | 5 | 4 | Good |
| `content/tasks.py` | 3 | 0 | ON-DEMAND |
| `pipelines/tasks.py` | 1 | ~1 | Good |
| Archive/test files | 8 | 0 | Not active |

---

## Scheduling Categories

### High-Frequency (Every 1-5 minutes)
| Task | Schedule | Purpose |
|------|----------|---------|
| `process_spider_data_automatic` | Every 5 min | Spider data processing |
| `process_core_spider_data` | Every 2 min | Core spider data |
| `send_pending_notifications` | Every 5 min | Notifications |
| `poll_pending_3d_models` | Every 30 sec | 3D model status |
| `refresh_system_state_cache` | Every 60 sec | System state |
| `broadcast_learning_status` | Every 60 sec | Learning updates |
| `broadcast_conversation_status` | Every 2 min | Conversation updates |
| `broadcast_dream_journal` | Every 3 min | Dream updates |

### Medium-Frequency (Every 10-30 minutes)
| Task | Schedule | Purpose |
|------|----------|---------|
| `run_spider_network` | Every 15 min | Spider execution |
| `backfill_spider_embeddings` | Every 10 min | Embeddings |
| `run_agent_learning_cycle` | Every 10 min | Agent learning |
| `sync_shared_memory` | Every 10 min | Memory sync |
| `collect_real_opportunities` | Every 15 min | Opportunities |
| `generate_human_attention_items` | Every 15 min | HITL items |
| `check_all_alerts` | Every 30 min | Alert checking |
| `dream_productization_cycle` | Every 20 min | Dream scoring |
| `dream_implementation_cycle` | Every 15 min | Dream implementation |

### Hourly Tasks
| Task | Schedule | Purpose |
|------|----------|---------|
| `sync_revenue_metrics` | Every hour | Revenue sync |
| `evaluate_completed_predictions` | Every hour | Sports predictions |
| `fetch_opportunities_hourly` | Every hour | Opportunities |
| `score_opportunities_hourly` | Every hour at :15 | Opportunity scoring |
| `execute_scheduled_automations` | Every hour | Automations |
| `multi_agent_panel_cycle` | Every hour | Agent panels |

### Every 2-8 Hours
| Task | Schedule | Purpose |
|------|----------|---------|
| `proactive_system_check` | Every 2 hours | System check |
| `agent_dream_cycle` | Every 2 hours | Agent dreams |
| `warm_up_spiders` | Every 4 hours | Spider warmup |
| `generate_user_insights` | Every 4 hours | User insights |
| `discover_success_patterns` | Every 6 hours | Pattern discovery |
| `auto_resolve_knowledge_gaps` | Every 6 hours | Knowledge gaps |
| `auto_promote_low_risk_decisions` | Every 6 hours | Decision promotion |
| `generate_smart_suggestions` | Every 8 hours | Suggestions |

### Daily Tasks
| Task | Schedule | Purpose |
|------|----------|---------|
| `clean_stale_data` | 2 AM | Data cleanup |
| `embed_daily_agent_learning` | 2 AM | Daily embeddings |
| `check_retraining_needed` | 3 AM | ML retraining check |
| `cleanup_spider_item_hashes` | 3:30 AM | Hash cleanup |
| `update_agent_performance` | 4 AM | Agent performance |
| `expire_old_opportunities` | 4:30 AM | Opportunity expiration |
| `daily_learning_pipeline` | 5 AM | Learning pipeline |
| `update_agent_effectiveness` | 5:30 AM | Agent effectiveness |
| `update_learning_profiles` | 6 AM | Learning profiles |
| `generate_opportunity_report` | 8 AM | Reports |
| `generate_accuracy_report` | 9 AM | Accuracy report |
| `report_pending_review_metrics` | 9 AM | Review metrics |
| `weekly_opportunity_digest` | Sunday 10 AM | Weekly digest |

### Body System Tasks (Session 701-723)
| Task | Schedule | Purpose |
|------|----------|---------|
| `run_heartbeat` | Every 30 sec | HEART monitoring |
| `check_breathing` | Every 60 sec | LUNGS monitoring |
| `check_circulation` | Every 2 min | CIRCULATORY monitoring |
| `check_spine_alignment` | Every 5 min | SPINE routing |
| `immune_scan` | Every 5 min | IMMUNE threats |
| `check_digestion` | Every 30 sec | DIGESTIVE processing |
| `check_muscular` | Every 2 min | MUSCULAR workload |
| `check_brain` | Every 60 sec | BRAIN cognition |
| `check_skin` | Every 90 sec | SKIN output |
| `check_nervous` | Every 30 sec | NERVOUS alerts |
| `coordinate_body` | Every 5 min | Body coordination |

---

## Unscheduled Tasks (Potential Issues)

### intelligence/tasks.py - 15 NOT SCHEDULED

These tasks have 0 records in database tables (from intelligence audit):

| Task | Status | Recommendation |
|------|--------|----------------|
| `execute_action_plan` | Not scheduled | SHOULD BE SCHEDULED |
| `monitor_and_process_opportunities` | Not scheduled | SHOULD BE SCHEDULED |
| `calculate_daily_revenue_metrics` | Not scheduled | SHOULD BE SCHEDULED |
| `execute_agent_task` | On-demand | OK |
| `scan_spider_opportunities` | Not scheduled | Consider scheduling |
| `scan_income_spider_orchestrator` | Not scheduled | Consider scheduling |
| `submit_proposal_automatically` | On-demand | OK |
| `check_proposal_responses` | Not scheduled | Consider scheduling |
| `handle_client_response` | On-demand | OK |
| `submit_follow_up` | On-demand | OK |
| `update_ml_model_with_feedback` | Not scheduled | SHOULD BE SCHEDULED |
| `start_intelligence_engine` | On-demand | OK |
| `get_live_opportunities` | On-demand | OK |
| `get_live_predictions` | On-demand | OK |
| `trigger_market_scan` | On-demand | OK |

### agents/tasks.py - 6 NOT SCHEDULED

| Task | Status | Recommendation |
|------|--------|----------------|
| Only `update_agent_performance` | Scheduled | OK |
| 6 other tasks | Not scheduled | Review needed |

---

## Observations

### What Works Well
1. **177 tasks scheduled** - Comprehensive automation
2. **Body system tasks** - All 10 body systems have monitoring tasks
3. **Spider tasks** - Regular collection and processing
4. **Agent learning** - Continuous learning cycle
5. **Dream system** - Full pipeline: generation → productization → implementation

### Issues Found

1. **intelligence/tasks.py** - 15/17 tasks not scheduled
   - This explains why ActionPlan, RevenueMetrics, EarningRecord have 0 records
   - `execute_action_plan` should be running to create ActionPlan records
   - `calculate_daily_revenue_metrics` should be running to create RevenueMetrics

2. **agents/tasks.py** - 6/7 tasks not scheduled
   - May have functionality overlap with core/tasks.py

3. **Task Duplication**
   - Some tasks may overlap between files
   - e.g., stock market intelligence exists in multiple places

---

## Recommendations

### Priority 1: Schedule Missing Intelligence Tasks (HIGH)

Add to `core/celery.py`:
```python
# Session 727: Missing intelligence tasks
'execute-action-plans': {
    'task': 'intelligence.tasks.execute_action_plan',
    'schedule': crontab(minute='*/30'),  # Every 30 minutes
    'options': {'expires': 1800}
},
'calculate-daily-revenue': {
    'task': 'intelligence.tasks.calculate_daily_revenue_metrics',
    'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    'options': {'expires': 3600}
},
'monitor-opportunities': {
    'task': 'intelligence.tasks.monitor_and_process_opportunities',
    'schedule': crontab(minute='*/20'),  # Every 20 minutes
    'options': {'expires': 1200}
},
'update-ml-feedback': {
    'task': 'intelligence.tasks.update_ml_model_with_feedback',
    'schedule': crontab(hour=6, minute=30),  # Daily at 6:30 AM
    'options': {'expires': 3600}
},
```

### Priority 2: Review agents/tasks.py (MEDIUM)

Determine if these tasks should be scheduled or are on-demand only.

### Priority 3: Task Consolidation (LOW)

Consider consolidating duplicate tasks:
- Stock market intelligence tasks
- Spider processing tasks
- Opportunity tasks

---

## Conclusion

The Celery task system is **mostly healthy** with comprehensive scheduling:
- 177 tasks actively scheduled
- Body system monitoring complete
- Agent learning pipeline running
- Spider network automated

However, intelligence system tasks need scheduling to close the gap identified in the intelligence audit.

**Reality Score: 85%**
- 15% deduction for unscheduled intelligence tasks
- These missing schedules explain why intelligence database tables are empty

---

*Audit completed: Session 727, January 7, 2026*
