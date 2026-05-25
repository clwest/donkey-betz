# Session 668: ML Scoring Engine Assessment & Improvement Roadmap

**Date:** January 5, 2026
**Status:** Phase 1 & 2 COMPLETE | Model v7.1 Active
**Priority:** High (affects opportunity scoring accuracy)
**Location:** `core/services/ml_scoring_engine.py`

---

## Executive Summary

The ML Scoring Engine has been significantly improved through Phase 1 (dead feature fixes) and Phase 2 (feature engineering + model optimization).

**Progress: 6/10 → 9/10 ACHIEVED**

### Completed Phases

| Phase | Session | Status | Key Changes |
|-------|---------|--------|-------------|
| **Phase 1** | 669 | ✅ COMPLETE | Fixed dead features, expanded keywords, v5.0 |
| **Phase 2A** | 670 | ✅ COMPLETE | 24 features (embedding, temporal, text quality), v6.0 |
| **Phase 2B** | 670 | ✅ COMPLETE | LightGBM + Optuna hyperparameter tuning, v7.1 |

### Model Performance Progression

| Version | Model | Test R² | Improvement |
|---------|-------|---------|-------------|
| v4.0 | XGBoost | - | 47% dead features |
| v5.0 | XGBoost | - | Fixed keyword extraction |
| v6.0 | XGBoost | 0.3158 | +9 features |
| v7.0 | XGBoost + Optuna | 0.5383 | +70% |
| **v7.1** | **LightGBM + Optuna** | **0.6276** | **+99%** ✅ |

---

## Original Assessment (Historical)

---

## Current State Analysis

### Model Details

| Attribute | Value |
|-----------|-------|
| Model Version | v4.0 |
| Algorithm | XGBoost Regressor |
| Training Date | December 21, 2025 |
| Training Samples | 150 (from OpportunityOutcome) |
| Features | 15 (7 dead) |
| Hybrid Weights | 60% ML / 40% Rules |
| Explainability | SHAP TreeExplainer |

### XGBoost Parameters (Current)

```python
XGBRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42,
    objective='reg:squarederror'
)
```

### Feature Importance Analysis

```
WORKING FEATURES (53% of feature space):
─────────────────────────────────────────
historical_success_rate   22.18%  ⚠️ Uses hardcoded defaults!
category_creative         17.21%
category_financial        15.69%
category_news             12.16%
data_freshness_hours      11.65%
category_tech              9.73%
source_authority           6.48%
category_jobs              4.91%

DEAD FEATURES (47% of feature space - 0% importance):
─────────────────────────────────────────
relevance_score            0.00%  ❌
title_length               0.00%  ❌
has_url                    0.00%  ❌
keyword_ai                 0.00%  ❌
keyword_trending           0.00%  ❌
keyword_urgent             0.00%  ❌
keyword_opportunity        0.00%  ❌
```

---

## Critical Issues to Fix

### Issue 1: Hardcoded Historical Success Rates (HIGH PRIORITY)

**Location:** `ml_scoring_engine.py` lines 339-352

**Current Code (WRONG):**
```python
def _get_historical_success_rate(self, spider_name: str) -> float:
    """Get historical success rate for a spider source."""
    # Note: Query OpportunityOutcome for actual rates
    # For now, use default rates based on source type
    default_rates = {
        'remoteok': 0.65,
        'weworkremotely': 0.60,
        'hackernews': 0.55,
        # ... hardcoded values
    }
    return default_rates.get(spider_name, default_rates['default'])
```

**Problem:** This feature has 22.18% importance but returns static values regardless of actual outcomes.

