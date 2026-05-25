# Session 783: Spider News Feed

**Date:** January 20, 2026
**Focus:** Human-facing news feed for spider data with agent annotations

## Overview

Created a Reddit/Yahoo News-style feed that surfaces spider data annotated by agents. Humans can browse, filter, search, and vote on items that agents have flagged as useful, profitable, podcast-worthy, etc.

## What Was Built

### 1. Database Model: `SpiderDataAnnotation`

**File:** `core/models_unified_system.py` (line ~3190)

```python
class SpiderDataAnnotation(models.Model):
    ANNOTATION_TYPES = [
        ('useful', 'Useful'),
        ('profitable', 'Profitable Opportunity'),
        ('podcast_worthy', 'Podcast Worthy'),
        ('breaking_news', 'Breaking News'),
        ('investment_opportunity', 'Investment Opportunity'),
        ('action_required', 'Action Required'),
        ('warning', 'Warning/Risk'),
        ('trending', 'Trending'),
    ]

    spider_data = ForeignKey(SpiderData, related_name='annotations')
    annotation_type = CharField(max_length=50, choices=ANNOTATION_TYPES)
    confidence_score = FloatField(default=0.5)  # 0.0-1.0
    note = TextField(blank=True)
    agent_name = CharField(max_length=100)
    upvotes = IntegerField(default=0)
    downvotes = IntegerField(default=0)
    view_count = IntegerField(default=0)
```

**Migration:** `core/migrations/0177_spider_data_annotation.py`

### 2. Backend API: 6 Endpoints

**File:** `core/views_spider_feed.py` (new, 500 lines)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/spider-feed/` | Main feed with filters & pagination |
| GET | `/api/spider-feed/trending/` | Most annotated items (24h) |
| GET | `/api/spider-feed/item/<id>/` | Single item detail |
| POST | `/api/spider-feed/<id>/annotate/` | Agent creates annotation |
| POST | `/api/spider-feed/<id>/vote/` | Human upvote/downvote |
| GET | `/api/spider-feed/stats/` | Feed statistics |

**Query Parameters for Main Feed:**
- `page`, `per_page` - Pagination
- `source` - Filter by spider_name
- `category` - Filter by data_type
- `annotation_type` - Filter by annotation type
- `search` - Full-text search
- `sort` - newest, popular, trending
- `hours` - Only items from last N hours

### 3. Agent Integration

**File:** `core/agents/base_agent.py` (added method)

```python
def _annotate_spider_data(
    self,
    spider_data_id: str,
    annotation_type: str,
    confidence: float = 0.7,
    note: str = ""
) -> bool:
    """Annotate a spider data item with intelligence insight."""
```

This allows any agent to flag interesting spider data during execution.

### 4. Frontend: SpiderFeedPage

**File:** `frontend/src/pages/SpiderFeedPage.tsx` (new, 588 lines)

Features:
- Stats summary cards (4 cards: annotated items, total annotations, 24h, 7d)
- Trending items section (top 3 most annotated)
- Filterable feed (source, category, annotation type, search, sort)
- Colored annotation badges:
  - `breaking_news` - Red
  - `profitable` - Green
  - `podcast_worthy` - Purple
  - `warning` - Orange
  - `useful` - Blue
  - `trending` - Cyan
  - `investment_opportunity` - Emerald
  - `action_required` - Amber
- Upvote/downvote functionality
- Item detail modal with full data

**Route:** `/spider-feed`

### 5. Other Files Modified

| File | Change |
|------|--------|
| `core/urls.py` | Added 6 spider-feed routes + imports |
| `core/auth_middleware.py` | Added `/api/spider-feed/` to PUBLIC_PATHS |
| `frontend/src/lib/api.ts` | Added `spiderFeedApi` client |
| `frontend/src/App.tsx` | Added route + import for SpiderFeedPage |
| `frontend/src/components/layout/Sidebar.tsx` | Added Spider Feed nav link with Newspaper icon |

## API Response Examples

### Stats Response
```json
{
  "status": "success",
  "stats": {
    "total_annotated_items": 5,
    "total_annotations": 6,
    "annotations_24h": 6,
    "annotations_7d": 6,
    "top_sources": [{"spider_name": "theodds", "count": 2}],
    "type_distribution": [{"annotation_type": "breaking_news", "count": 1}],
    "top_agents": [{"agent_name": "ResearchAgent", "count": 1}]
  }
}
```

### Feed Item Response
```json
{
  "id": "uuid",
  "spider_name": "hackernews",
  "title": "...",
  "preview": "First 200 chars...",
  "created_at": "2026-01-20T10:30:00Z",
  "relevance_score": 85,
  "annotations": [
    {"type": "breaking_news", "agent": "ResearchAgent", "confidence": 0.92, "note": "..."}
  ],
  "score": 15,
  "badges": ["breaking_news", "profitable"]
}
```

## How Agents Can Annotate

```python
# In any agent's execute() method:
spider_item_id = spider_context.get('source_item_id')
if spider_item_id and self._is_noteworthy(result):
    self._annotate_spider_data(
        spider_item_id,
        'profitable',
        confidence=0.85,
        note='High ROI opportunity based on market analysis'
    )
```

## Test Data Created

| Spider | Annotation Type | Agent |
|--------|----------------|-------|
| theodds | breaking_news, useful | TestAgent, ResearchAgent |
| kalshi | profitable | OpportunityScoringAgent |
| etherscan_api | podcast_worthy | PodcastCoordinatorAgent |
| giphy | trending | TrendAnalysisAgent |
| noaa_weather | investment_opportunity | MarketIntelligenceAgent |

## Commits

```
60c39ab3 feat(Session 783): Spider News Feed with agent annotations
e2d23d0d feat(Session 783): Add Spider Feed to sidebar navigation
```

## Verification

1. Backend APIs all working via curl tests
2. Frontend builds successfully (1,817 KB bundle)
3. Sidebar shows "Spider Feed" link with Newspaper icon
4. Data flows through: SpiderData -> SpiderDataAnnotation -> API -> React UI

## Future Enhancements

1. **Auto-annotation by agents**: Have agents automatically call `_annotate_spider_data()` when they find interesting items
2. **Celery task for annotation cleanup**: Remove old/low-engagement annotations
3. **User-specific feeds**: Filter by user's interests
4. **Notification system**: Alert users to new breaking_news or action_required items
5. **Analytics dashboard**: Track which annotations lead to user actions
