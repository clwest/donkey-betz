# Session 303: Database Audit + Unified Intelligence Integration

**Date:** December 1, 2025
**Focus:** Database relationship audit + Unified Intelligence Search implementation
**Status:** Complete

---

## Executive Summary

This audit examined all database models and agent implementations to map relationships, identify gaps, and ensure data integrity across the unified platform.

---

## Database Model Inventory

### Core Content Models (`content/models.py`)

| Model | Key Relationships | Notes |
|-------|-------------------|-------|
| `ImageHistory` | `user`, `session`, `project`, `parent_image` | Properly linked to projects |
| `VideoHistory` | `user`, `session`, `project`, `source_image` | Properly linked to projects |
| `CreativeProject` | `user`, `sessions` | Container for all content |
| `AISession` | `user`, `project` | Conversation sessions |
| `MiniFigAsset` | `user` | 3D model storage |

### Unified System Models (`core/models_unified_system.py`)

| Model | Key Relationships | Notes |
|-------|-------------------|-------|
| `SpiderData` | None (standalone) | Raw spider crawl data |
| `Opportunity` | `spider_data` (FK) | Scored from spider data |
| `BusinessResearchResult` | None (standalone) | Stores competitor/customer research with embeddings |
| `PartnershipProject` | `related_research` (M2M to BusinessResearchResult) | Session 302 addition |

### Agent Models (`agents/models.py`)

| Model | Key Relationships | Notes |
|-------|-------------------|-------|
| `UnifiedAgentTemplate` | `creator`, `parent_template` | Agent definitions |
| `AgentExecution` | `template`, `user`, `parent_orchestration` | Execution tracking |
| `AgentContribution` | `agent`, `project`, `image`, `video`, `minifig_asset`, `execution` | Links agents to content |
| `AgentOrchestration` | `user` | Multi-agent workflows |
| `AgentChannel` | `orchestration`, `created_by` | Agent communication |
| `AgentChannelMessage` | `channel`, `agent_instance`, `user` | Messages in channels |

---

## Agent Database Usage Analysis

### Clean Architecture Agents (`core/agents/`)

| Agent | Database Writes | Database Reads | Issues |
|-------|-----------------|----------------|--------|
| `ImageAgent` | Via `_execute_generate_image` → `ImageHistory` | None | Indirect writes OK |
| `VideoAgent` | Via video functions → `VideoHistory` | None | Indirect writes OK |
| `AudioAgent` | None (no AudioHistory model) | None | **MISSING: AudioHistory model** |
| `WorkflowAgent` | None directly | Delegates to other agents | OK - orchestrator pattern |
| `ResearchAgent` | None | SpiderData queries | OK - read-only |
| `CompetitorAnalysisAgent` | `BusinessResearchResult.save_competitor_analysis()` | Prior research via semantic search | **GOOD** |
| `CustomerResearchAgent` | `BusinessResearchResult.save_customer_research()` | Prior research via semantic search | **GOOD** |

### Business Research Flow (Session 302)

```
User Request
    ↓
CompetitorAnalysisAgent
    ├── Queries SpiderData for market intel
    ├── GPT analysis with gpt-5-mini
    └── Saves to BusinessResearchResult
            ↓
CustomerResearchAgent
    ├── Queries SpiderData for customer insights
    ├── Retrieves prior BusinessResearchResult (semantic search)
    ├── GPT analysis with cumulative context
    └── Saves to BusinessResearchResult
            ↓
Create Project Button (Direct API)
    ├── POST /api/projects/from-research/
    └── Creates PartnershipProject with related_research M2M
```

### Image Generation Flow

```
User Request
    ↓
ImageAgent.execute()
    ├── GPT decides parameters
    └── _execute_tool_call("generate_image")
            ↓
_execute_generate_image() (core/views_image.py:421)
    ├── Stability AI API call
    ├── ImageHistory.objects.create() with:
    │   ├── user, prompt, parameters
    │   ├── session (if available)
    │   └── project (if available)
    └── AgentContribution.objects.create()
            ↓
ImageHistory record with project association
```

