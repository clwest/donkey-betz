# Spider Network Reference

**Last Updated:** Session 273 (November 29, 2025)

---

## Overview

The Spider Network consists of **70 spiders** collecting real-time data from **24 real sources** across **20 categories**. Data is stored in the `SpiderData` model and queried via `SpiderIntelligenceService`.

---

## Quick Stats

| Metric | Count |
|--------|-------|
| Total Spiders | 70 |
| Real Data Sources | 24 |
| Categories | 20 |
| Records in DB | 3,400+ |

---

## Data Sources by Category

### Tech News (9 spiders)

| Source | Type | Data |
|--------|------|------|
| HackerNews | JSON API | Top stories, discussions |
| TechCrunch | RSS | Tech news, startups |
| The Verge | RSS | Tech, culture |
| Wired | RSS | Tech, science |
| MIT Tech Review | RSS | Research, innovation |
| Axios | RSS | Tech news |
| Dev.to | JSON API | Developer articles |
| Hashnode | RSS | Developer blogs |
| ProductHunt | RSS | New products |

### Financial (8 spiders)

| Source | Type | Data |
|--------|------|------|
| CoinGecko | JSON API | Crypto prices, trends |
| Yahoo Finance | JSON API | Stock prices, news |
| SeekingAlpha | RSS | Analysis |
| Bloomberg Terminal | Mock | Market data |
| Reuters Eikon | Mock | Financial news |
| Etherscan | API | Ethereum data |
| OpenSea | API | NFT trends |
| Plus more... | | |

### Jobs (7 spiders)

| Source | Type | Data |
|--------|------|------|
| RemoteOK | JSON API | Remote jobs (real-time) |
| WeWorkRemotely | RSS | Remote positions |
| Adzuna | JSON API | Global job aggregator |
| FlexJobs | RSS | Flexible work |
| AngelList | RSS | Startup jobs |
| GitHub Jobs | Mock | Developer positions |
| StackOverflow Jobs | Mock | Tech jobs |

### Creative (5 spiders)

| Source | Type | Data |
|--------|------|------|
| Dribbble | RSS | Design shots |
| Behance | RSS | Creative projects |
| Unsplash | JSON API | Photography trends |
| Envato | RSS | Digital assets |
| Creative Market | RSS | Design resources |

### AI/Creative Tools (4 spiders)

| Source | Type | Data |
|--------|------|------|
| HuggingFace | API | Models, datasets |
| Midjourney | Mock | AI art trends |
| Civitai | RSS | AI models |
| RunwayML | Mock | AI video |

### Digital Products (5 spiders)

| Source | Type | Data |
|--------|------|------|
| Gumroad | RSS | Digital products |
| Etsy | RSS | Handmade/digital |
| LemonSqueezy | RSS | SaaS products |
| AppSumo | RSS | Software deals |
| Sellfy | RSS | Digital downloads |

### Content (3 spiders)

| Source | Type | Data |
|--------|------|------|
| Medium | RSS | Articles |
| Substack | RSS | Newsletters |
| Patreon | RSS | Creator content |

### Community (1 spider)

| Source | Type | Data |
|--------|------|------|
| Reddit | JSON API | 20+ subreddits |

**Reddit Subreddits Monitored:**
- r/technology, r/programming, r/webdev
- r/MachineLearning, r/artificial
- r/design, r/graphic_design, r/UI_Design
- r/freelance, r/digitalnomad
- r/Entrepreneur, r/startups
- r/SideProject, r/IndieHackers
- r/cryptocurrency, r/Bitcoin
- And more...

### Education (3 spiders)
- Teachable, Udemy, Skillshare

### Legal (4 spiders)
- CourtListener, Justia, FindLaw, LII

### Innovation (3 spiders)
- Indiegogo, Kickstarter, ProductHunt

