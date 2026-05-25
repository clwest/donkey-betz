# Session 280: Agent Architecture Unification - Audit Complete

**Date:** November 29, 2025
**Status:** AUDIT & COMPATIBILITY SHIM COMPLETE
**Handoff Reference:** HANDOFF_02_AGENT_ARCHITECTURE_UNIFICATION.md

---

## Summary of Work Completed

### 1. Compatibility Shim Created

Updated `agents/__init__.py` with:
- Deprecation warnings for clean agents when imported from `agents`
- Automatic redirect to `core.agents` for migrated agents
- Legacy agent paths preserved for unmigrated agents
- `__getattr__` magic method for dynamic import handling

**Usage:**
```python
# OLD (shows deprecation warning):
from agents import ImageAgent

# NEW (preferred, no warning):
from core.agents import ImageAgent
```

---

## Complete Agent Audit

### Clean Architecture Agents (`core/agents/`) - 10 Agents

| Agent | Lines | Description | Tools |
|-------|-------|-------------|-------|
| `BaseAgent` | 313 | Abstract base with TimeTravelMixin | N/A |
| `ImageAgent` | 370 | Image generation ONLY | `generate_image` |
| `VideoAgent` | 324 | Video generation ONLY | `generate_video`, `image_to_video` |
| `AudioAgent` | 298 | Audio/TTS generation ONLY | `generate_audio`, `text_to_speech` |
| `ThreeDAgent` | 248 | 3D model generation ONLY | `generate_3d_model` |
| `ImageEditingAgent` | 351 | Image editing operations | `upscale`, `remove_bg`, `variations` |
| `VideoEditingAgent` | 437 | Video editing operations | `trim`, `add_text`, `effects` |
| `ResearchAgent` | 382 | Web search + spider queries | `web_search`, `spider_query` |
| `WorkflowAgent` | 288 | Multi-step workflow orchestration | `delegate_to_agent` |
| `PersonalAssistantAgent` | 567 | Main entry point, routes to agents | All delegation tools |

**Total Clean Agents:** 10 agents, ~3,578 lines

---

### Legacy Agents (`agents/`) - 22 Agent Files

| Agent | Lines | Status | Migration Plan |
|-------|-------|--------|----------------|
| `image_agent.py` | 876 | **DUPLICATED** | Keep core/agents version, deprecate legacy |
| `video_agent.py` | 1,886 | **DUPLICATED** | Keep core/agents version, deprecate legacy |
| `audio_agent.py` | 664 | **DUPLICATED** | Keep core/agents version, deprecate legacy |
| `research_agent.py` | 763 | **DUPLICATED** | Keep core/agents version, deprecate legacy |
| `base_agent.py` | 383 | **KEEP** | Legacy base class (BaseContentAgent) |
| `workflow_orchestration_agent.py` | 2,631 | **REVIEW** | Has workflow_orchestration_agent features |
| `content_strategy_agent.py` | 610 | **MIGRATE** | Session 2 candidate |
| `brand_identity_agent.py` | 640 | **MIGRATE** | Session 2 candidate |
| `seo_optimizer_agent.py` | 557 | **MIGRATE** | Session 2 candidate |
| `social_media_agent.py` | 586 | **MIGRATE** | Session 2 candidate |
| `cto_agent.py` | 846 | **MIGRATE** | Session 2 candidate |
| `coo_agent.py` | 510 | **MIGRATE** | Session 2 candidate |
| `creative_director_agent.py` | 773 | **MIGRATE** | Session 2 candidate |
| `meeting_coordinator_agent.py` | 618 | **MIGRATE** | Session 2 candidate |
| `trend_analysis_agent.py` | 617 | **MIGRATE** | Session 3 candidate |
| `opportunity_scoring_agent.py` | 1,012 | **MIGRATE** | Session 3 candidate |
| `character_training_agent.py` | 468 | **MIGRATE** | Session 3 candidate |
| `trained_creation_agent.py` | 295 | **MIGRATE** | Session 3 candidate |
| `memory_isolation_agent.py` | 540 | **MIGRATE** | Session 3 candidate |
| `creation_agent.py` | 165 | **DEPRECATE** | Replaced by ImageAgent |
| `bookmaker_agent.py` | 897 | **DEPRECATE** | Sports betting legacy, not AI creation |
| `three_d_generation_agent.py` | 420 | **DUPLICATED** | Keep core/agents ThreeDAgent |

