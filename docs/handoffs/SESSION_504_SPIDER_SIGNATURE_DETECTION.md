# Session 504: Spider Signature Detection & Legal Spider Fixes

**Date:** December 19, 2025
**Focus:** Fix spiders with different method signatures and Playwright browser installation

## Summary

Continuing from Session 503's spider fixes, this session addressed the remaining spiders showing "partial" status by:
1. Adding signature detection logic to handle different `fetch_data()` method patterns
2. Installing Playwright browsers for legal spiders
3. Fixing FindLaw spider's constructor signature

## Problem

After Session 503 fixes, several spiders still showed "partial" status with 0 items:
- Legal spiders (colorado_family_law, justia_family_law) - Playwright not installed + different signature
- Session 495 spiders (crunchbase, venturebeat, etc.) - Already fixed by fetch_data support
- FindLaw spider - Constructor didn't accept standard spider kwargs
- Discord training spider - Fixed by signature detection

## Root Causes

### 1. Different Method Signatures
Some spiders use `fetch_data(target: SpiderTarget)` (standard BaseIntelligenceSpider pattern), while others use `fetch_data(max_results: int = 100)` (legal spiders pattern).

### 2. Playwright Not Installed
Legal spiders using Playwright (colorado_family_law, justia_family_law) failed because browsers weren't installed:
```
Executable doesn't exist at /Users/donkeyking/Library/Caches/ms-playwright/chromium_headless_shell-1187
```

### 3. FindLaw Constructor Mismatch
FindLaw spider had `__init__(self)` with no parameters, but tasks.py passes `spider_id`, `targets`, etc.

## Fixes Applied

### 1. core/tasks.py - Signature Detection (3 locations)

Added `inspect.signature()` to detect method signature and call appropriately:

**Lines 172, 310, 838** (all 3 locations where fetch_data is called):
```python
elif hasattr(spider, 'fetch_data'):
    import asyncio
    import inspect
    from ai_core.spiders.base_spider import SpiderTarget

    async def run_fetch():
        # Session 503: Detect method signature - some spiders use fetch_data(target),
        # others use fetch_data(max_results=100)
        fetch_method = spider.fetch_data
        sig = inspect.signature(fetch_method)
        params = list(sig.parameters.keys())

        # Check first param type hint or name
        first_param = params[0] if params else None
        if first_param and first_param in ('target', 'url'):
            # Standard BaseIntelligenceSpider pattern
            target = SpiderTarget(url='internal://spider-execution')
            raw = await spider.fetch_data(target)
        else:
            # Legal spiders pattern: fetch_data(max_results=100)
            if asyncio.iscoroutinefunction(fetch_method):
                raw = await spider.fetch_data()
            else:
                raw = spider.fetch_data()
        # ... process_data handling
```

### 2. Playwright Browser Installation

```bash
.venv/bin/playwright install chromium
# Downloaded Chromium 140.0.7339.16
```

### 3. findlaw_spider.py - Fixed Constructor

```python
# Before
def __init__(self):
    ...

# After
def __init__(self, spider_id: str = 'findlaw', targets: List = None,
             subscribers: List = None, redis_config: Dict = None, **kwargs):
    self.spider_id = spider_id
    ...
```

## Verification Results

### Spider Status After Fixes:
- **67 spiders with success status** (up from previous runs)
- **5 partial** (stale data from before Celery restart)
- **0 failed**

### Individual Spider Tests:
| Spider | Status | Items |
|--------|--------|-------|
| discord_training | SUCCESS | 1 (768 conversations inside) |
| crunchbase | SUCCESS | 10 articles |
| kickstarter | SUCCESS | 28 projects |
| findlaw | SUCCESS | 5 articles |
| colorado_family_law | SUCCESS | 55 forms |
| kaggle | SUCCESS | 45 items |
| etherscan_api | SUCCESS | 31 items |

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | Added signature detection in 3 locations (+87 lines) |
| `ai_core/spiders/specialized/findlaw_spider.py` | Fixed constructor (+12 lines) |

## Technical Notes

### Signature Detection Logic
Uses Python's `inspect.signature()` to examine method parameters at runtime:
- If first parameter is `target` or `url` -> call with SpiderTarget
- Otherwise -> call without arguments (uses defaults)

### Async/Sync Handling
Also added `asyncio.iscoroutinefunction()` checks for spiders that have sync `fetch_data` methods:
```python
if asyncio.iscoroutinefunction(fetch_method):
    raw = await spider.fetch_data()
else:
    raw = spider.fetch_data()
```

## Next Steps for Session 505+

1. Monitor spider execution logs to ensure all 72 spiders consistently collect data
2. Consider standardizing all spiders to use the same `fetch_data(target)` signature
3. Add more legal spiders using Playwright pattern (now that browsers are installed)

## Dependencies

- Playwright browsers installed: Chromium 140.0.7339.16
- Python `inspect` module (stdlib)
