# Autonomous Content Studio - Complete Implementation Plan

**Session:** 466 (Current)
**Status:** PLANNING → IMPLEMENTATION
**Type:** Tier 1 Autonomous Situation #3
**Dependencies:** Session 445 (AI Series Workflow), Sessions 442-444 (Voice), Session 465 (Learning Loop Pattern)

---

## Vision

**"Give me a topic domain → The system runs a content channel forever"**

Example:
- User: "Run a channel about AI for kids"
- System: Autonomously creates daily/weekly content, optimizes based on performance, never stops

---

## The 5 Autonomous Situation Properties

### 1. Persistent Context ✅
**What:** Channel remembers what content performed well, what topics resonate, what styles work

**Implementation:**
- `ContentChannel` model - stores channel config and history
- `ChannelPerformance` model - tracks views, engagement per episode
- `TopicPreference` model - learns which topics work best for audience

### 2. Incoming Signals ✅
**What:** System monitors trends, audience feedback, competitor content

**Inputs:**
- Spider network (62 spiders) - trending topics in niche
- YouTube/TikTok APIs (optional) - competitor analysis
- Performance metrics - what's working/not working
- User feedback - Discord reactions, comments

### 3. Internal Disagreement ✅
**What:** Agents debate content angles before creating

**Agents:**
- **Topic Miner** - "We should cover X because it's trending"
- **Contrarian Agent** - "Everyone's covering X, let's do Y instead"
- **Performance Analyst** - "Our audience prefers Z based on data"
- **Creative Director** - "Here's a unique angle on the topic"

### 4. Outputs with Consequences ✅
**What:** Content is published, tracked, and performance affects future decisions

