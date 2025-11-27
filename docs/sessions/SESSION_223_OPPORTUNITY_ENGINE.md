# Session 223: Opportunity Engine (Phase 1 - Creative Intelligence Empire)

**Date:** November 27, 2025
**Focus:** Transform spider data into scored, actionable opportunities

---

## Summary

Session 223 implements Phase 1 of the Creative Intelligence Empire master plan - the Opportunity Engine. This system transforms raw spider-collected data into scored, actionable opportunities that feed directly into content creation workflows.

## The Core Loop

```
DISCOVER (Spiders) → ANALYZE (Scoring Agent) → CREATE (Workflows) → DISTRIBUTE → EARN → LEARN
```

This session implements the first two stages: DISCOVER and ANALYZE.

---

## What Was Built

### 1. Enhanced Opportunity Model (`core/models_unified_system.py`)

Extended the existing `Opportunity` model with new scoring fields:

**Scoring Fields (1-100):**
- `profit_potential` - How much money could this make?
- `competition_level` - How saturated is this market?
- `effort_required` - How much work to capitalize?
- `time_sensitivity` - How urgent is this opportunity?
- `overall_score` - Calculated overall score

**New Fields:**
- `spider_data` - ForeignKey link to SpiderData
- `source_type` - trend, job, product, news, tech, etc.
- `category` - digital_product, freelance, content, template, etc.
- `suggested_content_types` - ['logo', 'thumbnail', 'video']
- `suggested_workflows` - Recommended workflows
- `estimated_cost` - Cost to create content
- `keywords` - Related keywords/tags
- `market_data` - Market research data
- `advisor_recommendations` - Advisor input
- `scored_at` - When opportunity was scored
- `acted_on_at` - When user started acting

**New Methods:**
- `calculate_overall_score()` - Scoring algorithm
- `score_opportunity()` - Calculate and save score
- `is_scored` - Property checking if scored
- `estimated_roi` - Property calculating ROI
- `urgency_level` - Property categorizing urgency

### 2. Supporting Models

**OpportunityScore (`core/models_unified_system.py:682`):**
- Detailed scoring breakdown with reasoning
- `profit_reasoning`, `competition_reasoning`, `effort_reasoning`, `timing_reasoning`
- `confidence_level` (1-100)
- `data_sources` - List of sources used
- `advisors_consulted` - List of advisors
- `scoring_model_version` - Version tracking

**OpportunityAction (`core/models_unified_system.py:751`):**
- Track actions taken on opportunities
- `action_type` - viewed, analyzed, approved, started, content_created, published, revenue_logged
- `content_ids` - IDs of content created
- `workflow_used` - Which workflow was executed
- `outcome` - Outcome data for learning loop

### 3. Opportunity Scoring Agent (`agents/opportunity_scoring_agent.py`)

A 650+ line AI agent that:
- Scores spider data automatically
- Analyzes custom trends on-demand
- Suggests content types and workflows
- Estimates revenue and costs
- Consults advisors for strategic input

**Key Methods:**
- `score_spider_data(hours, limit, user)` - Batch score spider data
- `analyze_trend(topic, trend_data, user)` - Analyze custom trend
- `score_job_opportunity(job_data, user)` - Score job opportunities
- `get_top_opportunities(limit, category, min_score, user)` - Get top scored
- `rescore_opportunity(opportunity_id)` - Re-score existing opportunity

**Scoring Algorithm:**
```python
# Weighted combination
score = (
    profit_potential * 0.35 +
    (100 - competition_level) * 0.35 +
    (100 - effort_required) * 0.20 +
    time_sensitivity * 0.10
)
```

### 4. API Endpoints (`core/views_opportunity.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/opportunities/` | GET | List opportunities with filters |
| `/api/opportunities/<id>/` | GET | Get opportunity detail |
| `/api/opportunities/score/` | POST | Trigger scoring of spider data |
| `/api/opportunities/<id>/act/` | POST | Start acting on opportunity |
| `/api/opportunities/top/` | GET | Get top-scored opportunities |
| `/api/opportunities/<id>/rescore/` | POST | Re-score opportunity |
| `/api/opportunities/analyze/` | POST | Analyze custom trend |
| `/api/opportunities/stats/` | GET | Get statistics |

