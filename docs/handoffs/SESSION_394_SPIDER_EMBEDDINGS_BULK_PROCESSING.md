# Session 394: Spider Embeddings Bulk Processing

**Date:** December 8, 2025
**Focus:** Bulk embedding processing and spider content analysis

---

## Summary

Addressed the critical issue of only 0.3% of spider data having embeddings (36/12,449 entries). Implemented bulk processing and discovered that most spider entries lack embeddable content.

---

## Key Accomplishments

### 1. Created Bulk Embedding Management Command

**File:** `core/management/commands/bulk_embed_spiders.py`

```bash
# Usage examples
python manage.py bulk_embed_spiders              # Process all (7 days)
python manage.py bulk_embed_spiders --batch=200  # Custom batch size
python manage.py bulk_embed_spiders --hours=24   # Only last 24 hours
python manage.py bulk_embed_spiders --dry-run    # Preview without changes
python manage.py bulk_embed_spiders --mark-empty # Mark entries with no items
```

### 2. Processed All Pending Embeddings

| Before | After |
|--------|-------|
| 36 with embeddings (0.3%) | 2,006 with embeddings (16.1%) |
| 12,413 pending | 0 pending |
| N/A | 10,443 marked as no-content (83.9%) |

### 3. Discovered Spider Content Issue

**Critical Finding:** 83.9% of spider entries don't contain embeddable content!

| Spider | Issue | Example Raw Data |
|--------|-------|------------------|
| hackernews | Reference-only IDs | `{'id': 46193931, 'type': 'reference', 'source': 'hackernews'}` |
| kickstarter | Metadata only | `{'seed': ..., 'search_url': ..., 'has_more': true}` |
| behance | Error messages | `{'note': '...', 'message': '...', 'categories': [...]}` |
| dribbble | Error messages | `{'note': '...', 'message': '...'}` |
| guru | Status messages | `{'message': '...', 'platforms_checked': [...]}` |

**Spiders with actual content that can be embedded:**
- TechCrunch, MIT Tech Review, Wired, The Verge, Axios (RSS feeds with titles/descriptions)
- WeWorkRemotely, RemoteOK (job listings with full details)
- Dev.to (articles with titles and content)
- Product Hunt (product launches with descriptions)
- Reddit (posts with titles and content)
- Medium, Substack (article summaries)

### 4. Updated Embedding Infrastructure

**File:** `core/services/spider_semantic_search.py`
- Added `marked_empty` count to `get_embedding_stats()`
- Updated `backfill_embeddings()` to skip already-marked entries
- Distinguishes between actual embeddings vs marked as no-content

**File:** `core/tasks.py`
- Increased default batch size from 50 to 200
- Updated logging to show marked_empty count

---

## Embedding Stats After Processing

```
============================================================
FINAL EMBEDDING STATS
============================================================
Total SpiderData entries:     12,449
With real embeddings:         2,006 (16.1%)
Marked as no-content:         10,443 (83.9%)
Pending (NULL):               0 (0.0%)
============================================================
Searchable for semantic:      2,006 entries
============================================================
```

---

## Root Cause Analysis

### Why Most Entries Lack Content

1. **HackerNews Spider** (147 entries): Only fetches story IDs, not actual story content
   - Fetches: `https://hacker-news.firebaseio.com/v0/topstories.json`
   - Returns: `[46193931, 46192846, ...]` (just IDs)
   - **Should fetch**: Individual story details from `https://hacker-news.firebaseio.com/v0/item/{id}.json`

2. **Kickstarter Spider** (25 entries): Stores search metadata, not project details
   - Returns: `{'seed': ..., 'total_hits': 42, 'has_more': true}`
   - **Should fetch**: Project titles, descriptions, categories

3. **Behance/Dribbble** (24 entries): Return error/note messages
   - Returns: `{'note': 'API requires authentication', 'message': '...'}`
   - **Needs**: Valid API credentials or scraping approach

