---
originating_session: 812
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 812 - Content Production Teams

**Date:** January 24, 2026
**Focus:** Multi-Agent Content Creation + Persona Advisory Integration
**Status:** BUILT BUT NOT VERIFIED

---

## Summary

Built a comprehensive content production orchestration system that enables agents to work together automatically to create complete content packages. When creating a blog post, the system automatically triggers ResearchAgent, ContentWriterAgent, ImageAgent (for hero images, thumbnails, graphics), SEOOptimizerAgent, and SocialMediaAgent - all coordinated with proper dependencies.

Additionally integrated 149 Persona Agents as strategic advisors who provide guidance before and after content creation phases.

**CRITICAL NOTE:** The system was deployed to Railway but we only verified `--list` works. We NEVER ran an actual content production to verify end-to-end functionality.

---

## What Was Built

### 1. Content Production Orchestrator

**File:** `core/services/content_production_orchestrator.py` (~1000 lines)

A service that coordinates multiple agents to produce complete content packages:

- **Production Teams**: Pre-defined teams for each content type
- **Asset Dependencies**: Assets specify what they depend on (images depend on content for titles)
- **Parallel Execution**: Independent assets execute in parallel (3 images at once)
- **Async Support**: Productions can run via Celery
- **Graceful Degradation**: Production continues even if optional assets fail

### 2. Persona Advisor Service

**File:** `core/services/persona_advisor_service.py` (~450 lines)

Enables 149 persona agents (database records without Python code) to participate in content production via LLM conversations enriched with spider data:

- Loads persona agent from database
- Fetches relevant spider context for their domain
- Generates LLM response from their perspective
- Returns structured advice for use in content production

### 3. Management Command

**File:** `core/management/commands/produce_content.py` (~220 lines)

```bash
# List available teams
python manage.py produce_content --list

# Produce a blog post
python manage.py produce_content blog_post "AI trends for 2026"

# With options
python manage.py produce_content blog_post "Topic" --tone conversational --skip research --json --async
```

### 4. Celery Task

**File:** `core/tasks.py` (+50 lines)

```python
@shared_task(bind=True, max_retries=1, default_retry_delay=120)
def produce_content_package(self, production_id, content_type, topic, context, skip_assets, user_id):
    """Async content production via Celery."""
```

---

## Production Teams

### Blog Post Team (9 assets)

| Phase | Asset | Agent | Type | Depends On |
|-------|-------|-------|------|------------|
| 0 | strategy_advice | Content Strategy Planner | Persona | - |
| 1 | research | ResearchAgent | Core | - |
| 2 | blog_content | ContentWriterAgent | Core | research, strategy_advice |
| 3 | hero_image | ImageAgent | Core | blog_content |
| 3 | thumbnail | ImageAgent | Core | blog_content |
| 3 | inline_graphics | ImageAgent | Core | blog_content |
| 4 | seo_metadata | SEOOptimizerAgent | Core | blog_content |
| 5 | marketing_advice | Digital Marketing Strategist | Persona | blog_content |
| 6 | social_posts | SocialMediaAgent | Core | blog_content, marketing_advice |

### Podcast Team (8 assets)

| Phase | Asset | Agent | Type |
|-------|-------|-------|------|
| 0 | strategy_advice | Content Strategy Planner | Persona |
| 1 | research | ResearchAgent | Core |
| 2 | podcast_script | ContentWriterAgent | Core |
| 3 | podcast_audio | AudioAgent | Core |
| 3 | episode_artwork | ImageAgent | Core |
| 4 | promo_video | VideoAgent | Core |
| 4 | show_notes | ContentWriterAgent | Core |
| 5 | social_posts | SocialMediaAgent | Core |

### Video Team (8 assets)

| Phase | Asset | Agent | Type |
|-------|-------|-------|------|
| 0 | strategy_advice | Content Strategy Planner | Persona |
| 1 | research | ResearchAgent | Core |
| 2 | video_script | ContentWriterAgent | Core |
| 3 | video_voiceover | AudioAgent | Core |
| 3 | video_thumbnail | ImageAgent | Core |
| 3 | video_graphics | ImageAgent | Core |
| 4 | seo_metadata | SEOOptimizerAgent | Core |
| 5 | social_posts | SocialMediaAgent | Core |

### Newsletter Team (5 assets)

| Phase | Asset | Agent | Type |
|-------|-------|-------|------|
| 0 | strategy_advice | Content Strategy Planner | Persona |
| 1 | research | ResearchAgent | Core |
| 2 | newsletter_content | ContentWriterAgent | Core |
| 3 | header_image | ImageAgent | Core |
| 3 | section_graphics | ImageAgent | Core |

