# Session 398 Handoff: Spider System Audit + Database Cleanup

**Date:** December 8, 2025
**Status:** COMPLETE - System ready for data exploration
**Next Session Focus:** Explore using spider data for intelligence and agent training

---

## What Was Accomplished

### 1. Full Spider System Audit
Comprehensive audit of the entire spider network:
- **62 registered spiders** across 30 categories
- **57 actually working** (collecting real data)
- Tested 20 representative spiders - 100% success rate
- Verified SpiderIntelligenceService returns real trending topics

### 2. Database Cleanup (6,906 Records Deleted)
Removed placeholder data from 40 removed spiders:
- **Before:** 14,049 records
- **After:** 7,143 records (50% reduction)
- All remaining records have real content

Removed spiders included: sellfy, etsy, gumroad, toptal, guru, peopleperhour, ninetyninedesigns, flexjobs, skillshare, teachable, bloomberg_terminal, reuters_eikon, opensea, seekingalpha, midjourney, civitai, runwayml, replicate, and 22 more.

### 3. Embedding Pipeline Verification
- Celery Beat running `backfill-spider-embeddings` every 10 minutes
- Bulk embedding processed all pending entries
- **Final Stats:** 1,830 searchable embeddings (25.6% coverage)

### 4. RSS Feed Fixes
Fixed broken feeds that were timing out or returning 403/404:

| Spider | Old (Broken) | New (Working) |
|--------|--------------|---------------|
| food | Serious Eats, Bon Appetit | Eater, Smitten Kitchen |
| travel | Lonely Planet, CN Traveler | Matador Network |
| government | politico.com/rss | rss.politico.com |

### 5. Agent Integration Verified
- 167 knowledge transfers from spiders to agents
- Agents are learning from spider data
- Collective intelligence system connected

---

## Current System State

### Spider Network
```
Registered Spiders: 62
Working Spiders: 57
Database Records: 7,143
With Embeddings: 1,830 (25.6%)
Need API Keys: 6 (bluesky, discord, spotify, etc.)
```

### Key Services Working
- **SpiderIntelligenceService** - Trending topics with topic filtering
- **SpiderSemanticSearch** - Semantic search across all spider data
- **Celery Beat** - Auto-embeddings every 10 min, spider runs every 15 min
- **Agent Learning** - Knowledge transfers from spider data

---

## How to Use the Spider Data

### 1. Get Trending Topics
```python
from core.services.spider_intelligence import SpiderIntelligenceService

service = SpiderIntelligenceService()

# Get what's trending (last 24 hours)
topics = service.get_trending_topics(hours=24, limit=10)
# Returns: [{'topic': 'AI', 'count': 436, 'sources': ['hackernews', 'techcrunch', ...]}, ...]

# Filter by topic area
trends = service.get_tech_trends(hours=72, limit=15, topic_filter='ai')
# Available filters: 'ai', 'web', 'security', 'cloud', 'design'
```

### 2. Semantic Search
```python
from core.services.spider_semantic_search import get_spider_semantic_search

search = get_spider_semantic_search()

# Search with natural language
results = search.semantic_search("AI tools for developers", limit=10)
for r in results:
    print(f'[{r.source}] {r.title}')
    print(f'  Similarity: {r.similarity:.3f}')
    print(f'  URL: {r.url}')

# Get embedding stats
stats = search.get_embedding_stats()
# {'total_entries': 7143, 'with_embedding': 1830, 'percentage': 25.6}
```

### 3. Unified Intelligence Search (Spiders + Research)
```python
from core.services.unified_intelligence_search import get_unified_intelligence_search

search = get_unified_intelligence_search()

# Search both spider data AND business research results
results = search.unified_search("AI content generation")

# Get context for agent prompts
context = search.get_research_context("market analysis")
```

### 4. Direct Database Access
```python
from core.models_unified_system import SpiderData
from django.utils import timezone
from datetime import timedelta

# Recent entries
recent = SpiderData.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=24)
).order_by('-created_at')[:20]

# Entries with embeddings (searchable)
searchable = SpiderData.objects.exclude(embedding__isnull=True)

# By source
hackernews = SpiderData.objects.filter(spider_name='hackernews')
```

---

## Important Technical Notes

### SemanticSearchResult is a dataclass
Use attribute access, NOT dict access:
```python
# CORRECT
result.title
result.source
result.similarity

# WRONG - will error
result.get('title')
result['source']
```

### SpiderData Field Names
```python
# Field is 'spider_name', not 'source'
SpiderData.objects.filter(spider_name='hackernews')  # Correct
SpiderData.objects.filter(source='hackernews')  # Wrong - FieldError
```

### Topic Filters for get_tech_trends()
| Filter | Keywords Matched |
|--------|-----------------|
| `ai` | AI, ML, machine learning, neural network, GPT, LLM |
| `web` | JavaScript, React, Vue, CSS, frontend |
| `security` | cybersecurity, encryption, privacy, hacking |
| `cloud` | AWS, Azure, Kubernetes, Docker, DevOps |
| `design` | UI, UX, Figma, typography, branding |

---

## Files Modified This Session

| File | Changes |
|------|---------|
| `ai_core/spiders/real_data_collector.py` | Fixed RSS feeds (food, travel, government) |
| `00-START-NEXT-SESSION.md` | Updated for Session 398 |
| `docs/SPIDERS.md` | Updated stats (7,143 records, 25.6% coverage) |

---

## Suggested Next Steps

1. **Explore Data Usage**
   - Use SpiderIntelligenceService to find trending topics
   - Use semantic search to find relevant content
   - Connect spider insights to agent workflows

2. **Improve Embedding Coverage**
   - Current: 25.6% (1,830 of 7,143)
   - Some content is genuinely empty (marked_empty)
   - Could optimize embedding text extraction

3. **Agent Integration**
   - Create workflows that use trending topics
   - Auto-suggest content based on spider intelligence
   - Feed spider data to content strategy agents

4. **API Keys to Configure**
   - Bluesky (BLUESKY_IDENTIFIER + PASSWORD already in .env)
   - Discord (need bot token)
   - Spotify (OAuth flow needed)

---

## Quick Verification Commands

```bash
# Start services
make start && make celery

# Check spider stats
.venv/bin/python manage.py shell -c "
from core.services.spider_semantic_search import get_spider_semantic_search
search = get_spider_semantic_search()
stats = search.get_embedding_stats()
print(f'Records: {stats[\"total_entries\"]}, Searchable: {stats[\"with_embedding\"]}')"

# Test semantic search
.venv/bin/python manage.py shell -c "
from core.services.spider_semantic_search import get_spider_semantic_search
search = get_spider_semantic_search()
results = search.semantic_search('AI trends', limit=3)
for r in results: print(f'[{r.source}] {r.title[:50]}')"

# Check trending topics
.venv/bin/python manage.py shell -c "
from core.services.spider_intelligence import SpiderIntelligenceService
service = SpiderIntelligenceService()
topics = service.get_trending_topics(hours=24, limit=5)
for t in topics: print(f'{t[\"topic\"]}: {t[\"count\"]} mentions')"
```

---

## Session 398 Commits

1. `docs(Session 398): Update SPIDERS.md with cleaned database stats`
2. Plus 10 commits from Sessions 395-398 covering spider audit, cleanup, and fixes

**All systems verified and ready for next session!**
