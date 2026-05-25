# Session 453: Personal Assistant Routing Overhaul

**Date:** December 15, 2025
**Status:** READY FOR IMPLEMENTATION
**Priority:** HIGH - Critical for Go-To-Market trust

---

## The Problem

The Personal Assistant is the gateway to the entire platform. For the Golden Goose Strategy to work, users must be able to trust the assistant to:
- Route to correct agents without micromanagement
- Know when to answer directly vs delegate
- Suggest appropriate workflows (research before creation)
- Handle ambiguous requests intelligently

**Current State:** Works ~90% of the time, but edge cases erode user trust.

---

## Architecture Overview

The system uses a **3-tier routing strategy**:

```
User Request → PersonalAssistantAgent
  ├→ Tier 0: Question detection (answer directly vs route)
  ├→ Tier 1: Semantic routing (embedding similarity, 0.45 threshold)
  ├→ Tier 2: Keyword matching (deterministic fallback)
  └→ Tier 3: GPT routing (only if all else fails)
```

**Key Design:** Routing is primarily deterministic (90%), with GPT as fallback.

---

## Critical Issues to Fix

### Issue 1: Question Detection is Fuzzy

**Location:** `core/agents/personal_assistant_agent.py` lines 538-585

**Problem:** Research-related keywords are excluded from "direct answer" path, causing unnecessary agent routing.

**Example:**
- User: "What's trending in AI?"
- Current: Routes to ResearchAgent (slow, unnecessary)
- Expected: Answer directly with GPT using spider data

**Code causing issue (lines 545-555):**
```python
research_indicators = [
    'trending', 'trend', 'latest', 'recent', 'whats hot',
    'hot in', 'update on', 'news about'
]
# These are EXCLUDED from direct answers, causing routing
```

**Fix:** Distinguish between:
- "What's trending?" → Answer directly (informational)
- "Research trends and create content" → Route to agent (action)

---

### Issue 2: Business Research Guard Too Simplistic

**Location:** `core/agents/personal_assistant_agent.py` lines 660-679

**Problem:** The `has_creation` boolean blocks business research routing even when research is needed.

**Example:**
- User: "Create a logo for my AI startup"
- Current: Goes straight to ImageAgent (creation detected)
- Expected: Suggest market research first, then create

**Code causing issue:**
```python
if not has_creation:  # Only routes to research if NO creation words
    if 'for my startup' in task_lower:
        return 'CompetitorAnalysisAgent'
```

**Fix:** Detect business context separately, suggest research workflow:
```
"I see you're working on a startup. Would you like me to:
1. Research the market first, then create visuals
2. Just create the logo now"
```

---

### Issue 3: Fragmented Sources of Truth

**Problem:** Agent capabilities defined in 4+ places that can get out of sync.

| File | What It Defines |
|------|-----------------|
| `personal_assistant_agent.py` lines 119-220 | INTENT_KEYWORDS |
| `semantic_routing.py` lines 60-150+ | AGENT_CAPABILITIES |
| `tool_descriptions.py` lines 22-497 | TOOL_DESCRIPTIONS |
| `tool_definitions.py` | Tool schemas for GPT |

**Fix:** Create single source of truth - `core/routing/agent_registry.py`:
```python
AGENT_REGISTRY = {
    'ImageAgent': {
        'keywords': ['logo', 'banner', 'image', ...],
        'description': 'Creates static visual content',
        'capabilities': ['logos', 'banners', 'illustrations'],
        'when_to_use': 'User wants to create images...',
    },
    ...
}
```

All other files import from this registry.

---

### Issue 4: Semantic Routing Fails Silently

**Location:** `core/agents/personal_assistant_agent.py` lines 37-49

**Problem:** If embedding service fails on startup, semantic routing is disabled forever with no retry.

```python
try:
    _semantic_router = SemanticRoutingService()
except Exception:
    _semantic_router = False  # Never retried!
```

**Fix:**
- Add retry logic with exponential backoff
- Log when falling back to keyword matching
- Periodic health check to re-enable semantic routing

---

### Issue 5: No Routing Analytics/Feedback

**Problem:** No way to know if routing decisions are correct or improving.

**Current:** Decisions recorded via `record_decision()` but no dashboard/metrics.

**Fix:** Add routing analytics:
```python
# Track in database
RoutingDecision.objects.create(
    user=user,
    input_text=task,
    detected_intent=intent,
    routed_to=agent_name,
    routing_method='semantic|keyword|gpt',
    confidence=0.85,
    user_feedback=None  # Updated later if user corrects
)
```

Dashboard to show:
- Routing accuracy by method (semantic vs keyword)
- Most common misroutes
- Agents usage distribution

---

### Issue 6: Keyword Scoring Has No Tie-Breaking

**Location:** `core/agents/personal_assistant_agent.py` lines 712-726

**Problem:** Simple `max()` on scores, no handling of ties.

```python
if agent_scores:
    best_agent = max(agent_scores, key=agent_scores.get)
    return best_agent
```

**Example:** "Create video animation about AI research" - both VideoAgent and ResearchAgent could score equally.

**Fix:** Add confidence-based tie-breaking:
1. Prefer agents where keywords appear earlier in text
2. Weight compound matches higher ("video animation" > "video" alone)
3. Use semantic routing as tie-breaker