### Social Campaign Team (4 assets)

| Phase | Asset | Agent | Type |
|-------|-------|-------|------|
| 1 | campaign_strategy | ContentStrategyAgent | Core |
| 2 | campaign_copy | ContentWriterAgent | Core |
| 3 | campaign_visuals | ImageAgent | Core |
| 3 | video_shorts | VideoAgent | Core |

---

## Persona Agent Catalog

**149 Persona Agents** across 20 categories:

| Category | Count | Examples |
|----------|-------|----------|
| Income Generation | 8 | Freelance Income Optimizer, Passive Income Strategist |
| Career Development | 8 | Career Transition Coach, Leadership Development Coach |
| Job Search | 8 | Resume Optimization Expert, Interview Success Coach |
| Content Creation | 8 | Blog Post Generator, Copywriting Specialist |
| Marketing & Growth | 8 | SEO Content Optimizer, Growth Hacker Pro |
| Financial Planning | 8 | Budget Optimization Expert, Tax Strategy Advisor |
| AI & Machine Learning | 8 | Prompt Engineering Master, AI Ethics Consultant |
| Automation & Productivity | 8 | Workflow Automation Expert, Time Management Coach |
| Business Strategy | 8 | Content Strategy Planner, E-commerce Growth Expert |
| Data & Analytics | 8 | Data Visualization Expert, A/B Testing Expert |
| Research & Analysis | 7 | Market Research Analyst, Trend Analysis Expert |
| Creative Services | 7 | Brand Identity Designer, Video Content Strategist |
| Consulting & Advisory | 7 | Business Consultant Pro, Change Management Expert |
| Investment & Trading | 7 | Stock Market Analyst, Value Investing Expert |
| Crypto & Web3 | 7 | Crypto Portfolio Manager, DeFi Strategy Expert |
| E-commerce & Retail | 7 | Amazon FBA Expert, Shopify Store Optimizer |
| Real Estate | 6 | Real Estate Investment Analyst, House Flipping Strategist |
| Health & Wellness | 6 | Wellness Business Coach, Fitness Business Strategist |
| Education & Learning | 6 | Online Course Creator, Coaching Business Developer |
| Audience Engagement | 7 | Community Manager Pro, Retention Strategy Expert |

**Plus 25 Legendary Advisors:** Warren Buffett, Charlie Munger, Ray Dalio, Elon Musk, etc.

---

## PRs Merged

- **PR #109**: feat(Session 812): Content Production Teams - Multi-Agent Content Creation
- **PR #110**: feat(Session 812): Persona Advisory Integration for Content Production

---

## Key Design Decisions

1. **Team-Based Architecture**: Each content type has a pre-defined team
2. **Dependency Graph**: Assets specify what they depend on
3. **Optional vs Required**: Core assets required; promotional optional
4. **Context Propagation**: Results from earlier phases inform later phases
5. **Graceful Degradation**: Production continues even if optional assets fail
6. **Persona as Advisors**: Persona agents provide strategic advice, core agents produce artifacts

---

## UNVERIFIED - Session 813 Priority

The following needs end-to-end verification:

```bash
# Run this and verify all 9 assets are created:
python manage.py produce_content blog_post "AI trends for 2026" --json
```

Expected: strategy_advice, research, blog_content, hero_image, thumbnail, inline_graphics, seo_metadata, marketing_advice, social_posts

---

## Architecture Diagram

```
Content Production Flow
═══════════════════════

User Request: "Create a blog post about AI trends"
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  ContentProductionOrchestrator   │
        │  1. Load PRODUCTION_TEAMS        │
        │  2. Get blog_post team           │
        │  3. Sort by parallel_group       │
        └──────────────────────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
 Group 0               Group 1               Group 2
(Advisory)           (Research)            (Content)
    │                     │                     │
    ▼                     ▼                     ▼
Content Strategy    ResearchAgent      ContentWriterAgent
  Planner                │                     │
(Persona LLM)            │                     │
    │                    │                     │
    └────────────────────┴─────────────────────┘
                           │
                           ▼
                      Group 3
                (Images - Parallel)
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
      hero_image      thumbnail    inline_graphics
      (ImageAgent)   (ImageAgent)   (ImageAgent)
           │               │               │
           └───────────────┴───────────────┘
                           │
                           ▼
                      Group 4-6
              (SEO → Marketing → Social)
                           │
                           ▼
              Complete Content Package
```
