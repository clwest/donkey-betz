<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_WHAT_IT_IS.md`](/docs/PLATFORM_WHAT_IT_IS.md) and [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.

# Autonomous Systems - Situations, Triggers & Self-Running Intelligence

**Last Updated:** December 17, 2025 (Session 484) — narrative preserved; counts may drift
**Status:** Production-Ready | 19 Situations | 35 Triggers | 44 Celery Tasks (Session 484 snapshot — canonical Celery task count = 365; see PLATFORM_INVENTORY)

---

## Overview

The platform implements a sophisticated **Autonomous Intelligence Architecture** with:

- **19 Tier 1 Autonomous Situations** - Self-running intelligence cycles
- **35 Pre-configured Triggers** - Real-time event detection
- **44 Celery Beat Tasks** - Scheduled automation
- **Event-Driven Architecture** - Instant response to signals

---

## The 5 Autonomous Properties

Every Tier 1 Autonomous Situation implements these 5 properties:

| Property | Description | Implementation |
|----------|-------------|----------------|
| **1. Persistent Context** | Database-backed state that survives restarts | `ContentChannel`, `TopicPerformance` models |
| **2. Incoming Signals** | Spider data feeding decisions | Spider network (67 spiders) |
| **3. Internal Disagreement** | Multi-agent debates before decisions | 3-4 agent debate system |
| **4. Outputs with Consequences** | Performance tracked and affects future | `performance_score`, `confidence_score` |
| **5. Self-Renewal** | Auto-schedules next cycle | `schedule_next_content()` methods |

---

## The 19 Autonomous Situations

### Creative & Content Domain (3 Situations)

#### Situation #1: Autonomous Content Studio
**Sessions:** 466, 468, 469
**Status:** FULLY OPERATIONAL

Creates content autonomously with agent debates:

```
ContentChannel → TopicMinerAgent (FOR)
                          ↓
              ContrarianAgent (AGAINST)
                          ↓
              PerformanceAnalystAgent (DATA)
                          ↓
              CreativeDirectorAgent (FINAL)
                          ↓
              ChannelEpisode (OUTPUT)
                          ↓
              TopicPerformance (LEARNING)
