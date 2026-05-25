# Session 503: Spider API Fixes (Etherscan + Kaggle)

**Date:** December 19, 2025
**Focus:** Fix broken spider data collection for Etherscan API and Kaggle API spiders

## Problem

Spider operations dashboard showed "partial" status with 0 items for:
- `etherscan_api` - Always returning empty results despite valid API key
- `kaggle` - 401 Unauthenticated errors with new API token

## Root Causes Identified

### 1. Spider Orchestration Gap (core/tasks.py)
The spider execution code in `core/tasks.py` only looked for `scrape` or `collect_data` methods:
```python
# OLD - only checked these methods
if hasattr(spider, 'fetch'):
    data = spider.fetch()
elif hasattr(spider, 'scrape'):
    data = asyncio.run(spider.scrape())
# MISSING: fetch_data(target) pattern!
```

Many spiders (including Etherscan and Kaggle) use `fetch_data(target)` pattern from BaseIntelligenceSpider.

### 2. Wrong IntelligenceData Parameters (etherscan_api_spider.py)
The Etherscan spider used incorrect parameter names:
```python
# WRONG parameters
IntelligenceData(
    source=self.spider_id,        # Wrong - should be spider_id
    url="https://etherscan.io",   # Wrong - should be source_url
    category='blockchain',         # Wrong - should be data_type
    relevance_score=score,         # Wrong - should be quality_score
)
```

### 3. Kaggle Authentication Change (kaggle_spider.py)
Kaggle changed their API authentication:
- **Old tokens**: Use Basic auth with `username:key`
- **New KGAT_* tokens**: Use Bearer auth with just the token

## Fixes Applied

### 1. core/tasks.py - Added fetch_data Support (3 locations)

**Location 1 - dispatch_spiders_by_category (lines 155-198)**
**Location 2 - execute_single_spider (lines 239-279)**
**Location 3 - Main spider execution fallback (lines 741-762)**

Each location now includes:
```python
elif hasattr(spider, 'fetch_data'):
    import asyncio
    from ai_core.spiders.base_spider import SpiderTarget

    async def run_fetch():
        target = SpiderTarget(url='internal://spider-execution')
        raw = await spider.fetch_data(target)
        if raw and hasattr(spider, 'process_data'):
            result = await spider.process_data(raw, target)
            if result:
                return {'items': [result.content] if hasattr(result, 'content') else [], 'raw_data': raw}
        return raw if raw else {'items': []}

    data = asyncio.run(run_fetch())
```

### 2. etherscan_api_spider.py - Fixed IntelligenceData (lines 232-251)

```python
return IntelligenceData(
    spider_id=self.spider_id,
    source_url="https://etherscan.io",
    data_type='blockchain',
    content={
        'transactions': large_transfers,
        'whale_alerts': whale_alerts,
        'recent_blocks': raw_data.get('recent_blocks', []),
        'summary': summary,
        'insights': insights,
        'title': f"Ethereum Network Activity: {summary}",
    },
    metadata={
        'relevance_score': self._calculate_relevance(raw_data),
        'freshness': 1.0,
    },
    quality_score=self._calculate_relevance(raw_data) / 100.0,
    timestamp=datetime.now(timezone.utc)
)
```

### 3. kaggle_spider.py - Updated Auth System (lines 53-70)

**Constructor - Support multiple env var names:**
```python
# Session 503: Support KAGGLE_API_TOKEN (official), KAGGLE_API_KEY, and KAGGLE_KEY (legacy)
self.kaggle_key = os.getenv('KAGGLE_API_TOKEN', os.getenv('KAGGLE_API_KEY', os.getenv('KAGGLE_KEY', '')))
```

**Auth header - Detect token type:**
```python
def _get_auth_header(self) -> Dict[str, str]:
    if self.kaggle_key:
        # Session 503: New KGAT_* tokens use Bearer auth, old tokens use Basic auth
        if self.kaggle_key.startswith('KGAT_'):
            return {'Authorization': f'Bearer {self.kaggle_key}'}
        elif self.kaggle_username:
            # Legacy Basic auth for old-style keys
            credentials = f"{self.kaggle_username}:{self.kaggle_key}"
            encoded = base64.b64encode(credentials.encode()).decode()
            return {'Authorization': f'Basic {encoded}'}
    return {}
```

## Verification Results

```
=== Spider Verification ===
Kaggle: 15 competitions, 15 datasets (source: kaggle_api)
Etherscan: 30 transfers, 0 whale alerts, 1 blocks
✅ Both spiders working!
```

**Real data now being collected:**
- Kaggle: Competitions like "Deep Past Challenge", "Diabetes Prediction", "AI Mathematical Olympiad"
- Etherscan: Transactions from Binance, Coinbase, Aave v3 (current block ~24,049,789)

## Environment Variables

Required in `.env`:
```bash
KAGGLE_API_TOKEN=KGAT_xxxx...    # New official format (Bearer auth)
KAGGLE_USERNAME=your_username    # Still needed for profile info
ETHERSCAN_API_KEY=your_key       # Free tier: 5 calls/sec, 100k/day
```

## Files Modified

1. `core/tasks.py` - 3 locations for fetch_data method support
2. `ai_core/spiders/specialized/etherscan_api_spider.py` - Fixed IntelligenceData parameters
3. `ai_core/spiders/specialized/kaggle_spider.py` - Updated env var and auth method

## Next Steps for Session 504

1. Monitor spider execution logs to verify consistent data collection
2. Consider adding more blockchain spiders (BSCScan, PolygonScan) using same pattern
3. May want to use official `kaggle` Python package for advanced features

## Dependencies

- Installed `kaggle` Python package for potential future use
- Etherscan API v2 endpoints (v1 deprecated Dec 2025)
