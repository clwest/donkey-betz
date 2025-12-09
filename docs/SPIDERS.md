# Spider Network Reference

**Last Updated:** Session 397 (December 8, 2025)

---

## Overview

The Spider Network consists of **62 registered spiders**, with **54 actually working** after Session 397 cleanup. Session 397 removed 26 broken spiders that had no public API.

---

## Quick Stats

| Metric | Count |
|--------|-------|
| Total Registered | 62 |
| **Actually Working** | **54** |
| With Configured URLs | 48 |
| Need API Keys | 6 |
| Records in DB | 13,700+ |
| Searchable (with embeddings) | ~2,000 |

**Session 397:** Cleaned registry - removed 26 broken spiders (no public API/placeholders)

---

## Spider Status (Session 397 Update)

### Working Spiders (48)

These spiders are configured and collecting real data:

| Spider | Source Type | Status |
|--------|-------------|--------|
| techcrunch | RSS | Working |
| youtube | YouTube API | Working (via GOOGLE_API_KEY) |
| theverge | RSS | Working |
| wired | RSS | Working |
| mit_tech_review | RSS | Working |
| axios | RSS | Working |
| hackernews | JSON API | Working (Session 394 fixed) |
| devto | JSON API | Working |
| remoteok | JSON API | Working |
| weworkremotely | RSS | Working |
| coingecko | JSON API | Working |
| yahoo_finance | JSON API | Working |
| dribbble | HTML Scrape | Blocked (Cloudflare) |
| behance | RSS | Working |
| producthunt | RSS | Working |
| medium | RSS | Working |
| hashnode | JSON API | Working |
| udemy | JSON API | Working |
| kickstarter | JSON API | Blocked (403) |
| indiegogo | JSON API | Working |
| reddit | JSON API | Working (8 subreddits) |
| indiehackers | RSS | Working |
| bluesky | AT Protocol | Needs API keys |
| youtube | YouTube API | Needs API key |
| discord | Discord API | Needs bot token |

#### Session 395 Additions (Phase 1 - 11 spiders)
| Spider | Source Type | Status |
|--------|-------------|--------|
| bbc | RSS | Working |
| cnn | RSS | Working |
| npr | RSS | Working |
| reuters_rss | RSS | Working |
| arstechnica | RSS | Working |
| substack | RSS | Working (3 newsletters) |
| lifehacker | RSS | Working |
| variety | RSS | Working |
| smashingmagazine | RSS | Working |
| openmeteo | JSON API | Working |
| huggingface | JSON API | Working |

#### Session 396 Additions (Phase 2 - 8 spiders)
| Spider | Source Type | Status |
|--------|-------------|--------|
| noaa_weather | NOAA GeoJSON API | Working (weather alerts) |
| github | GitHub API | Working (trending AI repos) |
| github_jobs | GitHub API | Working (good first issues) |
| coingecko_trending | CoinGecko API | Working |
| science | RSS | Working (ScienceDaily, Phys.org, Nature) |
| health | RSS | Working (STAT News, KFF, FierceHealthcare) |
| education_rss | RSS | Working (EdSurge, Chronicle) |
| business_news | RSS | Working (Bloomberg, Fortune) |

#### Session 397 Additions (Phase 3 - 7 spiders)
| Spider | Source Type | Status |
|--------|-------------|--------|
| polygon_finance | Polygon.io API | Working (market news) |
| etherscan | Etherscan V2 API | Working (ETH supply/blocks) |
| newsapi | NewsAPI.org | Working (tech headlines) |
| giphy | Giphy API | Working (trending GIFs) |
| unsplash | Unsplash API | Working (popular photos) |
| adzuna | Adzuna API | Working (remote jobs) |
| finnhub | Finnhub API | Working (stock quotes, market news) |

### Session 397 Cleanup - Removed Spiders (26)

These spiders were removed from the registry because they have no public API:

**Freelance Platforms (6):** toptal, guru, peopleperhour, ninetyninedesigns, flexjobs, angellist
**Education (2):** teachable, skillshare
**Financial (4):** opensea, seekingalpha, bloomberg_terminal, reuters_eikon
**Tech (2):** kaggle, stackoverflow_jobs
**Creative Assets (5):** envato, creativemarket, adobestock, shutterstock, canva
**AI/Creative Tools (4):** midjourney, civitai, runwayml, replicate
**Digital Products (4):** etsy, lemonsqueezy, sellfy, appsumo
**Content Creation (3):** convertkit, notion, figma
**Content (3):** gumroad, patreon, kofi
**Placeholders (5):** financial, innovation, social_sentiment, market_data, news_harvester
**Sports (2):** horse_racing, combat_sports (not in current focus)

