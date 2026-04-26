<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Frontend data-flow audit
>
> **Where to look now:**
> - [docs/topics/frontend.md](/docs/topics/frontend.md)
> - [docs/FRONTEND_BACKEND_DATA_FLOW_AUDIT.md](/docs/FRONTEND_BACKEND_DATA_FLOW_AUDIT.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Frontend Data Audit - Complete API Analysis

**Created:** Session 697 (January 6, 2026)
**Updated:** Session 697 (January 6, 2026)
**Purpose:** Document ALL backend API data available vs. what's currently displayed in React frontend

> **Session 697 Progress:** 6 major enhancements implemented - Dashboard Intelligence Metrics, Knowledge Transfer Modal, Agent Keywords/Examples, Gate Checklist Viewer

---

## Executive Summary

This audit examines every React page and identifies rich data returned by backend APIs that is NOT currently displayed. Many APIs return detailed metadata, metrics, and content that could significantly enhance the UI.

### Quick Stats
| Metric | Value |
|--------|-------|
| Total React Pages | 14 |
| Total API Endpoints Used | 60+ |
| Data Fields Hidden | 100+ |
| High-Impact Opportunities | 15 |

---

## 1. DashboardPage (`/`)

**File:** `frontend/src/pages/DashboardPage.tsx` (12.5 KB)

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `ecosystemApi.stats()` | `/api/ecosystem/stats/` | System statistics |
| `dashboardApi.health()` | `/api/v1/health/` | Health check |
| `activityApi.recent()` | `/api/recent-activity/` | Recent activity feed |
| `spidersApi.status()` | `/api/v1/intelligence/spider-status/` | Spider health |

### Ecosystem Stats API - Hidden Data

```json
{
  "stats": {
    "total_agents": 72,           // DISPLAYED
    "active_spiders": 77,         // DISPLAYED
    "celery_tasks": 146,          // DISPLAYED
    "knowledge_transfers": 1970,  // HIDDEN - Rich metric!
    "collaborations": 1013,       // HIDDEN - Shows agent teamwork
    "solutions_deployed": 693,    // HIDDEN - Success metric
    "active_connections": 415,    // HIDDEN - Network health
    "learning_rate": 91.5,        // HIDDEN - AI learning velocity
    "system_efficiency": 94.3     // HIDDEN - Overall health %
  }
}
```

### Dashboard Enhancement Opportunities

| Priority | Enhancement | Data Source | Impact | Status |
|----------|-------------|-------------|--------|--------|
| **HIGH** | Add Knowledge Transfers stat card | `stats.knowledge_transfers` | Shows agent learning volume | **DONE** (Session 697) |
| **HIGH** | Add System Efficiency gauge | `stats.system_efficiency` | Visual health indicator | **DONE** (Session 697) |
| **MEDIUM** | Add Collaborations count | `stats.collaborations` | Shows teamwork | **DONE** (Session 697) |
| **MEDIUM** | Add Learning Rate trend | `stats.learning_rate` | AI improvement velocity | **DONE** (Session 697) |
| **LOW** | Add Solutions Deployed | `stats.solutions_deployed` | Success tracking | **DONE** (Session 697) |
| **LOW** | Add Active Connections | `stats.active_connections` | Network health | **DONE** (Session 697) |

### Recent Activity - Hidden Data

| Field | Currently Displayed | Notes |
|-------|---------------------|-------|
| `id` | No | Could enable click-to-detail |
| `type` | Yes (as title) | |
| `icon` | Yes | |
| `title` | Yes | |
| `subtitle` | Yes | |
| `timestamp` | Yes | |
| `timestamp_display` | No | "20m ago" format available |
| `agents` | No | List of participating agents |

---

## 2. AgentsPage (`/agents`)

**File:** `frontend/src/pages/AgentsPage.tsx` (94 KB)
**Status:** Most enhanced page after Session 694-697 work

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `agentsApi.comprehensive()` | `/api/v1/agents/comprehensive/` | Agent directory |
| `activityApi.recent()` | `/api/recent-activity/` | Activity feed |
| `activityApi.learning()` | `/api/agent-learning/activity/` | Learning feed |
| `dreamsApi.list()` | `/api/agent-dreams/` | Dream gallery |
| `conversationsApi.list()` | `/api/agent-conversations/` | Conversations |
| `decisionsApi.list()` | `/api/boardroom/decisions/` | Decisions |
| `experimentsApi.list()` | `/api/pilot-experiments/` | Experiments |

### Agent Comprehensive API - Hidden Data

| Field | Currently Displayed | Enhancement |
|-------|---------------------|-------------|
| `name` | Yes | |
| `category` | Yes | |
| `description` | Yes | |
| `keywords` | **No** | Add as tags on agent cards |
| `examples` | **No** | Add as tooltip/modal content |
| `is_routable` | Yes (badge) | |
| `is_active` | **No** | Show active/inactive status |
| `priority` | **No** | Show routing priority |

### Recent Enhancements (Session 694-697)

| Feature | Status | Session |
|---------|--------|---------|
| Dream Gallery Modal | DONE | 695 |
| Conversation Thread Modal | DONE | 695 |
| Decision Insights Modal | DONE | 696 |
| Experiment Modal | DONE | 696 |
| Knowledge Transfer Modal | DONE | 697 |
| Activity timestamp_display | DONE | 694 |
| Top Learners section | DONE | 694 |

### Remaining Opportunities

| Priority | Enhancement | Data Source | Status |
|----------|-------------|-------------|--------|
| **MEDIUM** | Agent keywords as tags | `agent.keywords[]` | **DONE** (Session 697) |
| **MEDIUM** | Usage examples tooltip | `agent.examples[]` | **DONE** (Session 697) |
| **LOW** | Active/Inactive indicator | `agent.is_active` | Pending |
| **LOW** | Routing priority badge | `agent.priority` | Pending |

---

## 3. IntelligencePage (`/intelligence`)

**File:** `frontend/src/pages/IntelligencePage.tsx` (144 KB)
**Status:** Largest page, many tabs

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `pilotsApi.gates()` | `/api/pilot-gates/` | Gate management |
| `pilotsApi.dashboard()` | `/api/pilots/dashboard/` | Pilot overview |
| `experimentsApi.list()` | `/api/pilot-experiments/` | Experiments |
| `experimentsApi.portfolio()` | `/api/experiments/portfolio/` | Portfolio view |
| `experimentsApi.learnings()` | `/api/experiments/learnings/` | Learnings |
| `spidersApi.status()` | `/api/v1/intelligence/spider-status/` | Spider status |
| `opportunitiesApi.list()` | `/api/opportunities/` | Opportunities |

### Pilot Gates API - Hidden Rich Content

The `/api/pilot-gates/` API returns detailed AI-generated checklist content:

```json
{
  "checklist_items": [
    {
      "id": "uuid",
      "item_type": "basic_review",
      "title": "Basic Review",
      "description": "Quick review of approach",
      "status": "pending",
      "is_required": false,
      "generated_content": "# BASIC REVIEW CHECKLIST...(~500 lines of AI markdown)",
      "has_content": true
    }
  ],
  "latency": {
    "decision_to_readiness_hours": null,
    "readiness_duration_hours": null,
    "approval_wait_hours": null,
    "total_gate_hours": 2.8,
    "pilot_duration_hours": null
  }
}
```

### Gate Enhancement Opportunities

| Priority | Enhancement | Data Source | Status |
|----------|-------------|-------------|--------|
| **HIGH** | Checklist content viewer modal | `checklist_items[].generated_content` | **DONE** (Session 697) |
| **HIGH** | Latency visualization | `latency.*` fields | Pending |
| **MEDIUM** | Gate timeline chart | `decision_made_at`, `gate_approved_at` | Pending |
| **MEDIUM** | Risk level color coding | Already implemented | **DONE** |

### Experiments API - Hidden Data

| Field | Currently Displayed | Enhancement |
|-------|---------------------|-------------|
| `hypothesis` | Partially | Show full text in modal |
| `extracted_metrics.raw_content` | **No** | AI-generated metrics markdown |
| `learnings` | **No** | Lessons learned text |
| `halt_reason` | **No** | Why experiment was stopped |
| `secondary_kpis` | **No** | Additional KPI tracking |

---

## 4. ContentPage (`/content`)

**File:** `frontend/src/pages/ContentPage.tsx` (30 KB)

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `contentApi.gallery()` | `/api/v1/gallery/list/` | Image gallery |
| `contentApi.unifiedGallery()` | `/api/v1/gallery/all/` | All media |
| `contentApi.videoGallery()` | `/api/v1/gallery/videos/` | Video gallery |
| `contentApi.calendar()` | `/api/content-calendar/` | Content calendar |
| `contentApi.projects()` | `/api/creative-projects/` | Projects |

### Gallery API - Expected Rich Data

| Field | Expected | Purpose |
|-------|----------|---------|
| `id` | Yes | Item identifier |
| `title` | Yes | Display name |
| `prompt` | Yes | Generation prompt |
| `url` | Yes | Media URL |
| `created_at` | Yes | Timestamp |
| `is_favorite` | Yes | Favorite status |
| `metadata` | **Likely hidden** | Generation parameters |
| `agent_name` | **Likely hidden** | Which agent created it |
| `style` | **Likely hidden** | Art style used |

### Content Enhancement Opportunities

| Priority | Enhancement | Data Source |
|----------|-------------|-------------|
| **HIGH** | Generation metadata modal | `item.metadata` |
| **MEDIUM** | Agent attribution | `item.agent_name` |
| **MEDIUM** | Style filtering | `item.style` |
| **LOW** | Prompt history | `item.prompt_history` |

---

## 5. HumanPage (`/human`)

**File:** `frontend/src/pages/HumanPage.tsx` (32 KB)

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `humanApi.attention()` | `/api/human/attention/` | Attention queue |
| `humanApi.attentionStats()` | `/api/human/attention/stats/` | Queue stats |
| `humanApi.control()` | `/api/human/control/` | Agent control |
| `humanApi.preferences()` | `/api/human/preferences/` | User prefs |

### Attention Queue - Expected Rich Data

| Field | Expected | Purpose |
|-------|----------|---------|
| `id` | Yes | Item ID |
| `type` | Yes | decision/approval/review |
| `priority` | Yes | urgent/high/normal/low |
| `title` | Yes | Item title |
| `description` | Yes | Full description |
| `context` | **Likely hidden** | Full context object |
| `agent_reasoning` | **Likely hidden** | Why agent flagged this |
| `confidence_score` | **Likely hidden** | Agent confidence |
| `suggested_action` | **Likely hidden** | AI recommendation |
| `deadline` | **Likely hidden** | Time sensitivity |

### Human Control Enhancement Opportunities

| Priority | Enhancement | Data Source |
|----------|-------------|-------------|
| **HIGH** | Agent reasoning display | `item.agent_reasoning` |
| **HIGH** | Confidence score indicator | `item.confidence_score` |
| **MEDIUM** | Suggested action highlight | `item.suggested_action` |
| **MEDIUM** | Deadline countdown | `item.deadline` |

---

## 6. BettingPage (`/betting`)

**File:** `frontend/src/pages/BettingPage.tsx` (24 KB)

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `bettingApi.stats()` | `/api/v1/betting/stats/` | Betting statistics |
| `bettingApi.wagers()` | `/api/v1/betting/wagers/` | Wager history |
| `bettingApi.liveOdds()` | `/api/v1/sports/live-odds/` | Live odds |
| `bettingApi.arbitrageScan()` | `/api/v1/betting/arbitrage/scan/` | Arb detection |
| `bettingApi.lineMovement()` | `/api/v1/betting/line-movement/` | Line movement |

### Betting Stats API - Hidden Data

```json
{
  "stats": {
    "total_wagers": 0,
    "total_stake": 0.0,
    "total_profit_loss": 0.0,
    "wins": 0,
    "losses": 0,
    "pushes": 0,
    "pending": 0,
    "win_rate": 0.0,
    "roi": 0.0,
    "current_streak": 0,
    "longest_win_streak": 0,       // HIDDEN - streak tracking
    "longest_loss_streak": 0,      // HIDDEN - streak tracking
    "singles_record": {...},       // HIDDEN - bet type breakdown
    "parlays_record": {...},       // HIDDEN - parlay performance
    "stats_by_sport": {...}        // HIDDEN - sport breakdown
  }
}
```

### Betting Enhancement Opportunities

| Priority | Enhancement | Data Source |
|----------|-------------|-------------|
| **HIGH** | Streak visualization | `longest_win_streak`, `longest_loss_streak` |
| **HIGH** | Sport breakdown chart | `stats_by_sport` |
| **MEDIUM** | Singles vs Parlays comparison | `singles_record`, `parlays_record` |
| **MEDIUM** | ROI trend chart | Historical `roi` data |

---

## 7. LegalPage (`/legal`)

**File:** `frontend/src/pages/LegalPage.tsx` (18 KB)

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `legalApi.documents()` | `/api/legal/case-files/` | Case files |
| `legalApi.cases()` | `/api/legal/cases/` | Cases |
| `legalApi.activeCase()` | `/api/legal/active-case/` | Active case |
| `legalApi.litigationDocuments()` | `/api/legal/litigation/{caseId}/documents/` | Litigation docs |
| `legalApi.knowledgeGraph()` | `/api/legal/litigation/{caseId}/knowledge-graph/` | Knowledge graph |

### Legal Enhancement Opportunities

| Priority | Enhancement | Data Source |
|----------|-------------|-------------|
| **HIGH** | Knowledge graph visualization | `knowledgeGraph()` |
| **MEDIUM** | Document analysis results | `document.analysis` |
| **MEDIUM** | Case timeline | `case.events[]` |

---

## 8. PodcastPage (`/podcast`)

**File:** `frontend/src/pages/PodcastPage.tsx` (16 KB)

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `podcastApi.list()` | `/api/podcasts/list/` | Episode list |
| `podcastApi.stats()` | `/api/podcasts/stats/` | Podcast stats |
| `podcastApi.script()` | `/api/podcasts/{id}/script/` | Episode script |

### Podcast Enhancement Opportunities

| Priority | Enhancement | Data Source |
|----------|-------------|-------------|
| **HIGH** | Full script viewer modal | `script()` response |
| **MEDIUM** | Generation progress | `status()` response |
| **LOW** | Agent debate highlights | `episode.debate_summary` |

---

## 9. PortfolioPage (`/portfolio`)

**File:** `frontend/src/pages/PortfolioPage.tsx` (19 KB)

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `portfolioApi.platforms()` | `/api/distribution/platforms/` | Platforms |
| `portfolioApi.accounts()` | `/api/distribution/accounts/` | Connected accounts |
| `portfolioApi.content()` | `/api/distribution/content/` | Distributed content |
| `portfolioApi.stats()` | `/api/distribution/stats/` | Distribution stats |
| `portfolioApi.revenueDashboard()` | `/api/distribution/revenue/dashboard/` | Revenue |
| `portfolioApi.recommendations()` | `/api/distribution/recommendations/` | AI recommendations |

### Portfolio Enhancement Opportunities

| Priority | Enhancement | Data Source |
|----------|-------------|-------------|
| **HIGH** | Revenue dashboard visualization | `revenueDashboard()` |
| **HIGH** | AI recommendations panel | `recommendations()` |
| **MEDIUM** | Platform comparison chart | `comparePlatforms()` |

---

## 10. ProfilePage (`/profile`)

**File:** `frontend/src/pages/ProfilePage.tsx` (18 KB)

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `settingsApi.getProfile()` | `/api/v1/profile/` | User profile |
| `settingsApi.getProfileStats()` | `/api/v1/profile/stats/` | Profile stats |

### Profile Enhancement Opportunities

| Priority | Enhancement | Data Source |
|----------|-------------|-------------|
| **MEDIUM** | Activity heatmap | `stats.activity_by_day` |
| **LOW** | Achievement badges | `stats.achievements` |

---

## 11. SettingsPage (`/settings`)

**File:** `frontend/src/pages/SettingsPage.tsx` (32 KB)

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `settingsApi.getPreferences()` | `/api/preferences/` | User preferences |
| `settingsApi.getPreferenceStats()` | `/api/preferences/stats/` | Preference stats |
| `settingsApi.getNotifications()` | `/api/proactive/notifications/` | Notifications |

### Settings Enhancement Opportunities

| Priority | Enhancement | Data Source |
|----------|-------------|-------------|
| **MEDIUM** | Preference analytics | `getPreferenceStats()` |
| **LOW** | Notification history | `getNotifications()` |

---

## 12. AdminPage (`/admin`)

**File:** `frontend/src/pages/AdminPage.tsx` (29 KB)

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `adminApi.health()` | `/api/v1/health/` | System health |
| `adminApi.systemHealth()` | `/api/system-health/` | Detailed health |
| `adminApi.celeryStatus()` | `/api/celery/status/` | Celery workers |
| `adminApi.celeryStats()` | `/api/celery/stats/` | Celery metrics |
| `adminApi.spiderHealth()` | `/api/spider-health/summary/` | Spider health |
| `adminApi.monitoringHealth()` | `/api/monitoring/health/` | Monitoring |

### Admin Enhancement Opportunities

| Priority | Enhancement | Data Source |
|----------|-------------|-------------|
| **HIGH** | Celery task queue visualization | `celeryStats()` |
| **HIGH** | Spider execution history | `spiderExecutions()` |
| **MEDIUM** | Monitoring schedules display | `monitoringSchedules()` |

---

## 13. AssistantPage (`/assistant`)

**File:** `frontend/src/pages/AssistantPage.tsx` (32 KB)

### APIs Used
| API | Endpoint | Purpose |
|-----|----------|---------|
| `assistantApi.chat()` | `/api/v1/assistant/chat/` | Chat interface |
| `assistantApi.getContext()` | `/api/assistant/context/` | Context |
| `assistantApi.getLearning()` | `/api/assistant/learning/` | Learning data |
| `assistantApi.getAttentionItems()` | `/api/assistant/attention-items/` | Attention queue |
| `assistantApi.getTaskProgress()` | `/api/assistant/task-progress/` | Task progress |

### Assistant Enhancement Opportunities

| Priority | Enhancement | Data Source |
|----------|-------------|-------------|
| **HIGH** | Task progress sidebar | `getTaskProgress()` |
| **HIGH** | Context awareness indicator | `getContext()` |
| **MEDIUM** | Learning history | `getLearning()` |

---

## Priority Enhancement Roadmap

### Phase 1: High Impact, Low Effort (1-2 sessions)

1. **Dashboard Stats Expansion**
   - Add Knowledge Transfers, Collaborations, System Efficiency
   - ~30 minutes work

2. **Agent Keywords/Examples**
   - Add tags and tooltips to agent cards
   - ~1 hour work

3. **Gate Checklist Viewer**
   - Modal to show AI-generated checklist content
   - ~2 hours work

### Phase 2: Medium Impact (2-3 sessions)

4. **Betting Sport Breakdown**
   - Chart showing performance by sport
   - ~2 hours work

5. **Latency Visualization**
   - Timeline showing gate pipeline metrics
   - ~3 hours work

6. **Portfolio Revenue Dashboard**
   - Revenue visualization from API
   - ~3 hours work

### Phase 3: Lower Priority

7. Agent Active/Inactive indicators
8. Profile activity heatmap
9. Celery queue visualization
10. Spider execution history

---

## API Coverage Summary

| Page | APIs Used | Fields Displayed | Fields Hidden | Coverage % |
|------|-----------|------------------|---------------|------------|
| Dashboard | 4 | 8 | 6 | 57% |
| Agents | 7 | 25 | 8 | 76% |
| Intelligence | 7 | 30 | 15 | 67% |
| Content | 5 | 12 | 8 | 60% |
| Human | 4 | 10 | 10 | 50% |
| Betting | 6 | 15 | 10 | 60% |
| Legal | 6 | 10 | 8 | 56% |
| Podcast | 4 | 8 | 5 | 62% |
| Portfolio | 7 | 12 | 10 | 55% |
| Profile | 2 | 6 | 4 | 60% |
| Settings | 3 | 8 | 5 | 62% |
| Admin | 6 | 10 | 12 | 45% |
| Assistant | 5 | 5 | 10 | 33% |

**Overall Average Coverage: 57%** - Significant room for improvement!

---

## Recommendations

1. **Start with Dashboard** - Highest visibility, easiest wins
2. **Continue with Intelligence** - Most complex, most hidden data
3. **Focus on modals** - Pattern established in Session 694-697 works well
4. **Use consistent patterns** - Click-to-expand, hover tooltips, detail modals

---

## Files to Reference

| File | Purpose |
|------|---------|
| `frontend/src/lib/api.ts` | All API endpoint definitions |
| `frontend/src/pages/*.tsx` | Individual page implementations |
| `docs/current/RICH_DATA_AUDIT.md` | Previous detailed audit (Session 695) |

---

**Last Updated:** Session 697
