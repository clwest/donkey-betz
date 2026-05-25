# Session 470: Market Intelligence Architecture - ML Scoring Engine

**Date:** December 17, 2025
**Status:** Phase 1 COMPLETE | Phase 2 COMPLETE
**Policy Source:** Boardroom Decision adopted as canonical policy

---

## Executive Summary

Implemented Phase 1 of the Market Intelligence Architecture based on the adopted Boardroom Policy. This creates a hybrid ML + rule-based scoring system with SHAP explainability for opportunity scoring.

---

## What Was Built (Phase 1)

### 1. ML Scoring Engine (`core/services/ml_scoring_engine.py`)

A complete XGBoost-based scoring engine with SHAP explainability:

```python
from core.services.ml_scoring_engine import get_ml_scoring_engine

engine = get_ml_scoring_engine()
result = engine.score_opportunity(spider_data)

# Returns:
# - hybrid_score: Combined 60% ML + 40% rule-based score
# - ml_score: Pure ML prediction
# - rule_score: Rule-based calculation
# - shap_explanation: Feature contributions explaining the score
# - confidence: Confidence level (0-100%)
```

**Key Features:**
- 15 extracted features from SpiderData
- XGBoost gradient boosting model
- SHAP TreeExplainer for interpretability
- Graceful fallback to rule-based scoring when no model exists
- Model versioning and persistence

### 2. Database Models

**MLModelVersion** - Tracks trained model versions:
```python
class MLModelVersion(models.Model):
    version = models.CharField(max_length=20, unique=True)
    trained_at = models.DateTimeField()
    training_samples = models.IntegerField()
    train_mse = models.FloatField(null=True)
    test_mse = models.FloatField(null=True)
    train_r2 = models.FloatField(null=True)
    test_r2 = models.FloatField(null=True)
    feature_importance = models.JSONField(default=list)
    is_active = models.BooleanField(default=False)
    model_path = models.CharField(max_length=500)
```

**ScoringExplanation** - Stores SHAP explanations per opportunity:
```python
class ScoringExplanation(models.Model):
    opportunity = models.OneToOneField(Opportunity, related_name='ml_explanation')
    ml_score = models.FloatField()
    rule_score = models.FloatField()
    hybrid_score = models.FloatField()
    confidence = models.FloatField()
    shap_base_value = models.FloatField(null=True)
    shap_values = models.JSONField(default=list)
    feature_names = models.JSONField(default=list)
    top_positive_features = models.JSONField(default=list)
    top_negative_features = models.JSONField(default=list)
    model_version = models.ForeignKey(MLModelVersion, null=True)
```

### 3. OpportunityScoringAgent Integration

Modified `core/agents/analysis/opportunity_scoring_agent.py` to use hybrid ML scoring:

```python
def _calculate_score(self, spider_data) -> Dict[str, Any]:
    # Try ML scoring first
    ml_engine = _get_ml_scoring_engine()
    if ml_engine:
        ml_result = ml_engine.score_opportunity(spider_data)
        if ml_result.success:
            return {
                'overall_score': int(ml_result.hybrid_score),
                'ml_score': ml_result.ml_score,
                'rule_score': ml_result.rule_score,
                'scoring_method': 'hybrid_ml',
                # ... SHAP explanation included
            }
    # Fallback to pure rule-based scoring
```

### 4. Celery Tasks

**train_ml_scoring_model** (`core/tasks.py`):
- Trains XGBoost model on OpportunityOutcome data
- Scheduled: Sunday 3:30 AM (weekly)
- Requires 100+ samples to train
- Stores model in `core/ml_models/`

**evaluate_ml_model_performance** (`core/tasks.py`):
- Evaluates model accuracy against recent outcomes
- Scheduled: Daily 6:30 AM
- Triggers retraining if accuracy < 60% or MAE > 30

### 5. Dependencies Installed

```bash
pip install xgboost shap scikit-learn joblib
```

---

## Files Created/Modified

### New Files
| File | Lines | Purpose |
|------|-------|---------|
| `core/services/ml_scoring_engine.py` | ~500 | XGBoost + SHAP scoring engine |
| `core/migrations/0100_session_470_ml_scoring_models.py` | ~225 | Database migration |
| `core/ml_models/` | dir | Model storage directory |

### Modified Files
| File | Changes |
|------|---------|
| `core/models_unified_system.py` | Added MLModelVersion, ScoringExplanation models |
| `core/agents/analysis/opportunity_scoring_agent.py` | ML engine integration |
| `core/tasks.py` | Added 2 Celery tasks |
| `core/celery.py` | Added 2 beat schedule entries |

---

## How It Works

### Scoring Flow