**Fix Required:**
```python
def _get_historical_success_rate(self, spider_name: str) -> float:
    """Get historical success rate for a spider source from actual data."""
    from django.db.models import Count, Q
    from django.core.cache import cache

    cache_key = f"spider_success_rate_{spider_name}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        from core.models_unified_system import OpportunityOutcome, Opportunity

        # Get outcomes for this spider source (last 90 days)
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=90)

        outcomes = OpportunityOutcome.objects.filter(
            opportunity__spider_data__spider_name=spider_name,
            recorded_at__gte=cutoff
        ).values('outcome_type').annotate(count=Count('id'))

        total = sum(o['count'] for o in outcomes)
        if total < 5:  # Not enough data, use default
            return self._default_rates.get(spider_name, 0.35)

        # Calculate weighted success rate
        success_weights = {
            'success': 1.0, 'won': 1.0,
            'partial': 0.5, 'applied': 0.6,
            'rejected': 0.2, 'expired': 0.1,
            'failure': 0.0, 'lost': 0.0
        }

        weighted_sum = sum(
            o['count'] * success_weights.get(o['outcome_type'], 0.3)
            for o in outcomes
        )
        rate = weighted_sum / total

        # Cache for 1 hour
        cache.set(cache_key, rate, 3600)
        return rate

    except Exception as e:
        logger.warning(f"Error getting success rate for {spider_name}: {e}")
        return self._default_rates.get(spider_name, 0.35)
```

---

### Issue 2: Dead Keyword Features (HIGH PRIORITY)

**Location:** `ml_scoring_engine.py` lines 101-105, 278-317

**Root Cause Analysis:**

The keyword features are extracted correctly in `extract_features()`, but they always return 0.0 in the trained model. Likely causes:

1. **Keyword sets too narrow** - The keyword sets may not match actual titles
2. **Case sensitivity issues** - Already using `.lower()`, so unlikely
3. **Training data bias** - All 150 training samples may lack these keywords

**Diagnosis Script (run this first):**
```python
# Run in Django shell to diagnose
from core.models_unified_system import SpiderData
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=90)
recent = SpiderData.objects.filter(created_at__gte=cutoff)

# Check keyword prevalence
AI_KEYWORDS = {'ai', 'ml', 'machine learning', 'deep learning', 'gpt', 'llm', 'neural', 'automation'}
TRENDING_KEYWORDS = {'viral', 'trending', 'hot', 'breaking', 'surge', 'boom', 'skyrocket'}

ai_count = 0
trending_count = 0
total = 0

for sd in recent[:1000]:
    title = (sd.raw_data or {}).get('title', '').lower()
    total += 1
    if any(kw in title for kw in AI_KEYWORDS):
        ai_count += 1
    if any(kw in title for kw in TRENDING_KEYWORDS):
        trending_count += 1

print(f"AI keyword prevalence: {ai_count}/{total} = {100*ai_count/total:.1f}%")
print(f"Trending keyword prevalence: {trending_count}/{total} = {100*trending_count/total:.1f}%")
```

**Fix Required (expand keyword sets):**
```python
# Expanded keyword sets for better coverage
AI_KEYWORDS = {
    'ai', 'ml', 'machine learning', 'deep learning', 'gpt', 'llm', 'neural',
    'automation', 'artificial intelligence', 'chatgpt', 'claude', 'openai',
    'anthropic', 'copilot', 'gemini', 'model', 'transformer', 'diffusion',
    'stable diffusion', 'midjourney', 'generative', 'agent', 'rag',
    'embedding', 'vector', 'fine-tune', 'prompt'
}

TRENDING_KEYWORDS = {
    'viral', 'trending', 'hot', 'breaking', 'surge', 'boom', 'skyrocket',
    'exploding', 'soaring', 'rocketing', 'growing', 'rising', 'popular',
    'best', 'top', 'leading', 'fastest', 'record', 'unprecedented',
    'massive', 'huge', 'major', 'big', 'significant'
}

URGENT_KEYWORDS = {
    'urgent', 'asap', 'immediate', 'now', 'today', 'limited', 'deadline',
    'expires', 'ending', 'last chance', 'hurry', 'quick', 'fast',
    'closing', 'final', 'soon', 'act now', 'don\'t miss'
}

OPPORTUNITY_KEYWORDS = {
    'opportunity', 'potential', 'growth', 'profit', 'revenue', 'income',
    'earn', 'money', 'salary', 'remote', 'hiring', 'job', 'position',
    'role', 'career', 'freelance', 'contract', 'gig', 'project',
    'investment', 'roi', 'return', 'yield', 'gains'
}
```

