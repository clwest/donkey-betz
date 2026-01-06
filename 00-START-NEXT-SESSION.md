# Session 671 - Start Here

**Previous Session:** 670 (ML Scoring Engine Phase 2 - COMPLETE)
**Date:** January 5, 2026
**Focus:** Continue ML Improvements or New Priorities
**Status:** 100% Reality Score | ML Engine v7.1 (LightGBM) with 24 Features

---

## Session 670 Summary: ML Phase 2 - COMPLETE

### Part 1: Feature Engineering (24 Features)

1. **Embedding Similarity Feature** - `_get_embedding_similarity()`
   - Compares spider content to historically successful opportunities
   - Uses cosine similarity with 2-hour cache

2. **Temporal Features (4)** - hour_of_day, day_of_week, is_weekend, is_business_hours

3. **Text Quality Features (4)** - description_length, title_word_count, has_numbers, has_question

### Part 2: LightGBM + Optuna Optimization

Added alternative model backend and automatic hyperparameter tuning:

**New Capabilities:**
- `MODEL_TYPE_LIGHTGBM` and `MODEL_TYPE_XGBOOST` constants
- `optimize_hyperparameters()` - Bayesian search with Optuna (50 trials, 5-fold CV)
- `train_model_with_optimization()` - Full pipeline with auto-tuning
- LightGBM is now the default model backend

**Model Performance Comparison:**

| Version | Model | Test R² | Improvement |
|---------|-------|---------|-------------|
| v6.0 | XGBoost (default params) | 0.3158 | Baseline |
| v7.0 | XGBoost + Optuna | 0.5383 | +70% |
| **v7.1** | **LightGBM + Optuna** | **0.6276** | **+99%** ✓ |

**v7.1 is now the active model.**

---

## System Stats (Current)

| Component | Count | Status |
|-----------|-------|--------|
| **Agents** | 72 | 69 routable + 3 entry/special |
| **Spiders** | 77 | 72 working, 5 need API keys |
| **Services** | 93 | All healthy |
| **ML Model** | v7.1 | LightGBM + Optuna, 24 features |

---

## Session 671 Priorities

### Option A: ML Phase 3 - Spider-Specific Features

From the roadmap in `docs/handoffs/SESSION_668_ML_SCORING_ENGINE_IMPROVEMENTS.md`:

```python
# Category-specific features
'financial_market_cap',      # Financial spider specific
'financial_price_change',
'tech_github_stars',
'jobs_salary_min',
'jobs_remote_flag',

# Engagement features
'has_comments',
'comment_count',
'has_likes',
'engagement_score',
```

### Option B: ML Phase 4 - A/B Testing Framework

Set up randomized scoring strategy testing to measure real-world impact.

### Option C: New System Priorities

Check if there are other system priorities that take precedence over ML improvements.

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| `docs/handoffs/SESSION_668_ML_SCORING_ENGINE_IMPROVEMENTS.md` | Full ML roadmap with code examples |
| `docs/current/SYSTEM_INTEGRATION_GUIDE.md` | System integration guide |

---

## Quick Start

```bash
# 1. Start platform
make start
make celery

# 2. Verify ML engine v7.1 (LightGBM)
.venv/bin/python manage.py shell -c "
from core.services.ml_scoring_engine import MLScoringEngine, FEATURE_NAMES
engine = MLScoringEngine()
print(f'ML Model: {engine.model_version}')
print(f'Model Type: {engine.model_type}')
print(f'Features: {len(FEATURE_NAMES)}')
"

# 3. Test scoring with SHAP explanation
.venv/bin/python manage.py shell -c "
from core.services.ml_scoring_engine import MLScoringEngine
from core.models_unified_system import SpiderData

engine = MLScoringEngine()
sd = SpiderData.objects.order_by('-created_at').first()
result = engine.score_opportunity(sd)
print(f'Hybrid Score: {result.hybrid_score:.1f}')
print(f'Confidence: {result.confidence:.1f}')
print(f'Top factors: {[f[\"feature\"] for f in result.shap_explanation.get_top_features(3)]}')
"

# 4. Train new model with Optuna optimization (optional)
.venv/bin/python manage.py shell -c "
from core.services.ml_scoring_engine import MLScoringEngine, MODEL_TYPE_LIGHTGBM
engine = MLScoringEngine(model_type=MODEL_TYPE_LIGHTGBM)
result = engine.train_model_with_optimization(
    training_data,  # Your training data
    version='v8.0',
    n_trials=50,
    cv_folds=5
)
print(f'Best CV Score: {result[\"optimization\"][\"best_cv_score\"]:.4f}')
"
```

---

## ML Feature Progression

| Version | Features | Model | Test R² | Notes |
|---------|----------|-------|---------|-------|
| v4.0 | 15 | XGBoost | - | 47% dead features |
| v5.0 | 15 | XGBoost | - | Fixed text extraction |
| v6.0 | 24 | XGBoost | 0.3158 | +embedding, temporal, text quality |
| v7.0 | 24 | XGBoost + Optuna | 0.5383 | +70% improvement |
| **v7.1** | 24 | **LightGBM + Optuna** | **0.6276** | **+99% improvement** |

---

## Commits from Session 670

```
b6ce58c4 feat(Session 670): Add LightGBM + Optuna hyperparameter optimization
bd4b6bba feat(Session 670): ML Scoring Engine Phase 2 - 24 features + v6.0 model
```

---

*Ready for Session 671!*
