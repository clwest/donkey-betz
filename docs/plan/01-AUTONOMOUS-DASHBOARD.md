# Option 1: Autonomous Systems Dashboard

**Priority:** 1 (First)
**Status:** Not Started
**Estimated Effort:** Medium (2-3 sessions)

---

## Goal

Create a comprehensive dashboard to visualize and control the 19 autonomous situations running 24/7 on the platform.

---

## Problem Statement

The platform runs 19 autonomous situations with 35 event-driven triggers, but there's no way to:
- See what situations are currently running
- View when they last ran and when they'll run next
- Monitor trigger fire events
- Understand what actions were taken
- Enable/disable situations without code changes

---

## Deliverables

### 1. Situation Overview Panel

**Requirements:**
- [ ] Display all 19 situations in a grid/list
- [ ] Show for each situation:
  - Name and domain (content, income, financial, etc.)
  - Status: `active`, `paused`, `error`
  - Last run timestamp
  - Next scheduled run
  - Run count (last 24h / 7d / 30d)
  - Success rate
- [ ] Color-coded status indicators (green/yellow/red)
- [ ] Click to expand for details

**Data Sources:**
- `AutonomousSituationSession` model
- Celery Beat schedule inspection
- Situation-specific models (ContentChannel, JobMatch, etc.)

---

### 2. Trigger Activity Feed

**Requirements:**
- [ ] Real-time feed of trigger fire events
- [ ] Show for each trigger event:
  - Trigger name
  - Spider that provided data
  - Matched value
  - Severity (low/medium/high/critical)
  - Timestamp
  - Action taken (alert created, notification sent)
- [ ] Filtering by:
  - Domain (blockchain, stocks, content, etc.)
  - Severity
  - Time range
  - Specific trigger
- [ ] Pagination for historical events

**Data Sources:**
- `TriggerEvent` model
- `SituationTrigger` model

---

### 3. Situation Detail View

**Requirements:**
- [ ] Expandable detail panel for each situation
- [ ] Shows situation-specific data:
  - **Content Studio:** Channels, recent episodes, debates, performance
  - **Job Matching:** Recent matches, application status
  - **Market Intelligence:** Recent briefs, movements detected
  - **Blockchain Alerts:** Recent alerts, severity breakdown
  - (similar for all 19 situations)
- [ ] Recent activity timeline
- [ ] Configuration display

---

### 4. Control Panel

**Requirements:**
- [ ] Enable/disable toggle for each situation
- [ ] Pause/resume without disabling
- [ ] Manual trigger button ("Run Now")
- [ ] Cooldown adjustment
- [ ] Discord notification toggle per situation
- [ ] Confirmation dialogs for destructive actions

**Backend:**
- API endpoints for situation control
- Celery task management integration

---

### 5. Performance Metrics

**Requirements:**
- [ ] Charts showing:
  - Situation runs per day (line chart)
  - Success/failure rate (pie chart)
  - Trigger fires by domain (bar chart)
  - Most active situations (ranked list)
- [ ] Time range selector (24h, 7d, 30d, custom)
- [ ] Export capability (CSV, JSON)

---

### 6. Alert Configuration

**Requirements:**
- [ ] Configure which situations send Discord alerts
- [ ] Set alert thresholds (e.g., "alert if situation fails 3x in a row")
- [ ] Choose Discord channels per situation domain
- [ ] Email notification option (future)

---

## Technical Implementation

### Backend (Django)

#### New API Endpoints

```python
# Situation Management
GET  /api/autonomous/situations/                  # List all 19 situations
GET  /api/autonomous/situations/<id>/             # Situation detail
POST /api/autonomous/situations/<id>/toggle/      # Enable/disable
POST /api/autonomous/situations/<id>/run-now/     # Manual trigger
PATCH /api/autonomous/situations/<id>/config/     # Update config

# Trigger Management
GET  /api/autonomous/triggers/                    # List all 35 triggers
GET  /api/autonomous/triggers/<id>/events/        # Trigger fire history
PATCH /api/autonomous/triggers/<id>/              # Update threshold/cooldown

# Analytics
GET  /api/autonomous/analytics/summary/           # Dashboard summary
GET  /api/autonomous/analytics/runs/              # Run history
GET  /api/autonomous/analytics/triggers/          # Trigger analytics
```

#### New View File

Create: `core/views_autonomous_dashboard.py`

```python
# Key functions:
def list_situations(request)
def situation_detail(request, situation_type)
def toggle_situation(request, situation_type)
def run_situation_now(request, situation_type)
def list_trigger_events(request)
def get_analytics_summary(request)
```

#### Model Enhancements

May need to add to existing models:
- `AutonomousSituationSession.is_enabled` field
- `SituationTrigger.discord_channel` field
- Index on `TriggerEvent.fired_at` for fast queries

---

### Frontend (HTML/JS)

#### New Tab in AI Studio

Add "Autonomous" tab to main navigation with sub-sections:
- Overview (situation grid)
- Triggers (trigger feed)
- Analytics (charts)
- Settings (configuration)

#### Components to Build

1. **SituationCard** - Individual situation display
2. **TriggerFeed** - Real-time trigger event list
3. **SituationDetailModal** - Expanded situation view
4. **ControlPanel** - Enable/disable/run controls
5. **AnalyticsCharts** - Chart.js visualizations
6. **AlertConfigForm** - Notification settings

#### WebSocket Integration