### Plus 10 more categories...

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
# Returns:
# {
#     'discussions': [{'title': '...', 'url': '...', 'source': 'hackernews'}],
#     'projects': [{'title': '...', 'url': '...', 'source': 'producthunt'}],
#     'sources': {'hackernews': 10, 'devto': 5},
#     'last_updated': '2025-11-29T...'
# }
```

#### Topic Filters

| Filter | Keywords Matched |
|--------|-----------------|
| `ai` | AI, ML, machine learning, neural network, GPT, LLM, deep learning |
| `web` | JavaScript, React, Vue, CSS, HTML, web development, frontend |
| `security` | cybersecurity, encryption, privacy, authentication, hacking |
| `cloud` | AWS, Azure, Kubernetes, Docker, serverless, DevOps |
| `design` | UI, UX, design, typography, branding, Figma, illustration |

#### search_spider_data()
Full-text search across all spider data.

```python
results = service.search_spider_data(
    query="machine learning",
    category="tech",  # Optional
    hours=72,
    limit=20
)
```

#### get_market_insights()
Get financial/crypto market data.

```python
market = service.get_market_insights()
# Returns: {'crypto': [...], 'stocks': [...], 'trends': [...]}
```

#### get_job_market_summary()
Get remote job opportunities.

```python
jobs = service.get_job_market_summary(hours=48, limit=20)
# Returns: {'jobs': [...], 'categories': {...}, 'top_skills': [...]}
```

#### get_creative_trends()
Get design/creative trends from Dribbble, Behance, etc.

```python
creative = service.get_creative_trends(hours=72, limit=10)
# Returns: {'shots': [...], 'styles': [...], 'colors': [...]}
```

#### get_insights_for_prompt()
Get context to enrich AI prompts.

```python
insights = service.get_insights_for_prompt("Create a logo for an AI startup")
# Returns relevant trends, discussions, and style suggestions
```

---

## Spider Data Model

**Location:** `core/models_unified_system.py`

```python
class SpiderData(models.Model):
    spider_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    data = models.JSONField()  # Raw spider output
    title = models.CharField(max_length=500, null=True)
    url = models.URLField(max_length=1000, null=True)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['spider_name', 'created_at']),
            models.Index(fields=['category']),
        ]
```

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
# Run specific spider
python manage.py shell -c "
from ai_core.spiders.spider_registry import SpiderRegistry
registry = SpiderRegistry()
spider = registry.get_spider('hackernews')
spider.execute()
"

# Run all spiders in category
python manage.py shell -c "
from core.tasks import run_spiders_by_category
run_spiders_by_category.delay('tech')
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
```

---

## Spider Registry

**Location:** `ai_core/spiders/spider_registry.py`

```python
from ai_core.spiders.spider_registry import SpiderRegistry

registry = SpiderRegistry()

# List all spiders
spiders = registry.list_spiders()

# Get spider by name
hackernews = registry.get_spider('hackernews')

# Get spiders by category
tech_spiders = registry.get_spiders_by_category('tech')

# Get spider count
counts = registry.get_spider_count()
# {'total': 70, 'by_category': {'tech': 9, 'financial': 8, ...}}
```

---

## Category Mappings

```python
CATEGORY_MAPPINGS = {
    'tech': ['hackernews', 'techcrunch', 'devto', 'theverge', 'wired',
             'mit_tech_review', 'axios', 'hashnode', 'producthunt'],
    'financial': ['coingecko', 'yahoo_finance', 'seekingalpha', ...],
    'jobs': ['remoteok', 'weworkremotely', 'adzuna', 'flexjobs', ...],
    'creative': ['dribbble', 'behance', 'unsplash', 'envato', ...],
    # ... and 16 more categories
}
```

---

## Blacklist (Shopping/Deals Filter)

Spider results are filtered to remove shopping/deals content:

```python
SHOPPING_BLACKLIST = [
    'black friday', 'cyber monday', 'deal', 'discount',
    'sale', 'coupon', 'promo', 'off your', '% off',
    'save $', 'best buy', 'amazon', 'shopping'
]
```

---

## Adding New Spiders

1. Create spider class in `ai_core/spiders/specialized/`
2. Register in `ai_core/spiders/spider_registry.py`
3. Add to category mappings
4. Test execution

```python
# ai_core/spiders/specialized/my_spider.py
from ai_core.spiders.base import BaseSpider

class MySpider(BaseSpider):
    name = "my_source"
    category = "tech"
    source_url = "https://api.example.com/data"

    def execute(self):
        data = self.fetch_json(self.source_url)
        for item in data:
            self.save_data({
                'title': item['title'],
                'url': item['link'],
                'score': item.get('points', 0)
            })
```

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CAPABILITIES.md](CAPABILITIES.md) - Full feature list
- [AGENTS.md](AGENTS.md) - Agent reference
- [SCIFI_FEATURES.md](SCIFI_FEATURES.md) - Sci-fi features
