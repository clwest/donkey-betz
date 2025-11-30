# Session 293: Workflow Engine + Creative Toolbox + Business Research Agents + Semantic Routing

**Date:** November 30, 2025
**Previous Session:** 292 (Main/Project Assistant Separation)
**Session Type:** Feature Enhancement - Workflow Engine + Projects + Bug Fix + Business Intelligence + Semantic Routing
**Status:** ALL 6 HANDOFFS COMPLETE + WORKFLOW ENGINE ENHANCED + CREATIVE TOOLBOX FIXED + BUSINESS RESEARCH AGENTS ADDED + SEMANTIC ROUTING INTEGRATED

---

## SESSION 293 CHANGES

### NEW: Semantic Routing Service (Session 293 Part 3) - INTEGRATED!

**Problem:** The existing RAG/embedding system was completely ORPHANED - not connected to agent routing at all. Agent routing used crude keyword matching instead of semantic understanding.

**Solution:** Created `SemanticRoutingService` that uses OpenAI embeddings (`text-embedding-3-small`) to match user queries to agents based on semantic similarity.

**New Files:**
- `core/services/semantic_routing.py` - SemanticRoutingService with embedding-based routing

**How It Works:**
1. Pre-computes embeddings for each agent's capabilities (description + examples + keywords)
2. When a query comes in, generates embedding for the query
3. Calculates cosine similarity between query and each agent
4. Returns agent with highest similarity score (if above threshold 0.45)
5. Falls back to keyword matching if semantic confidence is low

**Integration Points:**
- `core/agents/personal_assistant_agent.py` - `_detect_agent()` now uses 2-tier routing:
  - **Tier 0:** Workflow patterns (highest priority - checked first)
  - **Tier 1:** Semantic routing (embeddings-based)
  - **Tier 2:** Keyword fallback (if semantic fails or low confidence)

**Agent Capabilities Embedded (12 agents):**
- ImageAgent, VideoAgent, AudioAgent, ThreeDAgent
- ImageEditingAgent, VideoEditingAgent
- ResearchAgent, CompetitorAnalysisAgent, CustomerResearchAgent
- WorkflowAgent, ContentStrategyAgent, BrandIdentityAgent

**Test Results (100% accuracy):**
```
Query: Research the AI writing assistant market for my startup...
  -> CompetitorAnalysisAgent (confidence=0.602, semantic)

Query: Create a cyberpunk logo for my tech company...
  -> ImageAgent (confidence=0.445, semantic)

Query: Build customer personas for fitness apps...
  -> CustomerResearchAgent (confidence=0.543, semantic)

Query: Upscale image 5 to 4x resolution...
  -> ImageEditingAgent (via semantic)

Query: Create a video showing a sunset...
  -> VideoAgent (via semantic)

Query: What's trending in design...
  -> ResearchAgent (keyword fallback)
```

---

### NEW: Memory Embedding Service (Session 293 Part 4) - COMPLETE!

**New File:** `core/services/memory_embedding_service.py`

Enables semantic search across agent memories (Memory Palace):
- `create_memory()` - Create memories with auto-generated embeddings
- `search_memories()` - Search agent memories by semantic similarity
- `backfill_embeddings()` - Generate embeddings for existing memories
- `get_memory_context()` - Get relevant memories as context for agent prompts
- Auto-connects related memories based on similarity (threshold 0.7)

**Usage:**
```python
from core.services.memory_embedding_service import get_memory_embedding_service

service = get_memory_embedding_service()
results = service.search_memories(agent, "What does the user prefer for logos?")
```

---

### NEW: Spider Semantic Search (Session 293 Part 5) - COMPLETE!

**Problem:** SpiderData (7,150+ entries) was only searchable via keyword matching.

**Solution:** Added embedding support directly to SpiderData model + semantic search service.

**Database Changes:**
- Added `embedding` JSONField to SpiderData model
- Added `item_embeddings` JSONField for individual item embeddings
- Added `embedding_text` TextField for debugging
- Added `get_searchable_text()` method to model
- Migration: `0056_add_spider_data_embeddings`

