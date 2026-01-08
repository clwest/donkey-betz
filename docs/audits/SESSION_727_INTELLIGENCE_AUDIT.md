# Session 727: Intelligence App Deep Audit

**Date:** January 7, 2026
**Auditor:** Claude Code (Session 727)
**Status:** CRITICAL FINDINGS - Massive Duplication & Partial Usage

---

## Executive Summary

The intelligence system is **MASSIVE** with significant duplication:

| Location | Lines | Files | Status |
|----------|-------|-------|--------|
| `intelligence/` | 48,100 | 76 | Partially connected |
| `ai_core/intelligence/` | 18,212 | 20+ | Partially connected |
| **TOTAL** | **66,312** | **96+** | **Major duplication** |

This represents the **largest subsystem** in the codebase - more than the entire mythology app by 30x!

---

## Critical Findings

### 1. TWO INTELLIGENCE APPS

Both registered in INSTALLED_APPS:
```python
'ai_core.intelligence',    # AI Intelligence & Learning System
'intelligence',            # Real-Time Intelligence Engine
```

### 2. DUPLICATED income_builder.py

| File | Lines | Features |
|------|-------|----------|
| `intelligence/income_builder.py` | 2,200 | MOCK classes, OpenAI integration |
| `ai_core/intelligence/income_builder.py` | 1,500+ | REAL agent_registry, MLEngine |

**Both are being imported in different places!**

Files importing from `intelligence/income_builder.py`:
- core/consumers_base.py
- core/consumers.py
- core/personal_ai_orchestrator.py
- intelligence/consumers.py (lines 381, 612)
- intelligence/tasks.py
- 20+ test files

Files importing from `ai_core/intelligence/income_builder.py`:
- core/intelligence_api.py
- core/views_diagnostics.py
- core/component_pipelines.py
- intelligence/consumers.py (line 633!)

**Note:** `intelligence/consumers.py` imports from BOTH files!

### 3. EMPTY DATABASE TABLES

| Model | Records | Location |
|-------|---------|----------|
| ActionPlan | 0 | intelligence/models.py |
| ActionPlanStep | 0 | intelligence/models.py |
| AgentExecution | 0 | intelligence/models.py |
| RevenueMetrics | 0 | intelligence/models.py |
| EarningRecord | 0 | intelligence/models.py |
| **SpiderIntelligenceNode** | **9,285** | intelligence/models/ |

Only `SpiderIntelligenceNode` has data - it extends `SpiderData`.

### 4. APP_LABEL MISMATCH

`intelligence/models.py` uses:
```python
class Meta:
    app_label = 'intelligence_rt'  # Doesn't match 'intelligence'!
```

This could cause migration/query issues.

---

## Architecture Analysis

### What intelligence/ Contains (76 modules)

**Core Systems:**
- `income_builder.py` - AI income generation (DUPLICATE)
- `tasks.py` - 17 Celery tasks (1,696 lines)
- `consumers.py` - WebSocket handlers
- `views.py` - API endpoints (1,015 lines)
- `models.py` - Database models

**Agent Integration:**
- `agent_executor.py` - Execute agents
- `agent_factory.py` - Create agents
- `agent_orchestrator.py` - Coordinate agents
- `agent_communication.py` - Agent messaging
- `agent_learning.py` - Agent learning

**Spider Integration:**
- `spider_agent_bridge.py`
- `spider_agent_connector.py`
- `spider_decision_bridge.py`
- `spider_opportunity_connector.py`
- `income_spider_orchestrator.py`

**Action Plans:**
- `action_plan_orchestrator.py`
- `action_plan_formatter.py`
- `action_plan_advisor_handoff.py`

**Revenue/Income:**
- `income_builder_automation.py`
- `income_builder_connector.py`
- `revenue_integration.py`
- `revenue_tracking_bridge.py`

### What ai_core/intelligence/ Contains

- `income_builder.py` - (DUPLICATE with REAL integrations)
- `consumers.py` - 82,574 bytes! (largest file)
- `learning_loop.py` - 52,042 bytes
- `agent_learning_engine.py`
- `bluesky_learning_bridge.py`
- `data_transformation_pipeline.py`
- `embedding_generator.py`
- `knowledge_base_manager.py`
- `learning_metrics_dashboard.py`

