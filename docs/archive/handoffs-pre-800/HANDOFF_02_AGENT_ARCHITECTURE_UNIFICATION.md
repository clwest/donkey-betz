# Handoff 02: Agent Architecture Unification

**Priority:** HIGH
**Estimated Sessions:** 2-3
**Dependencies:** None (can run parallel to Handoff 01)

---

## Problem Statement

The platform has **two parallel agent systems**:

1. **Legacy Agents** (`agents/*.py`): 22+ agents with inconsistent patterns
2. **Clean Agents** (`core/agents/*.py`): 9 agents with consistent architecture

This creates:
- Confusion about which system to use
- Duplicate functionality
- Import path confusion (`agents.image_agent` vs `core.agents.image_agent`)
- Inconsistent tool definitions
- Mixed usage in SuperPlatformCoordinator

---

## Current State Analysis

### Legacy Agents (`agents/`)
```
agents/
├── audio_agent.py           # 23,001 lines - DUPLICATED in core/agents
├── base_agent.py            # 11,947 lines - Different from core version
├── bookmaker_agent.py       # 35,128 lines - Legacy, sports-specific
├── brand_identity_agent.py  # 19,112 lines
├── character_training_agent.py
├── content_strategy_agent.py
├── coo_agent.py
├── creation_agent.py
├── creative_director_agent.py
├── cto_agent.py
├── image_agent.py           # 34,145 lines - DUPLICATED in core/agents
├── meeting_coordinator_agent.py
├── memory_isolation_agent.py
├── opportunity_scoring_agent.py
├── prompt_optimizer_agent.py
├── research_agent.py        # DUPLICATED in core/agents
├── seo_optimizer_agent.py
├── social_media_agent.py
├── three_d_generation_agent.py
├── trend_analysis_agent.py
├── video_agent.py           # DUPLICATED in core/agents
├── workflow_orchestration_agent.py
└── ... (22+ total)
```

### Clean Agents (`core/agents/`)
```
core/agents/
├── __init__.py
├── base_agent.py            # Abstract base with TimeTravelMixin
├── audio_agent.py           # Clean implementation
├── image_agent.py           # Clean implementation
├── image_editing_agent.py
├── personal_assistant_agent.py
├── research_agent.py        # Clean implementation
├── three_d_agent.py
├── video_agent.py           # Clean implementation
├── video_editing_agent.py
└── workflow_agent.py
```

### Key Differences

| Aspect | Legacy (`agents/`) | Clean (`core/agents/`) |
|--------|-------------------|------------------------|
| Base Class | `BaseContentAgent` | `BaseAgent` with `TimeTravelMixin` |
| Tool Isolation | No - tools leak between agents | Yes - each agent has isolated tools |
| Routing | Via registry lookup | Via `AgentRouter` deterministic routing |
| Feature Flag | Always used | `USE_CLEAN_AGENT_ARCHITECTURE` |
| Spider Context | Not integrated | Integrated via coordinator |
| Sci-Fi Features | Partially integrated | Fully integrated |

---

## Solution: Complete Migration to Clean Architecture

### Target State

```
core/agents/                    # PRIMARY - all agents here
├── __init__.py                 # Exports all agents
├── base_agent.py               # Single base class
├── mixins/
│   ├── time_travel_mixin.py
│   ├── memory_mixin.py
│   └── mood_mixin.py
├── generation/
│   ├── image_agent.py
│   ├── video_agent.py
│   ├── audio_agent.py
│   └── three_d_agent.py
├── editing/
│   ├── image_editing_agent.py
│   └── video_editing_agent.py
├── strategy/
│   ├── content_strategy_agent.py
│   ├── brand_identity_agent.py
│   ├── seo_optimizer_agent.py
│   └── social_media_agent.py
├── executive/
│   ├── cto_agent.py
│   ├── coo_agent.py
│   ├── creative_director_agent.py
│   └── meeting_coordinator_agent.py
├── research/
│   ├── research_agent.py
│   ├── trend_analysis_agent.py
│   └── opportunity_scoring_agent.py
├── workflow/
│   ├── workflow_agent.py
│   └── personal_assistant_agent.py
└── specialized/
    ├── character_training_agent.py
    ├── memory_isolation_agent.py
    └── bookmaker_agent.py      # If still needed

agents/                         # DEPRECATED - compatibility shim only
├── __init__.py                 # Re-exports from core.agents with warnings
└── README.md                   # Deprecation notice
```

