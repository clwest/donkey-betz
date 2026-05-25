# Session 449: Learning Loops for AI Content Pipeline

**Date:** December 14, 2025
**Status:** COMPLETE
**Focus:** Implement feedback mechanisms at every pipeline stage to enable continuous learning

---

## Summary

Implemented a comprehensive learning loop system for the AI Content Pipeline. The system collects feedback at each stage (Research, Script, Image, Voice, Video, Package), tracks style and voice performance, generates insights, and uses historical data to make recommendations for future content generation.

---

## Problem

The AI Series Workflow (Session 448) could generate content, but had no way to:
1. Learn which style presets work best for different audiences
2. Track which voices perform well with different content types
3. Collect user feedback to improve generation quality
4. Generate actionable insights from performance data

---

## Solution

### 1. Database Models (`core/models_pipeline_feedback.py`)

| Model | Purpose |
|-------|---------|
| `PipelineStageFeedback` | Generic feedback for any pipeline stage (1-5 rating) |
| `StylePresetPerformance` | Aggregated performance metrics per style/audience combo |
| `VoicePerformance` | Voice effectiveness tracking per series type |
| `ContentEngagement` | Track views, likes, shares, completion rates |
| `ResearchQueryPerformance` | Track which research queries lead to better content |
| `PipelineLearningInsight` | Generated insights like "Pixar works 23% better for kids" |

### 2. Learning Service (`core/services/pipeline_learning.py`)

Central service that handles:
- Recording stage feedback (automatic + manual)
- Aggregating performance metrics
- Generating style/voice recommendations
- Creating learning insights from data
- Providing statistics and leaderboards

Key methods:
```python
service = get_pipeline_learning_service()

# Record feedback
service.record_stage_feedback(stage='image', rating=4.5, context={...})

# Get recommendations
best_style = service.get_best_style_for_context('kids', 'educational')

# Get insights
insights = service.get_active_insights(stage='image')
```

### 3. AISeriesWorkflowAgent Integration

Added automatic feedback collection:
- After each episode completes, records automated ratings:
  - Script stage: Based on word count (200-300 optimal = 4.5, outside range = lower)
  - Image stage: Based on image count generated
  - Voice/Video: Success-based ratings
- Style recommendations used when no explicit style specified
- Learning service property for lazy-loading

### 4. REST API Endpoints (`/api/pipeline-learning/`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/feedback/` | POST | Record stage feedback |
| `/engagement/` | POST | Record engagement metrics |
| `/recommend/style/` | GET | Get style recommendation |
| `/recommend/voice/` | GET | Get voice recommendation |
| `/leaderboard/styles/` | GET | Style performance leaderboard |
| `/insights/` | GET | Get active learning insights |
| `/insights/generate/` | POST | Generate new insights |
| `/stats/` | GET | Get learning statistics |

### 5. Discord Commands

| Command | Description |
|---------|-------------|
| `/rate-series <id> <stage> <rating>` | Rate a series stage (1-5) |
| `/learning-stats` | View learning system statistics |
| `/style-recommend <audience>` | Get style recommendation |
| `/style-leaderboard` | View top-performing styles |

---

## Files Modified/Created

| File | Changes |
|------|---------|
| `core/models_pipeline_feedback.py` | **NEW** - All feedback and learning models |
| `core/services/pipeline_learning.py` | **NEW** - Learning loop service |
| `core/views_learning.py` | **NEW** - REST API endpoints |
| `core/agents/ai_series_workflow_agent.py` | Added learning service integration, auto-feedback |
| `core/services/discord_bot.py` | Added PipelineLearningCommands cog |
| `core/urls.py` | Added `/api/pipeline-learning/` routes |
| `core/models.py` | Import pipeline feedback models |
| `core/migrations/0093_session_449_pipeline_feedback.py` | **NEW** - Database migration |

---

## How the Learning Loop Works

### Feedback Collection Flow
```
1. User creates series with /series-create
2. AISeriesWorkflowAgent generates episodes
3. After each episode:
   - Automatic feedback recorded (script quality, image count, etc.)
   - Style/voice performance updated
4. User can optionally rate via /rate-series
5. Engagement tracked when content published
```

### Recommendation Flow
```
1. New series creation requested
2. If no style specified in lock_style():
   - Query StylePresetPerformance for best style
   - Check target_audience + series_type
   - Return learned recommendation (if sample_size >= 3)
   - Otherwise return default (pixar)
3. Apply recommendation to generation
4. Track outcome for future learning
```

### Insight Generation Flow
```
1. Call service.generate_insights()
2. Analyzes StylePresetPerformance table
3. Finds top performers per audience/type
4. Compares against baseline average
5. Creates PipelineLearningInsight records
6. Example: "Pixar style performs 23% better for kids content"
```

---

## Testing

### Test API Endpoint
```bash
# Get learning stats
curl http://localhost:8000/api/pipeline-learning/stats/

# Get style recommendation
curl "http://localhost:8000/api/pipeline-learning/recommend/style/?audience=kids&series_type=educational"

# Record feedback (requires auth)
curl -X POST http://localhost:8000/api/pipeline-learning/feedback/ \
  -H "Content-Type: application/json" \
  -d '{"stage": "image", "rating": 4.5, "context": {"style_preset": "pixar"}}'
```

### Test Discord Commands
```
/rate-series series_id:<uuid> stage:image rating:5 comment:Great style!
/learning-stats
/style-recommend audience:kids series_type:educational
/style-leaderboard limit:5
```

### Verify Models
```bash
.venv/bin/python manage.py shell -c "
from core.models_pipeline_feedback import StylePresetPerformance
print(StylePresetPerformance.objects.count())
"
```

---

## Remaining Work

### Analytics Dashboard (Future Session)
- Frontend UI for viewing learning insights
- Charts showing style performance over time
- Engagement metrics visualization
- A/B test integration

### Enhanced Feedback Sources
- Platform API integration (YouTube, TikTok analytics)
- Client approval tracking
- Revenue correlation analysis

---

## Related Sessions

- **Session 448:** Style preset integration (enum constraints)
- **Session 447:** Series view command, duplicate bug fixes
- **Session 445:** AISeriesWorkflowAgent initial implementation
- **Session 232:** Original Learning Loop (Phase 5) - for general content

---

## Golden Goose Strategy Progress

From the Golden Goose Strategy document:

| Stage | Learning Loop | Status |
|-------|---------------|--------|
| Research | Query performance tracking | IMPLEMENTED |
| Script | Word count quality scoring | IMPLEMENTED |
| Image | Style preset performance | IMPLEMENTED |
| Voice | Voice effectiveness tracking | IMPLEMENTED |
| Video | Success-based rating | IMPLEMENTED |
| Engagement | Platform metrics | Model ready, needs integration |

**Learning Loops: COMPLETE** - The AI Content Pipeline now learns from every generation.
