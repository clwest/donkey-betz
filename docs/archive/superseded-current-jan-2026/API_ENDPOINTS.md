<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** API endpoint catalog
>
> **Where to look now:**
> - [docs/API_PATH_POLICY.md](/docs/API_PATH_POLICY.md)
> - [core/urls*.py (source)](/core/urls*.py (source))
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# API Endpoints Documentation

**Total Endpoints:** 200+
**Location:** `core/urls.py`
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoint Categories](#endpoint-categories)
4. [Key Endpoints Detail](#key-endpoints-detail)

---

## Overview

The platform exposes 200+ REST API endpoints for agents, spiders, content, governance, and more.

### Base URL
```
http://localhost:8000/api/
```

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Success message"
}
```

### Error Format
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

---

## Authentication

### Session Authentication (Web)
Django session-based authentication for web UI.

### Token Authentication (API)
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/endpoint/
```

### Discord OAuth
For Discord-linked accounts.

---

## Endpoint Categories

### Health & Status (5)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health/ping/` | GET | Simple health check |
| `/health/status/` | GET | Detailed system status |
| `/health/services/` | GET | Service status |
| `/health/celery/` | GET | Celery status |
| `/health/database/` | GET | Database status |

### Agent Endpoints (15)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/agents/` | GET | List all agents |
| `/api/agents/<id>/` | GET | Agent details |
| `/api/agents/<id>/execute/` | POST | Execute agent task |
| `/api/agents/<id>/history/` | GET | Execution history |
| `/api/agents/<id>/knowledge/` | GET | Agent knowledge |
| `/api/agents/<id>/memories/` | GET | Agent memories |
| `/api/agents/<id>/dreams/` | GET | Agent dreams |
| `/api/agents/<id>/mood/` | GET | Current mood |
| `/api/agents/<id>/evolution/` | GET | XP and level |
| `/api/agents/<id>/relationships/` | GET | Relationships |
| `/api/agent-conversations/` | GET | List conversations |
| `/api/agent-conversations/<id>/` | GET | Conversation detail |
| `/api/agent-dreams/` | GET | List all dreams |
| `/api/hive-mind/` | POST | Start hive session |
| `/api/delegate/` | POST | Delegate to agent |

### Spider Endpoints (12)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/spiders/` | GET | List all spiders |
| `/api/spiders/<name>/` | GET | Spider details |
| `/api/spiders/<name>/run/` | POST | Run spider |
| `/api/spiders/<name>/data/` | GET | Spider data |
| `/api/spider-data/` | GET | All spider data |
| `/api/spider-data/search/` | POST | Search data |
| `/api/spider-data/trending/` | GET | Trending topics |
| `/api/spider-data/category/<cat>/` | GET | By category |
| `/api/spider-intelligence/` | GET | Intelligence summary |
| `/api/spider-network/run/` | POST | Run all spiders |
| `/api/spider-embeddings/` | GET | Embedding stats |
| `/api/spider-health/` | GET | Network health |

### Content Endpoints (20)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/images/` | GET | List images |
| `/api/images/generate/` | POST | Generate image |
| `/api/images/<id>/` | GET | Image detail |
| `/api/images/<id>/edit/` | POST | Edit image |
| `/api/videos/` | GET | List videos |
| `/api/videos/generate/` | POST | Generate video |
| `/api/videos/<id>/` | GET | Video detail |
| `/api/audio/` | GET | List audio |
| `/api/audio/generate/` | POST | Generate audio |
| `/api/content-packages/` | GET | List packages |
| `/api/content-packages/create/` | POST | Create package |
| `/api/content-packages/<id>/` | GET | Package detail |
| `/api/content-series/` | GET | List series |
| `/api/content-series/create/` | POST | Create series |
| `/api/content-series/<id>/` | GET | Series detail |
| `/api/style-presets/` | GET | Style presets |
| `/api/gallery/` | GET | User gallery |
| `/api/exports/` | GET | Export history |
| `/api/exports/<id>/download/` | GET | Download export |
| `/api/watermark/` | POST | Apply watermark |

### Workflow Endpoints (10)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/workflows/` | GET | List workflows |
| `/api/workflows/create/` | POST | Create workflow |
| `/api/workflows/<id>/` | GET | Workflow detail |
| `/api/workflows/<id>/execute/` | POST | Execute workflow |
| `/api/workflows/<id>/status/` | GET | Execution status |
| `/api/workflow-templates/` | GET | Templates |
| `/api/workflow-schedules/` | GET | Schedules |
| `/api/workflow-schedules/create/` | POST | Create schedule |
| `/api/workflow-analytics/` | GET | Analytics |
| `/api/workflow-artifacts/` | GET | Artifacts |

### Opportunity Endpoints (12)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/opportunities/` | GET | List opportunities |
| `/api/opportunities/<id>/` | GET | Opportunity detail |
| `/api/opportunities/<id>/apply/` | POST | Apply |
| `/api/opportunities/<id>/score/` | GET | ML score |
| `/api/opportunities/matches/` | GET | User matches |
| `/api/opportunity-alerts/` | GET | Alerts |
| `/api/opportunity-alerts/create/` | POST | Create alert |
| `/api/applications/` | GET | My applications |
| `/api/applications/<id>/` | GET | Application detail |
| `/api/opportunity-categories/` | GET | Categories |
| `/api/opportunity-tracking/` | GET | Tracking data |
| `/api/opportunity-conversions/` | GET | Conversion funnel |

### Governance Endpoints (15)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/boardroom/` | GET | List decisions |
| `/api/boardroom/<id>/` | GET | Decision detail |
| `/api/boardroom/<id>/promote/` | POST | Promote decision |
| `/api/boardroom/<id>/reject/` | POST | Reject decision |
| `/api/boardroom/<id>/review/` | GET | Review document |
| `/api/pilot-gates/` | GET | List pilot gates |
| `/api/pilot-gates/<id>/` | GET | Gate detail |
| `/api/pilot-gates/<id>/checklist/` | GET | Checklist items |
| `/api/pilot-gates/<id>/approve/` | POST | Approve gate |
| `/api/pilot-executions/` | GET | Pilot executions |
| `/api/pilot-executions/<id>/` | GET | Execution detail |
| `/api/pilot-outcomes/` | GET | Outcomes |
| `/api/experiments/` | GET | Experiments |
| `/api/experiments/<id>/` | GET | Experiment detail |
| `/api/kpi-tracking/` | GET | KPI data |

### Autonomous Situation Endpoints (10)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/situations/` | GET | List situations |
| `/api/situations/<id>/` | GET | Situation detail |
| `/api/situations/<id>/run/` | POST | Manual run |
| `/api/situations/<id>/history/` | GET | Execution history |
| `/api/situations/<id>/alerts/` | GET | Situation alerts |
| `/api/situation-triggers/` | GET | List triggers |
| `/api/situation-triggers/create/` | POST | Create trigger |
| `/api/content-channels/` | GET | Content channels |
| `/api/content-channels/<id>/` | GET | Channel detail |
| `/api/content-channels/<id>/episodes/` | GET | Episodes |

### Market Intelligence Endpoints (10)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/market-briefs/` | GET | Daily briefs |
| `/api/market-briefs/latest/` | GET | Latest brief |
| `/api/market-predictions/` | GET | Predictions |
| `/api/market-signals/` | GET | Detected signals |
| `/api/market-alerts/` | GET | Alerts |
| `/api/agent-accuracy/` | GET | Agent accuracy |
| `/api/prediction-outcomes/` | GET | Outcomes |
| `/api/kalshi/markets/` | GET | Kalshi markets |
| `/api/odds/` | GET | Sports odds |
| `/api/arbitrage/` | GET | Arbitrage opps |

### Voice & Audio Endpoints (10)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/voice-profiles/` | GET | Voice profiles |
| `/api/voice-profiles/create/` | POST | Create profile |
| `/api/voice-clone/` | POST | Clone voice |
| `/api/voice-generate/` | POST | Generate TTS |
| `/api/voice-marketplace/` | GET | Marketplace |
| `/api/voice-marketplace/<id>/` | GET | Listing detail |
| `/api/voice-purchases/` | GET | My purchases |
| `/api/podcasts/` | GET | Podcast shows |
| `/api/podcasts/<id>/` | GET | Show detail |
| `/api/podcasts/<id>/episodes/` | GET | Episodes |

### Legal Endpoints (8)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/legal-cases/` | GET | List cases |
| `/api/legal-cases/create/` | POST | Create case |
| `/api/legal-cases/<id>/` | GET | Case detail |
| `/api/legal-cases/<id>/documents/` | GET | Case documents |
| `/api/legal-cases/<id>/upload/` | POST | Upload document |
| `/api/legal-cases/<id>/analyze/` | POST | Analyze document |
| `/api/legal-motions/` | GET | Motions |
| `/api/legal-responses/` | GET | Response drafts |

### DaVinci Resolve Endpoints (5)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/resolve-renders/` | GET | List renders |
| `/api/resolve-renders/<id>/` | GET | Render detail |
| `/api/resolve-renders/<id>/download/` | GET | Download video |
| `/api/resolve-renders/<id>/rate/` | POST | Rate render |
| `/api/resolve-grades/` | GET | Color grades |

### User & Profile Endpoints (12)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/profile/` | GET | User profile |
| `/api/profile/update/` | POST | Update profile |
| `/api/preferences/` | GET | Preferences |
| `/api/preferences/update/` | POST | Update prefs |
| `/api/certifications/` | GET | Certifications |
| `/api/certifications/upload/` | POST | Upload cert |
| `/api/subscription/` | GET | Subscription |
| `/api/subscription/upgrade/` | POST | Upgrade tier |
| `/api/notifications/` | GET | Notifications |
| `/api/activity/` | GET | Activity log |
| `/api/sessions/` | GET | Chat sessions |
| `/api/bankroll/` | GET | Betting bankroll |

### Analytics Endpoints (8)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/analytics/dashboard/` | GET | Dashboard stats |
| `/api/analytics/content/` | GET | Content analytics |
| `/api/analytics/agents/` | GET | Agent analytics |
| `/api/analytics/spiders/` | GET | Spider analytics |
| `/api/analytics/revenue/` | GET | Revenue analytics |
| `/api/analytics/conversions/` | GET | Conversion data |
| `/api/analytics/roi/` | GET | ROI metrics |
| `/api/analytics/weekly-brief/` | GET | Weekly summary |

### Provenance Endpoints (5)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/provenance/` | GET | Provenance records |
| `/api/provenance/<id>/` | GET | Record detail |
| `/api/provenance/<id>/chain/` | GET | Hash chain |
| `/api/provenance/verify/` | POST | Verify integrity |
| `/api/audit-log/` | GET | Audit log |

---

## Key Endpoints Detail

### Execute Agent Task
```bash
POST /api/agents/<id>/execute/
Content-Type: application/json

{
  "task": "Create a cyberpunk logo",
  "context": {
    "style": "neon",
    "size": "1024x1024"
  }
}

Response:
{
  "success": true,
  "data": {
    "execution_id": "abc123",
    "status": "completed",
    "result": { ... }
  }
}
```

### Search Spider Data
```bash
POST /api/spider-data/search/
Content-Type: application/json

{
  "query": "AI trends 2025",
  "categories": ["tech", "ai"],
  "limit": 20,
  "use_embeddings": true
}

Response:
{
  "success": true,
  "data": {
    "results": [...],
    "total": 150,
    "search_type": "semantic"
  }
}
```

### Generate Image
```bash
POST /api/images/generate/
Content-Type: application/json

{
  "prompt": "A futuristic cityscape at sunset",
  "style": "cinematic",
  "size": "1024x1024",
  "model": "stability-core"
}

Response:
{
  "success": true,
  "data": {
    "id": "img123",
    "url": "/media/images/img123.png",
    "prompt": "...",
    "created_at": "2025-01-05T12:00:00Z"
  }
}
```

### Get ML Score
```bash
GET /api/opportunities/<id>/score/

Response:
{
  "success": true,
  "data": {
    "score": 0.85,
    "confidence": 0.92,
    "factors": {
      "title_relevance": 0.9,
      "source_authority": 0.8,
      "freshness": 0.95
    },
    "shap_values": { ... }
  }
}
```

---

## WebSocket Endpoints

### Chat
```
ws://localhost:8000/ws/chat/<session_id>/
```

### Agent Conversations
```
ws://localhost:8000/ws/conversations/
```

### System Updates
```
ws://localhost:8000/ws/updates/
```

---

## Rate Limits

| Tier | Requests/min | Requests/day |
|------|--------------|--------------|
| Free | 30 | 500 |
| Pro | 100 | 5,000 |
| Premium | 300 | 20,000 |

---

## Related Documentation

- [AGENTS.md](AGENTS.md) - Agent endpoints
- [SPIDERS.md](SPIDERS.md) - Spider endpoints
- [DISCORD.md](DISCORD.md) - Discord as alternative API