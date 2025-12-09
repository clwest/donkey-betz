# Session 399: Spider Renames & Data Feed API Fix

**Date:** December 8, 2025

---

## Summary

This session completed two major tasks:
1. Renamed 6 spiders to accurately reflect their actual data sources
2. Fixed a bug in the Data Feed API where empty string parameters returned no results

---

## Spider Renames

Six spiders were renamed because their original names no longer matched the data sources they were actually collecting from:

| Old Name | New Name | Reason |
|----------|----------|--------|
| cnn | google_news | CNN RSS feeds stale (2023 content) |
| dribbble | awwwards | Dribbble blocked (Cloudflare), returns 202 |
| indiehackers | hackernoon | IndieHackers RSS broken (returns HTML) |
| hashnode | freecodecamp | Hashnode API returns 404 |
| udemy | coursera | Udemy API requires auth |
| indiegogo | techcrunch_startups | Indiegogo API blocked (403) |

### Files Modified

1. **`ai_core/spiders/spider_registry.py`**
   - Removed old imports (DribbbleSpider, UdemySpider, HashnodeSpider, IndiegogoSpider, IndieHackersSpider, CNNSpider)
   - Added comments explaining why each was removed
   - Updated registrations to use new names and BaseIntelligenceSpider class

2. **`ai_core/spiders/real_data_collector.py`**
   - Updated SPIDER_TARGET_URLS with new names
   - Updated PHASE3_API_SPIDERS with new handler functions
   - Added handlers: `_collect_freecodecamp_data`, `_collect_coursera_data`, `_collect_techcrunch_startups_data`

### Database Cleanup

- Deleted 871 old records with stale spider names
- Created fresh data with correct spider names and categories:
  - google_news: 20 items (news)
  - awwwards: 30 items (design)
  - hackernoon: 20 items (community)
  - freecodecamp: 10 items (tech)
  - coursera: 10 items (education)
  - techcrunch_startups: 20 items (tech)

---

## Data Feed API Bug Fix

### Problem

When JavaScript sent an empty string for category (`category=`), Python's `request.GET.get('category', 'all')` returned the empty string, not 'all'. This caused the filter `data_type=''` to match nothing.

User reported: "we still are only showing (pills) tech and techcrunch_startups, and if trying to click on any of the categories that are listed they all display nothing"

### Solution

Changed lines 1128-1129 in `core/views_spider_intelligence.py`:

```python
# BEFORE (buggy):
category = request.GET.get('category', 'all')
source = request.GET.get('source', 'all')

# AFTER (fixed):
category = request.GET.get('category', 'all') or 'all'  # Handle empty string
source = request.GET.get('source', 'all') or 'all'  # Handle empty string
```

### Verification

After fix, Data Feed properly returns all items when category/source is empty or 'all'.

---

## Verification Commands

```bash
# Count registered spiders
python -c "from ai_core.spiders.spider_registry import SpiderRegistry; r = SpiderRegistry(); print(f'Total: {r.get_spider_count()[\"total\"]} spiders')"
# Expected: 62 spiders

# Verify old names removed
python manage.py shell -c "
from core.models_unified_system import SpiderData
old_names = ['cnn', 'dribbble', 'indiehackers', 'hashnode', 'udemy', 'indiegogo']
for name in old_names:
    count = SpiderData.objects.filter(spider_name=name).count()
    print(f'{name}: {count} records (should be 0)')
"

# Verify new names have data
python manage.py shell -c "
from core.models_unified_system import SpiderData
new_names = ['google_news', 'awwwards', 'hackernoon', 'freecodecamp', 'coursera', 'techcrunch_startups']
for name in new_names:
    count = SpiderData.objects.filter(spider_name=name).count()
    print(f'{name}: {count} records')
"

# Test Data Feed API with empty category
curl 'http://localhost:8000/api/spiders/data-feed/?category='
# Should return items, not empty response
```

---

## Related Files

- `ai_core/spiders/spider_registry.py` - Central spider registry
- `ai_core/spiders/real_data_collector.py` - Data collection with URLs and handlers
- `core/views_spider_intelligence.py` - Spider API endpoints (line 1128-1129 fixed)
- `docs/SPIDERS.md` - Updated with Session 399 changes

---

## Next Steps

1. Monitor new spider data collection for quality
2. Consider adding more RSS feeds for removed spiders
3. Update UI to display spider names without underscores (mentioned by user as future task)