**New File:** `core/services/spider_semantic_search.py`

**Key Methods:**
- `semantic_search()` - Semantic search with on-the-fly embeddings
- `semantic_search_with_db_embeddings()` - Fast search using pre-computed DB embeddings
- `backfill_embeddings()` - Generate embeddings for existing spider data
- `get_embedding_stats()` - Get embedding coverage stats
- `enhance_agent_context()` - Get relevant spider data for agent prompts

**Usage:**
```python
from core.services.spider_semantic_search import get_spider_semantic_search

search = get_spider_semantic_search()

# Fast search using DB embeddings
results = search.semantic_search_with_db_embeddings("AI machine learning tools", limit=10)

# Backfill embeddings (run periodically or via Celery)
stats = search.backfill_embeddings(batch_size=100)
```

---

### Fixed "Research and Create" Workflow - FULLY WORKING!

**Problems Fixed:**

1. **10 images instead of 3** - Now capped at 5, defaults to 3
2. **Research not injected** - Colors, mood, composition now INJECTED into prompt
3. **No project created** - Projects now auto-created with FULL metadata
4. **"Try Including" suggestions** - Changed to "Research Applied" confirmation
5. **Projects missing data** - Now includes Research Sources + Executive Recommendations

### Fixed Creative Toolbox Image Selection - WORKING!

**Problem:** When using Creative Toolbox (Upscale, Inpaint, etc.) from the Projects tab, the image dropdown showed "No images available" even though the project had images.

**Root Causes:**
1. API was filtering by `user=request.user` but workflow images were created by admin
2. All images were stored as data URIs (`data:image/png;base64,...`) and the API had `.exclude(file_path__startswith='data:')` filter
3. `_add_to_project` function was using wrong FK relationship

**Fixes Applied:**
1. **`core/views_image.py`**:
   - Modified `image_history` to not filter by user when `project_id` is provided
   - Removed data URI exclusion for project-based queries
   - Added URL replacement to use `/api/images/{id}/view/` instead of huge base64 strings
   - Added new `serve_image` endpoint to serve actual image data from data URIs

2. **`core/urls.py`**:
   - Added `path('api/images/<uuid:image_id>/view/', serve_image, name='serve-image')`

3. **`agents/workflow_engine.py`**:
   - Fixed `_add_to_project` to use `image.project = project; image.save()` instead of `project.images.add(image)`
   - Changed from `project.images.count()` to `project.project_images.count()`

### NEW: Business Research Agents (No Image/Video API Calls!) - FULLY WIRED!

Added 2 new specialized agents for business intelligence:

1. **CompetitorAnalysisAgent** (`core/agents/business/competitor_analysis_agent.py`)
   - Analyzes competitors in a given market
   - Generates SWOT analysis
   - Tracks features, pricing, positioning
   - Uses web search + spider data (no Stability AI needed)

2. **CustomerResearchAgent** (`core/agents/business/customer_research_agent.py`)
   - Researches customer pain points from Reddit/forums
   - Builds detailed customer personas
   - Extracts sentiment and customer quotes
   - Uses spider network (especially Reddit) - no APIs needed

**Files Modified for Full Integration:**
- `core/agents/business/__init__.py` - Package exports
- `core/agents/__init__.py` - Added to agent exports (now 24 total)
- `core/agent_router.py` - Added to AGENT_MAP
- `core/prompts/registry.py` - Added routing rules for business research
- `core/prompts/tool_descriptions.py` - Added tool descriptions
- `core/assistant/tool_definitions.py` - Added GPT tool definitions
- `core/personal_ai_assistant_enhanced.py` - Added tool call handlers

### Fixed Business Research Routing (Session 293 Part 2)

**Problem:** "Research AI writing assistant market for my startup idea" was routing to basic `ResearchAgent` instead of `CompetitorAnalysisAgent`.