---

## Implementation Plan

### Session 1: Audit and Compatibility Layer

**Goal:** Understand exact differences, create compatibility shim

**Tasks:**

1. **Audit each legacy agent**
   ```python
   # Create audit script: scripts/audit_agents.py
   import os
   import ast
   import json

   def analyze_agent(filepath):
       with open(filepath) as f:
           tree = ast.parse(f.read())

       classes = []
       for node in ast.walk(tree):
           if isinstance(node, ast.ClassDef):
               methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
               bases = [b.id if isinstance(b, ast.Name) else str(b) for b in node.bases]
               classes.append({
                   'name': node.name,
                   'bases': bases,
                   'methods': methods,
                   'line_count': node.end_lineno - node.lineno
               })

       return classes

   # Run on both directories
   legacy_agents = {}
   clean_agents = {}

   for f in os.listdir('agents'):
       if f.endswith('_agent.py'):
           legacy_agents[f] = analyze_agent(f'agents/{f}')

   for f in os.listdir('core/agents'):
       if f.endswith('_agent.py'):
           clean_agents[f] = analyze_agent(f'core/agents/{f}')

   # Compare and report
   print(json.dumps({
       'legacy': legacy_agents,
       'clean': clean_agents
   }, indent=2))
   ```

2. **Create compatibility shim**
   ```python
   # agents/__init__.py - UPDATED
   """
   DEPRECATED: This module is deprecated.
   Import from core.agents instead.

   Example:
       # Old (deprecated):
       from agents.image_agent import ImageAgent

       # New (correct):
       from core.agents import ImageAgent
   """
   import warnings
   from functools import wraps

   def _deprecated_import(name):
       def wrapper(*args, **kwargs):
           warnings.warn(
               f"Importing {name} from 'agents' is deprecated. "
               f"Use 'from core.agents import {name}' instead.",
               DeprecationWarning,
               stacklevel=2
           )
           from core import agents as core_agents
           return getattr(core_agents, name)
       return wrapper

   # Re-export with deprecation warnings
   def __getattr__(name):
       if name.endswith('Agent'):
           warnings.warn(
               f"Importing {name} from 'agents' is deprecated. "
               f"Use 'from core.agents import {name}' instead.",
               DeprecationWarning,
               stacklevel=2
           )
           from core import agents as core_agents
           return getattr(core_agents, name, None)
       raise AttributeError(f"module 'agents' has no attribute '{name}'")
   ```

3. **Document differences for each duplicated agent**
   - ImageAgent: Compare tool definitions, execute() signatures
   - VideoAgent: Compare tool definitions, execute() signatures
   - AudioAgent: Compare tool definitions, execute() signatures
   - ResearchAgent: Compare tool definitions, execute() signatures

**Deliverables:**
- [ ] Complete audit of all 22+ legacy agents
- [ ] Compatibility shim in `agents/__init__.py`
- [ ] Difference documentation for each duplicated agent
- [ ] List of agents that need migration vs. deprecation

---

### Session 2: Migrate Strategy and Executive Agents

**Goal:** Migrate non-generation agents to clean architecture

**Tasks:**

