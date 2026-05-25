---
originating_session: 954
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 954: Boardroom ML Improvements

**Date:** February 6, 2026
**Status:** Complete
**Builds on:** Session 940 (Boardroom Learning Service)

---

## Problem Statement

The existing boardroom learning system only used item_type and source_agent for recommendations. It lacked:
1. Content-aware predictions using actual item content
2. Proper statistical confidence (was just linear sample count)
3. Trained predictions based on similar past decisions

---

## What Was Implemented

### New BoardroomMLService

Created `core/services/boardroom_ml_service.py` with content-aware ML predictions:

#### Features:
- **Content Similarity**: Uses embeddings to find similar past items and their decisions
- **Wilson Score Confidence**: Proper Bayesian confidence scoring instead of linear
- **Multi-Signal Predictions**: Combines 4 signals with weighted averaging:
  - Content similarity (50% weight)
  - Type history (20% weight)
  - Source history (20% weight)
  - Urgency history (10% weight)

#### Key Methods:
```python
from core.services.boardroom_ml_service import get_boardroom_ml_service

service = get_boardroom_ml_service()

# Get prediction for an item
prediction = service.predict_decision(attention_item)
# Returns: {
#   'prediction': 'approve'|'ignore'|'uncertain',
#   'confidence': 0.0-1.0,
#   'approval_probability': 0.0-1.0,
#   'reasoning': 'Similar content: 5 matches, 80% approved',
#   'similar_items': [...]
# }

# Auto-populate ml_prediction fields on item
service.enrich_item_with_prediction(attention_item)

# Batch enrich pending items
stats = service.batch_enrich_pending_items(user, limit=50)

# Get accuracy summary
summary = service.get_recommendation_summary(user)
```

### ML Accuracy Tracking

Updated `core/services/boardroom_learning_service.py` to track prediction accuracy:

- New `_track_ml_accuracy()` method called when decisions are recorded
- Creates `LearningPattern` with type `boardroom_ml_accuracy`
- Tracks: correct, incorrect, total, accuracy rate

### Celery Task

Added `enrich_boardroom_ml_predictions` task in `core/tasks.py`:
- Runs every 15 minutes
- Finds pending items without ML predictions
- Enriches up to 20 items per user, 10 users per run

### Management Command

Created `core/management/commands/enrich_boardroom_ml.py`:

```bash
# Enrich pending items (default)
python manage.py enrich_boardroom_ml

# Show prediction accuracy stats
python manage.py enrich_boardroom_ml --stats

# Enrich all items without predictions
python manage.py enrich_boardroom_ml --all --limit=200
```

---

## Technical Details

### Wilson Score Confidence

Replaces the simple `0.5 + (count * 0.01)` formula with proper statistical confidence:

```python
def _wilson_score_confidence(self, successes, trials, z=1.96):
    """
    Wilson score - proper uncertainty for small samples.
    - 3 approvals / 3 trials → ~60% confidence (not 100%)
    - 80 approvals / 100 trials → ~90% confidence
    """
    p = successes / trials
    denominator = 1 + z * z / trials
    center = p + z * z / (2 * trials)
    spread = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials))
    # ... returns confidence 0-1
```

### Content Similarity

Uses the existing embedding service to compare item content:

```python
item_content = f"{item.title} {item.summary}"
item_embedding = self.embedding_service.get_embedding_sync(item_content)

for past_item in past_decisions[:100]:
    past_embedding = self.embedding_service.get_embedding_sync(past_content)
    similarity = cosine_similarity(item_embedding, past_embedding)
    if similarity >= 0.65:  # threshold
        similar_items.append({...})
```

### Signal Combination

Signals are combined using confidence-weighted averaging:

```python
for rate, confidence, weight in signals:
    effective_weight = weight * confidence
    weighted_rate += rate * effective_weight
    total_weight += effective_weight

combined_rate = weighted_rate / total_weight
```

---

## Files Changed

| File | Changes |
|------|---------|
| `core/services/boardroom_ml_service.py` | **NEW** - Content-aware ML predictions |
| `core/services/boardroom_learning_service.py` | +ML accuracy tracking method |
| `core/management/commands/enrich_boardroom_ml.py` | **NEW** - Backfill command |
| `core/tasks.py` | +enrich_boardroom_ml_predictions task |
| `core/celery.py` | +Celery Beat schedule for ML enrichment |

---

## Data State