**Total Legacy Agents:** 22 files, ~15,757 lines (many duplicated)

---

## Key Differences: Clean vs Legacy

### 1. Base Class

| Aspect | Legacy (`BaseContentAgent`) | Clean (`BaseAgent`) |
|--------|----------------------------|---------------------|
| Inheritance | Plain ABC | ABC + TimeTravelMixin |
| Constructor | `__init__(user, project_id, session_id)` | `__init__(user)` |
| Execute signature | `execute(**kwargs)` | `execute(task, context, scifi_context, spider_context)` |
| Result type | `Dict[str, Any]` | `AgentResult` dataclass |
| Tool isolation | No - all tools accessible | Yes - only domain tools |
| Sci-Fi integration | Optional/partial | Built-in context injection |
| Spider integration | Optional/partial | Built-in context injection |

### 2. ImageAgent Example Comparison

**Legacy (`agents/image_agent.py`):**
```python
class ImageAgent(SpiderContextMixin, TimeTravelMixin):
    # 876 lines
    # Has ALL image operations: generate, edit, upscale, logo, social
    # Has preference learning (preference_manager)
    # Has platform size presets
    # Multiple methods: generate(), generate_logo(), generate_social(), edit()
```

**Clean (`core/agents/image_agent.py`):**
```python
class ImageAgent(BaseAgent):
    # 370 lines
    # ONLY image generation
    # Single tool: generate_image
    # Delegates editing to ImageEditingAgent
    # Uses GPT to enhance prompts
    # Records decisions via TimeTravelMixin
```

**Key Difference:** Clean architecture follows **Single Responsibility Principle** - ImageAgent generates, ImageEditingAgent edits.

### 3. Tool Isolation

**Legacy Problem:**
```python
# GPT sees ALL tools and sometimes picks wrong one
tools = [generate_image, generate_video, upscale, remove_bg, web_search, ...]
# Result: "create a logo" might trigger video_generation_agent
```

**Clean Solution:**
```python
# ImageAgent ONLY has:
tools = [generate_image]
# CANNOT access video, audio, web search - no possibility of confusion
```

---

## Migration Priority List

### Already Migrated (Skip - Use core/agents versions)
1. ImageAgent
2. VideoAgent
3. AudioAgent
4. ThreeDAgent
5. ResearchAgent
6. WorkflowAgent (replaces workflow_orchestration_agent)

### Session 2: Strategy & Executive Agents
1. ContentStrategyAgent
2. BrandIdentityAgent
3. SEOOptimizerAgent
4. SocialMediaAgent
5. CTOAgent
6. COOAgent
7. CreativeDirectorAgent
8. MeetingCoordinatorAgent

### Session 3: Specialized Agents
1. TrendAnalysisAgent
2. OpportunityScoringAgent
3. CharacterTrainingAgent
4. TrainedCreationAgent
5. MemoryIsolationAgent

### Deprecate (No Migration Needed)
1. BookmakerAgent - Sports betting, not AI creation
2. CreationAgent - Replaced by ImageAgent

---

## Files Modified This Session

1. **`agents/__init__.py`** - Added compatibility shim with deprecation warnings

---

## Next Session Tasks

### Session 2: Migrate Strategy Agents

1. Create `core/agents/strategy/` directory
2. Migrate ContentStrategyAgent to clean architecture:
   ```python
   class ContentStrategyAgent(BaseAgent):
       name = "ContentStrategyAgent"
       system_prompt = "..."
       tools = [analyze_trends, recommend_content]
   ```
