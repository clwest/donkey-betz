# Deprecated Agents Inventory

**Date:** December 1, 2025
**Updated:** Session 308 - All high-priority agents wired!
**Purpose:** Evaluate deprecated agents for learning integration or replacement

---

## Summary

| Agent | Lines | Learning | Spider | TimeTravel | Recommendation |
|-------|-------|----------|--------|------------|----------------|
| OpportunityScoringAgent | 1342 | ✅ | ✅ | ❌ | **DONE** - Session 307 |
| BrandIdentityAgent | 555 | ✅ | ❌ | ❌ | **DONE** - Session 308 |
| SEOOptimizerAgent | 558 | ✅ | ❌ | ❌ | **DONE** - Session 308 |
| TrendAnalysisAgent | 618 | ✅ | ✅ | ❌ | **DONE** - Session 308 |
| ContentStrategyAgent | 468 | ✅ | ✅ | ❌ | **DONE** - Session 308 |
| SocialMediaAgent | 587 | ✅ | ❌ | ❌ | **DONE** - Session 308 |
| ImageAgent | 877 | ❌ | ✅ | ✅ | **REPLACE** - Use core/agents/image_agent.py |
| ResearchAgent | 764 | ❌ | ✅ | ✅ | **REPLACE** - Use core/agents/research_agent.py |
| CreativeDirectorAgent | 774 | ✅ | ❌ | ❌ | **DONE** - Session 306 |
| VideoAgent | 1887 | ❌ | ❌ | ❌ | **REPLACE** - Use core/agents/video_agent.py |
| AudioAgent | 665 | ✅ | ❌ | ❌ | **DONE** - Session 305 |
| CTOAgent | 847 | ✅ | ❌ | ❌ | **DONE** - Session 306 |
| COOAgent | 434 | ✅ | ❌ | ❌ | **DONE** - Session 306 |
| MeetingCoordinatorAgent | 448 | ✅ | ❌ | ❌ | **DONE** - Session 306 |
| CharacterTrainingAgent | 307 | ✅ | ❌ | ❌ | **DONE** - Session 306 |
| TrainedCreationAgent | 443 | ✅ | ❌ | ❌ | **DONE** - Session 306 |
| ThreeDGenerationAgent | 201 | ❌ | ❌ | ❌ | **REPLACE** - Use core/agents/three_d_agent.py |
| MemoryIsolationAgent | 385 | ✅ | ❌ | ❌ | **DONE** - Session 306 |

---

## Detailed Analysis

### HIGH PRIORITY - Wire with Learning Hooks

#### 1. ContentStrategyAgent (468 lines)
**Location:** `agents/_deprecated/content_strategy_agent.py`
**Current Features:** SpiderContextMixin
**Purpose:** Content recommendations from trends and market data
**Why Wire:** Already uses spider data. Learning would help it remember which strategies work best for different content types.
**Learning Value:** HIGH - Can learn from successful content patterns

#### 2. BrandIdentityAgent (555 lines)
**Location:** `agents/_deprecated/brand_identity_agent.py`
**Current Features:** None
**Purpose:** Brand colors, styles, consistency analysis
**Why Wire:** Brand patterns are highly learnable - successful color combos, style preferences
**Learning Value:** HIGH - Brand patterns are consistent and learnable

#### 3. SEOOptimizerAgent (558 lines)
**Location:** `agents/_deprecated/seo_optimizer_agent.py`
**Current Features:** None
**Purpose:** Hashtags, metadata, SEO optimization
**Why Wire:** SEO success is measurable - learning from what works
**Learning Value:** HIGH - Clear success metrics

#### 4. TrendAnalysisAgent (618 lines)
**Location:** `agents/_deprecated/trend_analysis_agent.py`
**Current Features:** None
**Purpose:** Trending topics, colors, styles analysis
**Why Wire:** Combine with spider data + learning for powerful trend prediction
**Learning Value:** HIGH - Patterns in trends are learnable

#### 5. SocialMediaAgent (587 lines)
**Location:** `agents/_deprecated/social_media_agent.py`
**Current Features:** None
**Purpose:** Platform-specific content optimization
**Why Wire:** Each platform has learnable patterns
**Learning Value:** MEDIUM-HIGH - Platform-specific learning