1. **Migrate ContentStrategyAgent**
   ```python
   # core/agents/strategy/content_strategy_agent.py
   from core.agents.base_agent import BaseAgent
   from typing import Dict, Any, List

   class ContentStrategyAgent(BaseAgent):
       """
       Content strategy recommendations based on trends and analytics.

       Migrated from agents/content_strategy_agent.py
       """

       name = "ContentStrategyAgent"
       description = "Provides content strategy recommendations"

       # Isolated tools - only what this agent needs
       tools = [
           {
               "name": "analyze_trends",
               "description": "Analyze current trends for content opportunities",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "topic": {"type": "string"},
                       "timeframe": {"type": "string", "enum": ["day", "week", "month"]}
                   },
                   "required": ["topic"]
               }
           },
           {
               "name": "recommend_content",
               "description": "Recommend content types and topics",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "niche": {"type": "string"},
                       "platform": {"type": "string"},
                       "goal": {"type": "string"}
                   },
                   "required": ["niche"]
               }
           }
       ]

       def execute(self, task: str, context: Dict[str, Any] = None, **kwargs):
           # Clean implementation
           self.record_decision("task_received", {"task": task})

           # Use spider context if available
           spider_context = kwargs.get('spider_context', {})
           trends = spider_context.get('relevant_trends', [])

           # Execute strategy logic
           result = self._analyze_and_recommend(task, trends)

           self.record_decision("strategy_complete", result)
           return self.create_result(success=True, data=result)
   ```

2. **Migrate Executive Agents (CTO, COO, CreativeDirector)**
   - Same pattern: inherit from `BaseAgent`
   - Define isolated tools
   - Integrate TimeTravelMixin decisions
   - Add spider context support

3. **Migrate Meeting Coordinator**
   - Clean up coordination logic
   - Add proper tool definitions

4. **Update AgentRouter**
   ```python
   # core/agent_router.py - ADD new agents
   class AgentRouter:
       AGENT_MAP = {
           # Generation agents
           'image': ImageAgent,
           'video': VideoAgent,
           'audio': AudioAgent,
           'three_d': ThreeDAgent,

           # Editing agents
           'image_editing': ImageEditingAgent,
           'video_editing': VideoEditingAgent,

           # Strategy agents (NEW)
           'content_strategy': ContentStrategyAgent,
           'brand_identity': BrandIdentityAgent,
           'seo': SEOOptimizerAgent,
           'social_media': SocialMediaAgent,

           # Executive agents (NEW)
           'cto': CTOAgent,
           'coo': COOAgent,
           'creative_director': CreativeDirectorAgent,
           'meeting_coordinator': MeetingCoordinatorAgent,

           # Research agents
           'research': ResearchAgent,
           'trend_analysis': TrendAnalysisAgent,
           'opportunity': OpportunityScoringAgent,

           # Workflow
           'workflow': WorkflowAgent,
           'personal_assistant': PersonalAssistantAgent,
       }
   ```

**Deliverables:**
- [ ] ContentStrategyAgent migrated to core/agents/strategy/
- [ ] BrandIdentityAgent migrated
- [ ] SEOOptimizerAgent migrated
- [ ] SocialMediaAgent migrated
- [ ] CTOAgent migrated to core/agents/executive/
- [ ] COOAgent migrated
- [ ] CreativeDirectorAgent migrated
- [ ] MeetingCoordinatorAgent migrated
- [ ] AgentRouter updated with all new agents

---

### Session 3: Migrate Research Agents and Cleanup

**Goal:** Complete migration, remove legacy duplicates, enable clean architecture by default

**Tasks:**

1. **Migrate remaining research agents**
   - TrendAnalysisAgent
   - OpportunityScoringAgent

2. **Migrate specialized agents**
   - CharacterTrainingAgent
   - MemoryIsolationAgent
   - BookmakerAgent (if still needed)

3. **Remove legacy duplicates**
   ```bash
   # After verifying clean versions work, remove duplicates
   # DO NOT delete yet - move to deprecated folder first

   mkdir -p agents/_deprecated

   # Move duplicated agents
   mv agents/image_agent.py agents/_deprecated/
   mv agents/video_agent.py agents/_deprecated/
   mv agents/audio_agent.py agents/_deprecated/
   mv agents/research_agent.py agents/_deprecated/
   ```

4. **Enable clean architecture by default**
   ```python
   # settings.py
   USE_CLEAN_AGENT_ARCHITECTURE = True  # Change from False
   ```

