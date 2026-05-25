# Frontend Integration Note - Session 699

**From:** Backend Claude (Session 699)
**To:** Frontend Claude (UI Development)
**Date:** January 6, 2026
**Updated:** Added 11 more agent configs (75 total)

---

## New LLM Routing API Endpoints Available

I've created 7 new API endpoints for the LLM routing system. These are ready for frontend integration:

### Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/llm-routing/status/` | GET | Public | Overall system status |
| `/api/v1/llm-routing/providers/` | GET | Public | List all 6 LLM providers |
| `/api/v1/llm-routing/models/` | GET | Public | List all 16 models with costs |
| `/api/v1/llm-routing/agent-configs/` | GET | Public | 75 agent-model mappings |
| `/api/v1/llm-routing/logs/` | GET | Public | Call logs with filtering |
| `/api/v1/llm-routing/cost-analytics/` | GET | Public | Cost analytics dashboard |
| `/api/v1/llm-routing/agent-configs/<agent>/` | POST | Auth Required | Update agent config |

### Query Parameters

**Models endpoint:**
- `?provider=openai` - Filter by provider
- `?capability=coding` - Filter by specialization

**Agent Configs endpoint:**
- `?agent=Content` - Filter by agent name
- `?model=claude` - Filter by model ID

**Logs endpoint:**
- `?hours=24` - Time range (default 24)
- `?agent=ThinkingAgent` - Filter by agent
- `?provider=anthropic` - Filter by provider
- `?success=true` - Filter by success status
- `?limit=50&offset=0` - Pagination

**Cost Analytics endpoint:**
- `?hours=168` - Time range (default 7 days)

### Sample Responses

#### Status Response
```json
{
  "success": true,
  "status": {
    "providers": {
      "total": 6,
      "active": 6,
      "with_keys": 4,
      "details": [
        {
          "name": "openai",
          "display_name": "OpenAI",
          "has_api_key": true,
          "model_count": 3,
          "calls_24h": 4,
          "cost_24h": 0.001581,
          "success_rate_24h": 100.0
        }
      ]
    },
    "models": {"total": 16, "active": 16},
    "agent_configs": {"total": 75},
    "activity_24h": {
      "total_calls": 10,
      "successful_calls": 8,
      "total_cost": 0.003493
    }
  }
}
```

#### Cost Analytics Response
```json
{
  "success": true,
  "analytics": {
    "overall": {
      "total_calls": 10,
      "successful_calls": 8,
      "success_rate": 80.0,
      "total_cost": 0.003493,
      "total_tokens": 1858,
      "avg_latency_ms": 1369.6
    },
    "by_provider": [
      {"provider": "openai", "calls": 4, "cost": 0.001581, "success_rate": 100.0},
      {"provider": "together", "calls": 2, "cost": 0.001351, "success_rate": 100.0},
      {"provider": "anthropic", "calls": 4, "cost": 0.000561, "success_rate": 50.0}
    ],
    "by_model": [...],
    "by_agent": [...],
    "daily_breakdown": [...],
    "hourly_breakdown": [...]
  }
}
```

### UI Suggestions

1. **Admin Page** - Add "LLM Routing" tab with:
   - Provider status cards (6 providers with health indicators)
   - Model list with costs per 1M tokens
   - Agent config table (editable model assignments)

2. **Dashboard Widget** - Cost summary card showing:
   - Total cost (24h/7d)
   - Calls by provider pie chart
   - Success rate indicator

3. **Agent Detail View** - Show which LLM model each agent uses

### Files Created

- `core/views_llm_routing.py` - API views (~450 lines)
- Updated `core/urls.py` - Added routes
- Updated `core/auth_middleware.py` - Added to PUBLIC_PATHS

---

**Backend is ready for frontend integration!**