---

### Issue 3: Missing Validation Logging

**Add to `score_opportunity()` method:**
```python
def score_opportunity(self, spider_data) -> MLScoringResult:
    # ... existing code ...

    # Add feature validation logging
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Features for {spider_data.spider_name}: {dict(zip(FEATURE_NAMES, features[0]))}")

        # Warn about zero features
        zero_features = [name for name, val in zip(FEATURE_NAMES, features[0]) if val == 0]
        if len(zero_features) > 10:
            logger.warning(f"High zero-feature count ({len(zero_features)}/{len(FEATURE_NAMES)}): {zero_features}")
```

---

## Phase 1: Quick Wins (1-2 hours) ✅ COMPLETE

**Completed in:** Session 669

### Task 1.1: Fix Historical Success Rate Query

1. Replace hardcoded `_get_historical_success_rate()` with actual database query
2. Add caching (1 hour TTL)
3. Add fallback for spiders with insufficient data (<5 outcomes)

**Files to modify:**
- `core/services/ml_scoring_engine.py` (lines 339-352)

**Test:**
```bash
.venv/bin/python manage.py shell -c "
from core.services.ml_scoring_engine import get_ml_scoring_engine
engine = get_ml_scoring_engine()

# Test with different spider names
for spider in ['hackernews', 'remoteok', 'techcrunch', 'unknown_spider']:
    rate = engine._get_historical_success_rate(spider)
    print(f'{spider}: {rate:.2f}')
"
```

### Task 1.2: Debug Dead Features

1. Run diagnosis script to check keyword prevalence
2. Expand keyword sets if prevalence is low
3. Verify feature extraction is working

**Test:**
```bash
.venv/bin/python manage.py shell -c "
from core.services.ml_scoring_engine import get_ml_scoring_engine
from core.models_unified_system import SpiderData

engine = get_ml_scoring_engine()
sample = SpiderData.objects.filter(spider_name='hackernews').first()
features = engine.extract_features(sample)

print('Feature values:')
for name, val in zip(engine.FEATURE_NAMES, features[0]):
    print(f'  {name}: {val}')
"
```

### Task 1.3: Add Validation Logging

1. Add debug logging for feature extraction
2. Add warning for high zero-feature counts
3. Log when falling back to rule-based scoring

---

## Phase 2: Feature Engineering (Half-day) ✅ COMPLETE

**Completed in:** Session 670

### Task 2.1: Add Embedding Similarity Feature

**New feature:** Semantic similarity between spider content and successful outcomes.

```python
def _get_embedding_similarity(self, spider_data) -> float:
    """Get similarity to historically successful opportunities."""
    if not spider_data.embedding_vector:
        return 0.5  # Neutral default

    try:
        from core.models_unified_system import SpiderData, OpportunityOutcome
        import numpy as np

        # Get embeddings from successful opportunities
        successful_embeddings = SpiderData.objects.filter(
            opportunity__outcomes__outcome_type__in=['success', 'won'],
            embedding_vector__isnull=False
        ).values_list('embedding_vector', flat=True)[:50]

        if not successful_embeddings:
            return 0.5

        # Calculate average cosine similarity
        query_vec = np.array(spider_data.embedding_vector)
        similarities = []
        for emb in successful_embeddings:
            target_vec = np.array(emb)
            sim = np.dot(query_vec, target_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(target_vec)
            )
            similarities.append(sim)

        return float(np.mean(similarities))
    except Exception as e:
        logger.warning(f"Embedding similarity error: {e}")
        return 0.5
```

### Task 2.2: Add Temporal Features

