# Session 393: Orchestrator BaseAgent Refactoring

**Date:** December 7, 2025
**Focus:** Refactor 3 legacy orchestrators to use BaseAgent pattern
**Status:** COMPLETE

---

## Summary

Continued the import cleanup from Session 392 by addressing the "complex orchestrators need deeper refactoring" issue. Instead of rewriting 5,400+ lines of battle-tested code, created clean architecture wrappers that preserve all functionality while gaining BaseAgent benefits.

---

## Problem Statement

Session 392 identified three legacy orchestrators as needing "deeper refactoring":

| Agent | Lines | Complexity |
|-------|-------|------------|
| `agents/workflow_orchestration_agent.py` | 3,120 | 17 workflow templates, spider integration, style extraction |
| `agents/opportunity_pipeline_orchestrator.py` | 1,759 | 5-stage async pipeline, value multiplication, memory-enhanced scoring |
| `agents/content_executor.py` | 568 | AI content generation, SEO scoring, fallback content |

These agents already had learning hooks via mixins (`PipelineLearningMixin`, `ContentExecutorLearningMixin`) but didn't follow the `BaseAgent` signature pattern used by clean agents in `core/agents/`.

---

## Solution: Wrapper Pattern

Instead of risky rewrites, created wrapper agents that:

1. **Inherit from BaseAgent** - Getting TimeTravelMixin, consistent interface
2. **Lazy-load legacy agents** - Via `@property` accessor
3. **Delegate execution** - Call legacy `execute()` or equivalent methods
4. **Convert results** - Transform legacy dict responses to `AgentResult`
5. **Add tracking** - Time travel decisions and learning hooks

---

## New Files Created

### 1. `core/agents/workflow_orchestration_agent.py`

```python
class WorkflowOrchestrationAgent(BaseAgent):
    """Clean wrapper for legacy WorkflowOrchestrationAgent."""

    name = "WorkflowOrchestrationAgent"

    @property
    def legacy_agent(self):
        """Lazy-load the legacy agent."""
        if self._legacy_agent is None:
            from agents.workflow_orchestration_agent import WorkflowOrchestrationAgent as LegacyAgent
            self._legacy_agent = LegacyAgent(user=self.user, project_id=self.project_id)
        return self._legacy_agent

    def execute(self, task, context, scifi_context, spider_context) -> AgentResult:
        # Wraps legacy execution with BaseAgent interface
        ...
```

**Features Preserved:**
- 17 workflow templates (`research_and_create_logos`, `youtube_thumbnail_package`, etc.)
- Spider intelligence integration
- Project research context injection
- Executive review steps
- Style/mascot extraction from prompts

### 2. `core/agents/opportunity_pipeline_agent.py`

```python
class OpportunityPipelineAgent(BaseAgent):
    """Clean wrapper for legacy OpportunityPipelineOrchestrator."""

    name = "OpportunityPipelineAgent"

    def execute(self, task, context, scifi_context, spider_context) -> AgentResult:
        # Wraps async pipeline with sync interface
        legacy_result = async_to_sync(
            self.legacy_orchestrator.orchestrate_opportunity_pipeline
        )(opportunity, pipeline_config)
        ...
```

**Features Preserved:**
- 5-stage pipeline: DISCOVERY → ANALYSIS → EXECUTION → OPTIMIZATION → MONITORING
- Value multiplication: 1.2x → 1.5x → 2.0x → 2.5x per stage
- Memory-enhanced agent selection
- Embedding-based similar opportunity search

### 3. `core/agents/content_executor_agent.py`

```python
class ContentExecutorAgent(BaseAgent):
    """Clean wrapper for legacy DonkeyBetzContentExecutor."""

    name = "ContentExecutorAgent"

    def execute(self, task, context, scifi_context, spider_context) -> AgentResult:
        content_result = self.legacy_executor._generate_donkey_betz_content(
            task=task,
            content_type=content_type,
            audience=target_audience
        )
        ...
```

**Features Preserved:**
- AI content generation using GPT-5-mini
- SEO optimization and scoring
- 8 content types (blog_post, article, tutorial, etc.)
- Fallback content when AI unavailable

---

## Updated Exports

### `core/agents/__init__.py` Changes

```python
# Orchestration Agents (Session 393: Added 3 new orchestrators)
from core.agents.workflow_agent import WorkflowAgent
from core.agents.workflow_orchestration_agent import (
    WorkflowOrchestrationAgent,
    get_workflow_orchestration_agent,
    AVAILABLE_WORKFLOWS,
)
from core.agents.opportunity_pipeline_agent import (
    OpportunityPipelineAgent,
    get_opportunity_pipeline_agent,
    PIPELINE_STAGES,
)
from core.agents.content_executor_agent import (
    ContentExecutorAgent,
    get_content_executor_agent,
    CONTENT_TYPES,
)
```

### Agent Counts Updated

| Category | Before | After |
|----------|--------|-------|
| Orchestration Agents | 2 | 4 |
| Total Code Agents | 28 | 31 |

---

## Usage Examples