Production data available for training:
- **1,329** total attention items
- **112** with decisions (training data)
- **52** pending (can be enriched)
- Decision breakdown: auto_dismiss (76), watch (20), defer (5), modify (4), dismiss (4), approve (3)

---

## Usage

### Immediate Test
```bash
# Railway production
railway run python manage.py enrich_boardroom_ml --stats
railway run python manage.py enrich_boardroom_ml --pending

# Sync Celery schedules to enable auto-enrichment
railway run python manage.py sync_celery_schedules
```

### Monitor Accuracy
The ML system will automatically track accuracy as users make decisions. Check with:
```bash
python manage.py enrich_boardroom_ml --stats
```

---

## Next Steps

1. **Run initial enrichment** on Railway to populate ml_prediction fields
2. **Sync Celery schedules** to enable automatic enrichment
3. **Monitor accuracy** over time as more decisions are made
4. Consider **UI integration** to show predictions to users

---

## Part 2: Initiative Source Cleanup (Option C)

### Problem
DecisionExtractor was creating 441+ junk initiatives from any decision with a `suggested_feature`, regardless of quality. Initiative names were often sentence fragments like "driven module that ingests..." or started with junk patterns.

### Solution
Added `_is_valid_initiative_name()` validation function that checks:
- Minimum length (10 chars)
- Doesn't start lowercase (sentence fragment)
- Doesn't start with junk patterns: `driven`, `plan`, `of-`, `Auto-created`, `A '`, `stage`, `type/`, etc.
- Doesn't contain markers like `[Learned]`, `[Synthesis]`
- Must start with capital letter or number

### Files Changed
| File | Changes |
|------|---------|
| `core/services/decision_extractor.py` | +`_is_valid_initiative_name()`, validation before initiative creation |
| `core/services/conversation_initiative_pipeline.py` | +validation with topic fallback |

### Effect
- Prevents junk initiatives from being created at the source
- Existing cleanup task (`cleanup_junk_initiatives`) still handles legacy junk
- New initiatives will have proper, actionable names

---

## Part 3: Learning Loop Refinement (Option D)

### Problem
The existing LearningLoopOrchestrator (Session 945) only had 3 success signals defined and lacked:
1. Signals for commonly-used tools (image generation, content writing, etc.)
2. User feedback integration from boardroom decisions
3. Learning effectiveness tracking
4. Dashboard API for viewing active learnings

### Solution

#### 1. Expanded SuccessSignal Definitions
Extended `DEFAULT_SUCCESS_SIGNALS` from 3 to 15+ tools:
- Research tools: `web_search`, `analyze_filing`, `get_stock_data`
- Content tools: `image_generation_agent`, `content_writer_agent`, `video_generation_agent`
- Agent tools: `universal_agent_tool`, `reasoning_engine_tool`
- System tools: `body_vitals_tool`, `system_alerts_tool`
- Intelligence tools: `predictions_tool`, `gates_tool`
- Business tools: `competitor_analysis_agent`, `customer_research_agent`
- Execution tools: `workspace_tool`, `human_decisions_tool`

#### 2. User Feedback Integration
New `analyze_user_feedback()` method connects HumanAttentionItem decisions to learning:
- Analyzes approval rates by source agent
- Tracks item type effectiveness
- Learns from urgency level patterns
- Extracts learnings: "Agent X items often ignored" or "Agent Y items highly valued"

#### 3. Learning Effectiveness Tracking
New methods to track and measure learning effectiveness:
- `track_learning_application(pattern_id, was_successful)` - Updates times_applied/success_when_applied
- `get_learning_effectiveness_stats()` - Returns comprehensive stats:
  - Total active learnings
  - Overall effectiveness rate
  - Most/least effective learnings
  - Recent patterns
  - Stats by pattern type

#### 4. Dashboard API Endpoints
New API endpoints in `views_learning_loop.py`:
- `GET /api/learning/loop/stats/` - Get learning loop effectiveness stats
- `POST /api/learning/loop/track/` - Track learning outcome
- `POST /api/learning/loop/run/` - Trigger learning cycle
- `GET /api/learning/loop/agent/?agent_name=X` - Get learnings for specific agent

### Files Changed
| File | Changes |
|------|---------|
| `core/services/learning_loop_orchestrator.py` | +12 SuccessSignals, +analyze_user_feedback(), +track_learning_application(), +get_learning_effectiveness_stats() |
| `core/views_learning_loop.py` | +4 new API endpoints for learning loop |
| `core/urls.py` | +4 URL patterns for new endpoints |

### Usage
```bash
# Test learning loop stats
curl http://localhost:8000/api/learning/loop/stats/ -H "Authorization: Token $TOKEN"