```

**Models:**
- `ContentChannel` - Channel configuration
- `ChannelEpisode` - Published content
- `TopicPerformance` - Learning metrics
- `ContentDebate` - Debate records

**Schedule:** Every 4 hours (checks channels due for content)

---

#### Situation #2: Narrative Drift Detector
**Session:** 471
**Status:** ACTIVE

Tracks how narratives evolve over time:
- Detects when trends break or reverse
- Analyzes cultural/narrative implications
- Historical context tracking

**Agents:** NarrativeHistorianAgent, TrendBreakDetectorAgent, CulturalImpactAgent

**Schedule:** Every 4 hours

---

#### Situation #3: Viral Content Predictor
**Session:** 479
**Status:** ACTIVE

Predicts content virality potential:
- Scores content for viral probability
- Tracks prediction accuracy
- Learns from outcomes

**Model:** `ViralContentPrediction`

**Schedule:** Every 4 hours at :30

---

### Creative Domain (2 Additional Situations)

#### Situation #4: Design Trends Monitor
**Session:** 479
**Status:** ACTIVE

Monitors design trends from creative sources:
- Dribbble, Behance, Awwwards data
- Momentum scoring for trends
- Design system update recommendations

**Models:** `DesignTrend`, `DesignSystemUpdate`

**Schedule:** Every 6 hours

---

#### Situation #5: Thumbnail A/B Optimizer
**Session:** 479
**Status:** ACTIVE

Optimizes thumbnail variations:
- Creates variants
- Tracks CTR performance
- Recommends winners

**Model:** `ThumbnailVariant`

---

### Income & Opportunities Domain (3 Situations)

#### Situation #6: Job Match Intelligence
**Session:** 479
**Status:** ACTIVE

Matches users to job opportunities:
- Profile-based matching
- ML scoring with explanations
- Application tracking

**Models:** `JobMatchProfile`, `JobMatch`

**Schedule:** Every 2 hours

---

#### Situation #7: Freelance Opportunity Scout
**Session:** 479
**Status:** ACTIVE

Discovers freelance opportunities:
- RemoteOK, WeWorkRemotely, Adzuna data
- Rate analysis
- Quick apply integration

**Model:** `FreelanceOpportunity`

---

#### Situation #8: Side Hustle Detector
**Session:** 479
**Status:** ACTIVE

Identifies side hustle opportunities:
- Passive income opportunities
- Skill-based matches
- Revenue potential estimation

**Model:** `SideHustle`

**Schedule:** Every 8 hours

---

### Financial Intelligence Domain (5 Situations)

#### Situation #9: Market Intelligence Desk
**Session:** 479
**Status:** ACTIVE

Daily market intelligence briefings:
- Stock market analysis
- Crypto market analysis
- Movement detection

**Models:** `MarketIntelligenceBrief`, `MarketMovement`

**Schedule:** Every 4 hours

---

#### Situation #10: SEC Filing Analyzer
**Session:** 479
**Status:** ACTIVE

Analyzes SEC filings (10-K, 10-Q, 8-K, 13F):
- Key insight extraction
- Institutional movement tracking
- Risk factor analysis

**Model:** `SECFilingAnalysis`

**Schedule:** Every 4 hours

---

#### Situation #11: Earnings Surprise Predictor
**Session:** 479
**Status:** ACTIVE

Predicts earnings surprises:
- Beat/miss predictions
- Confidence scoring
- Outcome tracking

**Model:** `EarningsPrediction`

---

#### Situation #12: Crypto Sentiment Monitor
**Session:** 479
**Status:** ACTIVE

Monitors crypto market sentiment:
- Reddit, BlueSky data
- Fear/greed indicators
- Whale movement alerts

**Model:** `CryptoSentiment`

**Schedule:** Every 2 hours at :15

---

#### Situation #13: Blockchain Security Alerts
**Session:** 461
**Status:** ACTIVE

Monitors blockchain for security issues:
- Whale movements
- Exploit detection
- Smart contract vulnerabilities

**Model:** `BlockchainSecurityAlert`

**Agents:** SmartContractAuditorAgent, WhaleWatcherAgent, ExploitDetectorAgent

---

### Research & Learning Domain (3 Situations)

#### Situation #14: Tech Stack Evolution Tracker
**Session:** 479
**Status:** ACTIVE

Tracks technology adoption trends:
- Framework popularity
- Language trends
- Tool adoption rates

**Model:** `TechStackTrend`

**Schedule:** Every 6 hours

---

#### Situation #15: AI Model Release Monitor
**Session:** 479
**Status:** ACTIVE

Monitors AI model releases:
- HuggingFace new models
- OpenAI/Anthropic releases
- Capability analysis

**Model:** `AIModelRelease`

**Schedule:** Every 4 hours at :30

---

#### Situation #16: Skill Gap Analyzer
**Session:** 479
**Status:** ACTIVE

Identifies skill gaps and learning opportunities:
- In-demand skills detection
- Learning path suggestions
- Market demand analysis

**Model:** `SkillGapAnalysis`

---

### Legal Intelligence Domain (2 Situations)

#### Situation #17: Case Law Monitor
**Session:** 479
**Status:** ACTIVE

Monitors case law updates:
- CourtListener data
- Precedent tracking
- Relevant case alerts

**Model:** `CaseLawUpdate`

**Schedule:** Every 6 hours

---

#### Situation #18: Regulatory Change Detector
**Session:** 479
**Status:** ACTIVE

Detects regulatory changes:
- Tech regulation (GDPR, FTC)
- Crypto regulation
- Industry-specific rules

**Model:** `RegulatoryChange`

**Schedule:** Every 8 hours

---

### Stock Market Domain (1 Situation)

#### Situation #19: Stock Market Real-Time Alerts
**Session:** 461
**Status:** ACTIVE

Real-time stock market alerts:
- Major moves (>5%)
- Institutional activity
- Breaking news

**Model:** `StockMarketAlert`

**Agents:** StockAnalystAgent, MarketMovementMonitorAgent, InstitutionalWatcherAgent

---

## Event-Driven Triggers

### Trigger System Architecture

**File:** `core/models_situation_triggers.py`

```python
class SituationTrigger(models.Model):
    name = CharField             # "Whale Movement (100+ ETH)"
    situation_type = CharField   # "blockchain"
    trigger_type = CharField     # "whale_movement"
    target_spiders = JSONField   # ['etherscan', 'etherscan_api']
    target_field = CharField     # "value"
    operator = CharField         # "gt" (greater than)
    threshold_value = CharField  # "100"
    severity = CharField         # "high"
    alert_title_template = CharField
    cooldown_minutes = IntegerField  # 15 (prevent spam)
    total_fires = IntegerField
    last_triggered_at = DateTimeField