```
SpiderData → MLScoringEngine.score_opportunity()
    ↓
Feature Extraction (15 features)
    ↓
┌─────────────────┬─────────────────┐
│  ML Prediction  │  Rule Scoring   │
│  (XGBoost)      │  (Heuristics)   │
└────────┬────────┴────────┬────────┘
         ↓                 ↓
    ML Score (60%)    Rule Score (40%)
         ↓                 ↓
         └────────┬────────┘
                  ↓
            Hybrid Score
                  ↓
         SHAP Explanation
                  ↓
           MLScoringResult
```

### Feature Extraction

| Feature | Description |
|---------|-------------|
| title_length | Length of opportunity title |
| has_price | Whether price/salary mentioned |
| has_deadline | Whether deadline mentioned |
| source_authority | Source reputation score |
| category_score | Category-based score |
| freshness_hours | Hours since creation |
| relevance_score | Spider relevance rating |
| keyword_score | Business keyword matches |
| actionability | How actionable the content is |
| competition_indicator | Competition level signals |
| profit_keywords | Profit-related keyword count |
| urgency_keywords | Urgency-related keyword count |
| tech_keywords | Technology keyword count |
| opportunity_keywords | Opportunity keyword count |
| negative_keywords | Negative signal count |

---

## Current State

- **ML Model**: Not trained yet (needs OpportunityOutcome data)
- **Scoring Mode**: Rule-based with hybrid structure ready
- **Database**: Migration 0100 applied, tables created
- **Celery**: Tasks registered, schedules configured

### To Train the Model

The model will auto-train when:
1. 100+ OpportunityOutcome records exist with actual_outcome values
2. Weekly Sunday 3:30 AM task runs

Or trigger manually:
```python
from core.tasks import train_ml_scoring_model
train_ml_scoring_model.delay(force_retrain=True, min_samples=10)
```

---

## Remaining Phases

### Phase 2: Real-time vs Batch Scoring Dispatcher (COMPLETE ✅)

**New Files Created:**
- `core/services/scoring_dispatcher.py` (~350 lines) - Routes scoring requests
- `core/services/realtime_scorer.py` (~350 lines) - Redis priority queue scorer

**New Models:**
- `ScoringConfiguration` - SLA settings, scoring mode preferences, metrics tracking
- `ScoringQueueItem` - Batch queue persistence with priority ordering

**New Celery Tasks:**
- `process_realtime_scoring_queue` - Every 30 seconds
- `process_batch_scoring_queue` - Every hour
- `cleanup_stale_scoring_requests` - Every 15 minutes
- `score_spider_data_async` - On-demand async scoring

**Features Implemented:**
- Three-tier priority queue (HIGH/NORMAL/LOW)
- Real-time scoring (<500ms SLA target)
- Batch queue with database persistence
- Auto-switch mode based on latency/queue depth
- SLA tracking and breach detection
- Dead letter queue for failed items

**Test Results:**
- HIGH priority → realtime (~2.8ms) ✅
- NORMAL priority → realtime (~1.4ms) ✅
- LOW priority → batch queue ✅
- SLA target: 500ms (well within)

### Phase 3: Human-in-the-Loop Validation (COMPLETE ✅)

**New Files Created:**
- `core/services/hitl_validation.py` (~450 lines) - Validation workflow engine
- `core/views_validation.py` (~400 lines) - API endpoints

**New Models:**
- `ValidationRequest` - Tracks items needing human review
- `ValidationDecision` - Records human decisions with reasoning
- `ValidationConfig` - Confidence thresholds, auto-assignment settings

**New Celery Tasks:**
- `process_hitl_escalations` - Every 15 minutes
- `expire_overdue_validations` - Every hour
- `score_and_route_opportunity` - On-demand scoring + routing

**API Endpoints:**
- `GET /api/validation/queue/` - List pending validations
- `GET /api/validation/stats/` - Validation statistics
- `GET /api/validation/<id>/` - Validation details
- `POST /api/validation/<id>/approve/` - Approve (with optional override)
- `POST /api/validation/<id>/reject/` - Reject (requires reasoning)
- `POST /api/validation/<id>/escalate/` - Escalate for review
- `POST /api/validation/<id>/defer/` - Defer for later
- `POST /api/validation/<id>/assign/` - Assign to reviewer
- `POST /api/validation/<id>/unassign/` - Unassign

**Features:**
- Auto-approve (confidence >= 85%)
- Validation queue (50-85%)
- Auto-reject (<50%)
- Time-bound escalation
- Priority-based assignment
- ML agreement tracking

### Phase 4: Centralized Event Bus (Redis Streams)

**New Files:**
- `core/services/event_bus.py` - Redis Streams pub/sub
- `core/services/event_handlers.py` - Event consumers

**Event Streams:**
- `mi:spider_data` - New spider data
- `mi:opportunity_scored` - Scored opportunities
- `mi:validation_required` - Needs human review
- `mi:outcome_recorded` - Actual outcomes

### Phase 5: Provenance & Compliance Layer

**New Files:**
- `core/services/provenance_tracker.py` - Data lineage
- `core/middleware/compliance.py` - Compliance checks