```python
# New features to add to FEATURE_NAMES
'hour_of_day',        # 0-23, captures timing patterns
'day_of_week',        # 0-6 (Monday=0)
'is_weekend',         # Boolean
'days_since_monday',  # 0-6, alternative encoding

# In extract_features():
created = spider_data.created_at
features.extend([
    created.hour,                          # hour_of_day
    created.weekday(),                     # day_of_week
    1.0 if created.weekday() >= 5 else 0.0,  # is_weekend
    created.weekday(),                     # days_since_monday
])
```

### Task 2.3: Add Text Quality Features

```python
# New features
'description_length',     # Character count of description
'title_word_count',       # Word count in title
'has_numbers',            # Contains numbers (prices, stats)
'question_mark',          # Title is a question
'exclamation_mark',       # Title has exclamation

# In extract_features():
description = raw_data.get('description', '') or ''
features.extend([
    min(len(description), 5000),                    # description_length
    len(title.split()),                              # title_word_count
    1.0 if any(c.isdigit() for c in title) else 0.0,  # has_numbers
    1.0 if '?' in title else 0.0,                    # question_mark
    1.0 if '!' in title else 0.0,                    # exclamation_mark
])
```

### Task 2.4: Update Feature List

**New FEATURE_NAMES (24 features):**
```python
FEATURE_NAMES = [
    # Original working features
    'relevance_score',
    'source_authority',
    'data_freshness_hours',
    'title_length',
    'has_url',
    'category_tech',
    'category_financial',
    'category_jobs',
    'category_creative',
    'category_news',
    'keyword_ai',
    'keyword_trending',
    'keyword_urgent',
    'keyword_opportunity',
    'historical_success_rate',

    # New Phase 2 features
    'embedding_similarity',    # Semantic similarity to successes
    'hour_of_day',             # 0-23
    'day_of_week',             # 0-6
    'is_weekend',              # Boolean
    'description_length',      # Text quality
    'title_word_count',
    'has_numbers',
    'question_mark',
    'exclamation_mark',
]
```

---

## Phase 2B: LightGBM + Optuna Optimization ✅ COMPLETE

**Completed in:** Session 670

Added as part of Phase 2, implementing Tasks 3.1 and 3.2 early:

### Implementation

- **LightGBM**: Added as alternative model backend (now default)
- **Optuna**: Bayesian hyperparameter search (50 trials, 5-fold CV)
- **New methods**:
  - `optimize_hyperparameters()` - Optuna-powered tuning
  - `train_model_with_optimization()` - Full pipeline with auto-tuning
  - `_create_model()` - Factory for XGBoost/LightGBM

### Results

v7.1 (LightGBM + Optuna) achieved **Test R² = 0.6276** (+99% vs baseline)

---

## Phase 3: Model Improvements (Remaining Tasks)

**Session Target:** 671+

### Task 3.1: Implement K-Fold Cross-Validation ✅ COMPLETE