```

### Operators Supported

| Operator | Description |
|----------|-------------|
| `gt` | Greater than |
| `gte` | Greater than or equal |
| `lt` | Less than |
| `lte` | Less than or equal |
| `eq` | Equal to |
| `neq` | Not equal to |
| `contains` | String contains |
| `regex` | Regular expression match |

### The 35 Pre-Configured Triggers

#### Blockchain Domain (5 Triggers)

| Trigger | Threshold | Cooldown |
|---------|-----------|----------|
| Whale Movement (100+ ETH) | value > 100 | 15 min |
| Mega Whale (1000+ ETH) | value > 1000 | 5 min |
| Price Crash (>10% Drop) | change < -10% | 30 min |
| Severe Crash (>20% Drop) | change < -20% | 15 min |
| Exploit/Hack Keywords | contains: exploit, hack, rug | 60 min |

#### Stock Market Domain (7 Triggers)

| Trigger | Threshold | Cooldown |
|---------|-----------|----------|
| Stock Mover (>5% Change) | change > 5% | 30 min |
| Major Stock Move (>10%) | change > 10% | 15 min |
| Stock Crash (>5% Drop) | change < -5% | 30 min |
| SEC Filing Detection | type: 13F, 13D, 8-K | 60 min |
| Breaking Market News | keywords | 30 min |
| Fed/Interest Rate News | keywords | 30 min |
| Market Intelligence | keywords | 60 min |

#### Content Domain (3 Triggers)

| Trigger | Threshold | Cooldown |
|---------|-----------|----------|
| Trending Content Topic | viral, trending, million | 60 min |
| High Engagement Signal | score > 500 | 30 min |
| Narrative Shift | pivot, shift, new direction | 120 min |

#### Creative Domain (3 Triggers)

| Trigger | Threshold | Cooldown |
|---------|-----------|----------|
| Design Trend Alert | 2024, 2025, trend, gradient | 120 min |
| Viral Visual Content | likes > 1000 | 60 min |
| Thumbnail Style Trend | thumbnail, click, ctr | 120 min |

#### Income Domain (5 Triggers)

| Trigger | Threshold | Cooldown |
|---------|-----------|----------|
| High-Paying Remote Job | salary > $150k | 60 min |
| Senior/Lead Position | senior, lead, principal | 60 min |
| Freelance Opportunity | freelance, contract | 60 min |
| High-Rate Freelance Gig | rate > $100/hr | 30 min |
| Side Hustle Opportunity | passive income, monetize | 120 min |

#### Research Domain (5 Triggers)

| Trigger | Threshold | Cooldown |
|---------|-----------|----------|
| New Tech Stack Trend | rust, go, kubernetes | 120 min |
| Framework Release | release, v2, v3, stable | 60 min |
| AI Model Release | gpt-5, claude, gemini | 30 min |
| AI Breakthrough | breakthrough, revolutionary | 60 min |
| In-Demand Skill | ai, ml, python, kubernetes | 120 min |

#### Legal Domain (4 Triggers)

| Trigger | Threshold | Cooldown |
|---------|-----------|----------|
| Case Law Update | court, ruling, verdict | 120 min |
| Tech Industry Legal | antitrust, patent, gdpr | 120 min |
| Regulatory Change | regulation, law, legislation | 120 min |
| Crypto Regulation | crypto regulation, stablecoin | 60 min |

#### Financial Domain (3 Triggers)

| Trigger | Threshold | Cooldown |
|---------|-----------|----------|
| Market Intelligence | dow, nasdaq, wall street | 60 min |
| Earnings Report | earnings, beat, miss | 30 min |
| Crypto Sentiment Shift | bitcoin, bull, bear, dump | 30 min |

---

## Trigger Evaluation Flow

```
1. Spider Data Arrives
   │
   ▼
