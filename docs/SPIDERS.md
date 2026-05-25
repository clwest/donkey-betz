<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md) (sole authoritative counts per `DOC_LIFECYCLE.md` §2c). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Spider Network Reference

**Last Updated:** Session 1100 (April 26, 2026 — count refresh; original Session 567 audit narrative below)

---

## Overview

**Total Registered Spiders: 80** | **All Working** | **Categories: 41**

The Spider Network collects real-time intelligence from 80 data sources across 41 categories. All spiders are registered in `ai_core/spiders/spider_registry.py` and orchestrated via Celery tasks.

> Source of truth: `docs/PLATFORM_INVENTORY.md`. The "41 categories" figure flagged uncontrolled proliferation (the Session 567 audit promised "20+" as a floor); see `docs/topics/spider-network.md` for consolidation recommendations.

### Architecture

```
SpiderRegistry (80 spiders)
    ↓
SpiderOrchestrator / SpiderArmyOrchestrator
    ↓
SpiderConnectorOrchestrator (Agent-Spider bridge)
    ↓
SpiderDataRouter → SpiderData model → Embeddings
    ↓
SpiderIntelligenceService (Query interface)
```

---

## Quick Stats

| Metric | Count |
|--------|-------|
| **Total Registered** | **80** |
| Working (no auth needed) | 80 |
| Need API Keys | 0 (all currently configured) |
| Playwright-Enabled | 2 |
| Records in DB | ~20,712+ |
| With Embeddings | ~88.1% |
| Data Collection Methods | REST API (32), RSS (30), Web Scraping (10), Playwright (2), JSON (3) |

---

## Spider Categories (77 Total)

### News & Media (10 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | techcrunch | TechCrunch | RSS | ✅ Working |
| 2 | theverge | The Verge | RSS | ✅ Working |
| 3 | bbc | BBC News | RSS | ✅ Working |
| 4 | cnn | CNN | RSS | ✅ Working |
| 5 | npr | NPR | RSS | ✅ Working |
| 6 | axios | Axios | RSS | ✅ Working |
| 7 | reuters_rss | Reuters | RSS | ✅ Working |
| 8 | variety | Variety | RSS | ✅ Working |
| 9 | google_news | Google News | RSS | ✅ Working |
| 10 | newsapi | NewsAPI.org | API | ✅ Working (80k+ sources) |

### Financial & Crypto (9 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | coingecko | CoinGecko | API | ✅ Working |
| 2 | yahoo_finance | Yahoo Finance | API | ✅ Working |
| 3 | polygon_finance | Polygon.io | API | ✅ Working |
| 4 | finnhub | Finnhub | API | ✅ Working |
| 5 | etherscan | Etherscan | API | ✅ Working |
| 6 | etherscan_api | Etherscan V2 | API | ✅ Working |
| 7 | sec_edgar | SEC EDGAR | API | ⚠️ Needs API Key |
| 8 | kalshi | Kalshi | API | ✅ Working (prediction markets) |
| 9 | theodds | The Odds API | API | ✅ Working (40+ bookmakers) |

### Tech & Development (8 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | hackernews | Hacker News | JSON | ✅ Working |
| 2 | devto | Dev.to | API | ✅ Working |
| 3 | github | GitHub | API | ✅ Working |
| 4 | github_jobs | GitHub Jobs | API | ✅ Working |
| 5 | arstechnica | Ars Technica | RSS | ✅ Working |
| 6 | smashingmagazine | Smashing Magazine | RSS | ✅ Working |
| 7 | kickstarter | Kickstarter | JSON | ✅ Working |
| 8 | freecodecamp | freeCodeCamp | RSS | ✅ Working |

### Legal (6 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | courtlistener | CourtListener | API | ✅ Working (court opinions) |
| 2 | findlaw | FindLaw | Scraper | ✅ Working (legal blogs) |
| 3 | lii | Cornell LII | Scraper | ✅ Working (US Code, CFR) |
| 4 | legal_news | Legal News | RSS | ✅ Working |
| 5 | colorado_family_law | CO Judicial | Playwright | ✅ Working (JDF forms) |
| 6 | justia_family_law | Justia | Playwright | ✅ Working (family law) |

