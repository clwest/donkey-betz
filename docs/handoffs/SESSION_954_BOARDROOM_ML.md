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

**Session 954 adds content-aware ML predictions to the boardroom system AND prevents junk initiative creation at the source.**
