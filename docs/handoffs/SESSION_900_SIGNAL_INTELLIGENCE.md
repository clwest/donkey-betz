---
originating_session: 900
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 900 - Signal Intelligence & Provenance

**Date:** February 1, 2026
**Focus:** Signal provenance for Origin & Trigger UI section

---

## Problem Statement

The Initiative UI shows "Trigger: scheduled triggered conversation" which tells WHEN but not WHY a conversation happened. Users need to see:
- What signals triggered this conversation
- What pattern was detected
- Why THIS topic was chosen

### Before (Useless)
```
Trigger: scheduled triggered conversation
```

### After (Cinematic)
```
Origin Signals
📡 Bluesky (12 posts)
📡 Reddit (6 threads)
📡 Job Listings (4 roles)

Detected Pattern
🧠 "Persona research demand spike"
Strength: 0.81 | Confidence: 0.83

Auto Topic
🎯 "Formalize Persona Research"
```

---

## Solution: Signal Intelligence Models

Created new models to track the full provenance chain:

```
SpiderData[] (multiple signals)
    ↓
SignalCluster (pattern from signals)
    ↓
AutoTopic (why THIS topic was chosen)
    ↓
HiveMindSession (linked to AutoTopic)
    ↓
AgentDecisionSummary
    ↓
Initiative
```

---

## New Models Created

### 1. SignalCluster (`core/models_signal_intelligence.py`)

Groups related spider signals into a detected pattern.

**Key Fields:**
- `name` - Pattern name (e.g., "Persona research demand spike")
- `pattern_type` - Classification (demand_spike, trend_emergence, sentiment_shift, etc.)
- `spider_data_ids` - List of SpiderData UUIDs that contributed
- `source_breakdown` - Count per source: `{"bluesky": 12, "reddit": 6}`
- `strength` - Signal strength (0-1)
- `novelty` - How new is this pattern (0-1)
- `confidence` - Pattern validity confidence (0-1)
- `keywords` - Keywords that define this cluster
- `sample_signals` - Sample snippets for display
- `status` - detecting, active, triggered, decayed, archived

**Pattern Types:**
- `demand_spike` - Increased interest in topic
- `trend_emergence` - New trend appearing
- `sentiment_shift` - Opinion change detected
- `opportunity_window` - Time-sensitive opportunity
- `knowledge_gap` - Missing information detected
- `competitive_signal` - Competitor activity
- `market_movement` - Market/price signals
- `skill_demand` - Job market signals
- `content_gap` - Underserved content area
- `user_need` - Direct user need detected

### 2. AutoTopic (`core/models_signal_intelligence.py`)

Records WHY a specific topic was chosen for discussion.

**Key Fields:**
- `name` - Topic name (e.g., "Formalize Persona Research")
- `signal_cluster` - FK to SignalCluster that triggered it
- `derived_from_pattern` - Pattern type that generated this
- `rationale` - Explanation of why this topic was generated
- `confidence` - Confidence score (0-1)
- `urgency` - Time-sensitivity (0-1)
- `suggested_agent_names` - Agents recommended for topic
- `suggested_conversation_type` - analytical, creative, debate, etc.
- `status` - pending, scheduled, triggered, skipped, expired
- `triggered_session_id` - UUID of HiveMindSession if triggered

### 3. TopicSuggestion (`core/models_signal_intelligence.py`)

Alternative topic suggestions from signal analysis (not chosen as primary).

---

## HiveMindSession Changes

Added FK fields to link sessions to their signal provenance:

```python
# Session 900: Signal provenance - WHY this conversation happened
signal_cluster = models.ForeignKey(
    'SignalCluster',
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name='triggered_sessions'
)
auto_topic = models.ForeignKey(
    'AutoTopic',
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name='triggered_sessions'
)
trigger_confidence = models.FloatField(
    null=True, blank=True,
    help_text='Confidence score of the trigger (0-1)'
)
```

---

## Files Changed

| File | Change |
|------|--------|
| `core/models_signal_intelligence.py` | NEW - SignalCluster, AutoTopic, TopicSuggestion models |
| `core/models/__init__.py` | Added import for signal intelligence models |
| `core/models_unified_system.py` | Added signal_cluster, auto_topic, trigger_confidence to HiveMindSession |
| `core/migrations/0211_session_900_signal_intelligence.py` | NEW - Migration for new models |
| `core/services/signal_aggregation_service.py` | NEW - Signal clustering and auto-topic generation |
| `core/tasks.py` | Added signal aggregation Celery tasks |
| `core/celery.py` | Added Celery Beat schedules for signal tasks |
| `core/views_research_demo.py` | Extended origin-trace API with origin_signals |
| `frontend/src/pages/workspace/tabs/InitiativesTab.tsx` | Added Signal Intelligence display in Initiative modal |

