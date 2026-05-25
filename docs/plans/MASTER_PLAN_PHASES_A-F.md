<!-- DOC-POINTER-V1 -->
> **⚠ HISTORICAL PLAN (Q4 2025 / Q1 2026 build phase).** Drafted during platform build-out; may be partially shipped, renamed in code, or quietly superseded. Preserved for historical reference, not current truth. For current truth see [`docs/INDEX.md`](../INDEX.md) + [`PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) + the latest handoff. See [`docs/plans/INDEX.md`](INDEX.md) for directory scope.

# Master Plan: Phases A-F - Intelligence-Driven AI Content Platform

**Created:** November 26, 2025 (Session 218)
**Goal:** Transform 67 spiders + AI content creation into an intelligent, personalized creative platform
**Current State:** 100% Reality Score | All core features complete

---

## EXISTING INFRASTRUCTURE DISCOVERED!

Before starting, we found significant existing code:

| File | Purpose | Status |
|------|---------|--------|
| `ai_core/agents/spider_agent_connector.py` | Redis pub/sub routing | Exists, needs AI Content mapping |
| `ai_core/spiders/spider_data_router.py` | Complex routing infrastructure | Exists, needs activation |
| `core/learning_bridges/spider_data_bridge.py` | Learning from spider data | Exists, needs testing |

**Key Insight:** Infrastructure exists but is configured for legacy agents (income_builder, trading).
We need to **update routing tables for AI Content Creation agents**.

---

## Overview

| Phase | Name | Focus | Dependencies |
|-------|------|-------|--------------|
| A | Spider → Agent Integration | Connect spider data to agents | None |
| B | Smart Content Recommendations | AI-powered content suggestions | Phase A |
| C | Agent Personalization & Learning | User preference learning | Phase A |
| D | Workflow Marketplace | Community workflow sharing | None |
| E | Real-Time Collaboration | Multi-user workspace | Phase D |
| F | Export & Integration | Platform connectivity | Phases A-C |

---

## Phase A: Spider → Agent Integration

**Goal:** Make the 67 spiders feed real-time intelligence to AI Content Creation agents

### EXISTING CODE TO LEVERAGE:
- `ai_core/agents/spider_agent_connector.py` - Already has pub/sub routing!
- `ai_core/spiders/spider_data_router.py` - Complex routing infrastructure!
- `core/learning_bridges/spider_data_bridge.py` - Learning from spider data!

### A1: Update Routing Tables for AI Content Creation ✅ PRIORITY
Update the existing routing tables to map our 67 spiders to AI Content agents.

**File to Modify:** `ai_core/agents/spider_agent_connector.py`

**Current routing_table (line 50-76):**
```python
# OLD - configured for income/trading agents
self.routing_table = {
    'sports_betting': [...],
    'trading': [...],
    'content': [...],  # Has some content agents
    'opportunities': [...]
}
```

**NEW routing_table for AI Content Creation:**
```python
self.routing_table = {
    # Creative Assets (Envato, CreativeMarket, AdobeStock, Shutterstock, Canva)
    'creative_assets': [
        'image_generation_agent',
        'design_assistant_agent',
        'brand_identity_agent',
        'template_curator_agent'
    ],

    # AI Creative Tools (Midjourney, CivitAI, RunwayML, Replicate)
    'ai_creative': [
        'image_generation_agent',
        'video_generation_agent',
        'style_discovery_agent',
        'prompt_engineering_agent',
        'model_recommender_agent'
    ],

    # Digital Products (Etsy, LemonSqueezy, Sellfy, AppSumo, Gumroad)
    'digital_products': [
        'product_idea_agent',
        'marketplace_analyst_agent',
        'pricing_strategy_agent',
        'template_builder_agent'
    ],

    # Content Creation (ConvertKit, Notion, Figma)
    'content_creation': [
        'content_strategy_agent',
        'design_system_agent',
        'productivity_agent',
        'newsletter_agent'
    ],

    # Tech/Innovation (HackerNews, DevTo, GitHub, ProductHunt)
    'tech': [
        'trend_analysis_agent',
        'research_agent',
        'tool_discovery_agent'
    ],

    # News (General)
    'news': [
        'trend_analysis_agent',
        'content_strategy_agent'
    ]
}
```

### A2: Create AI Content Agent Registry
Create the actual agents that will receive spider data.

**File to Create:** `core/services/ai_content_agents.py`

**Agent Definitions:**
| Agent Name | Purpose | Receives From |
|------------|---------|---------------|
| `image_generation_agent` | Image prompts & style suggestions | creative_assets, ai_creative |
| `video_generation_agent` | Video ideas & trends | ai_creative |
| `style_discovery_agent` | Track trending styles | ai_creative, creative_assets |
| `prompt_engineering_agent` | Analyze successful prompts | ai_creative |
| `product_idea_agent` | Digital product ideas | digital_products |
| `content_strategy_agent` | Content trends & topics | content_creation, news |
| `trend_analysis_agent` | Cross-platform trends | tech, news |

### A3: Wire Spiders to Publish Data
Update spiders to publish data via the connector when they collect.

**File to Modify:** Each spider in `ai_core/spiders/specialized/`

**Add to base spider `process_data` method:**
```python
# After processing, publish to agent connector
from ai_core.agents.spider_agent_connector import send_spider_data_to_agents

await send_spider_data_to_agents(
    spider_name=self.spider_id,
    spider_type=self.get_spider_category(),
    data=processed_data
)
```

### A4: Create API Endpoints for Agent Feeds
Expose agent intelligence feeds via REST API.

**File to Create:** `core/views_agent_intelligence.py`

**API Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agent-intelligence/feed/{agent_name}/` | GET | Get agent's intelligence feed |
| `/api/agent-intelligence/trends/` | GET | Get current trends across all agents |
| `/api/agent-intelligence/suggestions/` | GET | Get content suggestions |
| `/api/agent-intelligence/stats/` | GET | Get routing statistics |

### A5: UI Integration - Intelligence Panel
Add an "Intelligence" panel to AI Studio showing live spider feeds.

**Add to:** `ai_core/templates/ai_image_studio.html`

**UI Components:**
- "Trending Now" sidebar panel
- Intelligence feed by category
- "Use This" button to apply suggestion to current creation
- Refresh/filter controls

### A6: Testing & Validation
- Verify routing tables match 67 spiders
- Test data flow from spider → agent → UI
- Performance test with concurrent spider executions

---

## Phase B: Smart Content Recommendations

**Goal:** Turn spider intelligence into actionable content suggestions

### B1: Trend Analysis Engine
Analyze spider data to identify trending topics.

**Files to Create:**
- `core/services/trend_analysis.py` - Trend detection
- `core/views_recommendations.py` - API endpoints

**Trend Detection Algorithm:**
```python
class TrendAnalyzer:
    def detect_trends(self, timeframe_hours: int = 24) -> List[Trend]:
        """Analyze recent spider data for trending topics"""

    def calculate_trend_score(self, topic: str, data_points: List) -> float:
        """Score topic based on frequency, recency, sentiment"""

    def categorize_trend(self, trend: Trend) -> str:
        """Categorize: rising, hot, cooling, stable"""
```

### B2: Content Suggestion Generator
Generate specific content ideas from trends.

**Suggestion Types:**
| Type | Description | Example |
|------|-------------|---------|
| Image Prompt | Ready-to-use prompt | "Cyberpunk city with neon signs, trending style" |
| Product Idea | Digital product concept | "Notion template for project management (hot on Etsy)" |
| Style Suggestion | Design style to try | "Glassmorphism is trending on Figma" |
| Topic Alert | Content topic | "AI art controversy is trending - create content now" |

### B3: Personalized Recommendations
Tailor suggestions based on user history.

**Personalization Factors:**
- Past content created (styles, topics)
- Workflow preferences
- Engagement with previous suggestions
- Explicit preferences from settings

### B4: API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/recommendations/trending/` | GET | Current trending content ideas |
| `/api/recommendations/personalized/` | GET | User-specific suggestions |
| `/api/recommendations/by-type/{type}/` | GET | Filter by content type |
| `/api/recommendations/dismiss/{id}/` | POST | Don't show this again |

### B5: UI Integration
- "Trending Now" panel in AI Studio sidebar
- "Suggested for You" section
- One-click "Create from suggestion" button

---

## Phase C: Agent Personalization & Learning

**Goal:** Agents learn from user interactions and adapt

### C1: Interaction Logging
Track user interactions with agent outputs.

**Database Model:**
```python
class AgentInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agent_name = models.CharField(max_length=100)
    interaction_type = models.CharField(max_length=50)  # created, edited, saved, shared
    input_data = models.JSONField()
    output_data = models.JSONField()
    user_rating = models.IntegerField(null=True)  # 1-5
    was_modified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

### C2: Preference Learning Service
Learn user preferences from interactions.

**Files to Create:**
- `core/services/preference_learning.py`

**Learning Factors:**
- Preferred styles (based on image history)
- Common prompt patterns
- Favorite aspect ratios
- Typical workflow sequences
- Color preferences
- Content themes

### C3: Agent Memory System
Give agents memory of past interactions.

**Memory Types:**
| Type | Description | Retention |
|------|-------------|-----------|
| Session | Current session context | Session end |
| Short-term | Recent interactions | 7 days |
| Long-term | Learned preferences | Permanent |

### C4: Adaptive Prompting
Agents adjust their behavior based on learned preferences.

**Example:**
```python
def get_adaptive_context(user_id: int, agent_name: str) -> str:
    prefs = preference_service.get_user_preferences(user_id)

    context = f"""
    User Preferences:
    - Preferred style: {prefs.preferred_style}
    - Common themes: {', '.join(prefs.themes)}
    - Quality preference: {prefs.quality_level}
    - Typical aspect ratio: {prefs.aspect_ratio}
    """
    return context
```

### C5: UI for Preference Management
- View learned preferences
- Manually adjust preferences
- Reset learning data
- Export/import preferences

---

## Phase D: Workflow Marketplace

**Goal:** Community sharing and discovery of custom workflows

### D1: Workflow Publishing System
Allow users to publish workflows publicly.

**Database Model:**
```python
class PublishedWorkflow(models.Model):
    workflow = models.ForeignKey(CustomWorkflow, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50)
    tags = models.JSONField(default=list)
    preview_image = models.ImageField(null=True)
    is_featured = models.BooleanField(default=False)
    download_count = models.IntegerField(default=0)
    published_at = models.DateTimeField(auto_now_add=True)
```

### D2: Rating & Review System
```python
class WorkflowReview(models.Model):
    workflow = models.ForeignKey(PublishedWorkflow, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### D3: API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/marketplace/workflows/` | GET | Browse all workflows |
| `/api/marketplace/workflows/featured/` | GET | Featured workflows |
| `/api/marketplace/workflows/trending/` | GET | Trending by downloads |
| `/api/marketplace/workflows/{id}/` | GET | Workflow details |
| `/api/marketplace/workflows/{id}/install/` | POST | Install to my workflows |
| `/api/marketplace/publish/` | POST | Publish workflow |
| `/api/marketplace/reviews/` | POST | Add review |

### D4: Categories & Discovery
**Categories:**
- Image Generation
- Video Creation
- Audio Production
- Brand Identity
- Social Media
- E-commerce
- Research & Analysis

### D5: UI Components
- Marketplace tab in AI Studio
- Grid view with previews
- Filter by category, rating, downloads
- "Install" button with one-click setup

---

## Phase E: Real-Time Collaboration

**Goal:** Multiple users working on same project simultaneously

### E1: WebSocket Infrastructure
Extend existing WebSocket for real-time sync.

**Events:**
| Event | Description |
|-------|-------------|
| `project:join` | User joins project |
| `project:leave` | User leaves project |
| `content:update` | Content changed |
| `cursor:move` | User cursor position |
| `selection:change` | User selection changed |

### E2: Shared Project Model
```python
class SharedProject(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    collaborators = models.ManyToManyField(User, related_name='shared_projects')
    content = models.JSONField(default=dict)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### E3: Conflict Resolution
- Operational Transform (OT) for text
- Last-write-wins for settings
- Merge strategy for content arrays

### E4: Presence System
Show who's online and what they're doing.

### E5: Permission System
| Role | Permissions |
|------|------------|
| Owner | Full control, manage collaborators |
| Editor | Create, edit, delete content |
| Viewer | View only, comment |

---

## Phase F: Export & Integration

**Goal:** Connect platform to external services

### F1: Export Formats
| Format | Content Types |
|--------|---------------|
| PNG/JPG/WebP | Images |
| MP4/WebM | Videos |
| MP3/WAV | Audio |
| ZIP | Batch exports |
| JSON | Workflow definitions |

### F2: Platform Integrations
| Platform | Integration Type |
|----------|-----------------|
| Figma | Export designs |
| Canva | Import/export |
| Adobe CC | Plugin |
| Notion | Embed content |
| Slack | Share notifications |
| Discord | Bot integration |

### F3: API Key System
```python
class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)
    permissions = models.JSONField(default=list)
    rate_limit = models.IntegerField(default=1000)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True)
