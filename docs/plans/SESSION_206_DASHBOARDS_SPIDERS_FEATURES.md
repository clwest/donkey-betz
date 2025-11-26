# Session 206+: Dashboards, Advanced Features & Spider Activation

**Created:** November 26, 2025
**Status:** IN PROGRESS
**Previous Work:** Agent Architecture Refactor (Phases 1-5 COMPLETE)

---

## Overview

This document tracks the implementation of three major feature areas:

1. **Phase A: UI Dashboards** - Preferences & Spider visibility
2. **Phase B: Advanced Features** - Smart suggestions, batch learning, multi-agent
3. **Phase C: Spider Activation** - Connect 17 dormant spiders

---

## Phase A: UI Dashboards

### A1: Preferences Dashboard

**Goal:** Let users see and edit their learned preferences

**Location:** New page in AI Studio or modal component

**Features:**
- [ ] View current preferences by domain (image, video, audio, research)
- [ ] Edit/override learned preferences
- [ ] Clear preferences (per domain or all)
- [ ] View preference history/evolution
- [ ] See "learning stage" (new, learning, established)

**Backend Requirements:**
```python
# New API endpoints needed in core/views_preferences.py (CREATE)

GET  /api/preferences/                    # Get all preferences
GET  /api/preferences/{domain}/           # Get domain preferences
PUT  /api/preferences/{domain}/           # Update preferences
DELETE /api/preferences/{domain}/         # Clear preferences
GET  /api/preferences/history/            # Preference evolution over time
```

**Frontend Requirements:**
- New component: `PreferencesDashboard.jsx` or section in ai_image_studio.html
- Domain tabs (Image, Video, Audio, Research)
- Editable preference cards
- Learning stage indicator
- Clear/reset buttons

**Data Structure (from AgentPreferenceManager):**
```python
{
    'image': {
        'style': 'pixar',           # Learned favorite style
        'model': 'sd3-large-turbo', # Preferred model
        'aspect_ratio': '16:9',     # Preferred aspect ratio
        'quality': 'high',          # Quality preference
    },
    'video': {
        'duration': 5,              # Preferred duration
        'quality': 'gen4_turbo',    # Preferred quality
        'aspect_ratio': '16:9',
    },
    'audio': {
        'voice': 'Rachel',          # Preferred voice
        'model': 'eleven_multilingual_v2',
        'stability': 0.5,
        'similarity_boost': 0.75,
    },
    'research': {
        'sources': ['web', 'spiders'],
        'depth': 'standard',
        'max_results': 10,
    },
    'learning_stage': 'learning',   # new, learning, established
}
```

**Files to Create/Modify:**
| File | Action | Purpose |
|------|--------|---------|
| `core/views_preferences.py` | CREATE | API endpoints for preferences |
| `core/urls.py` | MODIFY | Add preference routes |
| `ai_core/templates/ai_image_studio.html` | MODIFY | Add dashboard section |
| `agents/preference_manager.py` | MODIFY | Add history tracking |

---

### A2: Spider Status Dashboard

**Goal:** Show active spiders, data flow, health status

**Location:** New page or section in AI Studio

**Features:**
- [ ] List all 46 spiders with status (active/dormant/error)
- [ ] Show last data collection time per spider
- [ ] Display data counts per spider
- [ ] Show spider categories/domains
- [ ] Health indicators (green/yellow/red)
- [ ] Manual trigger button for testing
- [ ] View recent data samples

**Backend Requirements:**
```python
# Endpoints in core/views_spider_dashboard.py (EXISTS - enhance)

GET  /api/spiders/                        # List all spiders with status
GET  /api/spiders/{name}/                 # Spider details
GET  /api/spiders/{name}/data/            # Recent data from spider
POST /api/spiders/{name}/trigger/         # Manual trigger
GET  /api/spiders/stats/                  # Aggregate statistics
GET  /api/spiders/health/                 # Health check all spiders
```

**Frontend Requirements:**
- Spider grid/list with status badges
- Category filters (Financial, Tech, Freelance, etc.)
- Status filters (Active, Dormant, Error)
- Data preview modal
- Health status indicators
- Last updated timestamps

