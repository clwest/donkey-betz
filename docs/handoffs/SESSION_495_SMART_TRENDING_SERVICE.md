# Session 495: SmartTrendingService & New Spiders

## Summary
Built a dynamic topic matching system that works for ANY trending query without hardcoded if/elif chains. Added 5 new spiders for startup ecosystem coverage. Fixed critical bug in BaseAgent that caused `'str' object has no attribute 'get'` errors.

## What Was Built

### 1. SmartTrendingService (`core/services/smart_trending_service.py`) - NEW
**580 lines** of dynamic topic matching:

- **36 categories** with 500+ keyword mappings covering:
  - Tech: ai_ml, startups, fintech, saas, hardware, crypto, gaming
  - Sector: defense_tech, healthtech, cybersecurity, climate
  - Creative: design, video, audio, photography
  - Business: marketing, sales, ecommerce, real_estate
  - And many more...

- **Features:**
  - Dynamic topic extraction from natural language queries
  - Multi-format data handling (title/summary, items array, name field)
  - 1-hour caching for performance
  - HTML artifact filtering in keyword extraction
  - Comprehensive stopword list (common words + web artifacts)

### 2. New Spiders (5 total)

| Spider | File | Purpose | Categories |
|--------|------|---------|------------|
| `crunchbase` | `crunchbase_spider.py` | Startup funding data | startups |
| `venturebeat` | `venturebeat_spider.py` | AI & enterprise news | tech, ai_ml |
| `defenseone` | `defenseone_spider.py` | Defense tech & Pentagon | defense_tech |
| `mobihealthnews` | `mobihealthnews_spider.py` | Digital health & biotech | healthtech |
| `securityweek` | `securityweek_spider.py` | Cybersecurity & breaches | cybersecurity |

### 3. TechCrunch Spider Enhancement
Added new category keywords:
- `defense_tech`: defense, military, dod, pentagon, government contract, aerospace
- `healthtech`: healthtech, biotech, medtech, digital health, telehealth, fda
- `cybersecurity`: cybersecurity, infosec, security startup, breach, ransomware
- `climate`: climate, cleantech, sustainability, carbon, green tech, renewable

### 4. PersonalAssistantAgent Integration
Updated `_fetch_fresh_trends_for_question()` to use SmartTrendingService:
```python
from core.services.smart_trending_service import get_smart_trending_service
service = get_smart_trending_service()
result = service.get_trending_for_query(query=task, hours=72, article_limit=15, use_cache=True)
```

### 5. Bug Fix: BaseAgent Format Mismatch
**Problem:** `'str' object has no attribute 'get'` error

**Root Cause:** SmartTrendingService returns trends as strings (`['crunchbase', 'enterprise', ...]`) but BaseAgent expected dicts with `.get('topic')`.

**Fix:** Updated both `_build_prompt()` and `_build_prompt_with_attribution()` in `core/agents/base_agent.py`:
```python
# Session 495: Handle both string lists (from SmartTrendingService) and dict lists (legacy)
for t in trends[:5]:
    if isinstance(t, str):
        trend_names.append(t)
    elif isinstance(t, dict) and t.get('topic'):
        trend_names.append(t.get('topic'))
```

## Files Changed/Created

### New Files
- `core/services/smart_trending_service.py` (~580 lines)
- `ai_core/spiders/specialized/crunchbase_spider.py` (~285 lines)
- `ai_core/spiders/specialized/venturebeat_spider.py` (~185 lines)
- `ai_core/spiders/specialized/defenseone_spider.py` (~195 lines)
- `ai_core/spiders/specialized/mobihealthnews_spider.py` (~195 lines)
- `ai_core/spiders/specialized/securityweek_spider.py` (~230 lines)

### Modified Files
- `ai_core/spiders/spider_registry.py` - Registered 5 new spiders
- `ai_core/spiders/specialized/techcrunch_spider.py` - Added new categories
- `core/agents/personal_assistant_agent.py` - SmartTrendingService integration
- `core/agents/base_agent.py` - Fixed string/dict format handling

## Test Results

### SmartTrendingService Topics
| Query | Categories Matched | Articles |
|-------|-------------------|----------|
| "What's trending in startups?" | startups | 10 |
| "defense tech news" | tech, defense_tech | 10 |
| "What's trending in cybersecurity?" | cybersecurity, financial | 10 |
| "healthtech trends" | tech, healthtech | 10 |
| "What's trending in AI?" | ai_ml | 5 |

### API Response
```json
{
  "success": true,
  "response": "Short answer: AI is driving most of the activity...",
  "knowledge_attribution": {
    "spider_sources": ["crunchbase", "venturebeat", "techcrunch_startups"],
    "confidence_score": 0.68,
    "data_freshness_hours": 1.0
  }
}
```

## Data Status After Session
- **Total spiders**: 72 (up from 67)
- **Spider data records**: 20,712
- **Records with embeddings**: 18,243 (88.1%)
- **New articles collected**: 75

## How It Works

1. **User asks**: "What's trending in startups?"
2. **SmartTrendingService** extracts topic "startups" from query
3. **Category matching**: Maps "startups" to `['startups']` category
4. **Spider selection**: Gets spiders registered under 'startups' category
5. **Data fetch**: Queries SpiderData for recent articles from those spiders
6. **Keyword extraction**: Extracts trending terms from article titles/summaries
7. **Response**: Returns articles + keywords to PersonalAssistantAgent
8. **GPT**: Uses the trending data to generate comprehensive answer

## Usage

```python
from core.services.smart_trending_service import get_smart_trending_service

service = get_smart_trending_service()
result = service.get_trending_for_query(
    query="What's trending in AI?",
    hours=72,      # Look back 72 hours
    article_limit=15,  # Max articles to return
    use_cache=True     # Use 1-hour cache
)

# Returns:
# {
#     'topic': 'ai',
#     'categories': ['ai_ml'],
#     'trends': ['openai', 'llm', 'gpt', ...],  # Trending keywords
#     'articles': [...],  # Article dicts with title, url, source
#     'cache_hit': False
# }
```

## Next Steps (Session 496+)
1. Add more spiders for underrepresented categories (education, legal, government)
2. Implement semantic search fallback when keyword matching fails
3. Add trend velocity detection (what's rising vs declining)
4. Consider ML-based topic classification for better accuracy
