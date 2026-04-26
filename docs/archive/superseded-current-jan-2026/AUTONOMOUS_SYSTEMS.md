<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Autonomous behavior overview
>
> **Where to look now:**
> - [docs/AUTONOMOUS_SYSTEMS.md](/docs/AUTONOMOUS_SYSTEMS.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Autonomous Systems Documentation

**Total Situations:** 19
**Event Trigger Types:** 29
**Default Triggers:** 34
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [The 5 Autonomous Properties](#the-5-autonomous-properties)
3. [Tier 1 Autonomous Situations](#tier-1-autonomous-situations)
4. [All 19 Situations](#all-19-situations)
5. [Event-Driven Triggers](#event-driven-triggers)
6. [Learning Loops](#learning-loops)

---

## Overview

Autonomous systems run continuously without human intervention, making decisions through agent debates and improving from outcomes.

### Architecture
```
Spider Data Collection (Every 30 min)
         │
         ▼
Event Trigger Evaluation
         │
         ▼
Situation Activation
         │
         ├── Agent Team Execution
         │   ├── Coordinator
         │   └── Sub-agents (debate/analysis)
         │
         ▼
Output Generation
         │
         ├── Content/Briefs/Alerts
         └── Learning Loop Recording
         │
         ▼
Performance Tracking
         │
         ▼
Self-Renewal (Schedule Next Cycle)
```

---

## The 5 Autonomous Properties

Every Tier 1 autonomous situation implements all 5 properties:

### 1. Persistent Context
- Configuration stored in database models
- Historical performance tracked
- State preserved across cycles

### 2. Incoming Signals
- Spider network data feeds
- Platform API metrics
- External event triggers

### 3. Internal Disagreement
- Agent debates before decisions
- Pro/Con analysis
- Multiple perspectives synthesized

### 4. Outputs with Consequences
- Actions tracked for outcomes
- Performance affects future decisions
- Revenue/engagement metrics

### 5. Self-Renewal
- Auto-schedules next execution
- Runs forever without intervention
- Adapts based on performance

---

## Tier 1 Autonomous Situations

### 1. Market Intelligence Desk

**Agents:** BullCaseAgent, BearCaseAgent, SignalScannerAgent, MarketIntelligenceCoordinator

**Schedule:** 6:30 AM weekdays (before market open)

**Flow:**
```
Spider Data (Financial)
     │
     ▼
SignalScannerAgent (detect signals)
     │
     ▼
BullCaseAgent vs BearCaseAgent (debate)
     │
     ▼
MarketIntelligenceCoordinator (synthesize)
     │
     ▼
Daily Brief Document
     │
     ├── TTS Audio (ElevenLabs)
     └── Discord Notification
```

**Output:**
- Executive Summary
- High Conviction Picks (3 stocks)
- Debate Zone (2 contested stocks)
- Risk Alerts
- What Changed (from yesterday)

**Learning Loop:**
- Track prediction outcomes
- Calculate agent accuracy
- Adjust confidence multipliers (0.5x-1.5x)

---

### 2. Autonomous Content Studio

**Agents:** TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent, AutonomousContentStudioCoordinator

**Schedule:** Every 4 hours per channel

**Flow:**
```
Spider Trends (Creative)
     │
     ▼
TopicMinerAgent (FOR trending topics)
     │
     ▼
ContrarianAgent (AGAINST saturation)
     │
     ▼
PerformanceAnalystAgent (historical data)
     │
     ▼
Coordinator (select winner)
     │
     ▼
Content Generation
     │
     ├── Script/Article
     ├── Thumbnail
     └── SEO Metadata
```

**Configuration:**
- ContentChannel model stores config
- TopicPerformance tracks success
- ContentDebate logs transparency

**Learning Loop:**
- Track views, retention, engagement
- Topic selection improves over time
- Confidence multipliers adjust

---

### 3. Narrative Drift Detector

**Agents:** NarrativeHistorianAgent, TrendBreakDetectorAgent, CulturalImpactAgent, NarrativeDriftCoordinator

**Schedule:** Every 6 hours

**Tracks:**
- 30 core narratives
- 8 domains (tech, markets, politics, culture, geopolitics, crypto, climate, health)
- Status: emerging → dominant → shifting → fading → dead

**Output:**
- Shift alerts
- Historical context
- Impact analysis
- Trend predictions

---

## All 19 Situations

### Financial Domain (8)

| Situation | Agents | Schedule |
|-----------|--------|----------|
| **Market Intelligence Desk** | Bull, Bear, Signal, Coordinator | 6:30 AM weekdays |
| **Stock Market Monitoring** | 5 stock agents | Market hours |
| **Blockchain Security** | 5 blockchain agents | Every 15 min |
| **Crypto Sentiment Monitor** | Analysis agents | Every 2 hours |
| **SEC Filing Analyzer** | Research agents | On new filings |
| **Earnings Surprise Predictor** | ML + Analysts | Before earnings |
| **Whale Movement Tracker** | WhaleWatcher | Real-time |
| **Arbitrage Scanner** | ArbitrageDetector | Every 5 min |

### Content Domain (2)

| Situation | Agents | Schedule |
|-----------|--------|----------|
| **Autonomous Content Studio** | 4 content agents | Every 4 hours |
| **Narrative Drift Detector** | 4 narrative agents | Every 6 hours |

### Creative Domain (3)

| Situation | Agents | Schedule |
|-----------|--------|----------|
| **Design Trends Monitor** | TrendAnalysis | Daily |
| **Viral Content Predictor** | ML + Analysis | Every 2 hours |
| **Thumbnail A/B Optimizer** | ML scoring | On generation |

### Income Domain (3)

| Situation | Agents | Schedule |
|-----------|--------|----------|
| **Job Match Intelligence** | Opportunity agents | Every hour |
| **Freelance Opportunity Scout** | Research agents | Every 2 hours |
| **Side Hustle Detector** | Analysis agents | Daily |

### Research Domain (2)

| Situation | Agents | Schedule |
|-----------|--------|----------|
| **Tech Stack Evolution Tracker** | Research agents | Weekly |
| **AI Model Release Monitor** | HuggingFace spider | Daily |

### Legal Domain (1)

| Situation | Agents | Schedule |
|-----------|--------|----------|
| **Case Law Monitor** | Legal spiders | Daily |

---

## Event-Driven Triggers

### Trigger Types (29)

| Category | Triggers |
|----------|----------|
| **Financial** | whale_movement, price_crash, price_surge, volume_spike, unusual_options |
| **Market** | market_open, market_close, earnings_release, dividend_announce |
| **Blockchain** | large_transfer, contract_deploy, exploit_detected, whale_accumulation |
| **Content** | viral_content, trending_topic, narrative_shift, competitor_post |
| **News** | breaking_news, regulatory_change, company_announcement |
| **Income** | high_value_opportunity, deadline_approaching, new_platform_listing |
| **Legal** | case_filed, ruling_issued, deadline_reminder |
| **System** | spider_anomaly, agent_error, learning_milestone |

### Default Triggers (34)

Pre-configured triggers that activate automatically:

```python
DEFAULT_TRIGGERS = [
    # Financial
    {"type": "whale_movement", "threshold": 1000000, "situation": "blockchain_security"},
    {"type": "price_crash", "threshold": -5, "situation": "market_intelligence"},
    {"type": "price_surge", "threshold": 10, "situation": "market_intelligence"},
    {"type": "volume_spike", "threshold": 3, "situation": "stock_monitoring"},

    # Content
    {"type": "viral_content", "threshold": 10000, "situation": "content_studio"},
    {"type": "narrative_shift", "threshold": 0.3, "situation": "narrative_drift"},

    # Income
    {"type": "high_value_opportunity", "threshold": 5000, "situation": "opportunity_scout"},

    # ... 27 more
]
```

### Trigger Flow

```
Spider Data Post-Save Signal
         │
         ▼
Trigger Evaluation (all 34 defaults)
         │
         ▼
Matching Triggers Fire
         │
         ▼
Situation Execution (instant)
         │
         ▼
Notification + Learning
```

---

## Learning Loops

### Market Intelligence Learning

```python
# Track prediction outcomes
def track_prediction(prediction_id, actual_outcome):
    prediction = Prediction.objects.get(id=prediction_id)
    prediction.actual = actual_outcome
    prediction.correct = (prediction.direction == actual_outcome.direction)
    prediction.save()

# Calculate agent accuracy
def calculate_accuracy(agent_name, days=30):
    predictions = Prediction.objects.filter(
        agent=agent_name,
        created_at__gte=timezone.now() - timedelta(days=days)
    )
    correct = predictions.filter(correct=True).count()
    total = predictions.count()
    return correct / total if total > 0 else 0.5

# Adjust confidence multiplier
def get_confidence_multiplier(agent_name):
    accuracy = calculate_accuracy(agent_name)
    if accuracy > 0.7:
        return 1.5
    elif accuracy > 0.55:
        return 1.0
    else:
        return 0.5
```

### Content Studio Learning

```python
# Grade scoring with performance data
def get_best_grade_for_trends(spider_trends):
    # Base score from trend matching
    base_scores = match_grades_to_trends(spider_trends)

    # Adjust with historical performance
    for grade, score in base_scores.items():
        performance = ContentPerformance.objects.filter(
            grade=grade
        ).aggregate(
            avg_views=Avg('views'),
            avg_retention=Avg('retention')
        )

        # Boost grades with good performance
        if performance['avg_retention'] > 0.5:
            score *= 1.3

    return max(base_scores, key=base_scores.get)
```

### Narrative Drift Learning

```python
# Track narrative accuracy
def track_narrative_prediction(narrative_id, prediction, actual):
    evidence = NarrativeEvidence.objects.create(
        narrative_id=narrative_id,
        predicted_status=prediction,
        actual_status=actual,
        accurate=(prediction == actual)
    )

    # Update narrative confidence
    narrative = Narrative.objects.get(id=narrative_id)
    recent_accuracy = NarrativeEvidence.objects.filter(
        narrative=narrative,
        created_at__gte=timezone.now() - timedelta(days=30)
    ).aggregate(accuracy=Avg('accurate'))

    narrative.confidence = recent_accuracy['accuracy'] or 0.5
    narrative.save()
```

---

## Monitoring & Control

### Discord Commands

```
/situations - List all 19 situations
/situation-status <name> - Check specific situation
/situation-run <name> - Manually trigger
/situation-alerts - View recent alerts
```

### API Endpoints

```
GET /api/situations/ - List all
GET /api/situations/<id>/ - Detail
POST /api/situations/<id>/run/ - Manual trigger
GET /api/situations/<id>/history/ - Execution history
GET /api/triggers/ - List triggers
POST /api/triggers/ - Create custom trigger
```

### Celery Tasks

```python
# Manual run
from core.tasks import run_market_intelligence_desk
run_market_intelligence_desk.delay()

# Check status
from core.models_autonomous_situations import SituationExecution
recent = SituationExecution.objects.filter(
    situation__name='market_intelligence_desk'
).order_by('-started_at')[:10]
```

---

## Related Documentation

- [AGENTS.md](AGENTS.md) - Agents used in situations
- [CELERY_TASKS.md](CELERY_TASKS.md) - Task scheduling
- [SPIDERS.md](SPIDERS.md) - Data sources for triggers