```python
from core.agents import (
    WorkflowOrchestrationAgent,
    OpportunityPipelineAgent,
    ContentExecutorAgent,
)

# Workflow packages
workflow_agent = WorkflowOrchestrationAgent(user=user)
result = workflow_agent.execute(
    task="Create logos for my AI startup",
    context={'workflow': 'research_and_create_logos', 'count': 3},
    scifi_context={},
    spider_context={}
)

# Opportunity pipeline
pipeline_agent = OpportunityPipelineAgent(user=user)
result = pipeline_agent.execute(
    task="Process freelance opportunity",
    context={'opportunity': {'title': 'Web dev gig', 'base_value': 500}},
    scifi_context={},
    spider_context={}
)

# Content generation
content_agent = ContentExecutorAgent(user=user)
result = content_agent.execute(
    task="Write a blog post about AI automation",
    context={'content_type': 'blog_post'},
    scifi_context={},
    spider_context={}
)
```

---

## Why Wrappers Instead of Rewrites?

1. **Risk Mitigation** - 5,400+ lines of code with complex integrations
2. **Feature Preservation** - All 17 workflows, 5 pipeline stages, SEO scoring intact
3. **Battle-Tested Logic** - Months of refinement in legacy code
4. **Incremental Migration** - Wrappers work now; can refactor internals later
5. **Quick Wins** - Gained BaseAgent benefits immediately

---

## Testing

```bash
# Test imports
.venv/bin/python -c "
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from core.agents import WorkflowOrchestrationAgent, OpportunityPipelineAgent, ContentExecutorAgent
print('All 3 new orchestrators imported successfully!')
"
```

All imports verified working.

---

## Remaining Work

### Optional Import Updates

Files importing from legacy locations can optionally be updated:
- `from agents.workflow_orchestration_agent import ...`
- `from agents.opportunity_pipeline_orchestrator import ...`
- `from agents.content_executor import ...`

These still work since wrappers delegate to legacy code. Updates are purely for consistency.

### Legacy CreationAgent

`agents/creation_agent.py` is another legacy agent not yet wrapped. Consider for future session.

---

## Part 2: Import Path Updates

### Files Updated (25+ imports)

**Batch 1 - `core/personal_ai_assistant_enhanced.py` (17 imports):**
- `agents._deprecated.*` → `core.agents.strategy`, `core.agents.analysis`, etc.
- `agents.router` → `core.agent_router`
- `agents.video_generation_agent` → `core.agents` (VideoAgent)

**Batch 2 - Core views and services:**
- `core/views_opportunity.py` - 4 OpportunityScoringAgent imports
- `core/services/workflow_builder.py` - 3 WorkflowOrchestrationAgent imports
- `core/views_image.py` - 2 imports

**Batch 3 - Intelligence and automation:**
- `intelligence/income_builder_automation.py` - OpportunityPipelineOrchestrator → OpportunityPipelineAgent
- `ai_core/intelligence/automation_integration.py` - Same change

**Batch 4 - Core components:**
- `core/tasks.py` - OpportunityScoringAgent from core.agents.analysis
- `core/super_platform/revenue_integration.py` - OpportunityScoringAgent
- `core/agents/business/base_business_research_agent.py` - ResearchAgent

---

## Part 3: Import Analysis Results

### Remaining `agents.*` Imports (~100)

Analyzed all remaining imports and categorized:

**Must Stay as `agents.*` (Django App Dependencies):**
- `agents.tasks` - Celery requires Django app module paths
- `agents.serializers` - Django REST framework serializers
- `agents.services` - Django app service layer
- `agents.views_*` - URL routing in core/urls.py
- `agents.models` - Database model references

**Intentionally Using Legacy API:**
- `agents.creation_agent.CreationAgent` - Different interface than ImageAgent
- `agents.content_executor.DonkeyBetzContentExecutor` - Uses `execute_content_creation()`
- `agents.ai_project_builder.AIProjectBuilder` - Specialized builder
- Various income agents - Specialized agents not wrapped

---

## Commits

1. `d5072bd` - feat(Session 393): Refactor 3 legacy orchestrators to use BaseAgent pattern
2. `40ac960` - refactor(Session 393): Update 16 deprecated agents.* imports to core.agents
3. `45f3fdd` - refactor(Session 393): Update OpportunityPipelineOrchestrator imports
4. `cd94edf` - refactor(Session 393): Update 3 more legacy imports to canonical paths

---

## Architecture Notes

### Agent Hierarchy After Session 393

```
core/agents/
├── base_agent.py              # BaseAgent + AgentResult
├── registry.py                # AgentRegistry (Session 392)
│
├── Orchestration (4)
│   ├── workflow_agent.py              # GPT-driven, dynamic delegation
│   ├── workflow_orchestration_agent.py # NEW - Predefined workflow packages
│   ├── opportunity_pipeline_agent.py   # NEW - Value multiplication pipeline
│   └── content_executor_agent.py       # NEW - AI content generation
│
├── Creation (4)
│   ├── image_agent.py
│   ├── video_agent.py
│   ├── audio_agent.py
│   └── three_d_agent.py
│
└── ... (27 more agents)
```

### Wrapper Design Pattern

```
User Request
    ↓
WorkflowOrchestrationAgent (core/agents/)  ← Clean interface
    ↓ lazy-load
LegacyWorkflowOrchestrationAgent (agents/)  ← Battle-tested logic
    ↓ delegate
AgentResult (clean response format)
```

---

## Next Steps for Future Sessions

1. **Optional**: Update remaining `agents.` imports to `core.agents`
2. **Optional**: Wrap `agents/creation_agent.py` similarly
3. **Continue**: Clean architecture improvements
4. **Monitor**: Verify wrappers work correctly in production

---

**Session Complete**