**Spider Categories (14 total):**
```python
SPIDER_CATEGORIES = {
    'financial': ['coingecko', 'financial', 'yahoo_finance', 'market_data',
                  'etherscan', 'opensea', 'seekingalpha'],
    'freelance': ['toptal', 'guru', 'peopleperhour', 'flexjobs', 'remoteok',
                  'weworkremotely', 'angellist'],
    'content': ['medium', 'gumroad', 'substack', 'patreon', 'kofi'],
    'tech': ['github_jobs', 'stackoverflow_jobs', 'kaggle', 'huggingface',
             'producthunt', 'hackernews', 'devto', 'hashnode'],
    'legal': ['courtlistener', 'justia', 'findlaw', 'lii'],
    'design': ['ninetyninedesigns', 'dribbble', 'behance'],
    'news': ['news_harvester'],
    'social': ['social_sentiment'],
    'sports': ['horse_racing', 'combat_sports'],
    'education': ['teachable', 'udemy', 'skillshare'],
    'crowdfunding': ['indiegogo', 'kickstarter'],
    'innovation': ['innovation'],
}
```

**Files to Create/Modify:**
| File | Action | Purpose |
|------|--------|---------|
| `core/views_spider_dashboard.py` | MODIFY | Enhance existing endpoints |
| `ai_core/templates/ai_image_studio.html` | MODIFY | Add spider dashboard section |
| `ai_core/spiders/spider_registry.py` | MODIFY | Add status/health methods |

---

## Phase B: Advanced Features

### B1: Smart Style Suggestions

**Goal:** Recommend styles based on content type and context

**How it works:**
1. User enters prompt: "Create a logo for a tech startup"
2. System detects: content_type=logo, industry=tech
3. System suggests: "minimalist", "modern", "geometric" styles
4. Based on: user history + industry trends + successful generations

**Implementation:**
```python
# New class in agents/style_suggester.py (CREATE)

class StyleSuggester:
    def suggest_styles(self, prompt: str, content_type: str, user) -> List[StyleSuggestion]:
        """
        Returns ranked style suggestions based on:
        1. User's preference history (from AgentPreferenceManager)
        2. Content type patterns (logo -> minimalist, mascot -> pixar)
        3. Industry trends (from spider data)
        4. Successful generation history
        """
        pass

    def get_trending_styles(self, category: str) -> List[str]:
        """Get trending styles from spider data (dribbble, behance, etc.)"""
        pass
```

**Data Sources:**
- `AgentPreferenceManager` - User's past preferences
- `StyleMemory` - Past successful generations
- Spider data from design platforms (dribbble, behance)
- Built-in style mappings (content_type -> recommended_styles)

**Files to Create/Modify:**
| File | Action | Purpose |
|------|--------|---------|
| `agents/style_suggester.py` | CREATE | Style suggestion engine |
| `agents/image_agent.py` | MODIFY | Integrate suggestions into generate() |
| `core/views_image.py` | MODIFY | Add suggestion endpoint |

---

### B2: Batch Preference Learning

**Goal:** Learn from entire project history at once

**How it works:**
1. User clicks "Learn from this project"
2. System analyzes all images/videos in project
3. Extracts common styles, models, settings
4. Updates preferences with weighted learning

**Implementation:**
```python
# New method in agents/preference_manager.py

def learn_from_project(self, project_id: str) -> Dict[str, Any]:
    """
    Analyze all content in a project and learn preferences.

    Returns:
        Dict with learned preferences and confidence scores
    """
    # Get all images in project
    images = ImageHistory.objects.filter(project_id=project_id)

    # Analyze patterns
    style_counts = Counter(img.style for img in images if img.style)
    model_counts = Counter(img.model for img in images if img.model)

    # Update preferences with batch weighting
    for style, count in style_counts.most_common(3):
        self.record_preference('image', 'style', style, weight=count/len(images))

    return {'styles_learned': dict(style_counts), ...}
```