---

## Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER                                         │
└─────────────────────────────────────────────────────────────────────┘
         │
         ├──────────────────┬──────────────────┬──────────────────┐
         ▼                  ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ CreativeProject │ │   AISession     │ │ PartnershipProj │ │UnifiedAgentTmpl │
│                 │ │                 │ │                 │ │                 │
│ - name          │ │ - project FK    │ │ - related_      │ │ - name          │
│ - description   │ │ - messages      │ │   research M2M  │ │ - system_prompt │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │                   │
         │                   │                   │                   │
    ┌────┴────┬──────────────┤                   │                   │
    ▼         ▼              ▼                   ▼                   ▼
┌────────┐ ┌────────┐ ┌──────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ Image  │ │ Video  │ │ MiniFigAsset │ │BusinessResearch  │ │AgentContribution│
│History │ │History │ │              │ │Result            │ │                 │
│        │ │        │ │              │ │                  │ │ - agent FK      │
│-project│ │-project│ │              │ │ - research_type  │ │ - project FK    │
│-session│ │-session│ │              │ │ - market_topic   │ │ - image FK      │
└────────┘ └────────┘ └──────────────┘ │ - embedding      │ │ - video FK      │
                                       └──────────────────┘ └─────────────────┘
                                                │
                                                │ semantic_search()
                                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         SpiderData                                   │
│  - source, content, url                                             │
│  - metadata, category                                               │
│  - processed_at                                                      │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Opportunity                                  │
│  - spider_data FK                                                   │
│  - opportunity_score                                                │
│  - revenue_potential                                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Issues Found

### 1. **MISSING: AudioHistory Model**
- **Location:** `agents/models.py:778-786` has commented-out AudioHistory FK
- **Impact:** AudioAgent cannot track generated audio
- **Recommendation:** Create `content.AudioHistory` model with same pattern as ImageHistory

### 2. **Clean Agents Don't Track AgentContribution**
- **Location:** `core/agents/image_agent.py` calls `_execute_generate_image` which does create AgentContribution
- **But:** The clean agent architecture should explicitly manage this
- **Impact:** Low - currently working via legacy path

### 3. **No Direct Link: BusinessResearchResult → SpiderData**
- **Location:** `core/models_unified_system.py`
- **Current:** BusinessResearchResult stores `sources_used` as JSON array of strings
- **Impact:** Cannot trace which exact SpiderData records were used
- **Recommendation:** Consider M2M relationship for better provenance

### 4. **PartnershipProject.related_research Missing Migration Check**
- **Location:** Session 302 added M2M field
- **Status:** Migration was created but needs verification
- **Action:** Run `python manage.py showmigrations` to confirm

---

## Healthy Patterns Found

### 1. BusinessResearchResult Semantic Search
- `save_customer_research()` and `save_competitor_analysis()` helper methods
- `generate_embedding()` for vector storage
- `semantic_search()` for finding related research
- `get_research_context_for_prompt()` for enriching image prompts

### 2. AgentContribution Tracking
- Properly links agents → projects → content
- Tracks execution time, tokens used, user rating
- Supports image, video, minifig_asset content types

### 3. Project Context Flow (Session 302)
- Business research agents accept `project_id` parameter
- Automatically inject project context into vague requests
- Related research linked via M2M on PartnershipProject

---

## Recommendations

### Priority 1: Create AudioHistory Model
```python
# content/models.py - Add this model
class AudioHistory(UnifiedBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    file_path = models.TextField()
    audio_type = models.CharField(max_length=50)  # tts, voice_clone, etc.
    prompt = models.TextField(blank=True)
    voice_id = models.CharField(max_length=100, blank=True)
    duration_seconds = models.FloatField(null=True)
    session = models.ForeignKey('AISession', null=True, on_delete=models.SET_NULL)
    project = models.ForeignKey('CreativeProject', null=True, on_delete=models.SET_NULL)
```