**Outputs:**
- Published videos (YouTube, TikTok, Instagram)
- Performance metrics (views, engagement, retention)
- Revenue tracking (if monetized)
- Learning records (what worked, what didn't)

### 5. Self-Renewal ✅
**What:** System schedules its own next content cycle and improves

**Self-Renewal:**
- Daily/weekly content calendar
- Automatic topic selection based on performance
- Style optimization (learns which styles work)
- Voice optimization (learns which voice/tone works)
- Self-triggered re-runs when performance drops

---

## What We Already Have (Session 445)

✅ **AISeriesWorkflowAgent** - Creates multi-episode series
✅ **Database Models** - AISeries, SeriesEpisode, SeriesCharacter
✅ **Discord Commands** - /series-create, /series-status, /series-list
✅ **Celery Task** - generate_ai_series
✅ **Content Pipeline** - Research → Script → Character → Voice → Video

**Gap:** Everything is MANUAL (user triggers). We need AUTONOMOUS operation.

---

## What We Need to Build

### NEW MODELS

#### 1. `ContentChannel` (Core)
```python
class ContentChannel(models.Model):
    """
    An autonomous content channel that runs forever.

    Example: "AI Explained for Kids" YouTube channel
    - Publishes 2 videos/week
    - Educational style, Pixar animation
    - Uses "Rachel" voice
    - Learns from engagement
    """
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)

    # Channel Config
    name = CharField(max_length=200)  # "AI for Kids"
    topic_domain = TextField()  # "artificial intelligence, machine learning, explained for children"
    target_audience = CharField(max_length=200)  # "Kids 8-12"
    content_frequency = CharField()  # 'daily', 'weekly', 'bi-weekly'

    # Style Config
    visual_style = CharField()  # "pixar, colorful, friendly"
    voice_id = CharField()  # Voice from Session 442-444
    content_type = CharField()  # 'educational', 'entertainment', 'marketing'

    # Publishing Config
    platform = CharField()  # 'youtube', 'tiktok', 'instagram', 'all'
    publish_automatically = BooleanField(default=False)  # Auto-publish or queue for review

    # Performance Tracking
    total_episodes_created = IntegerField(default=0)
    total_views = IntegerField(default=0)
    total_engagement = IntegerField(default=0)
    avg_retention_rate = DecimalField(default=0.0)

    # Autonomous Control
    is_active = BooleanField(default=True)
    next_content_due = DateTimeField()  # When next episode is due
    last_content_created = DateTimeField(null=True)

    # Learning Config
    confidence_multiplier = DecimalField(default=1.0)  # Like Session 464 learning loop

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### 2. `ChannelEpisode` (Content Record)
```python
class ChannelEpisode(models.Model):
    """
    A single piece of content created for a channel.
    Links to AISeries/SeriesEpisode for actual content.
    """
    id = UUIDField(primary_key=True)
    channel = ForeignKey(ContentChannel)
    series = ForeignKey(AISeries, null=True)  # Link to Session 445 content

    # Episode Info
    title = CharField(max_length=200)
    topic = CharField(max_length=200)  # What this episode is about
    publish_date = DateTimeField(null=True)

    # Performance Metrics
    views = IntegerField(default=0)
    likes = IntegerField(default=0)
    comments = IntegerField(default=0)
    shares = IntegerField(default=0)
    watch_time = IntegerField(default=0)  # seconds
    retention_rate = DecimalField(default=0.0)  # 0-1

    # Learning
    performance_score = DecimalField(default=0.0)  # Calculated metric
    contributed_to_learning = BooleanField(default=False)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### 3. `TopicPerformance` (Learning)
```python
class TopicPerformance(models.Model):
    """
    Tracks which topics perform well for a channel.
    Enables learning: "Space topics get 2x views, aliens get 3x"
    """
    id = UUIDField(primary_key=True)
    channel = ForeignKey(ContentChannel)
    topic = CharField(max_length=200)

    # Performance
    episode_count = IntegerField(default=0)
    avg_views = DecimalField(default=0.0)
    avg_engagement = DecimalField(default=0.0)
    avg_retention = DecimalField(default=0.0)

    # Learning
    confidence_score = DecimalField(default=1.0)  # How confident we are this topic works
    last_tested = DateTimeField()
```

#### 4. `ContentDebate` (Internal Disagreement)
```python
class ContentDebate(models.Model):
    """
    Records agent debates about content decisions.
    Enables transparency: "Why did you choose this topic?"
    """
    id = UUIDField(primary_key=True)
    channel = ForeignKey(ContentChannel)
    debate_date = DateTimeField(auto_now_add=True)

    # Topic being debated
    proposed_topic = CharField(max_length=200)

    # Agent positions
    topic_miner_position = TextField()  # "Trending now because..."
    contrarian_position = TextField()  # "Too saturated, try..."
    analyst_position = TextField()  # "Past data shows..."
    director_position = TextField()  # "Unique angle could be..."

    # Decision
    final_decision = CharField(max_length=200)
    chosen_angle = TextField()
    decision_reasoning = TextField()
```

---

### NEW AGENTS

#### 1. `AutonomousContentStudioCoordinator` (Main)
**Purpose:** Orchestrates the entire autonomous content studio

**Responsibilities:**
- Monitors channel schedules (which channel needs content when)
- Triggers content creation cycles
- Coordinates agent debates
- Tracks performance and adjusts strategy
- Self-schedules next content cycle

**Tools:**
- `check_channel_schedule` - See which channels need content
- `initiate_content_debate` - Start agent discussion about next topic
- `trigger_content_creation` - Use AISeriesWorkflowAgent to create content
- `analyze_performance` - Check how recent content performed
- `update_channel_strategy` - Adjust based on learnings

#### 2. `TopicMinerAgent`
**Purpose:** Finds trending topics in channel's domain

**Tools:**
- `query_spiders` - Search spider data for trends
- `analyze_competitors` - See what's working for others
- `detect_gaps` - Find underserved topics
- `score_opportunity` - Rate topic potential

#### 3. `ContrarianAgent`
**Purpose:** Challenges obvious choices, finds unique angles

**Tools:**
- `challenge_topic` - Provide alternative view
- `find_unique_angle` - Suggest contrarian approach
- `detect_saturation` - Warn if topic is oversaturated

#### 4. `PerformanceAnalystAgent`
**Purpose:** Analyzes past performance to guide decisions

**Tools:**
- `analyze_topic_performance` - Which topics worked before
- `analyze_style_performance` - Which styles worked before
- `calculate_confidence` - How confident are we in this choice
- `predict_performance` - Estimate how new content will perform

---

### CELERY TASKS (Autonomous Scheduling)

#### 1. `run_autonomous_content_studio` (Main Loop)
**Schedule:** Every 4 hours (or configurable)

```python
@shared_task
def run_autonomous_content_studio():
    """
    Main autonomous loop - runs every 4 hours.

    1. Check which channels need content (next_content_due < now)
    2. For each channel:
       - Trigger agent debate about next topic
       - Create content if approved
       - Update channel schedule
       - Track performance of recent content
    """
    pass
```

#### 2. `track_content_performance` (Learning)
**Schedule:** Daily at 8 PM

```python
@shared_task
def track_content_performance():
    """
    Track performance of published content.

    1. Fetch metrics from publishing platforms (YouTube API, etc.)
    2. Update ChannelEpisode performance
    3. Update TopicPerformance learning
    4. Adjust channel confidence multipliers
    """
    pass
```

#### 3. `generate_content_for_channel` (Worker)
**Trigger:** Called by main loop when content is due

```python
@shared_task
def generate_content_for_channel(channel_id):
    """
    Creates content for a specific channel.

    1. Run agent debate (Topic Miner vs Contrarian vs Analyst)
    2. Decide on topic and angle
    3. Use AISeriesWorkflowAgent to create content
    4. Publish or queue for review
    5. Schedule next content cycle
    """
    pass
```

---

### DISCORD COMMANDS (Control)

#### 1. `/studio-create`
Create new autonomous content channel

```
/studio-create
  name: "AI for Kids"
  topic: "artificial intelligence explained for children"
  frequency: "weekly"
  style: "pixar"
  voice: "Rachel"
```

#### 2. `/studio-list`
List all active channels with status

#### 3. `/studio-status <channel_id>`
Show channel performance, next content due, recent debates

#### 4. `/studio-pause <channel_id>`
Pause autonomous content generation

#### 5. `/studio-resume <channel_id>`
Resume autonomous content generation

#### 6. `/studio-performance <channel_id>`
Show detailed performance analytics

---

## Implementation Phases

### Phase 1: Database & Models (Today)
- [ ] Create 4 new models (ContentChannel, ChannelEpisode, TopicPerformance, ContentDebate)
- [ ] Create migration
- [ ] Test database schema

### Phase 2: Core Coordinator Agent (Today)
- [ ] Build AutonomousContentStudioCoordinator
- [ ] Implement tools (check schedule, trigger creation, etc.)
- [ ] Test manual coordination

### Phase 3: Debate Agents (Tomorrow)
- [ ] Build TopicMinerAgent
- [ ] Build ContrarianAgent
- [ ] Build PerformanceAnalystAgent
- [ ] Test agent debates

### Phase 4: Celery Tasks (Tomorrow)
- [ ] Implement run_autonomous_content_studio
- [ ] Implement generate_content_for_channel
- [ ] Implement track_content_performance
- [ ] Wire up Celery Beat schedules

### Phase 5: Discord Integration (Day 3)
- [ ] Build 6 Discord commands
- [ ] Test channel creation
- [ ] Test channel control (pause/resume)

### Phase 6: End-to-End Testing (Day 3)
- [ ] Create test channel
- [ ] Let it run autonomously for 48 hours
- [ ] Verify content creation
- [ ] Verify performance tracking
- [ ] Verify learning loop

### Phase 7: Documentation (Day 3)
- [ ] Create handoff doc
- [ ] Update CAPABILITIES.md
- [ ] Update AGENTS.md
- [ ] Create user guide

---

## Success Criteria

The Autonomous Content Studio is complete when:

1. ✅ **Persistent Context** - Channel remembers performance data
2. ✅ **Incoming Signals** - Monitors trends via spiders
3. ✅ **Internal Disagreement** - Agents debate topics before creating
4. ✅ **Outputs with Consequences** - Content published & tracked
5. ✅ **Self-Renewal** - Schedules own next cycle, improves over time

**Demo:**
- Create channel "Space Facts for Kids"
- Let run for 1 week
- Show: 7 videos created autonomously, performance tracked, topics adjusted based on data

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `core/models_autonomous_studio.py` | CREATE | 4 new models |
| `core/agents/autonomous_content_studio_coordinator.py` | CREATE | Main coordinator |
| `core/agents/content/topic_miner_agent.py` | CREATE | Trend detection |
| `core/agents/content/contrarian_agent.py` | CREATE | Unique angles |
| `core/agents/content/performance_analyst_agent.py` | CREATE | Learning from data |
| `core/tasks.py` | MODIFY | Add 3 new Celery tasks |
| `core/celery.py` | MODIFY | Add Celery Beat schedules |
| `core/services/discord_bot.py` | MODIFY | Add 6 new commands |
| `core/migrations/0093_autonomous_studio.py` | CREATE | Database migration |

---

## Next Steps

**RIGHT NOW:**
1. Create the 4 database models
2. Run migration
3. Build AutonomousContentStudioCoordinator skeleton
4. Test basic flow

**Then proceed phase by phase until 100% complete.**