```

### F4: Webhook System
```python
class Webhook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    events = models.JSONField(default=list)  # ['content.created', 'workflow.completed']
    secret = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
```

### F5: External API Endpoints
| Endpoint | Description |
|----------|-------------|
| `/api/v1/generate/image/` | Generate image via API |
| `/api/v1/generate/video/` | Generate video via API |
| `/api/v1/workflows/execute/` | Execute workflow via API |
| `/api/v1/content/{id}/` | Get content by ID |

---

## Implementation Priority

### Recommended Order:
1. **Phase A** - Spider → Agent (Foundation for B & C)
2. **Phase B** - Recommendations (Quick wins, user value)
3. **Phase C** - Personalization (Builds on A & B)
4. **Phase D** - Marketplace (Independent, high value)
5. **Phase E** - Collaboration (Complex, later priority)
6. **Phase F** - Export/API (Polish, monetization)

### Estimated Scope:
| Phase | New Files | New Endpoints | New Models |
|-------|-----------|---------------|------------|
| A | 3 | 5 | 1 |
| B | 2 | 4 | 0 |
| C | 2 | 5 | 2 |
| D | 2 | 7 | 2 |
| E | 3 | 6 | 2 |
| F | 3 | 8 | 2 |

---

## Quick Reference

### Key Files by Phase:
- **Phase A:** `core/services/spider_agent_bridge.py`
- **Phase B:** `core/services/trend_analysis.py`, `core/views_recommendations.py`
- **Phase C:** `core/services/preference_learning.py`
- **Phase D:** `core/views_marketplace.py`
- **Phase E:** `core/consumers_collaboration.py`
- **Phase F:** `core/views_external_api.py`

### Current Infrastructure:
- **67 Spiders:** `ai_core/spiders/spider_registry.py`
- **Spider Data Model:** `core/models_unified_system.py` → `SpiderData`
- **WebSocket:** `core/consumers.py`
- **Custom Workflows:** `agents/workflow_orchestration_agent.py`

---

**Start with Phase A → Spider-Agent Bridge!**