5. **Update all imports across codebase**
   ```bash
   # Find all legacy imports
   grep -r "from agents\." --include="*.py" | grep -v "_deprecated" | grep -v "__pycache__"

   # Update each to use core.agents
   ```

6. **Create agent index documentation**
   ```python
   # core/agents/__init__.py
   """
   Unified Agent System
   ====================

   All agents inherit from BaseAgent and follow these principles:
   1. Isolated tools - each agent only has access to its own tools
   2. Time Travel Debugging - all decisions are recorded
   3. Spider Context - agents receive relevant spider data
   4. Sci-Fi Integration - mood, memory, evolution affect behavior

   Generation Agents:
       ImageAgent - Image generation (Stability AI, DALL-E, Replicate)
       VideoAgent - Video generation (Runway ML)
       AudioAgent - Audio generation (ElevenLabs)
       ThreeDAgent - 3D model generation

   Editing Agents:
       ImageEditingAgent - Image editing operations
       VideoEditingAgent - Video editing operations

   Strategy Agents:
       ContentStrategyAgent - Content recommendations
       BrandIdentityAgent - Brand consistency
       SEOOptimizerAgent - SEO optimization
       SocialMediaAgent - Social media content

   Executive Agents:
       CTOAgent - Technical decisions
       COOAgent - Operations oversight
       CreativeDirectorAgent - Creative direction
       MeetingCoordinatorAgent - Team coordination

   Research Agents:
       ResearchAgent - Web research with spider integration
       TrendAnalysisAgent - Trend detection
       OpportunityScoringAgent - Opportunity evaluation

   Workflow Agents:
       WorkflowAgent - Multi-step workflow orchestration
       PersonalAssistantAgent - Main entry point for user interaction
   """

   # Generation
   from .generation.image_agent import ImageAgent
   from .generation.video_agent import VideoAgent
   from .generation.audio_agent import AudioAgent
   from .generation.three_d_agent import ThreeDAgent

   # ... etc
   ```

**Deliverables:**
- [ ] All agents migrated to core/agents/
- [ ] Legacy duplicates moved to _deprecated folder
- [ ] USE_CLEAN_AGENT_ARCHITECTURE = True by default
- [ ] All imports updated across codebase
- [ ] Agent documentation in __init__.py
- [ ] Compatibility shim working for any remaining legacy imports

---

## Validation Checklist

After all sessions, verify:

- [ ] `from core.agents import ImageAgent` works
- [ ] `from agents import ImageAgent` shows deprecation warning but still works
- [ ] SuperPlatformCoordinator uses clean agents
- [ ] AgentRouter routes to all agents correctly
- [ ] Time Travel Debugging works for all agents
- [ ] Spider context is passed to all agents
- [ ] All workflows still function
- [ ] No import errors in logs

---

## Files to Modify

1. `core/agents/*.py` - Add new agents
2. `core/agent_router.py` - Update routing map
3. `agents/__init__.py` - Add deprecation warnings
4. `core/super_platform/coordinator.py` - Ensure using clean agents
5. `settings.py` - Enable clean architecture flag
6. All files with `from agents.` imports

---

## Risk Mitigation

1. **Feature flag** - `USE_CLEAN_AGENT_ARCHITECTURE` allows rollback
2. **Compatibility shim** - Legacy imports still work with warnings
3. **_deprecated folder** - Don't delete legacy code, just move it
4. **Test each agent** after migration before proceeding

---

## Success Metrics

| Metric | Before | Target |
|--------|--------|--------|
| Agent systems | 2 | 1 |
| Import paths | agents.* + core.agents.* | core.agents.* only |
| Agents in clean architecture | 9 | 20+ |
| Deprecation warnings in logs | 0 | 0 (all migrated) |

---

## Commands for Next Claude Session

