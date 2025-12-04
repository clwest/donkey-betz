# Session 335: Living Projects System

**Date:** December 3, 2025
**Status:** Complete
**Focus:** Projects that autonomously learn from the agent ecosystem

---

## What We Built

The **Living Project System** - projects that "subscribe" to the autonomous agent ecosystem and receive relevant insights automatically.

### The Problem
- 199 agents with 194K+ learning transfers
- 324 autonomous conversations
- 259 decisions (12 canonical)
- 74 spiders collecting real-time data
- But: All this activity was self-contained, not benefiting user projects

### The Solution
Projects now receive automatic insights when:
1. Spider data matches project topics
2. Agent conversations relate to project themes
3. Canonical decisions affect project areas

---

## Files Created/Modified

### New Files
- `core/services/living_project_service.py` - The brain of Living Projects
- `core/migrations/0067_living_project_system.py` - Database migration

### New Models
- `ProjectInsight` - Insights surfaced to projects from ecosystem
- `LivingProjectConfig` - Configuration for what a project watches

### Modified Files
- `core/models_unified_system.py` - Added Living Project models + hook in `promote_to_canonical()`
- `core/tasks.py` - Added hooks for spider data and conversation processing
- `core/views_projects_api.py` - Added Living Project API endpoints
- `core/urls.py` - Added URL routes for new endpoints

---

## New API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects/<id>/feed/` | GET | Get project insight feed |
| `/api/projects/<id>/activate-living/` | POST | Activate project as "living" |
| `/api/projects/<id>/insights/<id>/status/` | POST | Update insight status |
| `/api/projects/<id>/living-config/` | POST | Update living config |

---

## How It Works

1. **Topic Extraction**: Projects get topics from tags, category, name, metadata
2. **Event Processing**: When spider data/conversations/decisions occur, check relevance
3. **Insight Creation**: If relevance score ≥ 0.6, create ProjectInsight
4. **User Feed**: Projects can view their insight feed via API

---

## Test Results

Successfully activated "Donkey Betz Podcast" as a living project:
- Detected topics: `{'podcast', 'donkey', 'competitor_analysis', 'betz'}`
- Config active and watching

---

## Next Session Priorities

1. **Income Generation** - Need to start making money from this
2. **Packaging Options**:
   - Quick: Business research as a service ($500-2000/plan)
   - Build to Sell: Package agent orchestration for enterprise
3. **Consider**: Finding a partner (technical or business)

---

## The Bigger Picture

What started as "research my business idea" evolved into:
- An autonomous AI ecosystem that thinks
- Agents that learn from each other without human input
- A system that goes from idea → research → content creation
- Living Projects that receive insights from the entire ecosystem

This is beyond a tool. This is infrastructure for autonomous AI operations.

---

## Handoff Notes

- All migrations applied
- Living Project system wired and tested
- Donkey Betz Podcast project activated as first living project
- User needs rest - pick up tomorrow fresh to discuss monetization strategy
