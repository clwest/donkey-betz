# Session 773 - Deep Data Flow Audit

**Date:** January 18, 2026
**Focus:** Field-by-field comparison of backend API responses vs frontend display

---

## Overview

This audit compares what each backend endpoint returns against what the frontend actually displays to the user. The goal is to identify:
1. Unused endpoints (built but never called)
2. Hidden fields (returned but not displayed)
3. Bugs (wrong field names, incorrect calculations)
4. Missing data (frontend expects but backend doesn't provide)

---

## FINDING 1: Four Unused Endpoints

### Endpoint: `/api/dashboard/stats/` (NEVER CALLED)

**Backend:** `core/views_dashboard_stats.py:21` - `dashboard_stats()`
**Frontend Definition:** `dashboardApi.stats()` in `frontend/src/lib/api.ts:566`
**Called By:** Nothing (0 references in frontend code)

**Full Response Structure:**
```python
{
    # Core metrics
    'total_revenue': float,           # Sum of completed Revenue objects
    'active_opportunities': int,      # Count of active/pending Opportunity objects
    'success_rate': int,              # Percentage of successful applications
    'active_agents': int,             # Count of active agents assigned to user

    # Extended metrics
    'active_advisors': int,           # Count of active Advisor objects
    'spider_data_points': int,        # SpiderData count in last 24h
    'recent_collaborations': int,     # Collaboration count in last 7 days
    'agent_executions_24h': int,      # AgentExecution count in last 24h
    'profile_completion': int,        # Percentage (0-100) of profile fields filled

    # Detailed breakdowns
    'opportunities_by_type': [        # Array of {opportunity_type, count, potential_revenue}
        {'opportunity_type': str, 'count': int, 'potential_revenue': float}
    ],
    'revenue_trend': [                # Last 7 days revenue
        {'date': 'YYYY-MM-DD', 'amount': float}
    ],
    'top_agents': [                   # Top 5 agents by execution count
        {'name': str, 'type': str, 'executions': int, 'success_rate': float}
    ],

    # AI usage metrics
    'token_usage_24h': int,           # Total tokens used in last 24h
    'ai_cost_24h': float,             # Total AI cost in last 24h

    # System health
    'system_status': str,             # Always 'operational'
    'last_sync': str,                 # ISO timestamp

    # User context
    'user': {
        'username': str,
        'email': str,
        'is_premium': bool,
        'joined_date': str            # ISO timestamp
    }
}
```

**Why Unused:** DashboardPage evolved to use specialized endpoints instead:
- `ecosystemApi.stats()` for agent/spider counts
- `portfolioApi.revenueDashboard()` for revenue
- `learningApi.velocity()` for learning metrics

---

### Endpoint: `/api/dashboard/agents/` (NEVER CALLED)

**Backend:** `core/views_dashboard_stats.py:190` - `live_agent_activity()`
**Called By:** Nothing

**Full Response Structure:**
```python
{
    'agents': [
        {
            'id': int,
            'name': str,
            'type': str,
            'status': 'active' | 'idle',
            'current_task': str | None,
            'collaborating_with': [str],
            'last_active': str,           # ISO timestamp
            'metrics': {
                'tasks_completed': int,
                'success_rate': float,
                'specialization': str
            }
        }
    ],
    'total_agents': int,
    'timestamp': str
}
```

---

### Endpoint: `/api/dashboard/advisors/` (NEVER CALLED)

**Backend:** `core/views_dashboard_stats.py:240` - `advisor_insights()`
**Called By:** Nothing

**Full Response Structure:**
```python
{
    'insights': [
        {
            'advisor': {
                'name': str,
                'title': str,
                'expertise': str,
                'avatar': str
            },
            'insight': str,
            'confidence': float,
            'category': str,
            'actionable': bool,
            'created_at': str
        }
    ],
    'total_advisors': int,
    'timestamp': str
}
```

---

### Endpoint: `/api/dashboard/summary/` (NEVER CALLED)

**Backend:** `core/views_dashboard_stats.py:283` - `dashboard_summary()`
**Called By:** Nothing

**Full Response Structure:**
```python
{
    'success': True,
    'user_name': str,                 # First name or username for greeting
    'last_visit': str,                # ISO timestamp
    'while_away': {
        'new_spider_data': int,       # Spider data since last visit
        'agent_dreams': int,          # Dreams generated since last visit
        'agent_conversations': int,   # Conversations since last visit
        'new_opportunities': int,     # Opportunities since last visit
        'images_created': int         # Images created by user since last visit
    }
}
```

---

## FINDING 2: Bug in AgentsPage Monitoring Tab

### Location
**File:** `frontend/src/pages/AgentsPage.tsx`
**Line:** 2260

### The Bug
```typescript
// CURRENT CODE (BROKEN):
<p className="text-2xl font-bold">
    {((1 - (monitoringData.summary?.error_rate || 0)) * 100).toFixed(1)}%
</p>

// PROBLEM: Backend returns 'success_rate', NOT 'error_rate'
// When error_rate is undefined: 1 - 0 = 1, so it always shows 100%
```

### Backend Response (from `views_agent_execution.py:658-680`)
```python
{
    'success': True,
    'data': {
        'period': str,
        'summary': {
            'total_executions': int,
            'total_executions_24h': int,
            'completed': int,
            'failed': int,
            'success_rate': float,        # <-- THIS IS WHAT'S RETURNED
            'total_tokens': int,
            'total_cost': float,
            'avg_execution_time': float,
            'average_execution_time': float,
            'active_agents': int,
        },
        # ... more fields
    }
}
```

### Fix Required
```typescript
// FIXED CODE:
<p className="text-2xl font-bold">
    {(monitoringData.summary?.success_rate || 0).toFixed(1)}%
</p>
```

---

## FINDING 3: Hidden Fields in Monitoring Dashboard

### Backend Returns (but Frontend Ignores)

| Field Path | Type | Purpose | Display Recommendation |
|------------|------|---------|------------------------|
| `summary.total_tokens` | int | Total token usage in period | Add to summary stats |
| `summary.total_cost` | float | Total AI cost in period | Add to summary stats |
| `summary.completed` | int | Completed execution count | Show completed/failed breakdown |
| `summary.failed` | int | Failed execution count | Show completed/failed breakdown |
| `agents[name].total_tokens` | int | Per-agent token usage | Add column to agent table |
| `agents[name].total_cost` | float | Per-agent AI cost | Add column to agent table |
| `timeline` | array | Execution timeline data | Add timeline chart |
| `recent_executions` | array | 10 most recent executions | Add recent executions list |

### Timeline Data Structure (Unused)
```python
'timeline': [
    {
        'timestamp': str,        # ISO timestamp (hour or day)
        'executions': int,       # Total executions in period
        'successful': int,       # Successful executions in period
    }
]
```

### Recent Executions Data Structure (Unused)
```python
'recent_executions': [
    {
        'id': str,
        'agent_name': str,
        'status': str,
        'execution_time_ms': int,
        'tokens_used': int,
        'created_at': str,
    }
]
```

---

## FINDING 4: DashboardPage Uses Different Endpoints

### What Frontend Actually Calls (DashboardPage.tsx)

| Line | Query | Endpoint | Status |
|------|-------|----------|--------|
| 164-167 | `ecosystemApi.stats()` | `/api/ecosystem/stats/` | ✅ Working |
| 169-172 | `dashboardApi.health()` | `/api/v1/health/` | ✅ Working |
| 175-178 | `activityApi.recent(20, 24)` | Activity aggregator | ✅ Working |
| 181-184 | `portfolioApi.revenueDashboard()` | Revenue endpoint | ✅ Working |
| 187-190 | `learningApi.velocity()` | Learning velocity | ✅ Working |
| 193-197 | `researchApi.networkGraph()` | Network graph | ✅ Working |

### What Frontend DEFINES But Never Calls

| API Method | Endpoint | Status |
|------------|----------|--------|
| `dashboardApi.stats()` | `/api/dashboard/stats/` | ❌ Never called |

---

## FINDING 5: Monitoring Tab - Fields Being Displayed

### Currently Displayed (Working)

| UI Element | Data Source | Status |
|------------|-------------|--------|
| Success Rate | `summary.success_rate` | ⚠️ BROKEN (uses error_rate) |
| Executions (24h) | `summary.total_executions_24h` | ✅ Working |
| Avg Execution Time | `summary.average_execution_time` | ✅ Working |
| Active Agents | `summary.active_agents` | ✅ Working |
| CPU Usage | `system.cpu_percent` | ✅ Working |
| Memory Usage | `system.memory_percent` | ✅ Working |
| Uptime | `system.uptime` | ✅ Working |
| Cache Hit Rate | `cache.hit_rate` | ✅ Working |
| Cache Hits | `cache.hits` | ✅ Working |
| Cache Misses | `cache.misses` | ✅ Working |
| Agent Performance Table | `agents` dict | ✅ Partial (missing tokens/cost) |
| Alerts | `alertsData.alerts` | ✅ Working |

---

## ACTION ITEMS

### Immediate (Bug Fix)
- [x] Fix `AgentsPage.tsx:2260` - Change `error_rate` to `success_rate` ✅ FIXED

### High Priority (Display Hidden Data)
- [x] Add token usage card to Monitoring summary stats ✅ DONE
- [x] Add AI cost card to Monitoring summary stats ✅ DONE
- [x] Add completed/failed breakdown to Monitoring ✅ DONE
- [x] Add tokens/cost columns to agent performance table ✅ DONE

### Medium Priority (Unused Endpoints)
- [ ] Decide: Connect `dashboard_stats` to UI OR remove the endpoint
- [ ] Decide: Connect `live_agent_activity` to UI OR remove the endpoint
- [ ] Decide: Connect `advisor_insights` to UI OR remove the endpoint
- [ ] Decide: Connect `dashboard_summary` ("While You Were Away") to UI OR remove

### Low Priority (Enhancements)
- [ ] Add execution timeline chart using `timeline` data
- [ ] Add recent executions list using `recent_executions` data

---

## Files Referenced

| File | Purpose |
|------|---------|
| `core/views_dashboard_stats.py` | 4 unused endpoints |
| `core/views_agent_execution.py` | Monitoring dashboard endpoint |
| `core/views_ecosystem.py` | Ecosystem stats (actually used) |
| `frontend/src/pages/DashboardPage.tsx` | Dashboard frontend |
| `frontend/src/pages/AgentsPage.tsx` | Agents page with Monitoring tab bug |
| `frontend/src/lib/api.ts` | API definitions (line 565-569 for dashboardApi) |

---

## Verification Steps

Before making changes, verify these findings:

1. **Unused endpoints:** `grep -r "dashboardApi.stats" frontend/src/` should return 0 results
2. **Bug verification:** Look at line 2260 of AgentsPage.tsx for `error_rate`
3. **Hidden fields:** Call `/api/v1/agents/monitoring/dashboard/` and check response includes `timeline` and `recent_executions`

---

**Session 773 Complete**