```bash
# Start here
cd /Users/donkeyking/development/unified-donkey-betz

# Read this handoff
cat docs/handoffs/HANDOFF_02_AGENT_ARCHITECTURE_UNIFICATION.md

# Check current state
ls -la agents/*.py | wc -l
ls -la core/agents/*.py | wc -l

# Check feature flag
grep USE_CLEAN_AGENT_ARCHITECTURE core/settings.py

# Begin Session 1 tasks
```

---

## Session 281 Completion Notes

**Status: COMPLETE (22/25 agents migrated)**

### What Was Done:
- ✅ 22 agents migrated to clean architecture in `core/agents/`
- ✅ Compatibility shims created for all legacy imports
- ✅ `agents/_deprecated/` folder with 18 legacy files
- ✅ Feature flag enabled by default
- ✅ Comprehensive documentation in `core/agents/__init__.py`

### Remaining Legacy Agents (3):

| Agent | Lines | Usages | Decision |
|-------|-------|--------|----------|
| BookmakerAgent | 897 | 4 | Low usage, sports-specific - keep as legacy |
| CreationAgent | 154 | 72 | Overlaps ImageAgent - keep as legacy |
| **WorkflowOrchestrationAgent** | **2631** | **44** | **Complex - needs future work** |

---

## Future Work: WorkflowOrchestrationAgent Migration

**Priority:** LOW-MEDIUM (works fine as legacy)
**Estimated Effort:** 1-2 sessions

### Why It Wasn't Migrated:

The `WorkflowOrchestrationAgent` (2631 lines) is fundamentally different from the clean `WorkflowAgent` (289 lines):

| Aspect | WorkflowOrchestrationAgent | WorkflowAgent (Clean) |
|--------|---------------------------|----------------------|
| Approach | Pre-defined templates | Dynamic LLM-driven |
| Workflows | 14 hardcoded templates | None (GPT decides) |
| Predictability | High (fixed steps) | Variable |
| Integration | Spider + Co-leadership + Projects | Clean agents only |

### 14 Pre-built Workflow Templates:
1. `research_and_create_logos`
2. `research_and_create_images`
3. `youtube_thumbnail_package`
4. `brand_identity_package`
5. `product_photography_kit`
6. `video_thumbnail_series`
7. `logo_to_video`
8. `social_media_kit`
9. `podcast_visual_package`
10. `ebook_cover_series`
11. `video_production_kit`
12. `course_thumbnail_series`
13. `pitch_deck_visuals`
14. `product_launch_kit`

### Migration Strategy (When Ready):

1. **Extract workflow templates** into a configuration file (`core/agents/workflow_templates.py`)
2. **Enhance WorkflowAgent** to:
   - Load and execute pre-defined templates
   - Integrate with spider intelligence service
   - Call co-leadership agents for executive review
   - Auto-create CreativeProject with assets
3. **Add template execution mode** alongside dynamic mode
4. **Test each of the 14 workflows** thoroughly
5. **Update 44 usages** across codebase

### Key Methods to Migrate:
- `_execute_web_search_step()` - Research integration
- `_get_spider_intelligence()` - Spider data fetching
- `_execute_coleadership_step()` - Executive review
- `_execute_image_generation_step()` - Image creation
- `_execute_create_project_step()` - Project organization
- `_aggregate_executive_direction()` - Direction synthesis

### Files to Update When Migrating:
```
agents/workflow_orchestration_agent.py → core/agents/workflow_agent.py (enhance)
                                       → core/agents/workflow_templates.py (new)
```

---

## Verification Commands (Post-Completion)

```bash
# Verify 22 clean agents
.venv/bin/python manage.py shell -c "
from core.agent_router import AgentRouter
router = AgentRouter()
print(f'Clean agents: {len(router.AGENT_MAP)}')
"

# Verify compatibility shims work
.venv/bin/python manage.py shell -c "
import warnings
warnings.filterwarnings('default')
from agents.image_agent import ImageAgent
print('Shim works!')
"

# Check remaining legacy agents
ls agents/*.py | grep -E "(bookmaker|creation|workflow_orchestration)" | wc -l
# Should output: 3
```