### Priority 2: SpiderData Provenance Link
```python
# Add to BusinessResearchResult
source_spider_data = models.ManyToManyField(
    'SpiderData',
    blank=True,
    related_name='research_results',
    help_text="SpiderData records used in this research"
)
```

### Priority 3: Clean Agent Contribution Tracking
- Add explicit `AgentContribution.objects.create()` in clean agent base class
- Currently relies on legacy `_execute_generate_image` path

---

## Verification Commands

```bash
# Check migrations
python manage.py showmigrations

# Verify model relationships
python manage.py shell
>>> from content.models import ImageHistory, VideoHistory, CreativeProject
>>> from core.models_unified_system import BusinessResearchResult, SpiderData, PartnershipProject
>>> from agents.models import AgentContribution, UnifiedAgentTemplate

# Count records
>>> ImageHistory.objects.count()
>>> BusinessResearchResult.objects.count()
>>> AgentContribution.objects.count()

# Test semantic search
>>> results = BusinessResearchResult.semantic_search("AI tools", limit=3)
>>> for r, score in results: print(f"{r.research_type}: {score:.2%}")
```

---

## Next Session Recommendations

1. **Implement AudioHistory model** if audio generation is a priority
2. **Add SpiderData M2M** to BusinessResearchResult for better provenance
3. **Explicit AgentContribution** in clean agents base class
4. **Add unit tests** for database relationship integrity

---

## Files Examined

- `content/models.py` - ImageHistory, VideoHistory, CreativeProject, AISession
- `core/models_unified_system.py` - SpiderData, Opportunity, BusinessResearchResult, PartnershipProject
- `agents/models.py` - UnifiedAgentTemplate, AgentExecution, AgentContribution, AgentOrchestration
- `core/agents/base_agent.py` - BaseAgent class
- `core/agents/image_agent.py` - ImageAgent implementation
- `core/agents/workflow_agent.py` - WorkflowAgent implementation
- `core/agents/business/competitor_analysis_agent.py` - CompetitorAnalysisAgent
- `core/agents/business/customer_research_agent.py` - CustomerResearchAgent
- `core/views_image.py` - _execute_generate_image function

---

## Part 2: Unified Intelligence Integration (Session 303 Continued)

Following the database audit, we implemented a comprehensive unified intelligence system that:

1. **Combines SpiderData + BusinessResearchResult** into one searchable index
2. **Auto-refreshes spider data** before business research runs
3. **Enables prior research context** injection into new analyses

### New Files Created

| File | Purpose |
|------|---------|
| `core/services/unified_intelligence_search.py` | Unified search across spiders + research |

### Files Modified

| File | Changes |
|------|---------|
| `core/agents/business/competitor_analysis_agent.py` | Added unified search, auto-refresh, new tools |
| `core/agents/business/customer_research_agent.py` | Added unified search, auto-refresh, new tools |

### New Agent Tools

Both business research agents now have:

| Tool | Purpose |
|------|---------|
| `refresh_spider_data` | Trigger fresh spider crawls before analysis |
| `get_prior_research` | Retrieve relevant past research to build on |

### Architecture: Unified Intelligence Flow

```
User Request: "Analyze competitors for AI writing tools"
        │
        ▼
┌───────────────────────────────────────────────────────┐
│           CompetitorAnalysisAgent.execute()            │
│                                                        │
│  1. Auto-trigger spider refresh                       │
│     └─> unified_search.refresh_spiders_for_query()    │
│                                                        │
│  2. Get prior research context                        │
│     └─> unified_search.get_research_context()         │
│                                                        │
│  3. Inject context into prompt                        │
│     └─> "## Previous Research Findings..."            │
│                                                        │
│  4. GPT makes tool calls:                             │
│     ├─> get_prior_research (optional)                 │
│     ├─> refresh_spider_data (optional)                │
│     ├─> web_search                                    │
│     ├─> spider_query (uses semantic search)           │
│     └─> generate_swot                                 │
│                                                        │
│  5. Save result with embedding                        │
│     └─> BusinessResearchResult.save_competitor_analysis() │
└───────────────────────────────────────────────────────┘
        │
        ▼
Next research request now has access to this analysis
via unified_search.get_research_context()
```