*(Implemented via Optuna's cross_val_score in Phase 2B)*

```python
def train_model_with_cv(
    self,
    training_data: List[Dict[str, Any]],
    n_splits: int = 5,
    version: str = None
) -> Dict[str, Any]:
    """Train with k-fold cross-validation for better metrics."""
    from sklearn.model_selection import KFold, cross_val_score

    X = np.array([d['features'] for d in training_data])
    y = np.array([d['outcome'] for d in training_data])

    # Scale features
    self._feature_scaler = StandardScaler()
    X_scaled = self._feature_scaler.fit_transform(X)

    # Create model
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )

    # K-fold CV
    kfold = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_scaled, y, cv=kfold, scoring='r2')

    # Train final model on all data
    model.fit(X_scaled, y)
    self.model = model

    return {
        'cv_scores': cv_scores.tolist(),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'n_splits': n_splits
    }
```

### Task 3.2: Add Hyperparameter Tuning (Optuna) ✅ COMPLETE

*(Implemented in Phase 2B - see `optimize_hyperparameters()` method)*

```python
def tune_hyperparameters(
    self,
    training_data: List[Dict[str, Any]],
    n_trials: int = 50
) -> Dict[str, Any]:
    """Tune hyperparameters using Optuna."""
    import optuna
    from sklearn.model_selection import cross_val_score

    X = np.array([d['features'] for d in training_data])
    y = np.array([d['outcome'] for d in training_data])

    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
            'reg_alpha': trial.suggest_float('reg_alpha', 0, 1),
            'reg_lambda': trial.suggest_float('reg_lambda', 0, 1),
        }

        model = xgb.XGBRegressor(**params, random_state=42)
        scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        return scores.mean()

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)

    return {
        'best_params': study.best_params,
        'best_score': study.best_value,
        'n_trials': n_trials
    }
```

### Task 3.3: Add LightGBM Alternative

```python
def train_lightgbm(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Train LightGBM as alternative to XGBoost."""
    import lightgbm as lgb

    X = np.array([d['features'] for d in training_data])
    y = np.array([d['outcome'] for d in training_data])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = lgb.LGBMRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        verbose=-1
    )
    model.fit(X_train, y_train)

    # Compare with XGBoost
    lgb_score = model.score(X_test, y_test)
    xgb_score = self.model.score(X_test, y_test) if self.model else 0

    return {
        'lightgbm_r2': lgb_score,
        'xgboost_r2': xgb_score,
        'winner': 'lightgbm' if lgb_score > xgb_score else 'xgboost'
    }
```

### Task 3.4: Add Confidence Calibration

```python
def calibrate_confidence(self, validation_data: List[Dict]) -> None:
    """Calibrate confidence scores using isotonic regression."""
    from sklearn.isotonic import IsotonicRegression

    # Get predictions and actual outcomes
    predictions = []
    actuals = []

    for item in validation_data:
        result = self.score_opportunity_raw(item['spider_data'])
        predictions.append(result.confidence / 100.0)
        actuals.append(1.0 if item['outcome'] == 'success' else 0.0)

    # Fit calibration model
    self._calibrator = IsotonicRegression(out_of_bounds='clip')
    self._calibrator.fit(predictions, actuals)

    logger.info("Confidence calibration complete")
```

---

## Phase 4: Advanced Improvements (Multi-day)

**Session Target:** 674+

### Task 4.1: Ensemble Methods (Stacking)

```python
def create_stacking_ensemble(self, training_data: List[Dict]) -> Dict[str, Any]:
    """Create stacking ensemble of multiple models."""
    from sklearn.ensemble import StackingRegressor, RandomForestRegressor
    from sklearn.linear_model import Ridge

    base_models = [
        ('xgb', xgb.XGBRegressor(n_estimators=100, max_depth=5)),
        ('lgb', lgb.LGBMRegressor(n_estimators=100, max_depth=5)),
        ('rf', RandomForestRegressor(n_estimators=100, max_depth=5)),
    ]

    stacking = StackingRegressor(
        estimators=base_models,
        final_estimator=Ridge(),
        cv=5
    )

    X = np.array([d['features'] for d in training_data])
    y = np.array([d['outcome'] for d in training_data])

    stacking.fit(X, y)
    self._ensemble_model = stacking

    return {'ensemble_type': 'stacking', 'base_models': 3}
```

### Task 4.2: Online Learning

```python
def update_model_incrementally(self, new_outcome: 'OpportunityOutcome') -> bool:
    """Update model with new outcome data (online learning)."""
    try:
        # Extract features from the opportunity
        spider_data = new_outcome.opportunity.spider_data
        features = self.extract_features(spider_data)
        outcome_score = self._outcome_to_score(new_outcome.outcome_type)

        # Partial fit (for supported models)
        if hasattr(self.model, 'partial_fit'):
            self.model.partial_fit(features, [outcome_score])
            return True

        # For XGBoost, add to training buffer and retrain periodically
        self._training_buffer.append({
            'features': features[0].tolist(),
            'outcome': outcome_score
        })

        if len(self._training_buffer) >= 50:  # Retrain every 50 new samples
            self._retrain_with_buffer()

        return True
    except Exception as e:
        logger.error(f"Incremental update error: {e}")
        return False
```

### Task 4.3: A/B Testing Framework

```python
class MLModelABTest:
    """A/B testing framework for ML model comparison."""

    def __init__(self, model_a: str, model_b: str, split_ratio: float = 0.5):
        self.model_a_version = model_a
        self.model_b_version = model_b
        self.split_ratio = split_ratio
        self.results_a = []
        self.results_b = []

    def assign_variant(self, opportunity_id: str) -> str:
        """Deterministic assignment based on ID hash."""
        import hashlib
        hash_val = int(hashlib.md5(opportunity_id.encode()).hexdigest(), 16)
        return 'A' if (hash_val % 100) < (self.split_ratio * 100) else 'B'

    def record_outcome(self, opportunity_id: str, predicted_score: float, actual_outcome: float):
        """Record outcome for analysis."""
        variant = self.assign_variant(opportunity_id)
        result = {'predicted': predicted_score, 'actual': actual_outcome}

        if variant == 'A':
            self.results_a.append(result)
        else:
            self.results_b.append(result)

    def get_statistics(self) -> Dict[str, Any]:
        """Calculate A/B test statistics."""
        from scipy import stats

        if len(self.results_a) < 30 or len(self.results_b) < 30:
            return {'status': 'insufficient_data'}

        errors_a = [abs(r['predicted'] - r['actual']) for r in self.results_a]
        errors_b = [abs(r['predicted'] - r['actual']) for r in self.results_b]

        t_stat, p_value = stats.ttest_ind(errors_a, errors_b)

        return {
            'model_a': {'mean_error': np.mean(errors_a), 'n': len(errors_a)},
            'model_b': {'mean_error': np.mean(errors_b), 'n': len(errors_b)},
            'p_value': p_value,
            'significant': p_value < 0.05,
            'winner': 'A' if np.mean(errors_a) < np.mean(errors_b) else 'B'
        }
```

### Task 4.4: Model Drift Detection

```python
def detect_model_drift(self, window_days: int = 7) -> Dict[str, Any]:
    """Detect if model performance is degrading (drift)."""
    from django.utils import timezone
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(days=window_days)

    recent_outcomes = OpportunityOutcome.objects.filter(
        recorded_at__gte=cutoff
    ).select_related('opportunity__spider_data')

    errors = []
    for outcome in recent_outcomes:
        if not outcome.opportunity.spider_data:
            continue

        # Get what we predicted vs actual
        result = self.score_opportunity(outcome.opportunity.spider_data)
        predicted = result.hybrid_score / 100.0
        actual = self._outcome_to_score(outcome.outcome_type)
        errors.append(abs(predicted - actual))

    if len(errors) < 10:
        return {'status': 'insufficient_data'}

    recent_mae = np.mean(errors)

    # Compare to historical baseline
    if hasattr(self, '_baseline_mae'):
        drift_ratio = recent_mae / self._baseline_mae
        return {
            'recent_mae': recent_mae,
            'baseline_mae': self._baseline_mae,
            'drift_ratio': drift_ratio,
            'drift_detected': drift_ratio > 1.2,  # 20% degradation threshold
            'recommendation': 'retrain' if drift_ratio > 1.2 else 'monitor'
        }

    return {'recent_mae': recent_mae, 'status': 'no_baseline'}
```

---

## Testing & Validation

### Unit Tests to Add

```python
# tests/test_ml_scoring_engine.py

def test_feature_extraction():
    """Test that all features are extracted correctly."""
    engine = get_ml_scoring_engine()
    spider_data = create_test_spider_data(title="AI startup raises $10M")

    features = engine.extract_features(spider_data)

    assert features.shape == (1, len(FEATURE_NAMES))
    assert features[0, FEATURE_NAMES.index('keyword_ai')] == 1.0  # Should detect "AI"
    assert features[0, FEATURE_NAMES.index('has_numbers')] == 1.0  # Should detect "$10M"

def test_historical_success_rate_queries_db():
    """Test that success rate uses actual data, not hardcoded values."""
    engine = get_ml_scoring_engine()

    # Create test outcomes
    create_test_outcomes('hackernews', successes=8, failures=2)

    rate = engine._get_historical_success_rate('hackernews')

    # Should be ~0.8, not hardcoded 0.55
    assert 0.7 < rate < 0.9

def test_shap_explanation_has_correct_features():
    """Test SHAP explanation includes all features."""
    engine = get_ml_scoring_engine()
    spider_data = create_test_spider_data()

    result = engine.score_opportunity(spider_data)

    assert result.shap_explanation is not None
    assert len(result.shap_explanation.feature_names) == len(FEATURE_NAMES)
    assert len(result.shap_explanation.shap_values) == len(FEATURE_NAMES)
```

### Integration Test

```bash
# Run after each phase
.venv/bin/python manage.py shell << 'EOF'
from core.services.ml_scoring_engine import get_ml_scoring_engine
from core.models_unified_system import SpiderData

engine = get_ml_scoring_engine()

# Test on recent spider data
recent = SpiderData.objects.order_by('-created_at')[:10]
for sd in recent:
    result = engine.score_opportunity(sd)
    print(f"{sd.spider_name}: hybrid={result.hybrid_score:.1f}, confidence={result.confidence:.1f}")
    if result.shap_explanation:
        top = result.shap_explanation.get_top_features(3)
        for f in top:
            print(f"  - {f['feature']}: {f['shap_value']:+.3f} ({f['impact']})")
EOF
```

---

## Success Metrics

| Metric | Current | Phase 1 Target | Phase 3 Target |
|--------|---------|----------------|----------------|
| Working Features | 8/15 (53%) | 15/15 (100%) | 24/24 (100%) |
| Training Samples | 150 | 150 | 500+ |
| Test R² | Unknown | 0.40+ | 0.60+ |
| CV Score (5-fold) | N/A | 0.35+ | 0.55+ |
| Dead Features | 7 | 0 | 0 |
| Feature Importance Spread | Top 3 = 55% | More even | Top 5 = 60% |

---

## Dependencies to Add

```bash
# requirements.txt additions for Phase 3+
optuna>=3.0.0          # Hyperparameter tuning
lightgbm>=4.0.0        # Alternative model
scipy>=1.10.0          # Statistical tests (already have)
```

---

## Session Checklist

### Session 669: Phase 1 - Quick Wins
- [ ] Fix `_get_historical_success_rate()` to query actual data
- [ ] Run keyword prevalence diagnosis
- [ ] Expand keyword sets
- [ ] Add validation logging
- [ ] Test all fixes
- [ ] Retrain model v5.0

### Session 670-671: Phase 2 - Feature Engineering
- [ ] Add embedding similarity feature
- [ ] Add temporal features (4)
- [ ] Add text quality features (5)
- [ ] Update FEATURE_NAMES list
- [ ] Test feature extraction
- [ ] Retrain model v6.0

### Session 672-673: Phase 3 - Model Improvements
- [ ] Implement k-fold cross-validation
- [ ] Add Optuna hyperparameter tuning
- [ ] Test LightGBM alternative
- [ ] Add confidence calibration
- [ ] Compare models, select best
- [ ] Retrain final model v7.0

### Session 674+: Phase 4 - Advanced
- [ ] Implement stacking ensemble
- [ ] Add online learning capability
- [ ] Build A/B testing framework
- [ ] Add drift detection
- [ ] Set up monitoring dashboard

---

## Related Files

| File | Purpose |
|------|---------|
| `core/services/ml_scoring_engine.py` | Main engine (modify) |
| `core/tasks.py` | Training tasks (modify) |
| `core/models_unified_system.py` | MLModelVersion model |
| `core/ml_models/` | Saved model files |
| `core/services/scoring_dispatcher.py` | Uses ML engine |
| `core/agents/analysis/opportunity_scoring_agent.py` | Uses scores |

---

**Next Session:** Start with Phase 1 Quick Wins - fix the historical success rate and dead features issues for immediate accuracy improvement.