3. Add to AgentRouter.AGENT_MAP
4. Test routing works
5. Repeat for BrandIdentityAgent, SEOOptimizerAgent, SocialMediaAgent

### Session 3: Migrate Executive Agents

1. Create `core/agents/executive/` directory
2. Migrate CTOAgent, COOAgent, CreativeDirectorAgent, MeetingCoordinatorAgent
3. Add to AgentRouter.AGENT_MAP

### Session 4: Enable Clean Architecture by Default

1. Set `USE_CLEAN_AGENT_ARCHITECTURE = True` in settings.py
2. Update all legacy imports to use core.agents
3. Move legacy duplicates to `agents/_deprecated/`

---

## Verification Commands

```bash
# Test compatibility shim
.venv/bin/python manage.py shell -c "
import warnings
warnings.filterwarnings('always', category=DeprecationWarning)
from agents import ImageAgent  # Should show deprecation warning
from core.agents import VideoAgent  # No warning
print('ImageAgent:', ImageAgent)
print('VideoAgent:', VideoAgent)
"

# Check feature flag
grep USE_CLEAN_AGENT_ARCHITECTURE core/settings.py

# Count agents in each location
ls -1 agents/*.py | grep -E "agent\.py$" | wc -l  # Legacy: ~22
ls -1 core/agents/*.py | grep -E "agent\.py$" | wc -l  # Clean: ~10
```

---

## Architecture Diagram

```
CURRENT STATE (Two Systems):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Legacy System (agents/)          Clean System (core/agents/)       │
│  ├── BaseContentAgent             ├── BaseAgent + TimeTravelMixin   │
│  ├── ImageAgent (876 lines)       ├── ImageAgent (370 lines)        │
│  ├── VideoAgent (1886 lines)      ├── VideoAgent (324 lines)        │
│  ├── AudioAgent (664 lines)       ├── AudioAgent (298 lines)        │
│  ├── ResearchAgent (763 lines)    ├── ResearchAgent (382 lines)     │
│  ├── ... (22 total)               ├── WorkflowAgent (288 lines)     │
│  │                                └── PersonalAssistantAgent        │
│  │                                                                  │
│  └── Inconsistent routing         └── AgentRouter (deterministic)   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

TARGET STATE (Single System):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  core/agents/ (UNIFIED)                                             │
│  ├── base_agent.py                                                  │
│  ├── generation/                                                    │
│  │   ├── image_agent.py                                             │
│  │   ├── video_agent.py                                             │
│  │   ├── audio_agent.py                                             │
│  │   └── three_d_agent.py                                           │
│  ├── editing/                                                       │
│  │   ├── image_editing_agent.py                                     │
│  │   └── video_editing_agent.py                                     │
│  ├── strategy/                                                      │
│  │   ├── content_strategy_agent.py                                  │
│  │   ├── brand_identity_agent.py                                    │
│  │   ├── seo_optimizer_agent.py                                     │
│  │   └── social_media_agent.py                                      │
│  ├── executive/                                                     │
│  │   ├── cto_agent.py                                               │
│  │   ├── coo_agent.py                                               │
│  │   ├── creative_director_agent.py                                 │
│  │   └── meeting_coordinator_agent.py                               │
│  ├── research/                                                      │
│  │   ├── research_agent.py                                          │
│  │   ├── trend_analysis_agent.py                                    │
│  │   └── opportunity_scoring_agent.py                               │
│  └── workflow/                                                      │
│      ├── workflow_agent.py                                          │
│      └── personal_assistant_agent.py                                │
│                                                                     │
│  agents/ (DEPRECATED - shim only)                                   │
│  └── __init__.py (redirects to core.agents with warnings)           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

**Session 280 Complete. Ready for Session 2: Strategy Agent Migration.**
