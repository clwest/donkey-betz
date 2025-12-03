# Session 338: Implement Universal Agent Integration

**Date:** December 3, 2025
**Previous Session:** 337 - BrandStrategyAgent Complete + Universal Blueprint
**Branch:** `feature/session-52-ai-assistant`

---

## CRITICAL: Read the Blueprint First!

**`docs/handoffs/SESSION_337_UNIVERSAL_AGENT_INTEGRATION_BLUEPRINT.md`**

This blueprint is the culmination of 337 sessions. It shows how to connect ALL agents to the living, learning ecosystem with a `BaseBusinessResearchAgent` that reduces new agents from 1000+ lines to ~100 lines.

---

## Session 337 Achievements

### Part 1: BrandStrategyAgent Complete Integration
| Task | Status |
|------|--------|
| Fix JavaScript syntax error in report rendering | **Complete** |
| Add `raw_data` to AgentResult for source display | **Complete** |
| Fix "Add to Project" button (was creating new projects) | **Complete** |
| Source articles display in dropdown | **Complete** |
| Full feature parity with CustomerResearchAgent | **Complete** |

### Part 2: Universal Agent Integration Blueprint
| Task | Status |
|------|--------|
| Document current architecture gap | **Complete** |
| Design BaseBusinessResearchAgent class | **Complete** |
| Create child agent examples | **Complete** |
| Create 5-phase migration roadmap | **Complete** |
| Frontend configuration design | **Complete** |

---

## Quick Start

```bash
# Start the platform
make start && make celery

# Access AI Studio
open http://localhost:8000/ai-studio/

# Test working agents:
# 1. Click on "Donkey Betz Podcast" project
# 2. Say "Analyze competitors" - CompetitorAnalysisAgent
# 3. Say "Research customer pain points" - CustomerResearchAgent
# 4. Say "Create a brand strategy" - BrandStrategyAgent
# All should display with source data dropdown + Add to Project button
```

---

## The Vision: Universal Agent Pattern

```
BaseBusinessResearchAgent (~800 lines)
    ├── unified_search property
    ├── Auto spider refresh
    ├── Prior research context
    ├── Standard tools (refresh, prior_research, spider, web)
    ├── raw_data extraction
    └── BusinessResearchResult saving

    ↓ Child agents only define:

ContentStrategyAgent (~100 lines)
    ├── research_type = "content_strategy"
    ├── system_prompt
    └── get_synthesis_prompt()

MarketingStrategyAgent (~100 lines)
    ├── research_type = "marketing_strategy"
    ├── system_prompt
    └── get_synthesis_prompt()
```

**77% code reduction** + consistent behavior + easier maintenance.

---

## Implementation Roadmap

### Phase 1: Create Base Class (Session 338) ← YOU ARE HERE
1. Create `core/agents/business/base_business_research_agent.py`
2. Create `core/agents/business/content_strategy_agent.py`
3. Add tool definition + routing
4. Test full flow

### Phase 2: Add Marketing Strategy (Session 338-339)
1. Create `core/agents/business/marketing_strategy_agent.py`
2. Add tool definition + routing
3. Test full flow

### Phase 3: Migrate Existing Agents (Session 339-340)
1. Refactor CompetitorAnalysisAgent → use base class
2. Refactor CustomerResearchAgent → use base class
3. Refactor BrandStrategyAgent → use base class

### Phase 4: Add More Agents (Session 341+)
- SEOResearchAgent
- SocialMediaStrategyAgent
- EmailMarketingAgent
- PricingStrategyAgent
- PartnershipAgent

### Phase 5: Frontend Unification
- Make `formatAnalysisReport` data-driven
- Config object for icons/labels
- Universal research type handling

---

## Current Agent Status

### Fully Integrated (The Gold Standard)
| Agent | Location | Pattern |
|-------|----------|---------|
| CompetitorAnalysisAgent | business/ | Full integration |
| CustomerResearchAgent | business/ | Full integration |
| BrandStrategyAgent | business/ | Full integration |

### To Be Created with Base Class
| Agent | research_type | Purpose |
|-------|--------------|---------|
| ContentStrategyAgent | content_strategy | What content to create |
| MarketingStrategyAgent | marketing_strategy | How to market |
| SEOResearchAgent | seo_research | Keywords + optimization |

### Legacy (Different Pattern)
| Agent | Location | Notes |
|-------|----------|-------|
| ContentStrategyAgent | strategy/ | Clean architecture, not connected |
| SEOOptimizerAgent | strategy/ | Clean architecture, not connected |

---

## The Living, Learning Ecosystem

Every agent connects to:
```
User Request
    ↓
Personal Assistant → Routes to agent
    ↓
BaseBusinessResearchAgent
    ├── 74 Spiders → Fresh data
    ├── Prior Research → Cumulative intelligence
    ├── Project Context → Builds on existing work
    └── GPT + Tools → Intelligent gathering
    ↓
Save to BusinessResearchResult
    ↓
Becomes prior research for future agents
    ↓
Agent Learning System
    ├── Learns from feedback
    ├── Shares knowledge
    └── Dreams about improvements
```

**Every analysis makes the system smarter.**

---

## Files to Create (Session 338)

| File | Purpose | Lines |
|------|---------|-------|
| `core/agents/business/base_business_research_agent.py` | Base class | ~800 |
| `core/agents/business/content_strategy_agent.py` | Content agent | ~100 |
| `core/agents/business/marketing_strategy_agent.py` | Marketing agent | ~100 |

## Files to Modify

| File | Changes |
|------|---------|
| `core/agents/business/__init__.py` | Export new agents |
| `core/assistant/tool_definitions.py` | Add tool definitions |
| `core/personal_ai_assistant_enhanced.py` | Add keywords + handlers |
| `ai_core/templates/ai_image_studio.html` | Add RESEARCH_TYPES config |

---

## System Stats
- **199 total agents** (36 active + growing)
- **74 spiders** across 20 categories
- **47+ business research results**
- **610+ knowledge entries**
- **233+ agent conversations**
- **3 fully integrated business agents** (Competitor, Customer, Brand)

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| `docs/handoffs/SESSION_337_UNIVERSAL_AGENT_INTEGRATION_BLUEPRINT.md` | **THE BLUEPRINT** |
| `docs/handoffs/SESSION_337_BRAND_STRATEGY_COMPLETE_INTEGRATION.md` | BrandStrategy fixes |
| `docs/handoffs/SESSION_336_BRAND_STRATEGY_FEATURE_PARITY.md` | Feature parity work |

---

**Status:** Session 337 COMPLETE. Blueprint created. Ready to implement BaseBusinessResearchAgent!

**This is what 337 sessions have been building towards - a truly intelligent, self-improving AI platform.**
