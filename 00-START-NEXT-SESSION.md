# Session 669 - Start Here

**Previous Sessions:** 667 (Docs Review) + 668 (ML Scoring Engine Assessment)
**Date:** January 5, 2026
**Focus:** ML Scoring Engine Improvements - Phase 1
**Status:** 100% Reality Score | ML Engine needs optimization

---

## Session 668 Summary: ML Scoring Engine Assessment

**Key Finding:** 47% of ML features are DEAD (0% importance)

### Critical Issues Identified

1. **7 Dead Features** - Contributing nothing to predictions:
   - `relevance_score`, `title_length`, `has_url`
   - `keyword_ai`, `keyword_trending`, `keyword_urgent`, `keyword_opportunity`

2. **Hardcoded Success Rates** - `historical_success_rate` (22% importance) uses static values instead of actual outcome data

3. **Sparse Training Data** - Only 150 samples (need 500+)

### ML Engine Stats

| Metric | Current | Target |
|--------|---------|--------|
| Model Version | v4.0 | v7.0 (after Phase 3) |
| Working Features | 8/15 (53%) | 24/24 (100%) |
| Training Samples | 150 | 500+ |
| Dead Features | 7 | 0 |

### Improvement Roadmap Created

Full details: `docs/handoffs/SESSION_668_ML_SCORING_ENGINE_IMPROVEMENTS.md`

| Phase | Focus | Sessions |
|-------|-------|----------|
| **1 - Quick Wins** | Fix hardcoded rates, dead features | 669-670 |
| **2 - Features** | Add 9 new features (embeddings, temporal) | 670-671 |
| **3 - Model** | K-fold CV, hyperparameter tuning | 672-673 |
| **4 - Advanced** | Ensemble, online learning, A/B testing | 674+ |

---

## System Stats (Current)

| Component | Count | Status |
|-----------|-------|--------|
| **Agents** | 72 | 69 routable + 3 entry/special |
| **Spiders** | 77 | 72 working, 5 need API keys |
| **Services** | 93 | All healthy |
| **PA Tools** | 77 | 5.73% endpoint coverage |
| **Celery Tasks** | 127 | 49+ scheduled |
| **Discord Commands** | 112 | 29 cogs |
| **ML Model** | v4.0 | 53% feature efficiency |

---

## Quick Start

```bash
# 1. Start platform
make start
make celery

# 2. Access AI Studio
open http://localhost:8000/ai-studio/

# 3. Verify ML engine status
.venv/bin/python manage.py shell -c "
from core.services.ml_scoring_engine import get_ml_scoring_engine
engine = get_ml_scoring_engine()
print(f'ML Model: v{engine.model_version}')
print(f'Trained: {engine._is_trained}')
"
```

---

## Session 669 Priorities: ML Phase 1 - Quick Wins

### P0 - Fix Historical Success Rate (HIGH IMPACT)

**File:** `core/services/ml_scoring_engine.py` lines 339-352

**Task:** Replace hardcoded `_get_historical_success_rate()` with actual DB query

```python
# Current (WRONG): Returns static 0.55 for hackernews
# Fixed: Query OpportunityOutcome for actual success rate
```

**Test after:**
```bash
.venv/bin/python manage.py shell -c "
from core.services.ml_scoring_engine import get_ml_scoring_engine
engine = get_ml_scoring_engine()
for spider in ['hackernews', 'remoteok', 'techcrunch']:
    rate = engine._get_historical_success_rate(spider)
    print(f'{spider}: {rate:.2f}')
"
```

### P1 - Diagnose Dead Keyword Features

**Run diagnosis:**
```bash
.venv/bin/python manage.py shell << 'EOF'
from core.models_unified_system import SpiderData
from django.utils import timezone
from datetime import timedelta

AI_KEYWORDS = {'ai', 'ml', 'machine learning', 'deep learning', 'gpt', 'llm', 'neural', 'automation'}
TRENDING_KEYWORDS = {'viral', 'trending', 'hot', 'breaking', 'surge', 'boom', 'skyrocket'}

cutoff = timezone.now() - timedelta(days=90)
recent = SpiderData.objects.filter(created_at__gte=cutoff)[:1000]

ai_count = sum(1 for sd in recent if any(kw in (sd.raw_data or {}).get('title', '').lower() for kw in AI_KEYWORDS))
trending_count = sum(1 for sd in recent if any(kw in (sd.raw_data or {}).get('title', '').lower() for kw in TRENDING_KEYWORDS))

print(f"AI keyword prevalence: {ai_count}/1000 = {ai_count/10:.1f}%")
print(f"Trending keyword prevalence: {trending_count}/1000 = {trending_count/10:.1f}%")
EOF
```

**If prevalence is low:** Expand keyword sets (see handoff doc for expanded sets)

### P2 - Add Validation Logging

Add debug logging to `score_opportunity()` to track feature extraction quality.

### P3 - Retrain Model v5.0

After fixes, retrain:
```bash
.venv/bin/python manage.py shell -c "
from core.tasks import train_ml_scoring_model
train_ml_scoring_model.delay(force_retrain=True)
"
```

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| `docs/handoffs/SESSION_668_ML_SCORING_ENGINE_IMPROVEMENTS.md` | **NEW** Full roadmap |
| `docs/current/SYSTEM_INTEGRATION_GUIDE.md` | Complete integration guide |
| `docs/current/LEARNING_SYSTEM.md` | Learning hooks documentation |

---

## Key Files for ML Work

| File | Purpose |
|------|---------|
| `core/services/ml_scoring_engine.py` | **MODIFY** Main ML engine |
| `core/tasks.py` | Training task (`train_ml_scoring_model`) |
| `core/models_unified_system.py` | `OpportunityOutcome`, `MLModelVersion` |
| `core/ml_models/` | Saved model files (v2.0, v3.0, v4.0) |
| `core/services/scoring_dispatcher.py` | Uses ML engine |

---

## Feature Importance Reference (v4.0)

```
WORKING (53%):
  historical_success_rate   22.18%  <- USES HARDCODED VALUES!
  category_creative         17.21%
  category_financial        15.69%
  category_news             12.16%
  data_freshness_hours      11.65%
  category_tech              9.73%
  source_authority           6.48%
  category_jobs              4.91%

DEAD (47%):
  relevance_score            0.00%  <- Should be useful!
  title_length               0.00%
  has_url                    0.00%
  keyword_ai                 0.00%  <- Keywords not matching
  keyword_trending           0.00%
  keyword_urgent             0.00%
  keyword_opportunity        0.00%
```

---

## Success Criteria for Session 669

- [ ] `_get_historical_success_rate()` queries actual OpportunityOutcome data
- [ ] Keyword prevalence diagnosed and sets expanded if needed
- [ ] Validation logging added
- [ ] Model v5.0 trained with fixes
- [ ] At least 10/15 features have non-zero importance

---

*Ready for Session 669 - ML Quick Wins!*