2. Load Active Triggers for Spider
   │
   ▼
3. For Each Trigger:
   ├─ Extract target_field value
   ├─ Apply operator
   ├─ Check threshold
   ├─ If match AND not on cooldown:
   │   ├─ Create TriggerEvent
   │   ├─ Update last_triggered_at
   │   ├─ Increment total_fires
   │   └─ Dispatch to handlers
   └─ Continue to next trigger
   │
   ▼
4. Event Handlers Process
   ├─ Create domain-specific alert
   ├─ Send Discord notification
   └─ Update AI Assistant context
```

---

## Celery Beat Schedules (44 Tasks)

### High-Frequency Tasks

| Task | Frequency | Purpose |
|------|-----------|---------|
| `process-spider-data-automatic` | Every 5 min | Process incoming spider data |
| `backfill-spider-embeddings` | Every 10 min | Generate embeddings |
| `sync-shared-memory` | Every 10 min | Sync agent memories |
| `agent-learning-cycle` | Every 10 min | Agent learning updates |
| `collect-real-opportunities` | Every 15 min | Opportunity discovery |
| `run-spider-network` | Every 15 min | Spider data collection |

### Autonomous Situation Tasks

| Task | Frequency | Situation |
|------|-----------|-----------|
| `job-match-intelligence` | Every 2 hours | Job Matching |
| `crypto-sentiment-monitor` | Every 2 hours :15 | Crypto Sentiment |
| `autonomous-content-studio-check` | Every 4 hours | Content Studio |
| `narrative-drift-detector` | Every 4 hours | Narrative Drift |
| `viral-content-predictor` | Every 4 hours :30 | Viral Predictor |
| `ai-model-monitor` | Every 4 hours :30 | AI Model Monitor |
| `market-intelligence-desk` | Every 4 hours | Market Intelligence |
| `sec-filing-analyzer` | Every 4 hours | SEC Filings |
| `design-trends-monitor` | Every 6 hours | Design Trends |
| `tech-stack-tracker` | Every 6 hours | Tech Stack |
| `case-law-monitor` | Every 6 hours | Case Law |
| `side-hustle-detector` | Every 8 hours | Side Hustle |
| `regulatory-change-detector` | Every 8 hours | Regulatory |

### Learning & Agent Tasks

| Task | Frequency | Purpose |
|------|-----------|---------|
| `agent-dreams` | Every 15 min | Generate agent dreams |
| `agent-conversation` | Every 30 min | Agent conversations |
| `agent-learning-synthesis` | Every 30 min | Learning synthesis |
| `multi-agent-conversation` | Every 1 hour | Multi-agent hive mind |
| `auto-promote-decisions` | Every 30 min | Promote high-scoring dreams |
| `auto-resolve-knowledge-gaps` | Every 6 hours | Fill knowledge gaps |

### Daily Tasks

| Task | Time | Purpose |
|------|------|---------|
| `run-daily-learning-pipeline` | 5:00 AM | Daily learning |
| `update-agent-effectiveness` | 5:30 AM | Update metrics |
| `embed-daily-agent-learning` | 2:00 AM | Embed learnings |
| `clean-stale-data` | 2:00 AM | Cleanup old data |
| `check-retraining-needed` | 3:00 AM | ML model check |

### Weekly Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| `retrain-all-models-weekly` | Sunday 2 AM | Full ML retraining |
| `weekly-opportunity-digest` | Sunday 10 AM | Weekly summary |

---

## Content Studio Deep Dive

### Complete Workflow

```
USER CREATES CHANNEL
    name: "AI Explained"
    topic_domain: "AI, ML"
    target_audience: "developers"
    content_frequency: WEEKLY
          │
          ▼
CELERY BEAT (Every 4 Hours)
    SELECT ContentChannel
    WHERE status = 'ACTIVE'
    AND next_content_due <= NOW()
          │
          ▼