---

## Connection Status

### URLs - CONNECTED
```
/api/v1/intelligence/ → intelligence.urls (20+ endpoints)
```

Endpoints include:
- `/skynet/status/`
- `/opportunities/`
- `/predictions/`
- `/income-builder/analyze/`
- `/action-plan/create/`
- `/action-plan/execute/`
- `/revenue/opportunities/`

### WebSockets - CONNECTED
```
ws://localhost:8000/ws/intelligence/
ws://localhost:8000/ws/income-builder/
ws://localhost:8000/ws/unified-intelligence/
ws://localhost:8000/ws/content-intelligence-pipeline/
```

### Celery Tasks - PARTIALLY SCHEDULED

**Scheduled in core/celery.py:**
- `intelligence.tasks.fetch_all_opportunities`
- `intelligence.tasks.cleanup_old_opportunities`
- `intelligence.shared_memory.sync_all_entity_memories`

**Defined but NOT scheduled (14 tasks):**
- `execute_action_plan`
- `process_action_step`
- `run_agent_task`
- `batch_execute_agents`
- And 10 more...

### Core Imports - HEAVILY CONNECTED

**107 imports** from intelligence in core/*.py files!

---

## Reality Assessment

### What WORKS
- SpiderIntelligenceNode data collection (9,285 records)
- URL routing and API endpoints
- WebSocket connections
- Some Celery tasks scheduled

### What DOESN'T WORK
- ActionPlan system (0 records)
- Revenue tracking (0 records)
- EarningRecord (0 records)
- Most Celery tasks not scheduled
- Duplicate income_builder causing confusion

---

## Recommendations

### Priority 1: Consolidate income_builder.py (HIGH)

**Option A:** Keep `ai_core/intelligence/income_builder.py` (has real integrations)
```python
# Deprecate intelligence/income_builder.py
# Update all imports to use ai_core.intelligence.income_builder
```

**Option B:** Merge into one file
- Take REAL integrations from ai_core version
- Take OpenAI integration from intelligence version
- Delete the duplicate

### Priority 2: Fix app_label Mismatch (HIGH)

Change `intelligence/models.py`:
```python
class Meta:
    app_label = 'intelligence'  # NOT 'intelligence_rt'
```

Then run migrations.

### Priority 3: Schedule More Celery Tasks (MEDIUM)

Add to `core/celery.py`:
```python
'execute-action-plans': {
    'task': 'intelligence.tasks.execute_action_plan',
    'schedule': crontab(minute='*/5'),
}
```

### Priority 4: Consolidate intelligence/ and ai_core/intelligence/ (MEDIUM)

Consider merging these two apps:
- 48,100 + 18,212 = 66,312 lines
- Significant overlap in functionality
- Confusing architecture

---

## Files Analyzed

### intelligence/ Top Files by Size

| File | Lines | Purpose |
|------|-------|---------|
| tasks.py | 1,696 | Celery tasks |
| income_builder.py | 2,200 | Income generation |
| consumers.py | ~2,000 | WebSocket handlers |
| views.py | 1,015 | API endpoints |
| agent_factory.py | ~800 | Agent creation |
| agent_executor.py | ~700 | Agent execution |

### ai_core/intelligence/ Top Files by Size

| File | Bytes | Purpose |
|------|-------|---------|
| consumers.py | 82,574 | WebSocket handlers (HUGE!) |
| income_builder.py | 54,863 | Income generation |
| learning_loop.py | 52,042 | Learning system |
| bluesky_learning_bridge.py | 38,042 | BlueSky integration |
| data_transformation_pipeline.py | 36,148 | Data processing |

---

## Conclusion

The intelligence system is:
- **Massive:** 66,312 lines across 96+ files
- **Duplicated:** Two versions of key modules
- **Partially working:** SpiderIntelligenceNode works, ActionPlans don't
- **Connected:** URLs, WebSockets, and imports are wired

**Reality Score for Intelligence: 40%**
- Infrastructure exists and is connected
- But most business logic isn't producing data
- Duplication creates confusion

**Action Required:**
1. Consolidate the two income_builder.py files
2. Fix app_label mismatch
3. Schedule remaining Celery tasks
4. Consider merging the two intelligence apps

---

*Audit completed: Session 727, January 7, 2026*
