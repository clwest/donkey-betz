# Session 601: Weighted Learning Formula (ChatGPT Recommendation)

**Date:** December 29, 2025
**Previous Session:** 600 (Complete Learning Loop)
**Focus:** Implement ChatGPT's weighted learning model

---

## Executive Summary

Implemented ChatGPT's sophisticated learning weight formula:

```
learning_weight = outcome_signal × confidence_weight × decay_weight
```

This replaces simple static weights with an evidence-based learning system that:
- Rewards confidence (more data = more weight)
- Prevents permanent bias (decay over time)
- Distinguishes safety FAILs from execution FAILs
- Preserves innovation while respecting risk

---

## The Formula Components

### 1. Outcome Signal (Base Value)

| Outcome | Signal | Rationale |
|---------|--------|-----------|
| PASS | +1.0 | Success - positive signal |
| LEARN | +0.3 | Informative - weak positive |
| FAIL (safety/trust) | -1.0 | Strong negative - avoid |
| FAIL (execution/quality) | -0.5 | Informative, not fatal |

**Safety FAIL Classification (v1.1 - Strong/Weak System):**

| Keyword Type | Examples | Rule |
|--------------|----------|------|
| **Strong** | kill_switch, harmful, security, integrity_anomaly, data_breach | Single hit = safety FAIL |
| **Weak** | privacy, bias, trust, anomaly, safety | Need 2+ weak hits to classify |

This prevents false positives from neutral mentions of "privacy" etc.

### 2. Confidence Weight (Sample-Based)

```python
confidence_weight = min(1.0, log10(sample_size + 1))
```

| Samples | Confidence |
|---------|------------|
| 9+ | 1.0 (full) [log10(10) = 1.0] |
| 5 | ~0.78 |
| 3 | ~0.60 |
| 1 | ~0.30 |

This prevents knee-jerk learning from small samples.

### 3. Decay Weight (Time-Based)

```python
decay_weight = e^(-age_in_days / 21)
```

| Age (days) | Weight |
|------------|--------|
| 0 | 1.0 |
| 7 | ~0.72 |
| 21 | ~0.37 |
| 42 | ~0.14 |

Recent outcomes matter more. Old failures don't haunt the system forever.

### 4. Insufficient Evidence Flag (v1.1 - Novelty Penalty)

When a theme has very few samples, even PASS outcomes can be misleading.

```python
insufficient_evidence = sample_size < 3
evidence_status = 'promising' if insufficient_evidence else 'proven'
```

| Samples | Status | ThinkingAgent Guidance |
|---------|--------|------------------------|
| < 3 | `promising` | "Treat as promising, not proven" |
| ≥ 3 | `proven` | "Treat as reliable signal" |

This prevents premature conclusions from early spikes.

---

## New Service: WeightedLearningService

`core/services/weighted_learning.py`

### Key Methods

| Method | Purpose |
|--------|---------|
| `calculate_learning_weight()` | Calculate weight for single outcome |
| `aggregate_theme_scores()` | Cumulative weighted score for a theme |
| `check_permanent_ban_eligible()` | Guardrail for permanent bans |
| `get_weighted_learnings_for_thinking_agent()` | All weighted data for ThinkingAgent |

### Aggregation Features

For each theme/topic, calculates:
- **cumulative_score**: Sum of all weighted outcomes
- **confidence_interval**: high/medium/low/insufficient
- **trend_direction**: positive/negative/stable/stale
- **recommendation**: Strategic reasoning based on data

Example recommendations:
- "High variance, insufficient data → keep exploring with small pilots"
- "Consistent negative safety signal → gate harder, require review"
- "Positive momentum → propose scaled pilot, increase investment"

---

## Guardrail: Permanent Bans

No idea can be permanently banned unless:
- ≥2 independent safety FAILs
- across ≥2 pilots
- with confidence_weight ≥0.8

Everything else remains conditionally revisitable. This preserves innovation.

---

## ThinkingAgent Integration

### Context Enhancement

ThinkingAgent now receives weighted learnings in format:

```
🟢 **Experiment: Content Strategy Test** [PASS]
   Weight: 0.650 = 1.0 × 0.778 × 0.836
   Signal: pass, Age: 5d, Samples: 5
   Insight: High engagement with short-form content

🔴 **Experiment: Bias Detection Pilot** [FAIL]
   Weight: -0.420 = -1.0 × 0.602 × 0.698
   Signal: fail_safety, Age: 10d, Samples: 3
   Insight: User trust dropped below threshold
```

### Aggregate Learning Health

```
**Aggregate Learning Health:** POSITIVE
- Net Weight: +0.850
- Positive: +1.200, Negative: -0.350
```

### Strategic Reasoning Guidance

ThinkingAgent is instructed to:
- Interpret weighted scores as evidence, not absolute truth
- High positive weight (>0.5) → proven success, scale up
- High negative weight (<-0.5) with confidence → gate harder
- Low confidence (few samples) → keep exploring
- Decayed outcomes (old) → may need fresh validation

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `core/services/weighted_learning.py` | ~450 | Complete weighted learning system |

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/thinking_agent.py` | +40 lines - weighted learning context & prompt formatting |

---

## Example Calculations

### PASS with Good Confidence
```
Outcome: PASS, Samples: 8, Age: 3 days
outcome_signal = 1.0
confidence_weight = min(1.0, log10(9)) = 0.954
decay_weight = e^(-3/21) = 0.867
learning_weight = 1.0 × 0.954 × 0.867 = 0.827
```

### Safety FAIL with Limited Data
```
Outcome: FAIL (safety), Samples: 2, Age: 10 days
outcome_signal = -1.0
confidence_weight = min(1.0, log10(3)) = 0.477
decay_weight = e^(-10/21) = 0.621
learning_weight = -1.0 × 0.477 × 0.621 = -0.296
```

Even a safety failure has limited impact with only 2 samples (confidence = 0.477).

---

## Test Commands

```bash
# Test weighted learning calculation
.venv/bin/python manage.py shell -c "
from core.services.weighted_learning import WeightedLearningService

# Test PASS outcome
print(WeightedLearningService.calculate_learning_weight('pass', sample_size=5, age_days=7))

# Test safety FAIL
print(WeightedLearningService.calculate_learning_weight('fail', 'user trust dropped', sample_size=3, age_days=14))

# Test execution FAIL
print(WeightedLearningService.calculate_learning_weight('fail', 'error rate exceeded', sample_size=10, age_days=3))
"

# Test full weighted learnings
.venv/bin/python manage.py shell -c "
from core.services.weighted_learning import get_weighted_learnings_for_thinking_agent
print(get_weighted_learnings_for_thinking_agent())
"
```

---

## Why This Works

ChatGPT's model matches your system because:

| Principle | Implementation |
|-----------|----------------|
| Momentum over magnitude | Decay weight rewards recent signals |
| Governance-first | Safety FAILs get -1.0 signal (strongest) |
| Explainability | Full weight breakdown shown |
| Avoid narrative drift | Confidence prevents over-learning from noise |
| Preserve innovation | Guardrail prevents permanent bans |

---

## Session 602 Options

### Option A: Integrate with Boardroom
- Use weighted scores in decision prioritization
- Show historical success probability before approval

### Option B: Visualize Learning Momentum
- Dashboard showing weight trends over time
- Theme-level cumulative score charts

### Option C: Auto-Adjust Pilot Parameters
- Use weighted learnings to suggest pilot scope
- Recommend sample size for confidence target

---

**Session 601: Weighted Learning Formula - COMPLETE**
