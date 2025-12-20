# Session 511: ML Scoring Sub-Tab Enhancement

**Date:** December 19, 2025
**Status:** COMPLETE
**Focus:** Enhanced ML Scoring UI with 5 new features

---

## Summary

Enhanced the ML Scoring sub-tab (Autonomous → ML Scoring) with comprehensive visualization and control features. Added model training status, feature importance charts, score explanation modals, performance trends, and model comparison tables.

---

## What Was Built

### 1. Model Training Status Panel
- Shows last trained date and training sample count
- Progress bar showing samples collected vs 100 required minimum
- **"Train Now" button** - triggers manual model training via Celery
- Displays active model version and training duration

### 2. Feature Importance Visualization
- Horizontal bar chart showing top 10 ML features
- Uses Chart.js with purple/violet theme
- Features displayed in human-readable format (snake_case → Title Case)
- Shows importance scores 0-100

### 3. Score Explanation Modal
- Popup modal showing why an opportunity scored high
- SHAP breakdown: positive factors (green) and negative factors (red)
- Shows hybrid score breakdown (60% ML + 40% rule-based)
- Rule reasoning list with icons
- Confidence percentage

### 4. Performance Trends Chart
- Line chart showing model accuracy (R²) over versions
- Dual Y-axis: R² score (left) and training samples (right)
- Tracks model improvement over time

### 5. Model Comparison Table
- Side-by-side comparison of all model versions
- Shows: Version, Trained Date, R² Score, MSE, Samples, Status
- Active version highlighted
- Only shown when multiple versions exist

---

## Files Modified

### Backend

**core/views_autonomous_monitoring.py**
- Enhanced `api_ml_scoring_status()` (lines 657-838):
  - Added `model_training` object with training metadata
  - Added `feature_importance` array (top 10 features)
  - Added `performance_trends` array (all model versions)
  - Added `model_comparison` object
  - Enhanced `recent_high_score` with SHAP explanations

- Added `api_ml_scoring_train()` (lines 845-894):
  - POST endpoint to trigger manual model training
  - Validates minimum 100 samples required
  - Returns task_id for tracking

- Added `api_ml_scoring_explanation()` (lines 901-977):
  - GET endpoint for individual opportunity SHAP breakdown
  - Returns positive/negative factors and rule reasoning

**core/urls.py**
- Added 2 new URL patterns:
  - `api/monitoring/ml-scoring/train/`
  - `api/monitoring/ml-scoring/opportunity/<uuid>/explanation/`

### Frontend

**ai_core/templates/components/panels/autonomous_dashboard_panel.html**

HTML additions:
- Model Training Status panel (lines 395-408)
- Feature Importance chart canvas (lines 414-424)
- Performance Trends chart canvas (lines 426-436)
- Model Comparison table container (lines 493-505)
- Score Explanation modal (lines 534-555)

JavaScript additions:
- `renderMLTrainingStatus(training)` - Training panel with progress bar
- `renderFeatureImportanceChart(features)` - Chart.js horizontal bar
- `renderPerformanceTrendsChart(trends)` - Chart.js dual-axis line chart
- `renderModelComparison(comparison)` - Version comparison table
- `triggerMLTraining()` - POST to train endpoint with spinner
- `showScoreExplanation(opportunityId)` - Load explanation modal
- `renderScoreExplanationModal(data)` - Populate modal with SHAP data
- `renderSHAPFactors(factors, color)` - Bar visualization helper
- `formatFeatureName(name)` - snake_case to Title Case
- Enhanced `renderMLHighScore()` - Added "View Why" button per item
- Enhanced `loadMLScoring()` - Calls new render functions

---

## API Responses

### Enhanced /api/monitoring/ml-scoring/
```json
{
  "success": true,
  "data": {
    "model_training": {
      "last_trained": "2025-12-19T10:30:00Z",
      "training_samples": 150,
      "training_duration_seconds": 45.3,
      "min_samples_required": 100,
      "can_train_now": true,
      "active_version": "v3.0"
    },
    "feature_importance": [
      {"feature": "source_credibility", "importance": 0.23},
      {"feature": "recency_hours", "importance": 0.18}
    ],
    "performance_trends": [
      {"version": "v1.0", "trained_at": "...", "test_r2": 0.72, "test_mse": 145.3, "training_samples": 100}
    ],
    "model_comparison": {
      "versions_count": 3,
      "active_version": "v3.0",
      "versions": [...]
    },
    "recent_high_score": [{
      "id": "uuid",
      "title": "...",
      "explanation": {
        "top_positive": [...],
        "top_negative": [...],
        "confidence": 82.5
      }
    }]
  }
}
```

### POST /api/monitoring/ml-scoring/train/
```json
{"success": true, "task_id": "abc123", "message": "Training queued"}
```

### GET /api/monitoring/ml-scoring/opportunity/<uuid>/explanation/
```json
{
  "success": true,
  "data": {
    "opportunity_id": "uuid",
    "scores": {"ml_score": 75, "rule_score": 68, "hybrid_score": 72.2},
    "shap_values": [...],
    "positive_factors": [...],
    "negative_factors": [...],
    "rule_reasoning": [...]
  }
}
```

---

## Edge Cases Handled

| Scenario | Behavior |
|----------|----------|
| No trained model | Shows "No model trained yet", Train Now disabled if <100 samples |
| <100 training samples | Progress bar shows X/100, Train Now disabled |
| No ScoringExplanation | Modal shows "No explanation available" |
| Single model version | Model comparison section hidden |
| No feature importance | Chart shows "No data available" message |
| Training in progress | Button shows spinner, disabled |
| API errors | Toast notification, graceful fallback |

---

## Testing Verified

1. **Main API** (`/api/monitoring/ml-scoring/`):
   - Returns all new fields correctly
   - Gracefully handles no trained model scenario

2. **Train API** (`/api/monitoring/ml-scoring/train/`):
   - Correctly validates minimum 100 samples
   - Returns appropriate error when insufficient data

3. **Explanation API** (`/api/monitoring/ml-scoring/opportunity/<uuid>/explanation/`):
   - Returns 404-style error when no explanation exists
   - Ready to return full SHAP data when available

4. **Frontend**:
   - All 5 new JavaScript functions present
   - HTML elements properly structured
   - Chart.js canvases ready for rendering

---

## Dependencies

- Chart.js 4.4.1 (already loaded via CDN)
- XGBoost (backend ML)
- SHAP (explainability)
- Celery (async training)

---

## Next Steps (Session 512+)

1. Generate training data (100+ OpportunityOutcome records)
2. Train first ML model to see full visualization
3. Add training progress WebSocket for real-time updates
4. Add model rollback functionality
5. Add A/B testing between model versions

---

## Code Quality

- No new dependencies added
- Follows existing code patterns
- Proper error handling throughout
- Responsive design (mobile-friendly)
- Chart colors match existing theme (amber/green/purple)