### Education (5 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | teachable | Teachable/Thinkific | RSS | ✅ Working |
| 2 | udemy | Udemy (via ClassCentral) | RSS | ✅ Working |
| 3 | coursera | Coursera | RSS | ✅ Working |
| 4 | education_rss | EdWeek, EdSurge | RSS | ✅ Working |
| 5 | kaggle | Kaggle | API | ✅ Working |

### Community & Social (4 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | reddit | Reddit (8+ subreddits) | JSON | ✅ Working |
| 2 | bluesky | BlueSky | API | ⚠️ Needs Credentials |
| 3 | discord | Discord | API | ⚠️ Needs Bot Token |
| 4 | hackernoon | HackerNoon | RSS | ✅ Working |

**Reddit Subreddits:** r/webdev, r/MachineLearning, r/StableDiffusion, r/Entrepreneur, r/freelance, r/startups, r/SideProject, r/ChatGPT

### Design & Creative (2 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | behance | Behance | RSS | ✅ Working |
| 2 | awwwards | Awwwards/Codrops | RSS | ✅ Working |

### Content & Monetization (3 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | medium | Medium | Scraper | ✅ Working |
| 2 | substack | Substack | RSS | ✅ Working |
| 3 | producthunt | Product Hunt | Scraper | ✅ Working |

### Jobs & Freelance (3 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | remoteok | RemoteOK | JSON | ✅ Working |
| 2 | weworkremotely | WeWorkRemotely | RSS | ✅ Working |
| 3 | adzuna | Adzuna | API | ✅ Working |

### AI & Machine Learning (3 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | huggingface | HuggingFace | API | ✅ Working |
| 2 | kaggle | Kaggle | API | ✅ Working |
| 3 | discord_training | HuggingFace Datasets | API | ✅ Working (14 datasets) |

### Startups & VC (3 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | crunchbase | Crunchbase | RSS | ✅ Working |
| 2 | venturebeat | VentureBeat | RSS | ✅ Working |
| 3 | techcrunch_startups | TechCrunch Startups | RSS | ✅ Working |

### Specialty Tech (5 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | defenseone | DefenseOne | RSS | ✅ Working |
| 2 | mobihealthnews | MobiHealthNews | RSS | ✅ Working |
| 3 | securityweek | SecurityWeek | RSS | ✅ Working |
| 4 | wired | Wired | RSS | ✅ Working |
| 5 | mit_tech_review | MIT Tech Review | RSS | ✅ Working |

### Entertainment (4 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | spotify | Spotify | API | ⚠️ Needs OAuth |
| 2 | giphy | Giphy | API | ✅ Working |
| 3 | youtube | YouTube | API | ⚠️ Needs API Key |
| 4 | polygon_gaming | Polygon Gaming | RSS | ✅ Working |

### Lifestyle (4 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | lifehacker | Lifehacker | RSS | ✅ Working |
| 2 | travel | Lonely Planet, Skift | RSS | ✅ Working |
| 3 | parenting | Parents, Fatherly | RSS | ✅ Working |
| 4 | food | Serious Eats, Epicurious | RSS | ✅ Working |

### Weather (2 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | openmeteo | Open-Meteo | API | ✅ Working |
| 2 | noaa_weather | NOAA | API | ✅ Working |

### Science & Health (3 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | science | Nature, ScienceDaily | RSS | ✅ Working |
| 2 | health | WebMD, Healthline | RSS | ✅ Working |
| 3 | library | Archive.org, arXiv | RSS | ✅ Working |

### Business & Government (2 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | business_news | HBR, Forbes, Inc | RSS | ✅ Working |
| 2 | government | WhiteHouse, FedRegister | RSS | ✅ Working |

### Visual & Media (2 spiders)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | unsplash | Unsplash | API | ✅ Working |
| 2 | giphy | Giphy | API | ✅ Working |

### Real Estate (1 spider)

| # | Spider | Source | Type | Status |
|---|--------|--------|------|--------|
| 1 | real_estate | Realtor, Zillow, Inman | RSS | ✅ Working |

---

## Training Data Spider (Session 420)