### Spiders Needing API Keys (6)

These are registered but need credentials:
- `bluesky` - Needs BLUESKY_IDENTIFIER + BLUESKY_PASSWORD
- `discord` - Needs DISCORD_BOT_TOKEN
- `spotify` - Needs SPOTIFY_CLIENT_ID + SPOTIFY_CLIENT_SECRET (OAuth)
- `sec_edgar` - SEC_API_KEY (available in .env, needs testing)

---

## Semantic Search (Session 394)

Spider data can be searched semantically using embeddings:

```python
from core.services.spider_semantic_search import get_spider_semantic_search

search = get_spider_semantic_search()

# Semantic search
results = search.semantic_search("AI tools for developers", limit=10)

# Get stats
stats = search.get_embedding_stats()
# {'total_entries': 13783, 'with_embedding': 2006, 'marked_empty': 9298, ...}
```

### Bulk Embedding Command

```bash
python manage.py bulk_embed_spiders              # Process all (7 days)
python manage.py bulk_embed_spiders --batch=200  # Custom batch size
python manage.py bulk_embed_spiders --hours=24   # Only last 24 hours
python manage.py bulk_embed_spiders --dry-run    # Preview without changes
```

### Content Quality Notes

| Spider Type | Content Quality | Embedding Rate |
|-------------|-----------------|----------------|
| RSS Feeds (techcrunch, wired, etc.) | High | ~90% |
| Job Boards (remoteok, weworkremotely) | High | ~90% |
| Dev Content (devto, medium) | High | ~93% |
| Reddit | Medium | ~45% |
| HackerNews (post-fix) | High | Growing |
| Placeholder spiders | None | 0% |

---

## Working Data Sources by Category

### Tech News (9 spiders - 7 working)

| Source | Type | Status | Data |
|--------|------|--------|------|
| HackerNews | JSON API | Working | Top stories, discussions |
| TechCrunch | RSS | Working | Tech news, startups |
| The Verge | RSS | Working | Tech, culture |
| Wired | RSS | Working | Tech, science |
| MIT Tech Review | RSS | Working | Research, innovation |
| Axios | RSS | Working | Tech news |
| Dev.to | JSON API | Working | Developer articles |
| Hashnode | JSON API | Working | Developer blogs |
| ProductHunt | RSS | Working | New products |

### Financial (11 spiders - 2 working)

| Source | Type | Status |
|--------|------|--------|
| CoinGecko | JSON API | Working |
| Yahoo Finance | JSON API | Working |
| Others | Various | **NOT CONFIGURED** |

### Jobs (7 spiders - 2 working)

| Source | Type | Status |
|--------|------|--------|
| RemoteOK | JSON API | Working |
| WeWorkRemotely | RSS | Working |
| Adzuna | API | **NOT CONFIGURED** (easy fix) |
| FlexJobs | N/A | **No public API** |
| Others | Various | **NOT CONFIGURED** |

### Creative (5 spiders - 1 working)

| Source | Type | Status |
|--------|------|--------|
| Behance | RSS | Working |
| Dribbble | HTML | Blocked by Cloudflare |
| Others | Various | **NOT CONFIGURED** |

### Content (5 spiders - 2 working)

| Source | Type | Status |
|--------|------|--------|
| Medium | RSS | Working |
| ProductHunt | RSS | Working |
| Substack | RSS | **NOT CONFIGURED** (easy fix) |
| Patreon | API | **NOT CONFIGURED** |
| Ko-fi | N/A | **No public API** |

### Community (3 spiders - 2 working)

| Source | Type | Status |
|--------|------|--------|
| Reddit | JSON API | Working (8 subreddits) |
| IndieHackers | RSS | Working |
| Discord | Bot API | Needs token |

**Reddit Subreddits Monitored:**
- r/webdev, r/MachineLearning, r/StableDiffusion
- r/Entrepreneur, r/freelance, r/startups
- r/SideProject, r/ChatGPT

### Crowdfunding (2 spiders - 1 working)

| Source | Type | Status |
|--------|------|--------|
| Indiegogo | JSON API | Working |
| Kickstarter | JSON API | Blocked (403) |

---

## Fix Plan (Session 395)

### Phase 1: Quick Wins - Add RSS Feeds (25 spiders)

These have public RSS feeds - just add URLs:

