# Session 505 - Spider Routing Fixes

**Date:** December 19, 2025
**Previous Session:** 504 (Spider Signature Detection & Legal Spider Fixes)
**Status:** COMPLETE

---

## Summary

Fixed spider routing issues that caused several spiders (kickstarter, findlaw, kaggle) to return 0 items or fail with errors. The root cause was a combination of:

1. Missing `timestamp` field in kaggle spider's IntelligenceData
2. Duplicate function name `execute_single_spider` in core/tasks.py
3. Spiders defined in both `SPIDER_TARGET_URLS` and as proper spider classes, causing routing conflicts

---

## Issues Fixed

### 1. Kaggle Spider Missing Timestamp

**Error:** `IntelligenceData.__init__() missing 1 required positional argument: 'timestamp'`

**File:** `ai_core/spiders/specialized/kaggle_spider.py:359`

**Fix:** Added `timestamp=datetime.now(timezone.utc)` to the IntelligenceData constructor in `process_data()` method.

```python
return BaseIntelligenceData(
    spider_id=self.spider_id,
    source_url='kaggle.com',
    data_type='ml_trends',
    content={...},
    quality_score=0.9 if raw_data.get('source') != 'mock' else 0.3,
    metadata={...},
    timestamp=datetime.now(timezone.utc)  # Session 505: Added required field
)
```

### 2. Duplicate Function Names in tasks.py

**Problem:** Two functions named `execute_single_spider` existed in `core/tasks.py`:
- Line 239: Proper Celery task using spider class instances
- Line 1052: Lightweight version using `collect_spider_data_sync`

The second definition was overriding the first, causing all spiders to use the wrong code path.

**File:** `core/tasks.py:1052`

**Fix:** Renamed the second function to `execute_single_spider_lightweight`.

### 3. Spider Routing Conflicts

**Problem:** `kickstarter` and `findlaw` were defined in `SPIDER_TARGET_URLS` (and findlaw also in `PHASE3_API_SPIDERS`), but they also have proper spider classes in the spider registry. This caused `collect_spider_data_sync` to handle them instead of the proper spider classes.

**File:** `ai_core/spiders/real_data_collector.py`

**Fixes:**
- Removed `kickstarter` from `SPIDER_TARGET_URLS` (line 74)
- Removed `findlaw` from `SPIDER_TARGET_URLS` (line 276)
- Removed `findlaw` from `PHASE3_API_SPIDERS` (line 2148)

Now these spiders are properly handled by `KickstarterSpider` and `FindLawSpider` classes.

### 4. Embedding Coverage Fix (Huggingface/Kaggle)

**Problem:** Huggingface had 0% embedding coverage because `get_searchable_text()` only checked for `title` or `name` fields, but Huggingface items use `modelId` and `id` instead.

**File:** `core/models_unified_system.py:2947`

**Fix:** Updated `get_searchable_text()` to also check for `modelId` and `id` as fallbacks, and added handling for dict-type tags (common in Kaggle data).

```python
# Before
title = item.get('title') or item.get('name') or ''

# After (Session 505)
title = item.get('title') or item.get('name') or item.get('modelId') or item.get('id') or ''
```

**Results:**
- Huggingface: 0% → 5.2% (and improving with backfill)
- Hackernews: 37.3% → 42.2%

---

## Verification Results

After fixes, all spiders work correctly:

| Spider | Status | Items |
|--------|--------|-------|
| kaggle | SUCCESS | 1 (aggregated) |
| kickstarter | SUCCESS | 1 (aggregated) |
| findlaw | SUCCESS | 45 |
| colorado_family_law | SUCCESS | 55 |

---

## Files Modified

| File | Changes |
|------|---------|
| `ai_core/spiders/specialized/kaggle_spider.py` | Added missing `timestamp` field |
| `core/tasks.py` | Renamed duplicate function to `execute_single_spider_lightweight` |
| `ai_core/spiders/real_data_collector.py` | Removed kickstarter/findlaw from URL mappings |
| `core/models_unified_system.py` | Enhanced `get_searchable_text()` for better field coverage |

---

## Technical Notes

### Spider Execution Paths

There are two main paths for spider execution:

1. **Proper Spider Classes** (preferred):
   - Spider classes in `ai_core/spiders/specialized/`
   - Registered in `spider_registry.py`
   - Called via `execute_single_spider()` task
   - Uses `fetch_data()`, `process_data()`, `transform_data()` methods

2. **Legacy URL-based Collection** (fallback):
   - URLs defined in `SPIDER_TARGET_URLS`
   - Custom collectors in `PHASE3_API_SPIDERS`
   - Called via `collect_spider_data_sync()`
   - Less flexible, harder to maintain

**Recommendation:** Always prefer proper spider classes. Remove entries from `SPIDER_TARGET_URLS` when a spider class exists.

---

## Session 506 Ideas

1. Audit all spiders in `SPIDER_TARGET_URLS` to see if any others have proper classes that should be used instead
2. Add monitoring to track spider execution success rates
3. Continue standardizing spider patterns across the codebase