# Trigger learning cycle
curl -X POST http://localhost:8000/api/learning/loop/run/ -H "Authorization: Token $TOKEN"

# Get learnings for an agent
curl http://localhost:8000/api/learning/loop/agent/?agent_name=ResearchAgent -H "Authorization: Token $TOKEN"
```

---

---

## Part 4: RAG Observability Dashboard (Option E)

### Problem
The risk-aware RAG system (Session 949) had no visibility into:
1. Which critical docs are being used
2. How documents are classified by risk level and document class
3. Context budget utilization by priority tier
4. Risk boost effectiveness

### Solution

#### RAGObservabilityService
Created `core/services/rag_observability_service.py` with:

**Document Inventory Stats:**
- Total/critical/classified document counts
- Breakdown by risk_level: critical (18), high (332), medium (212)
- Breakdown by document_class: reference, architecture, constraint, security, etc.
- Freshness metrics (document age)

**Context Budget Stats:**
- Total budget: 4,000 tokens
- Reserved tier: 650 tokens (critical_docs: 300, incident_docs: 200, audit_findings: 150)
- Utilization by priority tier (CRITICAL, RESERVED, HIGH, MEDIUM, LOW)

**Risk Boost Stats:**
- Boost magnitudes by risk level and document class
- Expected boost values (is_critical: +0.30, postmortem: +0.20, etc.)
- Coverage of boostable documents

**Health Indicators:**
- Critical docs coverage validation
- Classification coverage check
- Reserved tier allocation verification

#### API Endpoints
8 new endpoints in `views_rag_observability.py`:
- `GET /api/rag/observability/dashboard/` - Full dashboard data
- `GET /api/rag/observability/inventory/` - Document inventory stats
- `GET /api/rag/observability/budget/` - Context budget utilization
- `GET /api/rag/observability/boost/` - Risk boost effectiveness
- `GET /api/rag/observability/critical-docs/` - Critical docs report
- `GET /api/rag/observability/risk-distribution/` - Risk matrix + gaps
- `GET /api/rag/observability/channels/` - Retrieval channel stats
- `POST /api/rag/observability/classify/` - Trigger classification

### Files Changed
| File | Changes |
|------|---------|
| `core/services/rag_observability_service.py` | **NEW** - RAG metrics service |
| `core/views_rag_observability.py` | **NEW** - 8 API endpoints |
| `core/urls.py` | +8 URL patterns |

### Production Data
```
Total documents: 562
Critical documents: 18
By risk level: critical=18, high=332, medium=212
By document class: reference=277, architecture=155, constraint=80, security=21
Reserved tier: 650 tokens (16.2% of budget)
```

### Usage
```bash
# Get full dashboard
curl http://localhost:8000/api/rag/observability/dashboard/ -H "Authorization: Token $TOKEN"

# Get critical docs report
curl http://localhost:8000/api/rag/observability/critical-docs/ -H "Authorization: Token $TOKEN"
```

---

## Part 5: Agent Provenance Extension (Option F)

### Problem
Only 21 agents (stocks, blockchain, analysis) had provenance tracking. Key content and executive agents lacked data source tracking.

### Solution
Extended provenance tracking to 5 additional agent categories:

| Agent | Report Type | Stale Threshold |
|-------|-------------|-----------------|
| ContentWriterAgent | content_generation | 72h |
| PodcastCoordinatorAgent | podcast_coordination | 48h |
| CTOAgent | technical_analysis | 24h |
| COOAgent | operational_analysis | 24h |
| FullStackDeveloperAgent | code_generation | 168h (1 week) |

### Implementation Pattern
```python
# Session 954: Build provenance for content generation
from core.agents.report_schemas import build_provenance, format_disclaimer

provenance_sources = [{
    'name': 'ResearchContext',
    'endpoint': 'input/research',
    'retrieved_at': datetime.now(timezone.utc).isoformat(),
    'record_count': len(research.split()),
}]

provenance = build_provenance(
    report_type='content_generation',
    agent_name=self.name,
    sources=provenance_sources,
    stale_threshold_hours=72.0,
)