### UnifiedIntelligenceSearch API

```python
from core.services.unified_intelligence_search import get_unified_intelligence_search

search = get_unified_intelligence_search()

# Search both spider data AND business research
results = search.unified_search(
    query="AI content generation",
    include_spiders=True,
    include_research=True,
    spider_limit=20,
    research_limit=10
)

# Get formatted context for prompt injection
context = search.get_research_context(
    query="AI content generation",
    max_spider_items=3,
    max_research_items=2
)

# Trigger fresh spider crawls
refresh_result = search.refresh_spiders_for_query(
    query="AI writing tools",
    categories=["tech", "news"]  # Optional
)

# Get intelligence stats
stats = search.get_intelligence_stats()
# Returns: {spider_data: {...}, business_research: {...}}
```

### Test Results

```
=== Testing Unified Intelligence Search ===

1. UnifiedIntelligenceSearch imported successfully
2. Intelligence Stats:
   Spider Data: 3017 total, 3012 last 24h
   Research: 28 total (20 competitor, 8 customer)
   Research with embeddings: 28

3. Testing unified search for "AI content generation"...
   Found 6 total results
   - [research] BusinessResearch: Competitor Analysis... (sim: 53.23%)
   - [research] BusinessResearch: Customer Research... (sim: 50.65%)
   - [spider] youtube: AI Video Generators Ranked... (sim: 50.27%)

4. Testing research context generation...
   Context generated: 864 chars

5. Testing spider refresh (dry run)...
   Categories to refresh: ['tech']

=== All Tests Passed! ===
```

### Agent Integration Test

```
=== Testing Agent Integration ===

1. CompetitorAnalysisAgent:
   Tools: [web_search, spider_query, analyze_competitor, generate_swot,
          refresh_spider_data, get_prior_research]
   Has unified_search: True

2. CustomerResearchAgent:
   Tools: [spider_query, web_search, analyze_pain_points, build_persona,
          extract_quotes, refresh_spider_data, get_prior_research]
   Has unified_search: True

3. unified_search property works on both agents
```

---

## Answers to Original Questions

### Q1: Is research being embedded properly?

**YES** - All 28 BusinessResearchResult records have 1536-dimensional embeddings.
The `save_customer_research()` and `save_competitor_analysis()` methods automatically
call `generate_embedding()` after saving.

**Gap Fixed:** SpiderData and BusinessResearchResult now share a unified search
interface via `UnifiedIntelligenceSearch`, so new research can reference both
prior research AND fresh spider data.

### Q2: Are spiders updating in development?

**YES** - 3,012 of 3,017 spider records are from the last 24 hours!
Celery Beat runs `run_spider_network` every 15 minutes.

**Enhancement:** Business research agents now automatically trigger spider
refreshes at the START of analysis to ensure fresh data.

---

## Notes for Future Claude

1. **Spider refresh is async** - The `run_spider_by_category.delay()` call
   triggers Celery tasks in the background. Fresh data won't be immediately
   available but will populate within 1-2 minutes.

2. **Prior research context** - The agents inject context at the start of
   their execute() method, so GPT sees it before making tool decisions.

3. **Unified search singleton** - Use `get_unified_intelligence_search()` to
   get the global instance. It lazy-loads dependencies.

4. **Embedding coverage** - Check `stats["business_research"]["with_embeddings"]`
   to verify all research has embeddings. Should be 100%.

---

---

## Part 3: Complete Agent Database Audit

### Clean Architecture Agents (`core/agents/`)