**Files to Create/Modify:**
| File | Action | Purpose |
|------|--------|---------|
| `agents/preference_manager.py` | MODIFY | Add learn_from_project() |
| `core/views_preferences.py` | MODIFY | Add batch learning endpoint |

---

### B3: Multi-Agent Collaboration

**Goal:** Agents consulting each other for complex tasks

**How it works:**
1. ImageAgent receives complex request
2. ImageAgent consults ResearchAgent for trends
3. ImageAgent consults StyleSuggester for recommendations
4. Combined intelligence produces better result

**Implementation:**
```python
# Enhanced ImageAgent with collaboration

class ImageAgent:
    def generate_with_collaboration(self, prompt: str, **kwargs):
        """
        Generate with multi-agent consultation.
        """
        # Consult ResearchAgent for context
        research = ResearchAgent(self.user).search(prompt)

        # Get style suggestions
        suggestions = StyleSuggester(self.user).suggest_styles(prompt)

        # Consult CoLeadership for strategic input (optional)
        if kwargs.get('strategic_review'):
            review = CoLeadershipAgent(self.user).review(prompt, research)

        # Generate with enriched context
        return self.generate(
            prompt=prompt,
            style=suggestions[0] if suggestions else None,
            context={'research': research, 'suggestions': suggestions}
        )
```

**Collaboration Matrix:**
| Agent | Can Consult | For What |
|-------|-------------|----------|
| ImageAgent | ResearchAgent | Trends, context |
| ImageAgent | StyleSuggester | Style recommendations |
| VideoAgent | AudioAgent | Voice selection |
| VideoAgent | ImageAgent | Thumbnail generation |
| All Agents | PreferenceManager | User preferences |

**Files to Create/Modify:**
| File | Action | Purpose |
|------|--------|---------|
| `agents/image_agent.py` | MODIFY | Add collaboration methods |
| `agents/video_agent.py` | MODIFY | Add collaboration methods |
| `agents/collaboration_mixin.py` | CREATE | Shared collaboration logic |

---

## Phase C: Spider Activation

### C1: Dormant Spider Inventory (17 total)

**Priority 1 - High Value (Activate First):**
| Spider | Category | Why Important | Difficulty |
|--------|----------|---------------|------------|
| dribbble | design | Design trends, inspiration | Medium |
| behance | design | Professional portfolios | Medium |
| hackernews | tech | Tech trends, discussions | Easy |
| devto | tech | Developer content | Easy |

**Priority 2 - Medium Value:**
| Spider | Category | Why Important | Difficulty |
|--------|----------|---------------|------------|
| weworkremotely | freelance | Remote jobs | Easy |
| angellist | freelance | Startup jobs | Medium |
| etherscan | financial | Blockchain data | Hard |
| opensea | financial | NFT market | Hard |

**Priority 3 - Lower Priority:**
| Spider | Category | Why Important | Difficulty |
|--------|----------|---------------|------------|
| teachable | education | Course data | Medium |
| udemy | education | Course data | Medium |
| skillshare | education | Course data | Medium |
| hashnode | tech | Dev blogs | Easy |
| indiegogo | crowdfunding | Campaigns | Medium |
| kickstarter | crowdfunding | Campaigns | Medium |
| seekingalpha | financial | Stock analysis | Hard |
| bloomberg_terminal | financial | Financial data | Hard |
| reuters_eikon | financial | News data | Hard |

---

### C2: Spider Implementation Template

For each dormant spider, create implementation:

```python
# ai_core/spiders/specialized/{spider_name}_spider.py

from ai_core.spiders.base_spider import BaseIntelligenceSpider, IntelligenceData
import aiohttp
import logging

logger = logging.getLogger(__name__)


class {SpiderName}Spider(BaseIntelligenceSpider):
    """
    Spider for collecting data from {Platform}.

    Data collected:
    - {List what data this spider collects}

    Usage:
        spider = {SpiderName}Spider(spider_id, targets, subscribers, redis_config)
        await spider.start()
    """

    def __init__(self, spider_id: str, targets: list, subscribers: list, redis_config: dict):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.platform = '{platform_name}'
        self.base_url = '{base_url}'

    async def process_data(self, raw_data: dict, target: str) -> IntelligenceData:
        """Process raw data into structured intelligence."""
        try:
            # Extract relevant fields
            items = self._extract_items(raw_data)

            # Calculate quality score
            quality_score = self._calculate_quality_score(items)

            # Create intelligence data
            return IntelligenceData(
                source=self.platform,
                data_type='{data_type}',
                content=items,
                quality_score=quality_score,
                metadata={
                    'target': target,
                    'item_count': len(items),
                    'collected_at': datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error processing {self.platform} data: {e}")
            return None

    def _extract_items(self, raw_data: dict) -> list:
        """Extract items from raw data."""
        # Platform-specific extraction logic
        items = []
        # ... extraction code ...
        return items

    def _calculate_quality_score(self, items: list) -> float:
        """Calculate quality score for the data."""
        if not items:
            return 0.0

        # Score based on completeness, recency, relevance
        completeness = sum(1 for item in items if self._is_complete(item)) / len(items)
        return min(1.0, completeness * 0.8 + 0.2)  # Base 0.2 + up to 0.8 for completeness

    def _is_complete(self, item: dict) -> bool:
        """Check if item has all required fields."""
        required_fields = ['title', 'url']  # Platform-specific
        return all(field in item for field in required_fields)
```

---

### C3: Spider Registration Update

After implementing spider, update registry:

```python
# ai_core/spiders/spider_registry.py

# Change from:
self.register_spider('dribbble', BaseIntelligenceSpider, {
    'category': 'design',
    'priority': 3,
    'placeholder': True,  # <-- REMOVE THIS
})

# To:
from ai_core.spiders.specialized.dribbble_spider import DribbbleSpider

self.register_spider('dribbble', DribbbleSpider, {
    'category': 'design',
    'priority': 2,
    'rate_limit': 1.0,
    'targets': ['dribbble.com/shots', 'dribbble.com/search'],
    'placeholder': False,  # <-- NOW ACTIVE
})
```

---

### C4: Connect Spiders to Agent Data Feeds

**Goal:** Make spider data flow to agents automatically

**Current Flow (Broken):**
```
Spider collects data → Redis pub/sub → ??? → Agents never see it
```

**Target Flow:**
```
Spider collects data
    → Redis pub/sub
    → SpiderDataProcessor
    → AgentIntelligenceFeed
    → Agents query when needed
```

**Implementation:**

```python
# New file: agents/intelligence_feed.py

class AgentIntelligenceFeed:
    """
    Provides real-time intelligence from spiders to agents.
    """

    def __init__(self, user=None):
        self.user = user
        self.redis = self._get_redis()

    def get_design_trends(self) -> List[Dict]:
        """Get latest design trends from design spiders."""
        return self._query_spider_data(['dribbble', 'behance', 'ninetyninedesigns'])

    def get_tech_trends(self) -> List[Dict]:
        """Get latest tech trends from tech spiders."""
        return self._query_spider_data(['hackernews', 'producthunt', 'github_jobs'])

    def get_market_data(self) -> List[Dict]:
        """Get latest market data from financial spiders."""
        return self._query_spider_data(['coingecko', 'yahoo_finance', 'market_data'])

    def get_job_opportunities(self) -> List[Dict]:
        """Get latest job opportunities from freelance spiders."""
        return self._query_spider_data(['toptal', 'guru', 'flexjobs', 'remoteok'])

    def _query_spider_data(self, spider_names: List[str], limit: int = 50) -> List[Dict]:
        """Query recent data from specified spiders."""
        from core.models_unified_system import SpiderData

        return list(SpiderData.objects.filter(
            spider_name__in=spider_names,
            is_processed=True
        ).order_by('-created_at')[:limit].values())
```

**Integration with Agents:**

```python
# In ImageAgent.generate()

def generate(self, prompt, **kwargs):
    # Get design intelligence if generating design content
    if self._is_design_content(prompt):
        feed = AgentIntelligenceFeed(self.user)
        trends = feed.get_design_trends()
        # Use trends to inform generation...
```