The `discord_training` spider collects high-quality conversation data from HuggingFace:

| Feature | Details |
|---------|---------|
| Datasets | 14 HuggingFace datasets |
| Quality Rate | 94% high quality |
| Topics | Business, AI, creative, programming |
| Schedule | Daily 1 AM (50 records), Weekly Sunday (200 records) |

**Tier 1 (Best):** OpenAssistant, Dolly-15k, Alpaca, SlimOrca, Capybara
**Tier 2 (Good):** WizardVicuna, OpenHermes, Topical-Chat
**Tier 3 (Gated):** lmsys-chat-1m (1M+ conversations)

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
| awwwards | RSS | Working (Session 399: renamed from dribbble) |
| behance | RSS | Working |
| producthunt | RSS | Working |
| medium | RSS | Working |
| freecodecamp | RSS | Working (Session 399: renamed from hashnode) |
| coursera | RSS | Working (Session 399: renamed from udemy) |
| kickstarter | JSON API | Blocked (403) |
| techcrunch_startups | RSS | Working (Session 399: renamed from indiegogo) |
| reddit | JSON API | Working (8 subreddits) |
| hackernoon | RSS | Working (Session 399: renamed from indiehackers) |
| bluesky | AT Protocol | Needs API keys |
| youtube | YouTube API | Needs API key |
| discord | Discord API | Needs bot token |

#### Session 395 Additions (Phase 1 - 11 spiders)
| Spider | Source Type | Status |
|--------|-------------|--------|
| bbc | RSS | Working |
| google_news | RSS | Working (Session 399: renamed from cnn) |
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

#### Session 397 Additions (Legal - 4 spiders, 3 working)
| Spider | Source Type | Status |
|--------|-------------|--------|
| courtlistener | REST API (free!) | Working (~20 items - court opinions, case law) |
| findlaw | Web scraping | Working (~25 items - legal blogs, practice areas) |
| lii | Web scraping | Working (~15 items - Cornell Law, US Code, CFR) |
| justia | RSS/Scraping | Blocked (Cloudflare) - Replaced by justia_family_law |

#### Session 403 Additions (Legal - 2 Playwright-enabled spiders)
| Spider | Source Type | Status |
|--------|-------------|--------|
| colorado_family_law | Playwright + Scraping | Working (12 JDF forms, Colorado Judicial Branch) |
| justia_family_law | Playwright + Scraping | Working (Cloudflare bypass, family law topics) |

**Session 403 spiders use Playwright** for JavaScript-rendered content and Cloudflare bypass. They include fallback data for reliability.

**Legal spiders now collect ~80+ items per run** covering court opinions, legal news, legislation, Colorado JDF forms, and family law topics.

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

## Semantic Search (Session 394, Updated Session 398)

Spider data can be searched semantically using embeddings:

```python
from core.services.spider_semantic_search import get_spider_semantic_search

search = get_spider_semantic_search()

# Semantic search - returns SemanticSearchResult objects (use attributes, not .get())
results = search.semantic_search("AI tools for developers", limit=10)
for r in results:
    print(f'[{r.source}] {r.title[:50]} (similarity: {r.similarity:.3f})')

# Get stats
stats = search.get_embedding_stats()
# {'total_entries': 7143, 'with_embedding': 1830, 'marked_empty': 5313, ...}
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
| FreeCodeCamp | RSS | Working | Developer blogs (Session 399: renamed from Hashnode) |
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

### Creative (5 spiders - 2 working)

| Source | Type | Status |
|--------|------|--------|
| Behance | RSS | Working |
| Awwwards | RSS | Working (Session 399: renamed from Dribbble) |
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
| HackerNoon | RSS | Working (Session 399: renamed from IndieHackers) |
| Discord | Bot API | Needs token |

**Reddit Subreddits Monitored:**
- r/webdev, r/MachineLearning, r/StableDiffusion
- r/Entrepreneur, r/freelance, r/startups
- r/SideProject, r/ChatGPT

### Crowdfunding/Startups (2 spiders - 1 working)

| Source | Type | Status |
|--------|------|--------|
| TechCrunch Startups | RSS | Working (Session 399: renamed from Indiegogo) |
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
