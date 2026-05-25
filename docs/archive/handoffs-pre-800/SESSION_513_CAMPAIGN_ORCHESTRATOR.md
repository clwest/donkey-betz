# Session 513 - Campaign Orchestrator Agent

**Date:** December 19, 2025
**Focus:** Building the Campaign Orchestrator - The Marketing Campaign Hub

---

## Overview

Built the **Campaign Orchestrator Agent** - the missing "hub" that finally connects:
- **Intelligence** (spider data, web search, research)
- **Agents** (creation, strategy, writing)
- **Autonomous** (performance monitoring)
- **Delivery** (Discord, download, client management)

A customer gives: **Product + Target Market + Budget**
The system produces: **Ad copies, images, videos, emails, social posts**

---

## What Was Built

### 1. Campaign Database Models (`core/models_campaign.py`)

**Campaign** - The main campaign entity
- Budget tiers: starter ($500), pro ($2,000), enterprise ($5,000), premium ($10,000)
- Status tracking: intake → research → strategy → creation → review → complete → delivered
- Stores product info, target market, brand assets, research data, strategy results
- Progress tracking with phase details and execution logging

**CampaignDeliverable** - Individual assets created for a campaign
- Types: ad_copy, image, video, email, social_post, banner, voiceover, brand_guide
- Platform targeting: facebook, instagram, twitter, linkedin, craigslist, youtube, email
- Status: pending → creating → complete/failed → approved/rejected
- Links to image history, video, audio IDs

**CampaignResearch** - Research findings
- Types: market_trends, competitor, customer, seo, pricing, content, web_search
- Stores source URLs and agent attribution

### 2. Campaign Orchestrator Agent (`core/agents/campaign_orchestrator_agent.py`)

~750 lines of orchestration logic with:

**Tools:**
- `create_campaign` - Create a new campaign from brief
- `run_research_phase` - Market trends, competitor analysis
- `run_strategy_phase` - Content strategy, SEO keywords, brand direction
- `run_creation_phase` - Generate deliverables based on tier
- `get_campaign_status` - Get current campaign progress

**Pipeline Phases:**
1. **RESEARCH (20%)** - Uses SmartTrendingService with web search fallback
2. **STRATEGY (20%)** - Content strategy, brand direction, SEO keywords
3. **CREATION (50%)** - Ad copies, social posts, emails, images, videos
4. **PACKAGING (10%)** - Bundle deliverables

**Budget Tier Deliverables:**
| Tier | Price | Includes |
|------|-------|----------|
| Starter | $500 | 5 ad copies, 5 images, 7 social posts |
| Pro | $2,000 | + email sequence, banner ads |
| Enterprise | $5,000 | + 30s video with voiceover |
| Premium | $10,000 | + 3 videos, brand guide |

### 3. Campaign API Endpoints (`core/views_campaign.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/campaigns/` | GET | List all campaigns |
| `/api/campaigns/create/` | POST | Create new campaign |
| `/api/campaigns/budget-tiers/` | GET | Get available tiers |
| `/api/campaigns/<id>/` | GET | Get campaign details |
| `/api/campaigns/<id>/start/` | POST | Start campaign execution |
| `/api/campaigns/<id>/status/` | GET | Get quick status |
| `/api/campaigns/<id>/deliverables/` | GET | Get deliverables |
| `/api/campaigns/<id>/delete/` | DELETE | Delete campaign |

### 4. Database Migration (`core/migrations/0116_session_513_campaign_orchestrator.py`)

Creates Campaign, CampaignDeliverable, CampaignResearch tables.

### 5. Agent Registration

- Added to `core/agents/__init__.py` exports
- Added to `core/agent_router.py` AGENT_MAP
- Factory function: `get_campaign_orchestrator_agent()`

---

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `core/models_campaign.py` | Created | ~343 |
| `core/agents/campaign_orchestrator_agent.py` | Created | ~750 |
| `core/views_campaign.py` | Created | ~360 |
| `core/migrations/0116_session_513_campaign_orchestrator.py` | Created | ~165 |
| `core/agents/__init__.py` | Modified | +10 |
| `core/agent_router.py` | Modified | +5 |
| `core/urls.py` | Modified | +20 |
| `core/migrations/0115_*` | Fixed | (no-op migration fix) |

---

## Web Search Fallback (Also Implemented This Session)

Enhanced SmartTrendingService with web search fallback:

1. **Topic relevance checking** - Detects when spider data doesn't match the topic
2. **Web search fallback** - Uses DuckDuckGo when spider data insufficient (<3 articles or <20% relevant)
3. **Multi-word topic extraction** - Better parsing of "Honda Civics in Denver" style queries

This means the platform now works for **ANY industry**, not just tech-focused topics.

---

## Example Campaign Creation

```python
# Create a campaign via API
POST /api/campaigns/create/
{
    "name": "Mike's Auto - Honda Civic Sale",
    "product_name": "2019 Honda Civic",
    "product_description": "Low miles, clean title, great condition. Perfect commuter car.",
    "target_market": "Young professionals in Denver metro area looking for reliable transportation",
    "target_location": "Denver, CO",
    "budget_tier": "pro",
    "platforms": ["facebook", "craigslist", "email"],
    "client_name": "Mike's Auto",
    "competitors": ["CarMax", "AutoNation"],
    "brand_style": "professional"
}

# Start the campaign
POST /api/campaigns/<uuid>/start/

# The orchestrator will:
# 1. Research market trends for used cars in Denver
# 2. Analyze competitors (CarMax, AutoNation)
# 3. Generate content strategy
# 4. Create 10 ad copy variations
# 5. Create 14 social posts (7 Facebook, 7 general)
# 6. Create 5-email sequence
# 7. Generate banner ads
```

---

## Testing

```bash
# Verify models import
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.models_campaign import Campaign
from core.agents.campaign_orchestrator_agent import CampaignOrchestratorAgent
from core.agent_router import AgentRouter
print('CampaignOrchestratorAgent registered:', 'CampaignOrchestratorAgent' in AgentRouter.AGENT_MAP)
"

# Test API (requires running server)
curl http://localhost:8000/api/campaigns/budget-tiers/
```

---

## The Big Picture

This session addressed the user's question: "What IS this platform?"

**Answer:** It's the ultimate marketing/advertising platform:

1. **Customer gives:** Product + Target Market + Budget
2. **System produces:** Complete marketing package (ads, images, videos, emails, social posts)
3. **Platform handles:** Research → Strategy → Creation → Delivery

The Campaign Orchestrator is the **hub** that ties together all the existing pieces:
- Spider Network → Research phase
- SmartTrendingService → Market intelligence
- Content agents → Ad copy, emails, social posts
- Image/Video agents → Visual assets
- Discord/Download → Delivery

---

## Next Session Ideas

1. **Campaign UI Tab** - Add Campaigns tab to AI Studio UI
2. **Image Generation Integration** - Hook up ImageAgent for actual image creation
3. **Video Generation Integration** - Hook up VideoAgent for Enterprise+ tiers
4. **Discord Campaign Commands** - `/campaign-create`, `/campaign-status`, `/campaign-deliver`
5. **Campaign Performance Tracking** - Track which deliverables perform best
6. **Client Portal** - Let clients review and approve deliverables

---

## System Status After Session 513

| Metric | Value |
|--------|-------|
| Routable Agents | **43** (+1 CampaignOrchestratorAgent) |
| API Endpoints | +8 campaign endpoints |
| Database Tables | +3 (Campaign, CampaignDeliverable, CampaignResearch) |
| Budget Tiers | 4 ($500-$10,000) |
