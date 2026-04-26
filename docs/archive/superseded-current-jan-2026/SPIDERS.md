<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Spider inventory snapshot
>
> **Where to look now:**
> - [docs/SPIDERS.md](/docs/SPIDERS.md)
> - [docs/topics/spider-network.md](/docs/topics/spider-network.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Spiders Documentation

**Total Spiders:** 77
**Working Spiders:** 72
**Need API Keys:** 5
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Spider Architecture](#spider-architecture)
3. [Spider Categories](#spider-categories)
4. [Complete Spider List](#complete-spider-list)
5. [Data Collection Methods](#data-collection-methods)
6. [Usage](#usage)

---

## Overview

The spider network collects real-time intelligence from 77 data sources across 20+ domains. Data flows through the Knowledge Pipeline to inform agent decisions.

### Data Flow
```
Spider Execution (Celery Beat - every 30 min)
     │
     ▼
SpiderData Model (Raw storage)
     │
     ▼
Embedding Service (Vector embeddings)
     │
     ▼
Spider Bridge Signal
     │
     ▼
AgentKnowledgeSource
     │
     ▼
Agent Prompt Injection
```

### Key Statistics
- **Total Records:** ~20,700+
- **With Embeddings:** ~88.1%
- **Collection Methods:** REST API (32), RSS (30), Web Scraping (10), Playwright (2), JSON (3)

---

## Spider Architecture

### Location
```
ai_core/spiders/
├── spider_registry.py         # Central registry
├── base_spider.py             # Base class
└── specialized/               # 77 spider implementations
    ├── techcrunch_spider.py
    ├── hackernews_spider.py
    ├── coingecko_spider.py
    └── ... (74 more)
```

### Base Spider Class
```python
class BaseIntelligenceSpider:
    name: str
    category: str
    priority: int
    rate_limit: float

    def collect_data(self) -> List[Dict]
    def validate_data(self, data: Dict) -> bool
    def transform_data(self, raw: Dict) -> Dict
```

---

## Spider Categories

### News & Media (10)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **TechCrunchSpider** | techcrunch.com | RSS | Working |
| **TheVergeSpider** | theverge.com | RSS | Working |
| **BBCSpider** | bbc.com | RSS | Working |
| **CNNSpider** | cnn.com | RSS | Working |
| **NPRSpider** | npr.org | RSS | Working |
| **ReutersRSSSpider** | reuters.com | RSS | Working |
| **AxiosSpider** | axios.com | RSS | Working |
| **VarietySpider** | variety.com | RSS | Working |
| **NewsAPISpider** | newsapi.org | API | Working |
| **BusinessNewsSpider** | Multiple | RSS | Working |

### Financial (9)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **CoinGeckoSpider** | coingecko.com | API | Working |
| **YahooFinanceSpider** | finance.yahoo.com | API | Working |
| **PolygonSpider** | polygon.io | API | Working |
| **FinnhubSpider** | finnhub.io | API | Working |
| **EtherscanSpider** | etherscan.io | API | Working |
| **EtherscanAPISpider** | etherscan.io | API V2 | Working |
| **KalshiSpider** | kalshi.com | API | Working |
| **TheOddsSpider** | the-odds-api.com | API | Working |
| **SECSpider** | sec.gov | API | Needs Key |

### Tech (8)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **HackerNewsSpider** | news.ycombinator.com | API | Working |
| **DevToSpider** | dev.to | API | Working |
| **GitHubSpider** | github.com | API | Working |
| **ArsTechnicaSpider** | arstechnica.com | RSS | Working |
| **SmashingMagazineSpider** | smashingmagazine.com | RSS | Working |
| **KickstarterSpider** | kickstarter.com | Scrape | Working |
| **TechCommunitySpider** | Multiple | RSS | Working |
| **WiredSpider** | wired.com | RSS | Working |

### Legal (6)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **CourtListenerSpider** | courtlistener.com | API | Working |
| **FindLawSpider** | findlaw.com | RSS | Working |
| **LegalInformationInstituteSpider** | law.cornell.edu | RSS | Working |
| **ColoradoFamilyLawSpider** | courts.state.co.us | Playwright | Working |
| **JustiaPlaywrightSpider** | justia.com | Playwright | Working |
| **LegalNewsSpider** | Multiple | RSS | Working |

### Education (5)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **TeachableSpider** | teachable.com | RSS | Working |
| **UdemySpider** | elearningindustry.com | RSS | Working |
| **KaggleSpider** | kaggle.com | API | Working |
| **EducationRSSSpider** | Multiple | RSS | Working |
| **HuggingFaceSpider** | huggingface.co | API | Working |

### Specialty Tech (5)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **CrunchbaseSpider** | crunchbase.com | Scrape | Working |
| **VentureBeatSpider** | venturebeat.com | RSS | Working |
| **DefenseOneSpider** | defenseone.com | RSS | Working |
| **MobiHealthNewsSpider** | mobihealthnews.com | RSS | Working |
| **SecurityWeekSpider** | securityweek.com | RSS | Working |

### Community (4)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **RedditSpider** | reddit.com | API | Working |
| **BlueSkySpider** | bsky.app | API | Working |
| **DiscordSpider** | discord.com | API | Working |
| **DiscordTrainingSpider** | HuggingFace | API | Working |

### Jobs & Freelance (6)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **RemoteOKSpider** | remoteok.io | API | Working |
| **WeWorkRemotelySpider** | weworkremotely.com | Scrape | Working |
| **AdzunaSpider** | adzuna.com | API | Working |
| **FlexJobsSpider** | flexjobs.com | Scrape | Working |
| **HimalayasSpider** | himalayas.app | API | Working |
| **ToptalSpider** | toptal.com | Scrape | Working |

### Creative (4)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **BehanceSpider** | behance.net | API | Working |
| **UnsplashSpider** | unsplash.com | API | Working |
| **GiphySpider** | giphy.com | API | Working |
| **YouTubeSpider** | youtube.com | API | Needs Key |

### Science & Weather (4)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **ScienceSpider** | Multiple | RSS | Working |
| **OpenMeteoSpider** | open-meteo.com | API | Working |
| **NOAASpider** | weather.gov | API | Working |
| **HealthSpider** | Multiple | RSS | Working |

### Lifestyle (6)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **LifehackerSpider** | lifehacker.com | RSS | Working |
| **TravelSpider** | Multiple | RSS | Working |
| **ParentingSpider** | Multiple | RSS | Working |
| **FoodSpider** | Multiple | RSS | Working |
| **RealEstateSpider** | Multiple | RSS | Working |
| **GovernmentSpider** | gov sites | RSS | Working |

### Content & Publishing (5)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **MediumIntelligenceSpider** | medium.com | RSS | Working |
| **ContentMonetizationSpider** | substack.com | RSS | Working |
| **LibrarySpider** | Multiple | RSS | Working |
| **SpotifySpider** | spotify.com | API | Needs Key |
| **PolygonGamingSpider** | polygon.com | RSS | Working |

### Innovation (3)

| Spider | Source | Method | Status |
|--------|--------|--------|--------|
| **MITTechReviewSpider** | technologyreview.com | RSS | Working |
| **InnovationSpider** | Multiple | RSS | Working |
| **ProductHuntSpider** | producthunt.com | Scrape | Working |

---

## Complete Spider List (77)

### Working (72)

```
1.  TechCrunchSpider
2.  TheVergeSpider
3.  BBCSpider
4.  CNNSpider
5.  NPRSpider
6.  ReutersRSSSpider
7.  AxiosSpider
8.  VarietySpider
9.  NewsAPISpider
10. BusinessNewsSpider
11. CoinGeckoSpider
12. YahooFinanceSpider
13. PolygonSpider
14. FinnhubSpider
15. EtherscanSpider
16. EtherscanAPISpider
17. KalshiSpider
18. TheOddsSpider
19. HackerNewsSpider
20. DevToSpider
21. GitHubSpider
22. ArsTechnicaSpider
23. SmashingMagazineSpider
24. KickstarterSpider
25. TechCommunitySpider
26. WiredSpider
27. CourtListenerSpider
28. FindLawSpider
29. LegalInformationInstituteSpider
30. ColoradoFamilyLawSpider
31. JustiaPlaywrightSpider
32. LegalNewsSpider
33. TeachableSpider
34. UdemySpider
35. KaggleSpider
36. EducationRSSSpider
37. HuggingFaceSpider
38. CrunchbaseSpider
39. VentureBeatSpider
40. DefenseOneSpider
41. MobiHealthNewsSpider
42. SecurityWeekSpider
43. RedditSpider
44. BlueSkySpider
45. DiscordSpider
46. DiscordTrainingSpider
47. RemoteOKSpider
48. WeWorkRemotelySpider
49. AdzunaSpider
50. FlexJobsSpider
51. HimalayasSpider
52. ToptalSpider
53. BehanceSpider
54. UnsplashSpider
55. GiphySpider
56. ScienceSpider
57. OpenMeteoSpider
58. NOAASpider
59. HealthSpider
60. LifehackerSpider
61. TravelSpider
62. ParentingSpider
63. FoodSpider
64. RealEstateSpider
65. GovernmentSpider
66. MediumIntelligenceSpider
67. ContentMonetizationSpider
68. LibrarySpider
69. PolygonGamingSpider
70. MITTechReviewSpider
71. InnovationSpider
72. ProductHuntSpider
```

### Need API Keys (5)

```
1. SECSpider - SEC_API_KEY
2. YouTubeSpider - YOUTUBE_API_KEY
3. SpotifySpider - SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
4. BloombergSpider - BLOOMBERG_API_KEY
5. LinkedInSpider - LINKEDIN_API_KEY
```

---

## Data Collection Methods

### REST API (32 spiders)
Direct API calls with rate limiting:
```python
response = requests.get(
    "https://api.coingecko.com/api/v3/coins/markets",
    params={"vs_currency": "usd", "order": "market_cap_desc"}
)
```

### RSS Feeds (30 spiders)
Standard RSS/Atom parsing:
```python
feed = feedparser.parse("https://techcrunch.com/feed/")
for entry in feed.entries:
    yield transform_entry(entry)
```

### Web Scraping (10 spiders)
BeautifulSoup-based extraction:
```python
soup = BeautifulSoup(response.text, 'html.parser')
articles = soup.find_all('article', class_='post')
```

### Playwright (2 spiders)
JavaScript-rendered content:
```python
async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto(url)
    content = await page.content()
```

### JSON Endpoints (3 spiders)
Direct JSON file fetching:
```python
response = requests.get("https://data.gov/catalog.json")
data = response.json()
```

---

## Usage

### Run Single Spider
```python
from ai_core.spiders.spider_registry import SpiderRegistry

registry = SpiderRegistry()
spider = registry.get_spider('hackernews')
data = spider.collect_data()
```

### Run Spider via Celery
```python
from core.tasks import execute_single_spider

execute_single_spider.delay('hackernews')
```

### Run Spider Category
```python
from core.tasks import run_spider_by_category

run_spider_by_category.delay('financial')
```

### Run Full Spider Network
```python
from core.tasks import run_spider_network

run_spider_network.delay()
```

### Discord Commands
```
/spiders - View spider network stats
/trending - Get trending topics from spider data
/research <topic> - Search spider data
```

### Query Spider Data
```python
from core.models_unified_system import SpiderData

# Recent data
recent = SpiderData.objects.filter(
    collected_at__gte=timezone.now() - timedelta(hours=24)
)

# By category
financial = SpiderData.objects.filter(category='financial')

# With embeddings (for semantic search)
with_embeddings = SpiderData.objects.exclude(embedding=None)
```

---

## Celery Beat Schedule

Spiders run on automated schedules:

| Schedule | Spiders | Frequency |
|----------|---------|-----------|
| Every 30 min | High priority (HackerNews, etc.) | ~48/day |
| Every hour | Medium priority | ~24/day |
| Every 4 hours | Low priority | ~6/day |
| Daily 1 AM | Training data | 1/day |
| Weekly Sunday | Full network | 1/week |

---

## Adding New Spiders

1. Create spider in `ai_core/spiders/specialized/`
2. Inherit from `BaseIntelligenceSpider`
3. Implement `collect_data()` method
4. Register in `SpiderRegistry`
5. Add Celery Beat schedule if needed

```python
# ai_core/spiders/specialized/my_spider.py
from ai_core.spiders.base_spider import BaseIntelligenceSpider

class MySpider(BaseIntelligenceSpider):
    name = "my_spider"
    category = "tech"
    priority = 2
    rate_limit = 1.0

    def collect_data(self):
        # Implementation
        response = requests.get("https://api.example.com/data")
        return self.transform_data(response.json())
```

---

## Related Documentation

- [CELERY_TASKS.md](CELERY_TASKS.md) - Spider scheduling
- [AGENTS.md](AGENTS.md) - Agents that use spider data
- [AUTONOMOUS_SYSTEMS.md](AUTONOMOUS_SYSTEMS.md) - Spider-triggered situations