# Result now includes:
# 'provenance': provenance.to_dict(),
# 'publishable': provenance.publishable,
# 'validation_status': provenance.validation_status,
```

### Files Changed
| File | Changes |
|------|---------|
| `core/agents/content_writer_agent.py` | +provenance tracking for content generation |
| `core/agents/podcast/podcast_coordinator_agent.py` | +provenance tracking for podcast coordination |
| `core/agents/executive/cto_agent.py` | +provenance tracking for technical analysis |
| `core/agents/executive/coo_agent.py` | +provenance tracking for operational analysis |
| `core/agents/fullstack_developer_agent.py` | +provenance tracking for code generation |

### Agents with Provenance (Now 26+)
- **Stocks (8):** BullCaseAgent, BearCaseAgent, SignalScannerAgent, MarketAnomalyDetectorAgent, MarketMovementMonitorAgent, InstitutionalWatcherAgent, StockAuditCoordinator, MarketIntelligenceCoordinator
- **Blockchain (5):** SmartContractAuditorAgent, TransactionMonitorAgent, WhaleWatcherAgent, ExploitDetectorAgent, BlockchainAuditCoordinator
- **Analysis (3):** TrendAnalysisAgent, OpportunityScoringAgent, MarketIntelligenceAgent
- **Content (2):** ContentWriterAgent, PodcastCoordinatorAgent
- **Executive (2):** CTOAgent, COOAgent
- **Development (1):** FullStackDeveloperAgent
- **Other (5):** BookmakerAgent, CreationAgent, SportsOddsAnalyst, StockAnalystAgent, etc.

---

---

## Part 6: Boardroom ML UI Integration (Option G)

### Problem
The BoardroomTab only showed a simple text label for ML recommendations. Users couldn't see:
- Confidence level
- Approval probability
- The reasoning behind predictions
- Similar past decisions that influenced the prediction

### Solution
Enhanced the BoardroomTab with a comprehensive ML Prediction Panel:

#### 1. Extended AttentionItem Interface
```typescript
interface MLPrediction {
  prediction: 'approve' | 'ignore' | 'uncertain'
  confidence?: number
  approval_probability?: number
  reasoning?: string
  similar_items?: SimilarItem[]
  predicted_at?: string
}

interface AttentionItem {
  // ... existing fields ...
  ml_recommendation?: string
  ml_confidence?: number
  ml_prediction?: MLPrediction
}
```

#### 2. MLPredictionPanel Component
Features:
- **Recommendation badge** - Color-coded (green=approve, red=ignore, amber=uncertain)
- **Confidence bar** - Visual percentage with color coding (green≥70%, amber≥40%, gray<40%)
- **Approval probability gauge** - Gradient slider from red→amber→green
- **Reasoning signals** - Parsed from pipe-separated string into individual badges
- **Similar past decisions** - Collapsible list showing title, decision, and similarity %

#### 3. Collapsed Row Indicator
- Added small ML badge in row header showing "AI" with confidence percentage
- Lets users quickly identify items with predictions without expanding

### Files Changed
| File | Changes |
|------|---------|
| `frontend/src/pages/workspace/tabs/BoardroomTab.tsx` | +MLPredictionPanel component, extended interfaces, ML badge in row |

### Visual Elements
- Brain icon (🧠) for AI prediction header
- Sparkles icon (✨) for signals section
- History icon (⏱️) for similar past decisions
- Color-coded confidence bars and recommendation badges

---

## Part 7: Learning Loop Frontend (Option H)

### Problem
The learning loop backend had comprehensive effectiveness tracking, but no UI to visualize:
- Overall learning effectiveness
- Most/least effective patterns
- Pattern type distribution
- Recent learnings extracted

### Solution
Added "AI Learning" sub-tab to LearningJourneyTab with comprehensive visualization.

#### EffectivenessSubTab Features:
- **Stats Cards:** Active Learnings, Times Applied, Successful, Overall Effectiveness %
- **Most Effective Patterns:** Top 5 with progress bars, thumbs up to mark helpful
- **Needs Improvement:** Bottom 5 patterns (< 50% effectiveness)
- **By Pattern Type:** Distribution with counts and average confidence
- **Recent Learnings:** Last 10 extracted with details
- **Interactive Controls:** Run Cycle button, Refresh, Track outcome buttons

### Files Changed
| File | Changes |
|------|---------|
| `frontend/src/pages/workspace/tabs/LearningJourneyTab.tsx` | +EffectivenessSubTab, +LearningLoopStats types, +"AI Learning" sub-tab |

---

**Session 954-956 adds content-aware ML predictions, prevents junk initiatives, refines the learning loop, provides RAG observability, extends provenance to 26+ agents, comprehensive boardroom ML UI, AND a complete learning loop effectiveness dashboard.**
