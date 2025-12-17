# Session 470: ML Scoring Engine Implementation

**Date:** December 17, 2025
**Status:** Complete - Phase 1
**Focus:** XGBoost-based ML scoring with SHAP explainability for opportunity scoring

## Summary

Session 470 implemented Phase 1 of the Market Intelligence Architecture - an ML Scoring Engine that uses XGBoost with SHAP explainability to score opportunities. The system uses a hybrid approach combining ML predictions with rule-based scoring.

## Components Built

| Component | File | Description |
|-----------|------|-------------|
| ML Scoring Engine | `core/services/ml_scoring_engine.py` | XGBoost model with SHAP explainability (~500 lines) |
| MLModelVersion Model | `core/models_unified_system.py` | Tracks model versions, metrics, feature importance |
| ScoringExplanation Model | `core/models_unified_system.py` | Stores SHAP values for each scored opportunity |
| Migration 0100 | `core/migrations/0100_session_470_ml_scoring_models.py` | Database migration (applied) |
| Training Task | `core/tasks.py` | `train_ml_scoring_model` - Weekly retraining |
| Evaluation Task | `core/tasks.py` | `evaluate_ml_model_performance` - Daily evaluation |
| Celery Beat Schedule | `core/celery.py` | Sunday 3:30 AM training, Daily 6:30 AM evaluation |

## Architecture

### Hybrid Scoring Formula
```
final_score = (0.6 * ml_score) + (0.4 * rule_based_score)
```

### Feature Extraction (15 features)
The ML model extracts these features from SpiderData:
1. Title length
2. Content length
3. Source authority score
4. Freshness (hours since discovery)
5. Category match score
6. Keyword relevance
7. Has URL (boolean)
8. Content quality indicators
9. Source reliability history
10. Time of day discovered
11. Day of week discovered
12. Topic trending score
13. Competition saturation
14. Historical performance (similar topics)
15. User preference alignment

### SHAP Explainability
Every scored opportunity includes feature contributions explaining WHY it received that score:
```json
{
  "score": 78.5,
  "explanation": {
    "source_authority": +12.3,
    "freshness": +8.7,
    "keyword_relevance": +6.2,
    "competition_saturation": -4.1,
    ...
  }
}
```

## How It Works

### Training Flow
1. Collect `OpportunityOutcome` records (user feedback on opportunities)
2. Extract features from corresponding `SpiderData`
3. Train XGBoost classifier/regressor
4. Calculate SHAP values for explainability
5. Store model version with metrics in `MLModelVersion`
6. Activate new model for scoring

### Scoring Flow
1. Receive SpiderData item to score
2. Extract 15 features
3. If ML model exists: Get ML prediction + SHAP explanation
4. Calculate rule-based score (fallback/hybrid component)
5. Combine: `final = 0.6*ML + 0.4*rules`
6. Store explanation in `ScoringExplanation`
7. Return score with transparency

### Auto-Retraining
- **Trigger:** 100+ OpportunityOutcome records
- **Schedule:** Weekly (Sunday 3:30 AM)
- **Evaluation:** Daily (6:30 AM) - checks accuracy, triggers retraining if degraded

## Database Models

### MLModelVersion
```python
class MLModelVersion(models.Model):
    version = models.CharField(max_length=50)
    model_type = models.CharField(max_length=50)  # 'xgboost', 'lightgbm', etc.
    trained_at = models.DateTimeField()
    training_samples = models.IntegerField()
    accuracy = models.DecimalField()
    precision = models.DecimalField()
    recall = models.DecimalField()
    f1_score = models.DecimalField()
    feature_importance = models.JSONField()  # {feature: importance}
    is_active = models.BooleanField(default=False)
    model_path = models.CharField()  # Path to serialized model
```

### ScoringExplanation
```python
class ScoringExplanation(models.Model):
    opportunity = models.ForeignKey('Opportunity')
    model_version = models.ForeignKey('MLModelVersion')
    ml_score = models.DecimalField()
    rule_score = models.DecimalField()
    final_score = models.DecimalField()
    shap_values = models.JSONField()  # {feature: contribution}
    created_at = models.DateTimeField()
```

## Current State

| Component | Status |
|-----------|--------|
| ML Model | Not yet trained (needs OpportunityOutcome data) |
| Scoring | Using rule-based fallback with hybrid structure |
| Database | Models created, migration applied |
| Celery Tasks | Registered and scheduled |
| Ready For | Auto-training once 100+ outcomes accumulate |

## Celery Beat Schedule

```python
# In core/celery.py
'train-ml-scoring-model': {
    'task': 'core.tasks.train_ml_scoring_model',
    'schedule': crontab(hour=3, minute=30, day_of_week='sunday'),
},
'evaluate-ml-model': {
    'task': 'core.tasks.evaluate_ml_model_performance',
    'schedule': crontab(hour=6, minute=30),
},
```

## Next Phases

### Phase 2: Real-time vs Batch Scoring Dispatcher
- `core/services/scoring_dispatcher.py` - Routes scoring requests
- `core/services/realtime_scorer.py` - Redis priority queue scorer
- SLA configuration (<500ms latency target)

### Phase 3: A/B Testing Framework for Scoring
- Compare ML vs rule-based performance
- User feedback collection
- Model variant testing

### Phase 4: Advanced Features
- Multi-model ensemble
- Online learning (continuous updates)
- Personalized scoring per user

## Testing

To test the ML scoring engine manually:
```python
from core.services.ml_scoring_engine import MLScoringEngine
from core.models import SpiderData

engine = MLScoringEngine()
spider_data = SpiderData.objects.first()
result = engine.score_opportunity(spider_data)
print(f"Score: {result['score']}")
print(f"Explanation: {result['explanation']}")
```

## Related Sessions

- Session 465: Market Intelligence Desk (foundation)
- Session 466: Autonomous Content Studio
- Session 469: Discord fixes + Real agent debates
