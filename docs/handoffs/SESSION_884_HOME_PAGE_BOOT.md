---
originating_session: 884
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 884: AI OS Boot Experience - Home Page

**Date:** January 30, 2026
**Focus:** Create the "boot experience" home page that makes users feel like they're starting up their AI operating system

---

## What Was Accomplished

### 1. Backend API: `/api/home/boot/` (NEW)

**File:** `core/views_home.py`

Created a single aggregated endpoint that returns all home page data:

```python
{
  "greeting": {
    "user_name": "Chris",
    "time_of_day": "morning"  # morning/afternoon/evening
  },
  "while_away": {
    "spider_findings": 3,      # SpiderData since last visit
    "high_score_dreams": 2,    # Dreams with score >= 0.7
    "initiatives_progressed": 1,
    "pending_decisions": 4,
    "hours_since_visit": 18.5
  },
  "active_projects": [
    {
      "id": "uuid",
      "name": "Content Empire",
      "type": "initiative",
      "completion_percentage": 60,
      "status": "decision_pending",  # or "in_progress"
      "current_stage": 3,
      "pending_decision": {
        "stage": 3,
        "title": "Approve Stage 3"
      }
    }
  ],
  "quick_stats": {
    "agents_active": 76,
    "system_health": "healthy"  # or "degraded"
  }
}
```

**Data Sources:**
- User name from `UserProfile.display_name` or `user.first_name` or `user.username`
- Time of day from `timezone.localtime().hour`
- Last visit tracked in session storage (`last_home_visit`)
- Spider findings from `SpiderData.objects.filter(created_at__gte=last_visit)`
- Dreams from `AgentDream.objects.filter(composite_score__gte=0.7, promoted_to_decision=False)`
- Initiatives from `Initiative.objects.filter(status='ACTIVE')`
- Decisions from `AgentDecisionSummary.objects.filter(is_canonical=False)`

### 2. Frontend Home Page Component

**File:** `frontend/src/pages/HomePage.tsx`

Component structure:
- `BootGreeting` - "Good morning, Chris. Your AI partner is ready."
- `WhileAwaySection` - Clickable cards showing activity since last visit
- `ActiveProjectsSection` - Projects with progress bars and pending decisions
- `NaturalLanguageInput` - Chat-style input that routes to `/assistant?message=...`
- `QuickActionsBar` - Create, Research, Decide, Review, Build buttons
- `SystemStatus` - Subtle footer showing system health

### 3. Routing Changes

**File:** `frontend/src/App.tsx`
- Changed: `<Route index element={<Navigate to="/workspace" replace />} />`
- To: `<Route index element={<HomePage />} />`

**File:** `frontend/src/components/layout/Sidebar.tsx`
- Added Home icon at top of navigation: `{ path: '/', label: 'Home', icon: Home }`

### 4. API Client

**File:** `frontend/src/lib/api.ts`
- Added: `homeApi.boot()` method

---

## Partnership Language Embedded

| Element | Language Used |
|---------|---------------|
| Greeting tagline | "Your AI partner is ready. What shall we accomplish together?" |
| Input placeholder | "What are we working on today?" |
| Quick actions | Create, Research, Decide, Review, Build |
| System status | "All systems ready" / "Limited capacity" |

---

## Files Changed

| File | Action | Purpose |
|------|--------|---------|
| `core/views_home.py` | CREATE | Backend boot API endpoint |
| `core/urls.py` | MODIFY | Added `/api/home/boot/` route |
| `frontend/src/pages/HomePage.tsx` | CREATE | Home page component |
| `frontend/src/lib/api.ts` | MODIFY | Added homeApi |
| `frontend/src/App.tsx` | MODIFY | Updated index route |
| `frontend/src/components/layout/Sidebar.tsx` | MODIFY | Added Home nav link |

---

## Verification Steps

1. **Backend:** `curl -H "Authorization: Token $TOKEN" http://localhost:8000/api/home/boot/`
2. **Frontend:** Navigate to `/` after login - should see Home page
3. **Natural language:** Type a request, verify it routes to `/assistant?message=...`
4. **Quick actions:** Click each button, verify navigation
5. **While away:** Log out, wait, log in - verify counts update

---

## Future Enhancements (Not in Scope)

- Boot animation (typewriter effect on greeting)
- WebSocket for real-time "while away" updates
- Project deep-dive modal
- Decision flow integration
- Voice input support