```python
# ai_core/spiders/real_data_collector.py
SPIDER_TARGET_URLS = {
    # ... existing ...
    'bbc': ['http://feeds.bbci.co.uk/news/rss.xml'],
    'cnn': ['http://rss.cnn.com/rss/cnn_topstories.rss'],
    'npr': ['https://feeds.npr.org/1001/rss.xml'],
    'arstechnica': ['https://feeds.arstechnica.com/arstechnica/index'],
    'lifehacker': ['https://lifehacker.com/rss'],
    'smashingmagazine': ['https://www.smashingmagazine.com/feed/'],
    'variety': ['https://variety.com/feed/'],
}
```

### Phase 2: Free APIs (15 spiders)

These need free API registration:
- OpenMeteo (no key needed!)
- HuggingFace, Unsplash, Adzuna, NewsAPI

### Phase 3: Cleanup

Remove or disable spiders with no public API:
- FlexJobs, Toptal, Guru, etc.

**Full plan:** `docs/handoffs/SESSION_395_SPIDER_AUDIT_AND_ACTION_PLAN.md`

---

## SpiderIntelligenceService

**Location:** `core/services/spider_intelligence.py`

### Basic Usage

```python
from core.services.spider_intelligence import SpiderIntelligenceService

service = SpiderIntelligenceService()
```

### Methods

#### get_trending_topics()
Get top trending topics across all sources.

```python
topics = service.get_trending_topics(
    hours=24,  # Look back period
    limit=10   # Number of topics
)
# Returns: [{'topic': 'AI', 'count': 42, 'sources': ['hackernews', 'techcrunch']}]
```

#### get_tech_trends()
Get tech discussions with optional topic filtering.

```python
trends = service.get_tech_trends(
    hours=72,
    limit=15,
    topic_filter='ai'  # ai, web, security, cloud, design
)
```

#### Topic Filters

| Filter | Keywords Matched |
|--------|-----------------|
| `ai` | AI, ML, machine learning, neural network, GPT, LLM, deep learning |
| `web` | JavaScript, React, Vue, CSS, HTML, web development, frontend |
| `security` | cybersecurity, encryption, privacy, authentication, hacking |
| `cloud` | AWS, Azure, Kubernetes, Docker, serverless, DevOps |
| `design` | UI, UX, design, typography, branding, Figma, illustration |

---

## Running Spiders

### Via Celery (Recommended)

```bash
# Start Celery worker
make celery

# Spiders run on schedule defined in core/celery.py
# Default: Every 30 minutes for most spiders
```

### Manual Execution

```bash
# Trigger spider network manually
python manage.py shell -c "
from core.tasks import run_spider_network
run_spider_network()
"
```

### Check Spider Status

```bash
# Count spiders
python -c "
from ai_core.spiders.spider_registry import SpiderRegistry
r = SpiderRegistry()
print(f'Total: {r.get_spider_count()[\"total\"]} spiders')
"

# Check recent data
python manage.py shell -c "
from core.models_unified_system import SpiderData
from django.utils import timezone
from datetime import timedelta

recent = SpiderData.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=1)
).count()
print(f'Records in last hour: {recent}')
"

# Check which spiders have real data vs placeholder
python manage.py shell -c "
from ai_core.spiders.real_data_collector import SPIDER_TARGET_URLS
print(f'Spiders with configured URLs: {len(SPIDER_TARGET_URLS)}')
for name in sorted(SPIDER_TARGET_URLS.keys()):
    print(f'  - {name}')
"
```

---

## Configuration

### SPIDER_TARGET_URLS

**Location:** `ai_core/spiders/real_data_collector.py`

This is where URLs are configured for each spider. If a spider isn't in this dict, it returns placeholder data.

```python
SPIDER_TARGET_URLS = {
    'techcrunch': ['https://techcrunch.com/feed/'],
    'theverge': ['https://www.theverge.com/rss/index.xml'],
    # ... etc
}
```

### API Spiders

Some spiders use custom API logic instead of URLs:
- `bluesky` - Requires `BLUESKY_IDENTIFIER` and `BLUESKY_PASSWORD` env vars
- `youtube` - Requires `GOOGLE_API_KEY` env var
- `discord` - Requires `DISCORD_BOT_TOKEN` env var

---

## See Also

- [SESSION_395_SPIDER_AUDIT_AND_ACTION_PLAN.md](handoffs/SESSION_395_SPIDER_AUDIT_AND_ACTION_PLAN.md) - Full audit and fix plan
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CAPABILITIES.md](CAPABILITIES.md) - Full feature list
- [AGENTS.md](AGENTS.md) - Agent reference