**Root Cause:** Multiple routing systems in the codebase weren't aware of the new business research agents:
1. `PersonalAssistantAgent` uses its own `INTENT_KEYWORDS` mapping for routing
2. The keyword scoring system was including business research agents even for creation requests

**Fixes Applied to `core/agents/personal_assistant_agent.py`:**
1. Added business research agents to `INTENT_AGENT_MAP`
2. Added business research keywords to `INTENT_KEYWORDS` (market, startup, competitors, etc.)
3. Added agents to the GPT `tools` enum
4. Updated system prompt to mention business research agents
5. Added special logic: Business research agents ONLY matched when there's NO creation intent
   - "Research market for my startup" → CompetitorAnalysisAgent
   - "Create a logo for my startup" → ImageAgent (creation intent takes priority)
6. Excluded business research agents from keyword scoring when creation intent detected

**Testing Verified:**
```
PASS | Research AI writing assistant market for my startup → CompetitorAnalysisAgent
PASS | Build customer personas for fitness apps → CustomerResearchAgent
PASS | Create a logo for my startup → ImageAgent
PASS | Research and create 3 logos → WorkflowAgent
```

**New Workflows Added:**
- `business_research` - Full business intelligence (market + competitors + customers)
- `competitor_analysis` - Deep dive into competitors
- `customer_personas` - Build customer personas from research

**Usage Examples:**
```
"Research the AI writing assistant market for my startup idea"
→ Market trends + Competitor analysis + Customer personas + SWOT

"Analyze competitors in the coffee subscription market"
→ Competitor list + Feature comparison + Pricing + SWOT analysis

"Build customer personas for fitness apps"
→ 3 detailed personas with pain points, goals, and quotes
```

### NEW: Full Project Creation with Intelligence Data

Projects created by workflow now include:

- **Status, Category, Colors, Tags** - Auto-populated from intent
- **Goal & Description** - Rich text with research insights
- **🔍 Research Sources (5)** - Clickable links from spider network
- **👔 Executive Team Recommendations (5)** - CTO, COO, CreativeDirector, CFO, DataAnalyst
- **🚀 Suggested Next Steps** - Actionable recommendations
- **🚀 Open Project button** - Navigate to Projects tab for 33 editing tools

**Files Changed:**

1. **`agents/workflow_engine.py`**
   - `_extract_count()`: Added logging, capped at 5 images max
   - `_generate_images()`: Hard cap at 5, default to 3, SD3 for all logos
   - `PromptEnhancer.enhance()`: NOW INJECTS colors, mood, composition into prompt
   - `_create_or_update_project()`: **COMPLETELY REWRITTEN** - Creates FULL projects with:
     - `metadata.research_links` - Spider research sources with titles, snippets, links
     - `metadata.agent_recommendations` - 5 executives with stance and response
     - `metadata.suggested_next_steps` - Actionable next steps
     - `metadata.spider_intelligence` - Summary, trending keywords, data points
     - `metadata.co_leadership` - Color, composition, mood recommendations
     - Category, colors, tags auto-populated
   - `_add_to_project()`: Fixed FK relationship for adding images to projects

2. **`ai_core/templates/ai_image_studio.html`**
   - Changed "Try Including in Your Next Prompt" to "Research Applied to Your Images"
   - Green styling to indicate success, not suggestion
   - Added "🚀 Open Project" button to navigate to Projects tab
   - Added `openProjectInTab()` function for seamless project navigation
   - Fixed predictions error with null checks
   - Research+create workflows now ALWAYS create NEW projects (not add to existing)
   - Added debug logging to `populateImageDropdown` function

3. **`content/models.py`**
   - Added `metadata` JSONField to CreativeProject model for rich intelligence data

4. **`core/prompts/registry.py`**
   - Updated routing rules for workflow_orchestration_agent
   - Made "research + create" pattern MANDATORY for workflow agent

5. **`core/personal_ai_assistant_enhanced.py`**
   - Updated tool descriptions to defer to workflow agent for research+create

