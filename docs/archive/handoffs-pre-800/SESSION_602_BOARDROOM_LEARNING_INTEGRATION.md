# Session 602: Boardroom Learning Integration

**Date:** December 29, 2025
**Previous Session:** 601 (Weighted Learning Formula)
**Focus:** Integrate weighted learning with Boardroom decisions

---

## Executive Summary

Connected the weighted learning system (Session 601) to the Boardroom decision-making UI. Decision-makers can now see:

- **Success Probability**: Historical likelihood based on similar past experiments
- **Risk Level**: Based on safety failures in similar decisions
- **AI Recommendation**: approve/pilot_first/defer/gate based on evidence
- **Similar Experiments**: Past experiments that inform this decision
- **Weighted Insights**: Key learnings with their weights

This closes the governance-learning loop:
```
Experiments generate learnings →
Learnings inform Boardroom decisions →
Decisions become policies/pilots →
Pilots generate new experiments
```

---

## New Components

### BoardroomLearningService

`core/services/boardroom_learning.py` (~350 lines)

| Method | Purpose |
|--------|---------|
| `get_decision_learning_context()` | Full learning context for a decision |
| `_find_similar_experiments()` | Find experiments related to decision themes |
| `_calculate_success_probability()` | Weighted success probability |
| `_calculate_risk_level()` | Risk assessment from safety failures |
| `_generate_recommendation()` | AI-generated guidance |
| `enrich_decisions_list()` | Light-weight summary for list views |

### Recommendation Actions

| Action | Criteria |
|--------|----------|
| `approve` | ≥70% success probability, high/medium confidence |
| `approve_with_monitoring` | ≥50% probability, low risk |
| `pilot_first` | Insufficient historical data |
| `defer` | Low probability or elevated risk |
| `gate` | High/critical risk with confidence |

---

## New API Endpoints

### Get Decision Learning Context

```
GET /api/boardroom/decisions/{decision_id}/learning/
```

Returns:
- `success_probability`: 0-100%
- `risk_level`: minimal/low/medium/high/critical
- `confidence_level`: high/medium/low/insufficient
- `similar_experiments`: List of related experiments with weights
- `weighted_insights`: Key learnings from experiments
- `recommendation`: Action + reasoning

### Get Boardroom Learning Summary

```
GET /api/boardroom/learning-summary/?status=draft&limit=10
```

Returns summary of pending decisions with learning metrics.

---

## UI Enhancements

### Learning Insight Button

Every Boardroom decision card now has a "📊 Learning Insight" button that opens a modal showing:

1. **Key Metrics Row**
   - Success Probability (color-coded: green ≥70%, yellow ≥50%, red <50%)
   - Risk Level (minimal → critical)
   - Recommendation icon

2. **AI Recommendation Box**
   - Action recommendation with reasoning
   - Confidence note

3. **Similar Experiments List**
   - Past experiments with relevance scores
   - Outcome badges (🟢 PASS / 🟡 LEARN / 🔴 FAIL)
   - Weighted learning values
   - Key insights from each

4. **Weighted Insights**
   - Top 5 learnings from similar experiments

---

## How It Works

### Theme Matching

The service builds search terms from:
1. Decision topic words
2. Decision type themes (policy → governance, rule, guideline)
3. Impact area themes (security → security, privacy, safety, trust)
4. Key insight words

These terms are matched against experiment names and hypotheses.

### Success Probability Calculation

```python
total_positive = sum(positive weighted learning scores)
total_negative = sum(|negative weighted learning scores|)
probability = (total_positive / (total_positive + total_negative)) * 100
```

### Risk Assessment

Safety failures (using Session 601's strong/weak keywords) contribute to risk:
- Risk score = sum of |negative safety weights|
- critical: risk_score ≥ 1.5
- high: risk_score ≥ 0.8
- medium: risk_score ≥ 0.3
- low: risk_score > 0
- minimal: risk_score = 0

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `core/services/boardroom_learning.py` | ~350 | Learning integration service |

## Files Modified

| File | Changes |
|------|---------|
| `core/views_agent_learning.py` | +2 endpoints (~100 lines) |
| `core/urls.py` | +2 imports, +2 URL routes |
| `ai_core/templates/ai_image_studio.html` | +1 modal, +2 JS functions (~180 lines) |

---

## Example Output

For a decision about "AI-powered content recommendations":

```json
{
  "success_probability": 72,
  "risk_level": "low",
  "confidence_level": "medium",
  "similar_experiments": 6,
  "recommendation": {
    "action": "approve",
    "reasoning": "High success probability (72%) based on medium confidence data. Similar decisions have performed well."
  }
}
```

---

## The Complete Learning-Governance Loop

```
Session 590-600: Learning Loop Infrastructure
        ↓
Session 601: Weighted Learning Formula
        ↓
Session 602: Boardroom Integration ← COMPLETE!
        ↓
Decision-makers now see:
- Historical success probability before approving
- Risk assessment from past failures
- AI-generated recommendations
- Evidence-based confidence levels
```

---

## Session 603 Options

### Option A: Auto-Prioritize Decision Queue
- Sort pending decisions by success probability
- Surface high-probability, low-risk decisions first
- Flag high-risk decisions for additional review

### Option B: Learning Velocity Dashboard
- Track how fast the system learns
- Visualize learning momentum over time
- Show which themes are improving/declining

### Option C: Experiment Suggestion Engine
- Based on learning gaps, suggest new experiments
- Identify themes with insufficient data
- Recommend sample sizes for confidence targets

---

**Session 602: Boardroom Learning Integration - COMPLETE**