---

## Signal Aggregation Service (Implemented)

**File:** `core/services/signal_aggregation_service.py`

The service clusters recent SpiderData into SignalClusters:

1. **Fetch recent spider data** (configurable lookback window)
2. **Extract keywords/topics** from raw_data content
3. **Cluster signals by topic similarity**
4. **Calculate metrics** (strength, confidence, novelty)
5. **Create SignalCluster records**
6. **Generate AutoTopic suggestions**

**Pattern Detection:**
- `demand_spike` - "need", "want", "looking for"
- `trend_emergence` - "new", "emerging", "trending"
- `sentiment_shift` - "changing", "shift", "prefer"
- `opportunity_window` - "limited time", "urgent"
- `knowledge_gap` - "confused", "don't understand"
- `skill_demand` - "hiring", "job", "role"
- `content_gap` - "no good content", "wish there was"

---

## Celery Tasks (Implemented)

**File:** `core/tasks.py` (added at end)

| Task | Schedule | Description |
|------|----------|-------------|
| `aggregate_spider_signals` | Every 30 min | Clusters SpiderData into SignalClusters |
| `process_pending_auto_topics` | Hourly at :45 | Triggers conversations from AutoTopics |
| `trigger_signal_driven_conversation` | On-demand | Creates HiveMindSession with provenance |
| `cleanup_expired_signals` | Daily 4:30 AM | Archives expired clusters/topics |

**Celery Beat Schedule:** Added to `core/celery.py`

---

## Deployment Complete

All components deployed and verified in production:

### 1. Railway Migration
- Applied `0211_session_900_signal_intelligence` migration
- Created SignalCluster, AutoTopic, TopicSuggestion tables

### 2. Signal Aggregation Verified
- Ran `aggregate_spider_signals` task in production
- Created **22 SignalClusters** from spider data
- Generated **10 AutoTopics** from actionable patterns

### 3. API Endpoint Extended
- Extended `GET /api/initiatives/{id}/origin-trace/` to include `origin_signals`
- Returns `signal_cluster` and `auto_topic` data when available
- Updated `trigger.type` to `signal_driven` when provenance exists

### 4. UI Update Implemented
**File:** `frontend/src/pages/workspace/tabs/InitiativesTab.tsx`

Added to ComprehensiveInitiativeModal:
- **Origin Signals** section with source breakdown (Bluesky, Reddit, etc.)
- **Pattern metrics** (strength, confidence, novelty percentages)
- **Keywords** extracted from signals
- **Sample signals** with source attribution
- **Auto Topic** section with name, rationale, and triggered timestamp
- **Signal-Driven badge** in Origin & Trigger section header
- **Complete Journey visualization** now shows signal chain

---

## Production Stats Verified

Connected to Railway production and verified:
- **1,152,295** AgentLearning records
- **782,640** learnings in last 7 days
- **820** successful experiments (88.2% success rate)
- **236** UserAgentLearning records
- **22** SignalClusters created
- **10** AutoTopics generated

---

## API Response Structure

```json
{
  "initiative_id": "17c6080c-edf3-4a77-b812-dfa4ac2e5726",
  "origin": {
    "signal_cluster": {
      "id": "...",
      "name": "Persona research demand spike",
      "pattern_type": "demand_spike",
      "source_breakdown": {
        "bluesky": 12,
        "reddit": 6,
        "job_listings": 4
      },
      "strength": 0.81,
      "confidence": 0.83,
      "keywords": ["persona", "customer research", "user profiles"],
      "sample_signals": [
        {"source": "bluesky", "text": "Every startup needs rigorous persona research..."},
        {"source": "reddit", "text": "How do you validate customer personas?"}
      ]
    },
    "auto_topic": {
      "id": "...",
      "name": "Formalize Persona Research",
      "rationale": "12 Bluesky posts + 6 Reddit threads indicate demand...",
      "confidence": 0.83,
      "triggered_at": "2026-02-01T06:29:00Z"
    }
  },
  "trigger_confidence": 0.83
}
```

---

## Migration

```bash
# Apply migration locally
python manage.py migrate core 0211_session_900_signal_intelligence

# Deploy to Railway
railway up
```