6. **`core/views_image.py`**
   - Fixed `image_history` API for project-based queries (no user filter, no data URI exclusion)
   - Added URL truncation for data URIs to prevent huge JSON responses
   - Added new `serve_image` endpoint to serve actual image data from data URIs

7. **`core/urls.py`**
   - Added `serve_image` URL pattern for `/api/images/<uuid:image_id>/view/`

---

## Workflow Engine Now Works Like This:

```
User: "Research trending AI logos and create a logo for my startup"
                    |
                    v
        Frontend detects pattern
                    |
                    v
    Calls /api/v2/workflow/execute/
                    |
                    v
        WorkflowEngine.execute()
                    |
    +---------------+---------------+
    |               |               |
    v               v               v
Spider Research  Executive Input  Intent Parse
(trending data)  (colors, mood)   (style, count)
    |               |               |
    +-------+-------+-------+-------+
            |
            v
    PromptEnhancer.enhance()
    - User style (SACRED)
    - User subject (SACRED)
    - INJECT colors, mood, composition  <-- NEW!
            |
            v
    Generate 3-5 images (SD3 for animated styles)
            |
            v
    Auto-create project with all images
            |
            v
    Return result with "Research Applied" confirmation
```

---

## All Handoffs Status - **100% COMPLETE**

| # | Handoff | Priority | Status |
|---|---------|----------|--------|
| 01 | Frontend Componentization | CRITICAL | **COMPLETE (60% reduction)** |
| 02 | Agent Architecture Unification | HIGH | **COMPLETE** |
| 03 | Sci-Fi Feature Rationalization | MEDIUM | **COMPLETE (15->7 features)** |
| 04 | Database Model Consolidation | MEDIUM-HIGH | **COMPLETE** |
| 05 | Test Infrastructure Overhaul | HIGH | **COMPLETE** |
| 06 | Spider Network Wiring | MEDIUM | **COMPLETE** |

---

## Platform Stats

```
CODEBASE HEALTH
├── Frontend: 22,605 lines (was 56,697) - 60% smaller
├── Spiders: 70/70 working (100%)
├── Agents: 11 clean + 22 legacy (24 in router)
├── Tests: 83 agent tests passing
├── Spider Data: 4,910+ entries
├── Sci-Fi: 7 active (was 15) - simplified
├── Synergy Pairs: 25+ defined
├── Assistants: Main + Project (separate)
├── Workflow Engine: FULLY WORKING!
└── Business Research: 2 agents (no image/video credits!)
```

---

## Quick Start

```bash
cd /Users/donkeyking/development/unified-donkey-betz
make start && make celery
open http://localhost:8000/ai-studio/
```

---

## Test the Workflow

Try this prompt in the AI Assistant:
```
Research trending AI logos and create a logo for my AI content generation app in the DreamWorks style.
```

You should see:
1. Spider Intelligence Research (trending topics)
2. Co-Leadership Creative Direction (colors, mood, composition)
3. Your Creative Vision (style preserved)
4. Research Applied to Your Images (confirmation)
5. Project Created (with all images bundled)
6. 5 Generated Logos (with research injected into prompts)
7. **🚀 Open Project button** - Click to access all 33 editing tools!

---

## Projects Tab - 33 Editing Tools

After workflow creates a project, click "🚀 Open Project" to access:

**Image Tools (11):**
- Upscale, Outpaint, Inpaint, Erase, Search & Replace
- Remove Background, Control Sketch, Control Structure
- Style, Relight, 3D Model

**Video Tools (12):**
- Create Video, Animate, Extend, Insert Frame
- Slow Motion, Color Grade, Effects, Transitions
- Audio Overlay, Export, Preview, Interpolate

**Audio Tools (5):**
- Text-to-Speech, Sound Effects, Voice Clone
- Music Generation, Audio Mix

**3D Tools (3):**
- 3D Model, Scene Generation, Texture

**Character Tools (2):**
- Train Character, Generate with Character

---

**ALL HANDOFFS COMPLETE! Workflow Engine fully operational!**
