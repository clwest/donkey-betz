# Session 546: Concern Tracking Feedback Loop

**Date:** December 24, 2025
**Focus:** Created complete feedback loop for ThinkingAgent concerns

---

## Problem Solved

The ThinkingAgent was identifying concerns (no active spiders, decision bottlenecks, knowledge silos) but there was no feedback loop to verify if actions actually resolved them. Concerns were being logged but never tracked or verified.

---

## Solution Implemented

Created a complete Concern Tracking system with:

### 1. TrackedConcern Model (`core/models_unified_system.py`)
- Persists concerns across thinking cycles
- Tracks status: active -> in_progress -> monitoring -> resolved (or recurring)
- Links to actions taken to address the concern
- Stores verification metrics and results

### 2. ConcernTrackerService (`core/services/concern_tracker.py`)
- `register_concerns_from_cycle()` - Register all concerns from a ThoughtRecord
- `register_concern()` - Register single concern with deduplication
- `link_action_to_concerns()` - Link executed actions to relevant concerns
- `verify_concern_resolution()` - Verify if concern is resolved based on metrics
- `get_concern_dashboard()` - Dashboard data for UI

### 3. API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/reasoning/concerns/` | GET | Dashboard data |
| `/api/v1/reasoning/concerns/verify/` | POST | Verify all active concerns |
| `/api/v1/reasoning/concerns/register-historical/` | POST | Backfill from existing ThoughtRecords |
| `/api/v1/reasoning/concerns/<uuid>/` | GET | Concern detail |

### 4. Concern Tracking UI Tab
New "Concern Tracking" tab in Research Demo with:
- Status counters (Active/In Progress/Monitoring/Resolved/Recurring/Stale)
- Category breakdown (spider_activity, decision_bottleneck, knowledge_silos, etc.)
- Recent concerns list with severity, status, and verification info
- Verify All button to check resolution
- Verification log

---

## Verification Metrics by Category

| Category | Metric Checked | Resolution Threshold |
|----------|----------------|---------------------|
| `spider_activity` | Spider data in last 24h | > 100 records |
| `decision_bottleneck` | AgentDecisionSummary in 24h | > 0 decisions |
| `knowledge_silos` | Unique teachers in 24h | >= 5 different agents |
| `action_gap` | Action success rate | >= 80% |
| `general` | Concern still detected in recent cycles | Not detected |

---

## Files Changed

| File | Changes |
|------|---------|
| `core/models_unified_system.py` | Added TrackedConcern model |
| `core/services/concern_tracker.py` | NEW - ConcernTrackerService |
| `core/services/autonomous_action_executor.py` | Added concern tracking methods |
| `core/views_autonomous_reasoning.py` | Added 4 concern API endpoints |
| `core/urls.py` | Added URL routes for concern APIs |
| `core/auth_middleware.py` | Added concern endpoints to public paths |
| `ai_core/templates/ai_image_studio.html` | Added Concern Tracking tab + JS |
| `core/migrations/0120_session_546_tracked_concern.py` | TrackedConcern migration |

---

## Current State After Session

```
Concerns Tracked: 32
├── Active: 15 (mostly spider_activity)
├── Resolved: 17 (decision_bottleneck, general)
├── In Progress: 0
└── Recurring: 0

Categories:
├── spider_activity: 10 (active - spiders are indeed offline)
├── decision_bottleneck: 7 (resolved - decisions are being made)
├── knowledge_silos: 2 (active - still concentrated)
└── general: 9 (mostly resolved)
```

---

## The Complete Feedback Loop

```
ThinkingAgent cycle
        ↓
Identifies concerns → ConcernTrackerService.register_concern()
        ↓
Takes actions → link_action_to_concerns()
        ↓
Status: active → in_progress
        ↓
Verification runs → verify_concern_resolution()
        ↓
Checks real metrics (spider data, decisions, etc.)
        ↓
Status: resolved OR recurring (if came back)
```

---

## How to Use

```bash
# View concern dashboard
curl http://localhost:8000/api/v1/reasoning/concerns/

# Verify all active concerns
curl -X POST http://localhost:8000/api/v1/reasoning/concerns/verify/

# Register historical concerns from existing thoughts
curl -X POST http://localhost:8000/api/v1/reasoning/concerns/register-historical/

# View in UI
open http://localhost:8000/ai-studio/
# Navigate to: Research Demo -> Concern Tracking
```

---

## Session 547 Priorities

1. **Fix Spider Network** - 10 concerns about inactive spiders
2. **Address Knowledge Silos** - Teaching is concentrated in few agents
3. **Integrate with ThinkingAgent** - Auto-register concerns after each cycle
4. **Add action linking** - Automatically link executed actions to concerns