**Query Parameters for List:**
- `status` - Filter by status
- `category` - Filter by category
- `source_type` - Filter by source type
- `min_score` - Minimum overall score
- `page`, `page_size` - Pagination
- `sort`, `order` - Sorting

### 5. Celery Tasks (`core/tasks.py`)

| Task | Schedule | Description |
|------|----------|-------------|
| `score_opportunities_from_spider_data` | Hourly at :15 | Score spider data |
| `expire_old_opportunities` | Daily at 4:30 AM | Mark old opportunities expired |
| `generate_opportunity_report` | Daily at 8 AM | Generate daily report |

### 6. UI - Opportunities Tab (`ai_core/templates/ai_image_studio.html`)

New tab in AI Studio with:
- Stats cards (Total, High Value, Avg Score, Time-Sensitive)
- Category and source type filters
- Minimum score filter
- "Analyze a Trend" input for custom analysis
- Scrollable opportunities list
- Detail modal with:
  - Score breakdown with progress bars
  - Reasoning explanations
  - Revenue/cost/ROI estimates
  - Suggested workflows with execute buttons
  - "Start Creating" action button

---

## Database Migration

Migration: `core/migrations/0028_session_223_opportunity_engine.py`

Adds:
- 16 new fields to `Opportunity` model
- `OpportunityScore` model
- `OpportunityAction` model

---

## Files Created/Modified

### Created:
- `agents/opportunity_scoring_agent.py` (650+ lines)
- `core/views_opportunity.py` (400+ lines)
- `core/migrations/0028_session_223_opportunity_engine.py`
- `docs/sessions/SESSION_223_OPPORTUNITY_ENGINE.md`

### Modified:
- `core/models_unified_system.py` - Added scoring fields and supporting models
- `core/urls.py` - Added opportunity API routes
- `core/tasks.py` - Added opportunity Celery tasks
- `core/celery.py` - Added Celery Beat schedules
- `ai_core/templates/ai_image_studio.html` - Added Opportunities tab and JS functions

---

## How to Use

### 1. Score Spider Data
```python
from agents.opportunity_scoring_agent import OpportunityScoringAgent

agent = OpportunityScoringAgent()
results = agent.score_spider_data(hours=24, limit=50)
```

### 2. Analyze a Trend
```python
result = agent.analyze_trend("AI video editing tools", user=user)
print(f"Score: {result.overall_score}")
print(f"Suggested content: {result.suggested_content_types}")
```

### 3. Get Top Opportunities
```python
opportunities = agent.get_top_opportunities(limit=10, min_score=70)
```

### 4. Via API
```bash
# Score spider data
curl -X POST http://localhost:8000/api/opportunities/score/

# Get top opportunities
curl http://localhost:8000/api/opportunities/top/?limit=10&min_score=70

# Analyze a trend
curl -X POST http://localhost:8000/api/opportunities/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI content creation tools"}'
```

### 5. Via UI
1. Go to AI Studio → Opportunities tab
2. Click "Score New" to score recent spider data
3. Enter a trend topic and click "Analyze & Score"
4. Click any opportunity to see details
5. Click "Start Creating" to begin acting on it

---

## Next Phase (Sessions 224-225)

Phase 2: **Revenue Reality**
- Track actual revenue from opportunities
- Link content created to revenue earned
- Build the learning loop
- Measure ROI accuracy

---

## Key Design Decisions

1. **Enhance existing model** rather than create duplicate - The Opportunity model already existed, so we extended it with scoring fields
2. **Weighted scoring formula** - Profit and low competition weighted highest (35% each), effort and timing lower
3. **Invert competition/effort** - Lower is better, so we calculate (100 - value) for the overall score
4. **Separate scoring details** - OpportunityScore model stores reasoning for transparency
5. **Action tracking** - OpportunityAction enables the future learning loop

---

## Reality Score Impact

This session establishes the foundation for transforming spider intelligence into actionable revenue opportunities. The scoring system provides:
- Automated prioritization of opportunities
- Data-driven content creation decisions
- Foundation for ROI tracking (Phase 2)
- Integration point for advisor consultation
