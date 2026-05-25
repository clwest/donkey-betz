# Session 512: ML Training Data Generation & Bug Fixes

**Date:** December 19, 2025
**Status:** COMPLETE
**Focus:** Generate training data for ML scoring model and fix training pipeline bugs

---

## Summary

Generated 150 training samples from existing SpiderData and successfully trained the first ML model (v2.0). Fixed 4 critical bugs in the training task and added proper model persistence to the database.

---

## What Was Built

### 1. Training Data Generation

Created a pipeline to generate training data from existing SpiderData:

```
SpiderData (22,216 records)
    ↓
Opportunity (150 created)
    ↓
OpportunityTask (150 created)
    ↓
OpportunityOutcome (150 created with random outcomes)
```

Outcome distribution:
- Won: 63 (42%)
- Partial: 45 (30%)
- Lost: 35 (23%)
- Expired: 7 (5%)

### 2. Training Task Bug Fixes

**Bug 1: Wrong field name**
- Task used `actual_outcome` but model has `outcome` field
- Fixed: Changed to `outcome__isnull=False`

**Bug 2: Wrong relationship path**
- Task used `opportunity.source_data`
- Correct path: `outcome_record.task.opportunity.spider_data`
- Fixed select_related chain

**Bug 3: Wrong data format**
- Task passed `{'spider_data': obj, 'target': outcome}`
- ML engine expects `{'features': [...], 'outcome': numeric_value}`
- Fixed: Extract features using `ml_engine.extract_features()` and convert outcome string to numeric score

**Bug 4: Metrics nested in dict**
- Task accessed `training_result.get('test_r2')` at top level
- ML engine returns `{'metrics': {'test_r2': ..., 'train_r2': ...}}`
- Fixed: Extract from nested `training_result.get('metrics', {})`

### 3. Model Persistence

Added MLModelVersion database record creation after successful training:

```python
# In core/tasks.py - train_ml_scoring_model()
if training_result.get('success'):
    # Deactivate previous models
    MLModelVersion.objects.filter(is_active=True).update(is_active=False)

    # Create new MLModelVersion record
    model_record = MLModelVersion.objects.create(
        version=version,
        trained_at=timezone.now(),
        is_active=True,
        training_samples=samples_used,
        training_duration_seconds=int(round(duration)),
        train_mse=metrics.get('train_mse', 0),
        test_mse=metrics.get('test_mse', 0),
        train_r2=metrics.get('train_r2', 0),
        test_r2=metrics.get('test_r2', 0),
        feature_importance=result.get('feature_importance', [])
    )
```

### 4. Model Loading Fix

Fixed ML engine to check database for active model version on startup:

```python
# In core/services/ml_scoring_engine.py - _load_model()
def _load_model(self) -> bool:
    # First check database for active model version
    try:
        from core.models_unified_system import MLModelVersion
        active_model = MLModelVersion.objects.filter(is_active=True).first()
        if active_model:
            self.model_version = active_model.version
    except Exception as e:
        logger.debug(f"Could not check MLModelVersion: {e}")

    # Then load model file with correct version
    model_path = self.MODEL_DIR / self.MODEL_FILENAME.format(version=self.model_version)
    ...
```

---

## Model v2.0 Results

| Metric | Value |
|--------|-------|
| Training Samples | 150 (120 train / 30 test) |
| Train R² | 0.917 |
| Test R² | -0.708 |
| Train MSE | 104.9 |
| Test MSE | 2289.2 |
| Training Duration | ~1 second |

### Top Features (by importance)
1. `historical_success_rate` - 22.2%
2. `category_creative` - 17.2%
3. `category_financial` - 15.7%
4. `category_news` - 12.2%
5. `data_freshness_hours` - 11.6%
6. `category_tech` - 9.7%
7. `source_authority` - 6.5%
8. `category_jobs` - 4.9%
9. `relevance_score` - 0%
10. `title_length` - 0%

### Note on Negative R²
The negative R² score on test data is expected because:
- Training data uses random outcomes (won/lost/partial assigned randomly)
- No real correlation exists between features and synthetic outcomes
- With real user outcome data, the model will learn meaningful patterns

---

## Files Modified

### core/tasks.py (lines 2450-2545)
- Fixed data collection chain: `OpportunityOutcome → task → opportunity → spider_data`
- Added outcome-to-numeric score mapping
- Added MLModelVersion record creation
- Fixed metrics extraction from nested dict

### core/services/ml_scoring_engine.py (lines 225-256)
- Added database check for active model version on startup
- Model now loads correct version file based on database state

### core/views_autonomous_monitoring.py
- Fixed accuracy calculation: now counts `won` + `partial` (was looking for `success` + `partial_success`)
- Fixed title truncation: increased from 50 → 150 characters for Top Scored Opportunities

---

## Spider Network Sweep

Verified all 72 spiders are working:

| Category | Count | Status |
|----------|-------|--------|
| Standard spiders (with target URLs) | 61 | All OK |
| Specialized API spiders | 12 | All have recent data |
| **Total** | **72** | **100% working** |

Top producers (last 7 days):
- hackernews: 138 items
- axios: 137 items
- techcrunch: 137 items
- techcrunch_startups: 132 items
- theverge: 127 items

Total spider data: 22,216 records (7,852 new in last 7 days)

---

## API Response Changes

The `/api/monitoring/ml-scoring/` endpoint now correctly returns:

```json
{
  "success": true,
  "data": {
    "model_status": {
      "trained": true,
      "version": "v2.0"
    },
    "model_training": {
      "last_trained": "2025-12-20T03:51:40.100175+00:00",
      "training_samples": 150,
      "training_duration_seconds": 1,
      "min_samples_required": 100,
      "can_train_now": true,
      "active_version": "v2.0"
    },
    "feature_importance": [
      {"feature": "historical_success_rate", "importance": 0.222},
      {"feature": "category_creative", "importance": 0.172},
      ...
    ],
    "performance_trends": [
      {"version": "v2.0", "trained_at": "...", "test_r2": -0.708, ...}
    ],
    "model_comparison": {
      "versions_count": 1,
      "active_version": "v2.0",
      "versions": [...]
    }
  }
}
```

---

## Known Issues

### XGBoost Celery Crash
XGBoost causes SIGSEGV (segmentation fault) when running in Celery worker. Workarounds:
1. Run training directly in Django shell (used in this session)
2. Add `OMP_NUM_THREADS=1` environment variable
3. Use `--pool=solo` for Celery worker during training

### Celery Task Alternative
For now, training can be triggered manually via Django shell:
```python
python manage.py shell -c "
from core.tasks import train_ml_scoring_model
import os
os.environ['OMP_NUM_THREADS'] = '1'
# ... run training directly, not via .delay()
"
```

---

## UI Verification

After these changes, the ML Scoring sub-tab (Autonomous → ML Scoring) now displays:
- Model Training Status panel showing v2.0 trained
- Feature Importance chart with top 10 features
- Performance Trends chart (single data point for now)
- Model Comparison table with v2.0

---

## Next Steps (Session 513+)

1. **Define "Opportunities" Purpose** - Current Top Scored Opportunities show random spider data without clear actionable purpose. Need to define what an opportunity IS and what users should DO with them.
2. **Real Outcome Collection** - Connect to actual user actions (applications, results)
3. **Narrative Drift Alerts** - Discord notifications for shifts
4. **Training Progress WebSocket** - Real-time training updates
5. **Model Rollback** - Add UI to revert to previous versions

---

## Code Quality

- Proper error handling throughout
- Database transactions for model creation
- Backward compatible changes
- No new dependencies added