---

## Key Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| `core/agents/personal_assistant_agent.py` | 1-50 | Architecture overview |
| `core/agents/personal_assistant_agent.py` | 53-116 | INTENT_AGENT_MAP |
| `core/agents/personal_assistant_agent.py` | 119-220 | INTENT_KEYWORDS |
| `core/agents/personal_assistant_agent.py` | 427-536 | execute() main logic |
| `core/agents/personal_assistant_agent.py` | 538-585 | _is_question() |
| `core/agents/personal_assistant_agent.py` | 587-733 | _detect_agent() |
| `core/agent_router.py` | 147-216 | AGENT_MAP |
| `core/agent_router.py` | 245-314 | route() execution |
| `core/services/semantic_routing.py` | 60-150+ | AGENT_CAPABILITIES |
| `core/prompts/tool_descriptions.py` | 22-497 | TOOL_DESCRIPTIONS |

---

## Available Agents (17 Total)

| Category | Agents |
|----------|--------|
| Creation | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| Editing | ImageEditingAgent, VideoEditingAgent |
| Research | ResearchAgent, CompetitorAnalysisAgent, CustomerResearchAgent |
| Strategy | BrandIdentityAgent, ContentStrategyAgent, SEOOptimizerAgent, SocialMediaAgent |
| Executive | CTOAgent, COOAgent, CreativeDirectorAgent |
| Analysis | TrendAnalysisAgent, OpportunityScoringAgent |
| Training | CharacterTrainingAgent, TrainedCreationAgent |
| Legal | LegalDocDrafterAgent |
| Orchestration | WorkflowAgent |

---

## Implementation Plan

### Phase 1: Quick Reliability Fixes (1 session)

1. **Fix question detection** - Stop routing pure questions
   - Modify `_is_question()` to better distinguish info vs action
   - Add "direct answer with context" path using spider data

2. **Add routing logging** - See why decisions are made
   - Log routing method used (semantic/keyword/gpt)
   - Log confidence scores
   - Add to existing time travel system

3. **Fix semantic routing resilience**
   - Add retry logic on failure
   - Log when falling back

### Phase 2: Business Intelligence Routing (1 session)

1. **Smart business context detection**
   - Detect "startup", "business", "market" without blocking creation
   - Suggest research-first workflow for business queries

2. **Workflow recommendations**
   - "I notice you're creating for a startup. Want me to research the market first?"
   - Store user preference (always research first / ask each time / never)

### Phase 3: Unified Registry (1-2 sessions)

1. **Create `core/routing/agent_registry.py`**
   - Single source of truth for all agent metadata
   - Keywords, descriptions, capabilities, when-to-use

2. **Migrate existing definitions**
   - Update INTENT_KEYWORDS to import from registry
   - Update TOOL_DESCRIPTIONS to import from registry
   - Update semantic routing to use registry

3. **Add validation**
   - Test that all agents have complete definitions
   - Lint for keyword conflicts

### Phase 4: Analytics Dashboard (1 session)

1. **Routing analytics model**
   - Track all routing decisions
   - Link to user feedback

2. **Dashboard UI**
   - Routing accuracy metrics
   - Agent usage distribution
   - Misroute patterns

---

## Test Cases for Validation

After fixes, these should all work correctly:

| Input | Expected Routing | Notes |
|-------|-----------------|-------|
| "What's trending in AI?" | Direct answer | Don't route, answer with GPT + spider data |
| "Create a logo for my startup" | Suggest workflow | "Want to research market first?" |
| "Research AI market and create logos" | WorkflowAgent | Multi-step detected |
| "Analyze my competitors" | CompetitorAnalysisAgent | Direct keyword match |
| "Create motion graphics video" | VideoAgent | Video keyword wins |
| "File a motion for custody" | LegalDocDrafterAgent | Legal priority |
| "Help me with my divorce case" | LegalDocDrafterAgent | Legal context |
| "Make me a voiceover" | AudioAgent | Audio keyword |
| "What agents do you have?" | Direct answer | Platform question |

---

## Success Criteria

1. **Routing accuracy > 95%** for common requests
2. **Zero silent failures** - all routing decisions logged
3. **Business queries get research suggestions** when appropriate
4. **Questions answered directly** without unnecessary agent routing
5. **Single source of truth** for agent definitions

---

## Quick Start for Next Session

```bash
# 1. Start the platform
make start
make celery

# 2. Read this document
cat docs/handoffs/SESSION_453_PERSONAL_ASSISTANT_ROUTING_OVERHAUL.md

# 3. Key files to modify
# - core/agents/personal_assistant_agent.py (main routing logic)
# - core/services/semantic_routing.py (semantic matching)
# - core/prompts/tool_descriptions.py (GPT guidance)

# 4. Test routing manually
# In AI Studio, try the test cases above and verify routing
```

---

## Related Documents

- `docs/GOLDEN_GOOSE_STRATEGY.md` - Why this matters for go-to-market
- `docs/AGENTS.md` - Full agent documentation
- `docs/CAPABILITIES.md` - Platform capabilities

---

**This work is critical for user trust. A reliable Personal Assistant is the difference between a tool users fight with and one they rely on.**