**Features:**
- Full data lineage: Spider → Opportunity → Score → Decision
- Immutable audit trail
- Source attribution

### Phase 6: ROI Metrics & Attribution

**New Files:**
- `core/services/roi_tracker.py` - ROI calculations
- `core/views_roi_metrics.py` - API endpoints

**Features:**
- Conversion tracking
- Revenue attribution
- Weekly intelligence briefs

---

## Testing Commands

```bash
# Test ML engine import
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.services.ml_scoring_engine import get_ml_scoring_engine
engine = get_ml_scoring_engine()
print(f'Engine loaded: {engine is not None}')
"

# Test scoring on SpiderData
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.services.ml_scoring_engine import get_ml_scoring_engine
from core.models_unified_system import SpiderData
engine = get_ml_scoring_engine()
sd = SpiderData.objects.first()
result = engine.score_opportunity(sd)
print(f'Score: {result.hybrid_score}, Method: {\"ML\" if engine.model else \"Rules\"}')"

# Test Celery task
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.tasks import train_ml_scoring_model
print(f'Task: {train_ml_scoring_model.name}')"
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                 MARKET INTELLIGENCE PLATFORM                 │
└─────────────────────────────────────────────────────────────┘

PHASE 1 (COMPLETE) ✅
├─ MLScoringEngine (XGBoost + SHAP)
├─ Hybrid Scoring (60% ML + 40% Rules)
├─ Feature Extraction (15 features)
├─ Model Versioning (MLModelVersion)
├─ Score Explanations (ScoringExplanation)
└─ Auto-Training Pipeline (Celery)

PHASE 2 (COMPLETE) ✅
├─ ScoringDispatcher (realtime vs batch routing)
├─ RealtimeScorer (Redis priority queue)
├─ ScoringConfiguration (SLA settings)
├─ ScoringQueueItem (batch persistence)
├─ 4 Celery tasks (queue processing)
└─ Tested: 2.8ms HIGH, 1.4ms NORMAL priority

PHASE 3 (COMPLETE) ✅
├─ HITLValidationService (validation workflow)
├─ ValidationRequest, ValidationDecision, ValidationConfig
├─ 9 API endpoints (/api/validation/*)
├─ 3 Celery tasks (escalation, expiry, scoring)
├─ Confidence thresholds (>=85% approve, <50% reject)
└─ Auto-assignment and priority-based queue

PHASE 4-6 (PENDING) ⏳
├─ Event Bus (Redis Streams)
├─ Provenance & Compliance
└─ ROI Metrics & Attribution
```

---

## Handoff Notes

### What's Complete

1. **Phase 1 - ML Scoring Engine** ✅
   - XGBoost + SHAP scoring ready
   - Using rule-based fallback until ML model trains
   - Auto-training when 100+ OpportunityOutcome records exist
   - Celery: Sunday 3:30 AM training, Daily 6:30 AM evaluation

2. **Phase 2 - Scoring Dispatcher** ✅
   - Real-time vs batch routing working
   - Three-tier priority queue (HIGH/NORMAL/LOW)
   - SLA tracking (<500ms target, achieving ~2ms)
   - Celery: 30-second realtime queue, hourly batch, 15-min cleanup

### Files Created This Session

| File | Lines | Purpose |
|------|-------|---------|
| `core/services/ml_scoring_engine.py` | ~500 | XGBoost + SHAP engine |
| `core/services/scoring_dispatcher.py` | ~350 | Realtime vs batch routing |
| `core/services/realtime_scorer.py` | ~350 | Redis priority queue |
| `core/migrations/0100_session_470_ml_scoring_models.py` | ~225 | Phase 1 models |
| `core/migrations/0101_session_470_scoring_dispatcher.py` | ~100 | Phase 2 models |

### Next Steps (Phase 3)

**Continue with Human-in-the-Loop Validation:**
- Create `core/services/hitl_validation.py` - Validation workflow
- Create `core/views_validation.py` - API endpoints
- Add ValidationRequest, ValidationDecision models
- Implement confidence thresholds:
  - >= 85%: Auto-approve
  - 50-85%: Queue for human review
  - < 50%: Auto-reject

### Quick Test Commands

```bash
# Test scoring dispatcher
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.services.scoring_dispatcher import get_scoring_dispatcher, ScoringPriority
from core.models_unified_system import SpiderData
dispatcher = get_scoring_dispatcher()
sd = SpiderData.objects.first()
result = dispatcher.dispatch(sd, ScoringPriority.HIGH, 'test')
print(f'Score: {result.score}, Mode: {result.mode}, Latency: {result.latency_ms}ms')
"

# Check queue status
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.models_unified_system import ScoringQueueItem
print(f'Pending: {ScoringQueueItem.objects.filter(status=\"pending\").count()}')
"
```

---

*Session 470 - Market Intelligence Architecture Phases 1 & 2*