| Agent | Database Writes | Database Reads | Pattern |
|-------|-----------------|----------------|---------|
| `ImageAgent` | Via `_execute_generate_image` → `ImageHistory` + `AgentContribution` | None | **GOOD** - delegated |
| `VideoAgent` | Via `_execute_generate_video` → `VideoHistory` | None | **GOOD** - delegated |
| `AudioAgent` | None (no AudioHistory model) | None | **MISSING** - needs AudioHistory |
| `ResearchAgent` | None | SpiderData queries via SpiderIntelligenceService | **OK** - read-only |
| `WorkflowAgent` | None directly | Delegates to other agents | **OK** - orchestrator |
| `CompetitorAnalysisAgent` | `BusinessResearchResult.save_competitor_analysis()` | Prior research via unified_search | **EXCELLENT** |
| `CustomerResearchAgent` | `BusinessResearchResult.save_customer_research()` | Prior research via unified_search | **EXCELLENT** |
| `ImageEditingAgent` | Via editing functions → updates `ImageHistory` | `ImageHistory` by ID | **GOOD** |
| `VideoEditingAgent` | Via editing functions → updates `VideoHistory` | `VideoHistory` by ID | **GOOD** |
| `ThreeDAgent` | Via 3D functions → `MiniFigAsset` | None | **GOOD** |
| `PersonalAssistantAgent` | None | Intent detection only | **OK** - router |

### Legacy Agents (`agents/`)

| Component | Database Operations | Pattern |
|-----------|---------------------|---------|
| `agents/views.py` | `AgentExecution.objects.create()` | Tracks all agent runs |
| `agents/views.py` | `AgentContribution.objects.create()` | Links agents to content |
| `agents/views.py` | `AgentChannel.objects.create()` | Agent communication |
| `agents/views.py` | `AgentChannelMessage.objects.create()` | Channel messages |
| `agents/views.py` | `AgentChannelMembership.objects.create()` | Channel membership |

### Database Write Flow

```
User Request → Agent.execute()
        │
        ├─── ImageAgent
        │      └─> _execute_generate_image() (core/views_image.py:421)
        │              ├─> ImageHistory.objects.create()
        │              └─> AgentContribution.objects.create()
        │
        ├─── VideoAgent
        │      └─> _execute_generate_video()
        │              └─> VideoHistory.objects.create()
        │
        ├─── CompetitorAnalysisAgent
        │      └─> BusinessResearchResult.save_competitor_analysis()
        │              └─> generate_embedding() (auto)
        │
        ├─── CustomerResearchAgent
        │      └─> BusinessResearchResult.save_customer_research()
        │              └─> generate_embedding() (auto)
        │
        └─── AudioAgent
               └─> ??? (NO AudioHistory model - MISSING)
```

### Audit Summary

**What's Working Well:**
1. `ImageHistory` correctly linked to `session`, `project`, `parent_image`
2. `AgentContribution` tracks agent → content relationships (Session 142)
3. `BusinessResearchResult` has automatic embedding generation
4. `BusinessResearchResult` has semantic search for prior research
5. `PartnershipProject.related_research` M2M for project-research links
6. Legacy agents use proper `AgentExecution` tracking

**What Needs Improvement:**

| Priority | Issue | Impact | Recommendation |
|----------|-------|--------|----------------|
| **HIGH** | Missing `AudioHistory` model | Audio generation not tracked | Create model |
| **MEDIUM** | No `SpiderData` → `BusinessResearchResult` link | Can't trace data provenance | Add M2M field |
| **LOW** | Clean agents rely on legacy path for `AgentContribution` | Works but indirect | Make explicit |
| **LOW** | `VideoEditingAgent` doesn't use session/project | Video edits not grouped | Pass context |

---

## Documentation Updates Made

| File | Changes |
|------|---------|
| `CLAUDE.md` | Session 303 summary, unified intelligence docs |
| `docs/AGENTS.md` | Added CompetitorAnalysisAgent, CustomerResearchAgent with new tools |
| `docs/ARCHITECTURE.md` | Added unified intelligence section, updated database models |
| `docs/handoffs/SESSION_303_DATABASE_RELATIONSHIP_AUDIT.md` | This document |

---

**Session 303 Complete: Database Audit + Unified Intelligence Integration + Full Agent Audit**

