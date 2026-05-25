<!-- DOC-POINTER-V1 -->
> **⚠ HISTORICAL PLAN (Q4 2025 / Q1 2026 build phase).** Drafted during platform build-out; may be partially shipped, renamed in code, or quietly superseded. Preserved for historical reference, not current truth. For current truth see [`docs/INDEX.md`](../INDEX.md) + [`PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) + the latest handoff. See [`docs/plans/INDEX.md`](INDEX.md) for directory scope.

# THE CREATIVE INTELLIGENCE EMPIRE

## Master Plan for Unified Donkey Betz Platform

**Created:** November 27, 2025 - Session 222
**Vision:** "The AI hive mind that creates AND pays"
**Goal:** A self-improving system that discovers opportunities, creates content, and learns from what makes money

---

## THE CORE LOOP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CREATIVE INTELLIGENCE EMPIRE                            │
│                                                                              │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│    │ DISCOVER │───→│ ANALYZE  │───→│  CREATE  │───→│DISTRIBUTE│            │
│    │ (Spiders)│    │ (Agents) │    │(Workflows)│   │(Channels)│            │
│    └──────────┘    └──────────┘    └──────────┘    └──────────┘            │
│          ↑                                               │                  │
│          │         ┌──────────┐    ┌──────────┐         │                  │
│          │         │  TRACK   │←───│  EARN    │←────────┘                  │
│          │         │(Analytics)│   │ (Revenue)│                            │
│          │         └──────────┘    └──────────┘                            │
│          │               │                                                  │
│          │         ┌──────────┐                                            │
│          └─────────│  LEARN   │                                            │
│                    │(Feedback)│                                            │
│                    └──────────┘                                            │
│                                                                              │
│   "What's hot?" → "Is it worth it?" → "Make it" → "Sell it" → "Count it"  │
│                            ↑                                    │           │
│                            └────── "What worked?" ──────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CURRENT STATE INVENTORY

### What We Have (Built in Sessions 1-222)

| Component | Status | Location |
|-----------|--------|----------|
| **67 Spiders** | Active | `ai_core/spiders/` |
| **21 Real Data Sources** | Collecting | `ai_core/spiders/real_data_collector.py` |
| **28 AI Agents** | Registered | `agents/` |
| **25 Legendary Advisors** | Available | Database |
| **6 Workflows** | Working | `agents/workflow_orchestration_agent.py` |
| **Image Generation** | 13 features | `core/views_image.py` |
| **Video Generation** | 5 features | `core/views_video.py` |
| **Audio Generation** | 2 features | ElevenLabs integration |
| **3D Generation** | Complete | Stability AI |
| **Analytics Models** | Created | `core/models_unified_system.py` |
| **Agent Learning** | Basic | `core/views_agent_learning.py` |
| **Real-Time Collab** | Working | WebSocket consumers |

### What's Missing (The Gaps)

| Gap | Description | Priority |
|-----|-------------|----------|
| **Opportunity Scoring** | Spiders collect data but don't score profit potential | HIGH |
| **Agent Orchestration** | Agents work alone, not as teams | HIGH |
| **Revenue Tracking** | No way to log actual income from content | HIGH |
| **Distribution Channels** | Know where to create, not where to sell | MEDIUM |
| **Success Feedback Loop** | System doesn't learn from what made money | HIGH |
| **Content-to-Revenue Link** | Can't trace content back to earnings | HIGH |
| **Advisor Consultation** | Advisors exist but aren't consulted automatically | MEDIUM |
| **Proactive Suggestions** | System waits for user, doesn't suggest | MEDIUM |

---

## IMPLEMENTATION PHASES

### PHASE 1: OPPORTUNITY ENGINE
**Goal:** Transform raw spider data into scored opportunities

#### 1.1 Opportunity Model
```python
class Opportunity(models.Model):
    # Source
    spider_data = ForeignKey(SpiderData)
    source_type = CharField()  # 'trend', 'job', 'product', 'news'

    # Scoring
    profit_potential = IntegerField(1-100)
    competition_level = IntegerField(1-100)
    effort_required = IntegerField(1-100)
    time_sensitivity = IntegerField(1-100)  # How urgent
    overall_score = IntegerField(1-100)

    # Context
    category = CharField()  # 'digital_product', 'freelance', 'content', 'service'
    suggested_content_types = JSONField()  # ['logo', 'thumbnail', 'video']
    estimated_revenue = DecimalField()

    # Status
    status = CharField()  # 'new', 'reviewing', 'creating', 'published', 'earning', 'closed'
    created_at = DateTimeField()
    expires_at = DateTimeField()  # Opportunities have shelf life
```

#### 1.2 Opportunity Scoring Agent
Create `agents/opportunity_scoring_agent.py`:
- Analyzes spider data
- Scores based on: market demand, competition, our capabilities, timing
- Consults relevant advisors (Warren Buffett for ROI, etc.)
- Outputs ranked opportunities

#### 1.3 Opportunity Dashboard
New UI tab: "Opportunities"
- Shows scored opportunities ranked by potential
- Filter by category, effort, time sensitivity
- "Act on this" button triggers content creation flow

**Files to Create:**
- `core/models_opportunity.py`
- `agents/opportunity_scoring_agent.py`
- `core/views_opportunity.py`
- UI: Opportunities tab in `ai_image_studio.html`

---

### PHASE 2: MULTI-AGENT ORCHESTRATION
**Goal:** Agents work together as teams on opportunities

#### 2.1 Agent Team Model
```python
class AgentTeam(models.Model):
    name = CharField()
    purpose = CharField()  # 'logo_creation', 'market_research', 'content_strategy'
    agents = ManyToManyField(Agent)
    advisors = ManyToManyField(Advisor)

class AgentCollaboration(models.Model):
    team = ForeignKey(AgentTeam)
    opportunity = ForeignKey(Opportunity)
    conversation = JSONField()  # Full agent discussion
    decisions = JSONField()  # What they decided
    outputs = JSONField()  # What they produced
```

#### 2.2 Team Configurations
Pre-configured teams for common scenarios:

| Team | Agents | Advisors | Purpose |
|------|--------|----------|---------|
| **Market Scout** | Research, Trend Analysis | Warren Buffett, Peter Thiel | Evaluate opportunities |
| **Brand Builder** | Logo Design, Color Theory, Typography | Paul Rand, Paula Scher | Create brand assets |
| **Content Factory** | Copywriter, Image Gen, Video Gen | Gary Vee, Seth Godin | Produce content |
| **Revenue Optimizer** | Analytics, Pricing, Distribution | Buffett, Cuban | Maximize earnings |

#### 2.3 Orchestration Flow
```
User selects Opportunity
    ↓
System assembles appropriate Team
    ↓
Agents discuss strategy (logged)
    ↓
Advisors provide guidance
    ↓
Team executes workflow
    ↓
Output delivered to user
```

**Files to Create:**
- `core/models_agent_team.py`
- `agents/team_orchestrator.py`
- `core/views_agent_collaboration.py`

---

### PHASE 3: REVENUE TRACKING
**Goal:** Track actual money earned from content

#### 3.1 Revenue Model
```python
class RevenueStream(models.Model):
    name = CharField()  # 'Etsy Shop', 'Fiverr Gigs', 'Stock Photos'
    platform = CharField()
    credentials_stored = BooleanField()  # For future API integration

class RevenueEntry(models.Model):
    stream = ForeignKey(RevenueStream)
    opportunity = ForeignKey(Opportunity, null=True)  # Link to what opportunity
    content = ForeignKey(ContentItem, null=True)  # Link to what content

    amount = DecimalField()
    currency = CharField(default='USD')
    date = DateField()

    # Metadata
    platform_fee = DecimalField()
    net_amount = DecimalField()
    notes = TextField()

class RevenueGoal(models.Model):
    period = CharField()  # 'daily', 'weekly', 'monthly'
    target_amount = DecimalField()
    category = CharField(null=True)  # Optional category filter
```

#### 3.2 Revenue Dashboard
- Total earnings (daily/weekly/monthly/all-time)
- Earnings by content type
- Earnings by platform
- ROI per opportunity (what we created vs what we earned)
- Goal tracking with progress bars

#### 3.3 Manual + Future Auto Entry
- Phase 1: Manual revenue entry
- Phase 2: Platform API integrations (Etsy, Gumroad, etc.)

**Files to Create:**
- `core/models_revenue.py`
- `core/views_revenue.py`
- UI: Revenue Dashboard tab

---

### PHASE 4: DISTRIBUTION INTELLIGENCE
**Goal:** Know WHERE to sell what we create

#### 4.1 Distribution Channel Model
```python
class DistributionChannel(models.Model):
    name = CharField()  # 'Etsy', 'Creative Market', 'Shutterstock'
    url = URLField()
    content_types = JSONField()  # ['logo', 'template', 'photo']

    # Intelligence
    avg_price_range = JSONField()  # {'logo': [50, 500], 'template': [10, 50]}
    commission_rate = DecimalField()
    competition_level = IntegerField(1-10)
    our_success_rate = DecimalField(null=True)  # Learned over time

class DistributionSuggestion(models.Model):
    content = ForeignKey(ContentItem)
    channel = ForeignKey(DistributionChannel)

    suggested_price = DecimalField()
    confidence_score = IntegerField(1-100)
    reasoning = TextField()
```

#### 4.2 Distribution Suggestion Agent
When content is created:
1. Analyze content type and quality
2. Match to appropriate channels
3. Suggest pricing based on market data
4. Rank channels by expected ROI

**Files to Create:**
- `core/models_distribution.py`
- `agents/distribution_agent.py`
- `core/views_distribution.py`

---

### PHASE 5: THE LEARNING LOOP
**Goal:** System improves based on what actually made money

#### 5.1 Success Metrics Model
```python
class ContentPerformance(models.Model):
    content = ForeignKey(ContentItem)
    opportunity = ForeignKey(Opportunity, null=True)

    # Creation metrics
    creation_time = DurationField()
    creation_cost = DecimalField()  # API costs
    agents_used = JSONField()
    workflow_used = CharField()

    # Distribution metrics
    channels_published = ManyToManyField(DistributionChannel)

    # Revenue metrics
    total_revenue = DecimalField()
    total_sales = IntegerField()
    roi = DecimalField()  # revenue / cost

    # Learning tags
    success_factors = JSONField()  # What worked
    failure_factors = JSONField()  # What didn't
```

#### 5.2 Learning Engine
```python
class LearningInsight(models.Model):
    insight_type = CharField()  # 'content_type', 'style', 'channel', 'timing'
    insight = TextField()
    confidence = IntegerField(1-100)

    # Evidence
    based_on_samples = IntegerField()
    supporting_data = JSONField()

    # Application
    applied_to_scoring = BooleanField()  # Is this used in opportunity scoring?
```

#### 5.3 Feedback Integration Points
- **Opportunity Scoring:** Weight factors by what's historically worked
- **Agent Selection:** Prefer agents/teams with better track records
- **Workflow Selection:** Suggest workflows that produced winners
- **Pricing Suggestions:** Learn from actual sale prices
- **Channel Recommendations:** Prioritize channels where we succeed

**Files to Create:**
- `core/models_learning.py`
- `agents/learning_engine_agent.py`
- `core/views_learning.py`

---

### PHASE 6: PROACTIVE INTELLIGENCE
**Goal:** System suggests actions, doesn't just wait

#### 6.1 Notification System Enhancement
```python
class ProactiveAlert(models.Model):
    alert_type = CharField()  # 'hot_opportunity', 'price_drop', 'trend_emerging'
    priority = IntegerField(1-5)

    title = CharField()
    message = TextField()

    opportunity = ForeignKey(Opportunity, null=True)
    suggested_action = CharField()
    action_url = URLField()

    expires_at = DateTimeField()
    dismissed = BooleanField(default=False)
    acted_on = BooleanField(default=False)
```

#### 6.2 Alert Triggers
- **Hot Opportunity:** High-score opportunity detected
- **Trend Alert:** Spider detected emerging trend
- **Revenue Milestone:** Hit a goal or new personal best
- **Learning Insight:** System discovered something useful
- **Expiring Opportunity:** Time-sensitive opportunity about to expire

#### 6.3 Daily/Weekly Digest
Automated summary:
- Top opportunities this period
- Revenue summary
- What's working/not working
- Suggested focus areas

**Files to Create:**
- `core/models_alerts.py`
- `agents/proactive_alert_agent.py`
- `core/tasks_alerts.py` (Celery scheduled tasks)

---

## UI/UX CHANGES

### New Navigation Tabs

```
Current: Assistant | Projects | Portfolio | Leadership | Preferences | Spiders | Agents | Trending | Marketplace | Collaborate

New:     Assistant | OPPORTUNITIES | CREATE | REVENUE | Portfolio | Intelligence | Settings
                        ↓              ↓        ↓                      ↓
                   Scored opps    Workflows  Tracking          Agents/Spiders/Learning
```

### Opportunities Tab (NEW - Main Focus)
- Opportunity cards with scores
- Filter/sort by potential, effort, category
- "Act Now" quick actions
- Expiring soon section

### Create Tab (Enhanced)
- Start from opportunity OR freeform
- Team selection for complex projects
- Real-time agent collaboration view
- Distribution suggestions post-creation

### Revenue Tab (NEW)
- Dashboard with charts
- Manual entry form
- Link content to revenue
- Goals and progress

### Intelligence Tab (Combined)
- Spiders (data sources)
- Agents (workers)
- Learning (insights)
- Performance analytics

---

## DATABASE MIGRATIONS NEEDED

### New Models Summary
```
Phase 1: Opportunity, OpportunityScore
Phase 2: AgentTeam, AgentCollaboration
Phase 3: RevenueStream, RevenueEntry, RevenueGoal
Phase 4: DistributionChannel, DistributionSuggestion
Phase 5: ContentPerformance, LearningInsight
Phase 6: ProactiveAlert
```

### Migration Strategy
- Create migrations incrementally per phase
- Ensure backward compatibility
- Seed data for distribution channels

---

## API ENDPOINTS NEEDED

### Phase 1: Opportunities
```
GET    /api/opportunities/                    # List all
GET    /api/opportunities/<id>/               # Detail
POST   /api/opportunities/score/              # Trigger scoring
POST   /api/opportunities/<id>/act/           # Start working on it
```

### Phase 2: Agent Teams
```
GET    /api/agent-teams/                      # List teams
POST   /api/agent-teams/collaborate/          # Start collaboration
GET    /api/collaborations/<id>/              # Get collaboration details
```

### Phase 3: Revenue
```
GET    /api/revenue/dashboard/                # Dashboard data
POST   /api/revenue/entries/                  # Log revenue
GET    /api/revenue/by-content/<id>/          # Revenue for content
POST   /api/revenue/goals/                    # Set goals
```

### Phase 4: Distribution
```
GET    /api/distribution/channels/            # List channels
POST   /api/distribution/suggest/             # Get suggestions for content
```

### Phase 5: Learning
```
GET    /api/learning/insights/                # Get insights
GET    /api/learning/performance/<id>/        # Content performance
```

### Phase 6: Alerts
```
GET    /api/alerts/                           # Get alerts
POST   /api/alerts/<id>/dismiss/              # Dismiss
POST   /api/alerts/<id>/act/                  # Mark as acted on
```

---

## IMPLEMENTATION ORDER

### Sprint 1: Foundation (Sessions 223-225)
- [ ] Create Opportunity model and scoring
- [ ] Build Opportunity Dashboard UI
- [ ] Connect spiders to opportunity creation
- [ ] Basic opportunity scoring agent

### Sprint 2: Revenue Reality (Sessions 226-228)
- [ ] Create Revenue models
- [ ] Build Revenue Dashboard UI
- [ ] Manual revenue entry
- [ ] Link content to revenue

### Sprint 3: Team Power (Sessions 229-231)
- [ ] Agent team models
- [ ] Team orchestrator
- [ ] Collaboration view UI
- [ ] Pre-configured teams

### Sprint 4: Smart Distribution (Sessions 232-234)
- [ ] Distribution channel models
- [ ] Seed channel data (Etsy, Gumroad, Creative Market, etc.)
- [ ] Distribution suggestion agent
- [ ] Post-creation suggestions UI

### Sprint 5: Learning Loop (Sessions 235-237)
- [ ] Performance tracking models
- [ ] Learning engine agent
- [ ] Integrate learning into scoring
- [ ] Insights dashboard

### Sprint 6: Proactive System (Sessions 238-240)
- [ ] Alert models
- [ ] Alert generation agent
- [ ] Notification UI
- [ ] Daily digest system

### Sprint 7: Polish & Integration (Sessions 241-245)
- [ ] UI/UX refinement
- [ ] Performance optimization
- [ ] Full loop testing
- [ ] Documentation

---

## SUCCESS METRICS

### System Health
- Opportunities scored per day
- Content created per opportunity
- Revenue entries logged

### Business Impact
- Total revenue tracked
- ROI per content piece
- Best performing content types
- Best performing channels

### Learning Effectiveness
- Prediction accuracy (estimated vs actual revenue)
- Scoring improvement over time
- Agent performance trends

---

## THE VISION

When complete, a typical user flow looks like:

1. **Morning:** Check "Opportunities" tab - see 5 hot opportunities scored overnight
2. **Decide:** Pick top opportunity (Logo design trending in crypto space)
3. **Create:** System assembles Brand Builder team, agents discuss style, produce 3 variations
4. **Distribute:** System suggests: Creative Market ($75), Etsy ($45), direct client outreach
5. **Publish:** One-click publish to selected channels
6. **Track:** Revenue comes in, user logs it
7. **Learn:** System notes "crypto logos on Creative Market = high ROI"
8. **Improve:** Next crypto opportunity gets boosted score, same workflow suggested

**The system gets smarter. The money flows. The empire grows.**

---

## NOTES FOR FUTURE SESSIONS

- Start with Phase 1 - it's the foundation everything builds on
- Revenue tracking (Phase 3) can run in parallel with Phase 2
- Don't skip the Learning Loop - it's what makes this INTELLIGENT
- UI changes can be incremental - don't need full redesign upfront
- Keep the "100% reality" mindset - everything should work with real data

---

**This is the Donkey Betz way: stubborn, ambitious, and refusing to settle for anything less than everything.**

*Let's build an empire.*