**Files to Create/Modify:**
| File | Action | Purpose |
|------|--------|---------|
| `agents/intelligence_feed.py` | CREATE | Spider data feed for agents |
| `agents/image_agent.py` | MODIFY | Integrate intelligence feed |
| `agents/research_agent.py` | MODIFY | Use spider data in research |

---

## Implementation Order

### Session 206: Phase A1 - Preferences Dashboard
1. Create `core/views_preferences.py` with API endpoints
2. Add routes to `core/urls.py`
3. Add dashboard UI to `ai_image_studio.html`
4. Test preference viewing/editing

### Session 207: Phase A2 - Spider Status Dashboard
1. Enhance `core/views_spider_dashboard.py`
2. Add spider status UI to `ai_image_studio.html`
3. Add health check endpoint
4. Test spider visibility

### Session 208: Phase B1 - Smart Style Suggestions
1. Create `agents/style_suggester.py`
2. Integrate into ImageAgent
3. Add suggestion endpoint
4. Test suggestions

### Session 209: Phase B2 & B3 - Batch Learning & Collaboration
1. Add `learn_from_project()` to PreferenceManager
2. Create `agents/collaboration_mixin.py`
3. Integrate collaboration into agents
4. Test multi-agent workflows

### Session 210+: Phase C - Spider Activation
1. Implement Priority 1 spiders (dribbble, behance, hackernews, devto)
2. Create `agents/intelligence_feed.py`
3. Connect spider data to agents
4. Implement remaining spiders as needed

---

## Testing Checklist

### Phase A Tests
- [ ] Can view preferences for all domains
- [ ] Can edit preferences
- [ ] Can clear preferences
- [ ] Spider dashboard shows all 46 spiders
- [ ] Spider status correctly shows active/dormant
- [ ] Can view spider data samples

### Phase B Tests
- [ ] Style suggestions appear for prompts
- [ ] Suggestions match content type
- [ ] Batch learning updates preferences
- [ ] Multi-agent collaboration works
- [ ] Agents consult each other correctly

### Phase C Tests
- [ ] Dormant spiders can be activated
- [ ] Activated spiders collect data
- [ ] Spider data flows to agents
- [ ] Agents use spider intelligence

---

## File Reference

### Files to CREATE
| File | Purpose |
|------|---------|
| `core/views_preferences.py` | Preferences API endpoints |
| `agents/style_suggester.py` | Style suggestion engine |
| `agents/intelligence_feed.py` | Spider data feed for agents |
| `agents/collaboration_mixin.py` | Shared collaboration logic |
| `ai_core/spiders/specialized/dribbble_spider.py` | Dribbble spider |
| `ai_core/spiders/specialized/behance_spider.py` | Behance spider |
| `ai_core/spiders/specialized/hackernews_spider.py` | HackerNews spider |
| `ai_core/spiders/specialized/devto_spider.py` | Dev.to spider |

### Files to MODIFY
| File | Purpose |
|------|---------|
| `core/urls.py` | Add new routes |
| `core/views_spider_dashboard.py` | Enhance spider endpoints |
| `agents/preference_manager.py` | Add history, batch learning |
| `agents/image_agent.py` | Add collaboration, suggestions |
| `agents/video_agent.py` | Add collaboration |
| `agents/research_agent.py` | Use spider data |
| `ai_core/spiders/spider_registry.py` | Activate dormant spiders |
| `ai_core/templates/ai_image_studio.html` | Add dashboard UIs |

---

## Quick Reference Commands

```bash
# Start server
make start

# Test preferences API
curl http://localhost:8000/api/preferences/

# Test spider API
curl http://localhost:8000/api/spiders/

# Run specific spider (manual test)
python manage.py shell
>>> from ai_core.spiders.spider_registry import spider_registry
>>> spider = spider_registry.create_spider_instance('dribbble', ...)
>>> await spider.start()

# Check Celery tasks
celery -A core inspect active
```

---

**Last Updated:** November 26, 2025
**Current Phase:** Ready to start Phase A1 (Preferences Dashboard)