Consider WebSocket for real-time updates:
- New trigger fires appear instantly
- Situation status changes reflected immediately

---

## Data Mapping

### The 19 Situations

| Situation | Domain | Model(s) | Schedule |
|-----------|--------|----------|----------|
| Content Studio | content | ContentChannel, ChannelEpisode | 4h |
| Narrative Drift | content | NarrativeDriftTopic | 4h |
| Viral Predictor | content | ViralContentPrediction | 4h |
| Design Trends | creative | DesignTrend | 6h |
| Thumbnail A/B | creative | ThumbnailVariant | on-demand |
| Job Matching | income | JobMatch | 2h |
| Freelance Scout | income | FreelanceOpportunity | 4h |
| Side Hustle | income | SideHustle | 8h |
| Market Desk | financial | MarketIntelligenceBrief | 4h |
| SEC Filing | financial | SECFilingAnalysis | 4h |
| Earnings Predictor | financial | EarningsPrediction | 4h |
| Crypto Sentiment | financial | CryptoSentiment | 2h |
| Blockchain Alerts | financial | BlockchainSecurityAlert | real-time |
| Tech Stack | research | TechStackTrend | 6h |
| AI Model Monitor | research | AIModelRelease | 4h |
| Skill Gap | research | SkillGapAnalysis | 6h |
| Case Law | legal | CaseLawUpdate | 6h |
| Regulatory Change | legal | RegulatoryChange | 8h |
| Stock Alerts | stocks | StockMarketAlert | real-time |

---

## UI Mockup (Text-Based)

```
┌─────────────────────────────────────────────────────────────────────┐
│  AUTONOMOUS SYSTEMS DASHBOARD                              [Settings]│
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  OVERVIEW                                                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │ Content      │ │ Income       │ │ Financial    │ │ Research     ││
│  │ 3 situations │ │ 3 situations │ │ 5 situations │ │ 3 situations ││
│  │ ● All Active │ │ ● All Active │ │ ● 4 Active   │ │ ● All Active ││
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘│
│                                                                      │
│  RECENT TRIGGER ACTIVITY                               [View All →] │
│  ┌──────────────────────────────────────────────────────────────────┐│
│  │ 🔴 HIGH   Whale Movement (250 ETH)      etherscan    2 min ago  ││
│  │ 🟡 MED    AI Model Release (Claude 4)   huggingface  15 min ago ││
│  │ 🟢 LOW    Trending Content Topic        hackernews   32 min ago ││
│  │ 🟡 MED    High-Paying Remote Job        remoteok     1 hour ago ││
│  └──────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  SITUATION STATUS                                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Situation          │ Status  │ Last Run    │ Next Run  │ Runs │ │
│  ├────────────────────┼─────────┼─────────────┼───────────┼──────┤ │
│  │ Content Studio     │ ● Active│ 2h ago      │ in 2h     │ 42   │ │
│  │ Job Matching       │ ● Active│ 45m ago     │ in 1h 15m │ 84   │ │
│  │ Crypto Sentiment   │ ● Active│ 1h ago      │ in 1h     │ 168  │ │
│  │ Market Desk        │ ○ Paused│ 6h ago      │ -         │ 21   │ │
│  │ ...                │         │             │           │      │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Steps

### Phase 1: Backend Foundation
1. [ ] Create `views_autonomous_dashboard.py`
2. [ ] Add situation listing endpoint
3. [ ] Add trigger events endpoint
4. [ ] Add analytics summary endpoint
5. [ ] Test all endpoints via curl/Postman

### Phase 2: Basic Frontend
1. [ ] Add "Autonomous" tab to navigation
2. [ ] Build situation overview grid
3. [ ] Build trigger activity feed
4. [ ] Add basic styling

### Phase 3: Controls & Details
1. [ ] Add enable/disable toggles
2. [ ] Add "Run Now" buttons
3. [ ] Build situation detail modals
4. [ ] Add confirmation dialogs

### Phase 4: Analytics & Polish
1. [ ] Add Chart.js visualizations
2. [ ] Add time range selectors
3. [ ] Add export functionality
4. [ ] Performance optimization

### Phase 5: Real-Time Updates
1. [ ] Add WebSocket consumer for live updates
2. [ ] Integrate with existing WebSocket infrastructure
3. [ ] Test real-time trigger display

---

## Testing Checklist

- [ ] All 19 situations display correctly
- [ ] Trigger events appear in real-time
- [ ] Enable/disable works for each situation
- [ ] "Run Now" triggers immediate execution
- [ ] Analytics data is accurate
- [ ] Charts render correctly
- [ ] Mobile responsive
- [ ] No performance issues with large trigger history

---

## Success Criteria

1. **Visibility:** Can see status of all 19 situations at a glance
2. **Control:** Can pause/resume any situation without code changes
3. **Monitoring:** Trigger fires visible within 5 seconds of occurring
4. **Analytics:** Clear understanding of what's most active
5. **Reliability:** Dashboard loads in <2 seconds

---

## Dependencies

- Existing models: `AutonomousSituationSession`, `SituationTrigger`, `TriggerEvent`
- Existing Celery Beat configuration in `core/celery.py`
- Situation-specific models in `core/models_autonomous_*.py`

---

## Notes

- Consider caching for analytics queries (Redis)
- May want to limit trigger event history to last 7 days in UI
- WebSocket optional for Phase 1, nice-to-have for Phase 2+
