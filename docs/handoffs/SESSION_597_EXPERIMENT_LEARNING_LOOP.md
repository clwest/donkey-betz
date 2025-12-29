# Session 597: Experiment Learning Loop

**Date:** December 29, 2025
**Previous Session:** 596 (Experiment Tracking Registry)
**Focus:** Capture experiment outcomes and feed learnings back to decision-making

---

## Executive Summary

Implemented a complete learning loop that:
- Auto-creates structured learnings when experiments complete
- Tracks success patterns by decision type
- Feeds learnings into ThinkingAgent context to improve future decisions
- Creates a feedback loop from pilots/experiments back to the decision-making process

Based on ThinkingAgent insight:
> *"Feed learnings back to decision-making, improve future success predictions, track success patterns by decision type"*

---

## Implementation

### 1. New Database Models

Added two models to `core/models_pilot_readiness.py`:

#### ExperimentLearning
Captures structured learnings from completed experiments:

| Field | Type | Description |
|-------|------|-------------|
| `experiment` | OneToOne FK | Link to Experiment |
| `outcome` | CharField | success/failure/partial/inconclusive |
| `what_worked` | TextField | Tactics that contributed to success |
| `what_failed` | TextField | Tactics that didn't work |
| `key_insight` | TextField | Main takeaway from experiment |
| `decision_type` | CharField | Category (content_strategy, market_strategy, etc.) |
| `decision_tags` | JSONField | Tags for pattern matching |
| `target_kpi` | CharField | Expected KPI value |
| `actual_kpi` | CharField | Actual achieved value |
| `kpi_delta_percent` | FloatField | % difference from target |
| `future_recommendation` | TextField | Actionable recommendation |
| `confidence_score` | FloatField | 0-1 confidence in learnings |
| `fed_to_thinking_agent` | BooleanField | Whether this was fed to ThinkingAgent |
| `fed_at` | DateTimeField | When fed to ThinkingAgent |

#### DecisionTypeSuccessPattern
Aggregated success patterns by decision type:

| Field | Type | Description |
|-------|------|-------------|
| `decision_type` | CharField | Unique decision category |
| `total_experiments` | IntegerField | Total experiments of this type |
| `successful_experiments` | IntegerField | Count of successes |
| `failed_experiments` | IntegerField | Count of failures |
| `success_rate` | FloatField | Percentage success (0-100) |
| `avg_kpi_delta_percent` | FloatField | Average KPI performance |
| `common_success_factors` | JSONField | Frequently occurring success factors |
| `common_failure_factors` | JSONField | Frequently occurring failure factors |
| `top_insights` | JSONField | Most impactful insights |

### 2. Auto-Learning Extraction

Modified `complete_experiment()` in `core/views_agent_learning.py`:
- When an experiment is marked complete, automatically creates an ExperimentLearning record
- Extracts decision type from the related Boardroom decision topic
- Calculates KPI delta if target and current values available
- Updates DecisionTypeSuccessPattern aggregations

### 3. ThinkingAgent Integration

Modified `core/agents/thinking_agent.py`:

#### Context Gathering (`gather_context()`)
- Gathers recent ExperimentLearnings (last 10)
- Gathers DecisionTypeSuccessPatterns
- Calculates overall success rate
- Marks learnings as fed to ThinkingAgent

#### Context Formatting (`_format_context_for_thinking()`)
- Displays recent learnings with insights and recommendations
- Shows success patterns by decision type
- Includes guidance on using learnings for future decisions

### 4. Decision Type Classification

The system auto-classifies decisions into types based on topic keywords:
- `content_strategy`: content, video, post, blog
- `market_strategy`: market, price, competitor
- `tech_adoption`: tech, platform, tool, api
- `resource_allocation`: team, hire, resource
- `general`: all others

---

## Files Modified

| File | Changes |
|------|---------|
| `core/models_pilot_readiness.py` | +ExperimentLearning, +DecisionTypeSuccessPattern (~330 lines) |
| `core/views_agent_learning.py` | Updated complete_experiment() for auto-learning extraction |
| `core/agents/thinking_agent.py` | Added experiment learnings to gather_context() and formatting |
| `core/migrations/0132_session_597_experiment_learning.py` | Migration for new models |

---

## API Changes

### Updated: Complete Experiment
`POST /api/experiments/<uuid:experiment_id>/complete/`

New optional fields in request body:
```json
{
    "status": "success|failure|inconclusive",
    "learnings": "What we learned",
    "what_worked": "Specific tactics that worked",
    "what_failed": "Specific tactics that didn't work",
    "recommendation": "Future recommendation"
}
```

New fields in response:
```json
{
    "success": true,
    "learning_created": true,
    "learning_id": "uuid"
}
```

---

## How It Works

### The Learning Loop Flow

```
1. Boardroom Decision Created
        ↓
2. Pilot Readiness Gate Created (Session 590)
        ↓
3. Pilot Started → Experiment Created (Session 596)
        ↓
4. Experiment Running...
        ↓
5. Experiment Completed (success/failure)
        ↓
6. ExperimentLearning Auto-Created (Session 597)
        ↓
7. DecisionTypeSuccessPattern Updated
        ↓
8. ThinkingAgent Reads Learnings
        ↓
9. Future Decisions Informed by Past Outcomes
        ↓
10. Better Decision Quality (the loop closes)
```

### ThinkingAgent Context Example

When ThinkingAgent runs, it now sees:

```markdown
### Experiment Learnings (Past Outcomes)
- Total Learnings: 5
- Success Rate: 60.0%

**Recent Learnings from Completed Experiments:**
- **Experiment: YouTube Tutorial Series** [success]
  - Insight: Educational content outperforms entertainment
  - Recommendation: Focus on actionable tutorials

**Decision Type Success Patterns:**
- content_strategy: 75.0% (4 experiments)
  - Key insight: Consistency beats virality
- tech_adoption: 33.3% (3 experiments)
  - Key insight: Start small, validate early

**IMPORTANT - Using Experiment Learnings:**
- Decision types with low success rates need different approaches
- Apply successful tactics from past experiments
- Avoid known failure patterns
```

---

## Testing

```bash
# 1. Start services
make start && make celery

# 2. Check models exist
.venv/bin/python manage.py shell -c "
from core.models_pilot_readiness import ExperimentLearning, DecisionTypeSuccessPattern
print(f'ExperimentLearning: {ExperimentLearning.objects.count()}')
print(f'DecisionTypeSuccessPattern: {DecisionTypeSuccessPattern.objects.count()}')
"

# 3. Complete an experiment to test learning creation
# (Create a pilot first via UI, then complete it)
curl -X POST http://localhost:8000/api/experiments/<uuid>/complete/ \
  -H "Content-Type: application/json" \
  -d '{"status": "success", "learnings": "Educational content works well"}'
```

---

## Session 598 Options

### Option A: Learning Loop UI
- Dashboard to view experiment learnings
- Success pattern visualization
- Decision type performance charts

### Option B: AI-Enhanced Learning Extraction
- Use LLM to extract structured learnings from experiment outcomes
- Auto-generate insights from patterns
- Smart recommendations based on similar past experiments

### Option C: Kill Switch Integration (from Session 596)
- Add "Stop Experiment" button
- Reason input required
- Auto-fails experiment
- Discord notification

---

**Session 597: Experiment Learning Loop - COMPLETE**