---

### MEDIUM PRIORITY - Evaluate for Wiring

#### 6. CreativeDirectorAgent (774 lines)
**Location:** `agents/_deprecated/creative_director_agent.py`
**Current Features:** None
**Purpose:** High-level creative direction and coordination
**Consideration:** Large and complex - may benefit from learning but needs review
**Learning Value:** MEDIUM - Creative direction is subjective

---

### ALREADY COMPLETE

#### 7. OpportunityScoringAgent (1342 lines) ✅
**Location:** `agents/_deprecated/opportunity_scoring_agent.py`
**Current Features:** Learning hooks, SpiderContextMixin
**Status:** Wired in Session 307
**Learning Value:** Already learning!

---

### REPLACE WITH CLEAN ARCHITECTURE

These deprecated agents have clean architecture replacements in `core/agents/`:

| Deprecated | Clean Replacement | Notes |
|------------|-------------------|-------|
| ImageAgent | core/agents/image_agent.py | Already has learning via BaseAgent |
| VideoAgent | core/agents/video_agent.py | Already has learning via BaseAgent |
| AudioAgent | core/agents/audio_agent.py | Already has learning via BaseAgent |
| ResearchAgent | core/agents/research_agent.py | Already has learning via BaseAgent |
| ThreeDGenerationAgent | core/agents/three_d_agent.py | Already has learning via BaseAgent |

---

### ARCHIVE - Low Priority

| Agent | Reason |
|-------|--------|
| CTOAgent | Executive role, not content generation |
| COOAgent | Executive role, not content generation |
| MeetingCoordinatorAgent | Low usage, niche use case |
| CharacterTrainingAgent | Niche - character/avatar training |
| TrainedCreationAgent | Depends on CharacterTrainingAgent |
| MemoryIsolationAgent | Infrastructure agent, not user-facing |

---

## Recommended Session 308 Actions

### Option A: Wire Top 3 Content Agents
1. **BrandIdentityAgent** - Brand pattern learning
2. **SEOOptimizerAgent** - SEO success learning
3. **TrendAnalysisAgent** - Trend pattern learning + spider data

### Option B: Wire All 5 High-Priority Agents
All 5 agents from "HIGH PRIORITY" section above

### Option C: Clean Up and Replace
1. Delete deprecated agents that have clean replacements
2. Wire remaining high-value agents
3. Archive low-priority agents

---

## Quick Reference - Files to Wire

```bash
# High priority (no clean replacement, high learning value):
agents/_deprecated/brand_identity_agent.py
agents/_deprecated/seo_optimizer_agent.py
agents/_deprecated/trend_analysis_agent.py
agents/_deprecated/content_strategy_agent.py
agents/_deprecated/social_media_agent.py

# Already wired:
agents/_deprecated/opportunity_scoring_agent.py  # Session 307

# Have clean replacements (use core/agents/ instead):
agents/_deprecated/image_agent.py      # Use core/agents/image_agent.py
agents/_deprecated/video_agent.py      # Use core/agents/video_agent.py
agents/_deprecated/audio_agent.py      # Use core/agents/audio_agent.py
agents/_deprecated/research_agent.py   # Use core/agents/research_agent.py
agents/_deprecated/three_d_generation_agent.py  # Use core/agents/three_d_agent.py
```

---

**Total Deprecated Agents:** 18
**Wired with Learning:** 14 (Sessions 305-308)
**Have Clean Replacements:** 4 (Image, Video, Research, 3D)
**Remaining:** 0 - All evaluated!

---

## Session Progress

| Session | Agents Wired |
|---------|--------------|
| 305 | AudioAgent |
| 306 | PromptEngineeringAgent, CTOAgent, COOAgent, MeetingCoordinatorAgent, CharacterTrainingAgent, TrainedCreationAgent, MemoryIsolationAgent, CreativeDirectorAgent |
| 307 | OpportunityScoringAgent |
| 308 | BrandIdentityAgent, SEOOptimizerAgent, TrendAnalysisAgent, ContentStrategyAgent, SocialMediaAgent |
