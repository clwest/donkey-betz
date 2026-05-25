# Session 395: Spider Audit and Action Plan

**Date:** December 8, 2025
**Focus:** Comprehensive audit of all 102 registered spiders and action plan for fixing

---

## Executive Summary

**Critical Finding:** Only 21 of 102 registered spiders (20%) have configured data sources!

| Status | Count | Percentage |
|--------|-------|------------|
| Configured with URLs | 21 | 20.6% |
| API spiders (custom logic) | 3 | 2.9% |
| **UNCONFIGURED (broken)** | **78** | **76.5%** |

This explains why only ~10% of spider data has embeddings - most spiders return "no real URLs configured" placeholder messages.

---

## Current Spider Status

### Working Spiders (24 total)

#### URL-Configured Spiders (21)
| Spider | Source Type | URL |
|--------|-------------|-----|
| techcrunch | RSS | `https://techcrunch.com/feed/` |
| theverge | RSS | `https://www.theverge.com/rss/index.xml` |
| wired | RSS | `https://www.wired.com/feed/rss` |
| mit_tech_review | RSS | `https://www.technologyreview.com/feed/` |
| axios | RSS | `https://api.axios.com/feed/` |
| hackernews | JSON API | `https://hacker-news.firebaseio.com/v0/topstories.json` |
| devto | JSON API | `https://dev.to/api/articles?per_page=30` |
| remoteok | JSON API | `https://remoteok.com/api` |
| weworkremotely | RSS | `https://weworkremotely.com/categories/remote-programming-jobs.rss` |
| coingecko | JSON API | `https://api.coingecko.com/api/v3/coins/markets?...` |
| yahoo_finance | JSON API | `https://query1.finance.yahoo.com/v8/finance/chart/SPY` |
| dribbble | HTML | `https://dribbble.com/shots/popular` |
| behance | RSS | `https://www.behance.net/feeds/projects` |
| producthunt | RSS | `https://www.producthunt.com/feed` |
| medium | RSS | `https://medium.com/feed/topic/technology` |
| hashnode | JSON API | `https://hashnode.com/api/feed/best` |
| udemy | JSON API | `https://www.udemy.com/api-2.0/discovery-units/bestseller/` |
| kickstarter | JSON API | `https://www.kickstarter.com/discover/advanced.json` |
| indiegogo | JSON API | `https://www.indiegogo.com/private_api/discover/main` |
| reddit | JSON API | `https://www.reddit.com/r/*/hot.json` (8 subreddits) |
| indiehackers | RSS | `https://www.indiehackers.com/feed.xml` |

#### API Spiders with Custom Logic (3)
| Spider | API Type | Status |
|--------|----------|--------|
| bluesky | AT Protocol | Requires `BLUESKY_IDENTIFIER` and `BLUESKY_PASSWORD` |
| youtube | YouTube Data API v3 | Requires `GOOGLE_API_KEY` |
| discord | Discord Bot API | Requires `DISCORD_BOT_TOKEN` |

---

## Unconfigured Spiders Analysis (78 total)

### Tier 1: Easy to Fix - Public RSS Feeds (25 spiders)

These have public RSS feeds available - just need URLs added:

| Spider | Category | RSS Feed URL |
|--------|----------|--------------|
| bbc | news | `http://feeds.bbci.co.uk/news/rss.xml` |
| cnn | news | `http://rss.cnn.com/rss/cnn_topstories.rss` |
| npr | news | `https://feeds.npr.org/1001/rss.xml` |
| reuters_rss | news | `https://www.reuters.com/rssFeed/topNews` |
| arstechnica | tech | `https://feeds.arstechnica.com/arstechnica/index` |
| lifehacker | lifestyle | `https://lifehacker.com/rss` |
| smashingmagazine | web_dev | `https://www.smashingmagazine.com/feed/` |
| variety | entertainment | `https://variety.com/feed/` |
| substack | content | `https://{publication}.substack.com/feed` (multiple) |
| education_rss | education | Various education blogs |
| science | science | Various science feeds |
| health | health | Various health feeds |
| food | food | Various food blogs |
| travel | travel | Various travel blogs |
| parenting | parenting | Various parenting blogs |
| business_news | business | Various business feeds |
| real_estate | real_estate | Various real estate feeds |
| government | government | Government news feeds |
| library | library | Library/book feeds |
| spotify | entertainment | Spotify blog RSS |

**Estimated time to fix: 2-3 hours**

### Tier 2: Easy to Fix - Free Public APIs (15 spiders)

These have free public APIs requiring registration but no cost:

| Spider | Category | API | Notes |
|--------|----------|-----|-------|
| openmeteo | weather | Open-Meteo | **No API key needed!** |
| noaa_weather | weather | NOAA | Public API |
| huggingface | ai_ml | HuggingFace Hub API | Free tier available |
| kaggle | ai_ml | Kaggle API | Free with account |
| unsplash | visual | Unsplash API | Free tier: 50 req/hr |
| giphy | social | Giphy API | Free tier available |
| adzuna | jobs | Adzuna API | Free tier available |
| finnhub | financial | Finnhub API | Free tier: 60 calls/min |
| polygon_finance | financial | Polygon.io | Free tier available |
| polygon_gaming | gaming | Polygon.io | Free tier available |
| newsapi | news | NewsAPI | Free tier: 100 req/day |
| etherscan | financial | Etherscan API | Free tier: 5 calls/sec |
| opensea | financial | OpenSea API | Free tier available |

**Estimated time to fix: 4-6 hours (includes registration)**

### Tier 3: Medium Effort - Requires API Keys/Accounts (18 spiders)

These require paid API keys or more complex setup:

| Spider | Category | Requirement | Notes |
|--------|----------|-------------|-------|
| github | tech | GitHub API | Rate limited without token |
| github_jobs | tech | GitHub API | Same as above |
| stackoverflow_jobs | tech | Stack Overflow | API key needed |
| sec_edgar | financial | SEC EDGAR | Free but complex |
| seekingalpha | financial | SeekingAlpha API | Premium API |
| bloomberg_terminal | financial | Bloomberg API | Enterprise only |
| reuters_eikon | financial | Refinitiv API | Enterprise only |
| civitai | ai_creative | Civitai API | API key needed |
| replicate | ai_creative | Replicate API | API key + billing |
| runwayml | ai_creative | Runway API | API key + billing |
| midjourney | ai_creative | No public API | Would need scraping |
| convertkit | content_creation | ConvertKit API | Account required |
| figma | content_creation | Figma API | OAuth required |
| notion | content_creation | Notion API | Integration required |
| gumroad | digital_products | Gumroad API | OAuth required |
| patreon | content | Patreon API | OAuth required |
| kofi | content | No public API | Would need scraping |
| teachable | education | No public API | Would need scraping |

**Estimated time to fix: 8-12 hours**

### Tier 4: Hard to Fix - No Public API/Blocked (12 spiders)

These are blocked, require enterprise access, or have no public API:

| Spider | Category | Issue |
|--------|----------|-------|
| flexjobs | remote_work | No public API (employer-only) |
| toptal | freelance | No public API |
| guru | freelance | No public API |
| peopleperhour | freelance | No public API |
| angellist | freelance | API deprecated |
| ninetyninedesigns | design | No public API |
| skillshare | education | No public API |
| adobestock | creative_assets | Enterprise API only |
| shutterstock | creative_assets | Paid API only |
| envato | creative_assets | Affiliate API only |
| creativemarket | creative_assets | No public API |
| canva | creative_assets | No public API |

**Recommendation: Remove or mark as "coming soon"**

### Tier 5: Internal/Placeholder Spiders (8 spiders)

These appear to be internal placeholders or aggregators:

| Spider | Category | Issue |
|--------|----------|-------|
| financial | financial | Generic placeholder |
| innovation | innovation | Generic placeholder |
| market_data | market | Generic placeholder |
| news_harvester | news | Generic placeholder |
| social_sentiment | social | Generic placeholder |
| combat_sports | sports_betting | No configured source |
| horse_racing | sports_betting | No configured source |
| appsumo | digital_products | No public API |

**Recommendation: Remove or repurpose**

---

## Action Plan

### Phase 1: Quick Wins (Day 1)
**Add RSS feeds for 25 spiders**

Priority spiders to fix first:
1. `bbc` - Major news source
2. `cnn` - Major news source
3. `npr` - Quality news source
4. `arstechnica` - Tech news
5. `smashingmagazine` - Web dev
6. `variety` - Entertainment
7. `lifehacker` - Lifestyle/tips

### Phase 2: Free APIs (Day 2-3)
**Register and configure 15 API-based spiders**

Priority:
1. `openmeteo` - No API key needed!
2. `huggingface` - AI/ML content
3. `unsplash` - Visual trends
4. `adzuna` - Job listings
5. `newsapi` - News aggregation

### Phase 3: Cleanup (Day 4)
**Remove or disable non-functional spiders**

1. Remove 8 internal placeholders
2. Disable 12 "no public API" spiders
3. Mark 18 "API key required" spiders as configurable

### Phase 4: Documentation
**Update all docs to reflect reality**

1. Update `docs/SPIDERS.md` with accurate counts
2. Update `CLAUDE.md` with actual working spiders
3. Add configuration guide for API-key spiders

---

## Implementation Details

### Adding an RSS Feed Spider

Add to `SPIDER_TARGET_URLS` in `ai_core/spiders/real_data_collector.py`:

```python
SPIDER_TARGET_URLS = {
    # ... existing spiders ...

    # NEW - News RSS Feeds
    'bbc': ['http://feeds.bbci.co.uk/news/rss.xml'],
    'cnn': ['http://rss.cnn.com/rss/cnn_topstories.rss'],
    'npr': ['https://feeds.npr.org/1001/rss.xml'],
    'arstechnica': ['https://feeds.arstechnica.com/arstechnica/index'],
    'lifehacker': ['https://lifehacker.com/rss'],
    'smashingmagazine': ['https://www.smashingmagazine.com/feed/'],
    'variety': ['https://variety.com/feed/'],
}
```

### Adding an API Spider

For spiders requiring API calls (like OpenMeteo), add a handler in `real_data_collector.py`:

```python
async def _collect_openmeteo_data() -> Dict[str, Any]:
    """Collect weather data from Open-Meteo (no API key needed!)"""
    url = "https://api.open-meteo.com/v1/forecast?latitude=39.7392&longitude=-104.9903&current_weather=true"
    # ... implementation
```

---

## Expected Results After Fix

| Metric | Before | After |
|--------|--------|-------|
| Working spiders | 24 | 60-70 |
| Embedding rate (all) | 10% | 50-60% |
| Embedding rate (real data) | 80% | 85-90% |
| Data collection per cycle | ~200 items | ~500+ items |

---

## Files to Modify

| File | Changes |
|------|---------|
| `ai_core/spiders/real_data_collector.py` | Add URLs and API handlers |
| `ai_core/spiders/spider_registry.py` | Optionally remove broken spiders |
| `docs/SPIDERS.md` | Update with accurate status |
| `CLAUDE.md` | Update spider counts |
| `.env` | Add API keys for configured APIs |

---

## Related Documents

- [SPIDERS.md](../SPIDERS.md) - Spider network reference
- [SESSION_394_SPIDER_EMBEDDINGS_BULK_PROCESSING.md](SESSION_394_SPIDER_EMBEDDINGS_BULK_PROCESSING.md) - Previous session