COORDINATOR AWAKENS
    1. Load channel context
    2. Fetch spider trends
    3. Initiate debate
          │
          ▼
DEBATE BEGINS
    TopicMinerAgent: "AI Safety trending (HN: 450)"
    ContrarianAgent: "AI Safety saturated, try Local AI"
    PerformanceAnalyst: "Local AI: 450 avg views"
    CreativeDirector: "Unique angle: Local AI Safety Tools"
          │
          ▼
DECISION REACHED
    final_decision: "Local AI Safety Tools"
    chosen_angle: "Practical implementations"
          │
          ▼
CONTENT CREATED
    AISeriesWorkflowAgent executes:
    Script → Storyboard → Assets → Voice → Video
          │
          ▼
EPISODE PUBLISHED
    ChannelEpisode created
    publish_automatically → YouTube
          │
          ▼
PERFORMANCE TRACKED (After 7 days)
    views: 3,200
    retention: 71%
    performance_score: 82.1
          │
          ▼
LEARNING UPDATED
    TopicPerformance.confidence_score += 0.2
          │
          ▼
SELF-RENEWAL
    channel.schedule_next_content()
    next_content_due = now() + 7 days
          │
          ▼
    (Cycle repeats forever)
```

---

## Models Reference

### Situation Models

| Model | File | Purpose |
|-------|------|---------|
| `ContentChannel` | `models_autonomous_studio.py` | Content channel config |
| `ChannelEpisode` | `models_autonomous_studio.py` | Published episodes |
| `TopicPerformance` | `models_autonomous_studio.py` | Topic learning |
| `ContentDebate` | `models_autonomous_studio.py` | Debate records |
| `DesignTrend` | `models_autonomous_situations.py` | Design trends |
| `JobMatch` | `models_autonomous_situations.py` | Job matches |
| `MarketIntelligenceBrief` | `models_autonomous_situations.py` | Market briefs |
| `BlockchainSecurityAlert` | `models_autonomous_situations.py` | Security alerts |
| `ViralContentPrediction` | `models_autonomous_situations.py` | Viral predictions |
| `CryptoSentiment` | `models_autonomous_situations.py` | Crypto sentiment |

### Trigger Models

| Model | File | Purpose |
|-------|------|---------|
| `SituationTrigger` | `models_situation_triggers.py` | Trigger configuration |
| `TriggerEvent` | `models_situation_triggers.py` | Trigger fire records |
| `TriggerGroup` | `models_situation_triggers.py` | Trigger grouping |

---

## Key Files

| File | Purpose |
|------|---------|
| `core/models_autonomous_situations.py` | 14 situation models |
| `core/models_autonomous_studio.py` | Content Studio models |
| `core/models_situation_triggers.py` | Trigger system (~950 lines) |
| `core/services/autonomous_loop.py` | Main conductor |
| `core/services/proactive_intelligence.py` | Intelligence injection |
| `core/celery.py` | Static beat schedule definitions; runtime rows live in `django-celery-beat` |
| `core/agents/autonomous_content_studio_coordinator.py` | Studio brain |

---

## Monitoring Commands

```bash
# Check active triggers
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.models_situation_triggers import SituationTrigger
triggers = SituationTrigger.objects.filter(is_active=True)
for t in triggers:
    print(f'{t.name}: {t.total_fires} fires')"

# Check pending trigger events
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.models_situation_triggers import TriggerEvent
pending = TriggerEvent.objects.filter(status='pending').count()
print(f'Pending events: {pending}')"

# Check content channels due
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from django.utils import timezone
from core.models_autonomous_studio import ContentChannel
due = ContentChannel.objects.filter(
    status='active',
    next_content_due__lte=timezone.now()
).count()
print(f'Channels due for content: {due}')"
```

---

## Session History

| Session | Feature |
|---------|---------|
| 461 | Blockchain + Stock audit agents |
| 466 | Autonomous Content Studio |
| 468 | Content Studio bug fixes |
| 469 | Real agent debates |
| 471 | Narrative Drift Detector |
| 479 | 14 additional situations |
| 481 | Event-driven triggers |
| 482 | AI Assistant integration |