4. **Guru/FlexJobs/RemoteOK** (33 entries): Some return status messages
   - Returns: `{'message': 'No jobs found matching criteria'}`
   - **Needs**: Better error handling to not save empty results

---

## Recommendations for Next Session

### High Priority Fixes

1. **Fix HackerNews Spider** - Fetch individual story content
   ```python
   # After getting story IDs, fetch each story:
   for story_id in story_ids[:30]:
       story = fetch_json(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json')
       # Now we have: title, url, score, by (author), time, descendants
   ```

2. **Fix Kickstarter Spider** - Extract project details from response

3. **Add Content Validation** - Don't save entries without actual content
   ```python
   def save_data(self, data):
       if not data.get('items') or not any(
           item.get('title') or item.get('description')
           for item in data.get('items', [])
       ):
           return  # Skip saving empty/reference-only data
   ```

4. **Handle API Errors Better** - Don't save error messages as data

### Medium Priority

5. **Fix Behance/Dribbble** - Implement proper API auth or RSS fallback
6. **Add Pre-Save Validation** - Ensure embeddable content exists before saving

---

## Files Changed

| File | Changes |
|------|---------|
| `core/management/commands/bulk_embed_spiders.py` | NEW - Bulk embedding command |
| `core/services/spider_semantic_search.py` | Updated stats and backfill logic |
| `core/tasks.py` | Increased batch size to 200 |

---

## Commands for Next Session

```bash
# Check current embedding stats
.venv/bin/python manage.py shell -c "
from core.services.spider_semantic_search import get_spider_semantic_search
search = get_spider_semantic_search()
print(search.get_embedding_stats())
"

# Run bulk embedding (if needed)
python manage.py bulk_embed_spiders --dry-run  # Preview
python manage.py bulk_embed_spiders --mark-empty  # Execute

# Test semantic search
.venv/bin/python manage.py shell -c "
from core.services.spider_semantic_search import get_spider_semantic_search
search = get_spider_semantic_search()
results = search.semantic_search('AI tools for developers', limit=5)
for r in results:
    print(f'{r[\"spider_name\"]}: {r[\"embedding_text\"][:100]}...')
"
```

---

---

## Spider Content Fix (Part 2)

### Root Cause Identified

The HackerNews spider was only fetching story IDs, not full content. The bug was in `ai_core/spiders/real_data_collector.py`:

```python
# BEFORE: Just stored IDs as references
elif isinstance(item, (int, str)):
    items.append({'id': item, 'source': source, 'type': 'reference'})
```

### Fix Applied

Added `fetch_hackernews_stories()` function to fetch full story details:

```python
async def fetch_hackernews_stories(session, story_ids):
    """Fetch full story details from HackerNews API."""
    stories = []
    for story_id in story_ids[:15]:
        url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
        story = await fetch(url)
        stories.append({
            'title': story.get('title', ''),
            'description': f"Score: {story.get('score')} | Comments: {story.get('descendants')}",
            'link': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
            ...
        })
    return stories
```

### Spider Status After Fix

| Spider | Status | Notes |
|--------|--------|-------|
| hackernews | ✅ Fixed | Now fetches 15 full stories with titles |
| behance | ✅ Working | 20 items with titles |
| devto | ✅ Working | 30 items with titles |
| techcrunch | ✅ Working | 20 items with titles |
| dribbble | ❌ Blocked | HTTP 202 (Cloudflare protection) |
| kickstarter | ❌ Blocked | HTTP 403 (API blocked) |

### Files Changed

| File | Changes |
|------|---------|
| `ai_core/spiders/real_data_collector.py` | Added `fetch_hackernews_stories()`, updated `collect_spider_data()` |

---

## Related Documents

- [SPIDERS.md](../SPIDERS.md) - Spider network reference
- [SESSION_393_ORCHESTRATOR_BASEAGENT_REFACTORING.md](SESSION_393_ORCHESTRATOR_BASEAGENT_REFACTORING.md) - Previous session
