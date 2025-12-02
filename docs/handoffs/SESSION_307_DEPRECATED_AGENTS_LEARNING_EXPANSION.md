# Session 307: Deprecated Agents Learning Expansion

**Date:** December 1, 2025
**Previous Session:** 306 (Legacy Agent Learning Expansion + Database Fix)
**Status:** COMPLETE

---

## Problem Statement

Session 306 wired learning hooks to 3 standalone agents (BookmakerAgent, CreationAgent, OpportunityPipelineOrchestrator). However, more agents in the `agents/` directory and `agents/_deprecated/` needed learning infrastructure, especially now that the learning system is working properly.

---

## Solution Implemented

### Agents Wired This Session

| Agent | File | Mixin | Learning Hooks |
|-------|------|-------|----------------|
| OpportunityScoringAgent | `agents/_deprecated/opportunity_scoring_agent.py` | OpportunityScoringLearningMixin | score_spider_data(), analyze_trend(), score_job_opportunity() |
| AIProjectBuilder | `agents/ai_project_builder.py` | ProjectBuilderLearningMixin | build_project() |
| DonkeyBetzContentExecutor | `agents/content_executor.py` | ContentExecutorLearningMixin | execute_content_creation() |
| LiveLearningOrchestrator | `agents/live_learning_orchestrator.py` | LiveLearningLearningMixin | broadcast_progress(), trigger_collaboration() |

### Each Mixin Provides

| Method | Purpose |
|--------|---------|
| `learning_loop` / `learning_loop_service` property | Lazy-load LearningLoopService |
| `memory_service` property | Lazy-load MemoryEmbeddingService |
| `agent_model` property | Lazy-load/create Agent model instance |
| `_record_learning_outcome()` | Record execution for XP and patterns |
| `_create_execution_memory()` | Create memories from interactions |
| `_share_knowledge()` | Share learned patterns cross-agent |
| `_get_shared_knowledge()` | Retrieve knowledge from other agents |

---

## Wiring Details

### OpportunityScoringAgent (Deprecated but Learning!)

Located in `agents/_deprecated/opportunity_scoring_agent.py`

Wired in 3 methods:
- `score_spider_data()` - Batch scores spider data, shares high-score opportunities (>=75)
- `analyze_trend()` - Analyzes trends, shares high-value discoveries (>=70)
- `score_job_opportunity()` - Scores jobs, shares high-value jobs (>=70 or salary >$75k)

```python
# Example knowledge shared
self._share_knowledge(
    knowledge_type='opportunity',
    title=f"High-score opportunity: {result.overall_score}",
    knowledge_value={
        'overall_score': result.overall_score,
        'profit_potential': result.profit_potential,
        'content_types': result.suggested_content_types,
    }
)
```

### AIProjectBuilder

Located in `agents/ai_project_builder.py`

Wired in `build_project()` method:
- Records learning outcome with project type and strategy
- Creates memory for successful builds (importance 0.75)
- Shares successful build patterns with revenue estimates

### DonkeyBetzContentExecutor

Located in `agents/content_executor.py`

Wired in `execute_content_creation()` method:
- Records learning outcome with content type and SEO score
- Creates memory for successful content (importance 0.7)
- Shares high-SEO content patterns (>=0.7 SEO score)

### LiveLearningOrchestrator

Located in `agents/live_learning_orchestrator.py`

Wired in 2 methods:
- `broadcast_progress()` - Records iterations, creates milestone memories
- `trigger_collaboration()` - Shares collaboration knowledge between agents

---

## Test Results

### Learning Hooks Verification

```
Testing Session 307 Learning Hook Wiring:
==================================================
✅ OpportunityScoringAgent
   - _share_knowledge: True
   - _record_learning_outcome: True
   - _create_execution_memory: True
   - _get_shared_knowledge: True
✅ AIProjectBuilder
   - _share_knowledge: True
   - _record_learning_outcome: True
   - _create_execution_memory: True
   - _get_shared_knowledge: True
✅ DonkeyBetzContentExecutor
   - _share_knowledge: True
   - _record_learning_outcome: True
   - _create_execution_memory: True
   - _get_shared_knowledge: True
✅ LiveLearningOrchestrator
   - _share_knowledge: True
   - _record_learning_outcome: True
   - _create_execution_memory: True
   - _get_shared_knowledge: True
```

### Functional Test

```
AgentKnowledgeSource: 4 → 6 records ✅ (2 new from Session 307 tests)
AgentMemory: 3 records ✅ (stable from Session 306)

Recent Knowledge Entries:
  - OpportunityScoringAgent: Session 307 Test: High-score opportunity...
  - AIProjectBuilder: Session 307 Test: Project build pattern...
  - OpportunityPipelineOrchestrator: Multi-stage pipeline successful...
  - Vegas AI: Test Knowledge - Session 306...
  - Creation Agent: Cyberpunk style works great...
```

---

## Files Modified

| File | Changes |
|------|---------|
| `agents/_deprecated/opportunity_scoring_agent.py` | +195 lines: OpportunityScoringLearningMixin + wiring in 3 methods |
| `agents/ai_project_builder.py` | +190 lines: ProjectBuilderLearningMixin + wiring in build_project() |
| `agents/content_executor.py` | +195 lines: ContentExecutorLearningMixin + wiring in execute_content_creation() |
| `agents/live_learning_orchestrator.py` | +200 lines: LiveLearningLearningMixin + wiring in 2 methods |
| `docs/handoffs/SESSION_307_DEPRECATED_AGENTS_LEARNING_EXPANSION.md` | This file |

---

## Learning Infrastructure Status

### Session 304 - Clean Architecture Agents (11)
All connected via `core/agents/base_agent.py`:
- ImageAgent, VideoAgent, AudioAgent, ThreeDAgent
- ResearchAgent, ImageEditingAgent, VideoEditingAgent
- WorkflowAgent, CompetitorAnalysisAgent, CustomerResearchAgent, PersonalAssistantAgent

### Session 305 - Legacy Agents via BaseContentAgent
- WorkflowOrchestrationAgent (explicitly wired)
- All other legacy agents inherit hooks

### Session 306 - Standalone Agents via Mixins
- BookmakerAgent (LearningMixin)
- CreationAgent (CreationLearningMixin)
- OpportunityPipelineOrchestrator (PipelineLearningMixin)

### Session 307 - Deprecated/Additional Agents via Mixins
- OpportunityScoringAgent (OpportunityScoringLearningMixin)
- AIProjectBuilder (ProjectBuilderLearningMixin)
- DonkeyBetzContentExecutor (ContentExecutorLearningMixin)
- LiveLearningOrchestrator (LiveLearningLearningMixin)

---

## Quick Verification

```python
from agents._deprecated.opportunity_scoring_agent import OpportunityScoringAgent
from agents.ai_project_builder import AIProjectBuilder
from agents.content_executor import DonkeyBetzContentExecutor
from agents.live_learning_orchestrator import LiveLearningOrchestrator
from core.models_unified_system import AgentKnowledgeSource, AgentMemory

# Verify learning hooks work
print(f"OpportunityScoringAgent has _share_knowledge: {hasattr(OpportunityScoringAgent(), '_share_knowledge')}")
print(f"AIProjectBuilder has _share_knowledge: {hasattr(AIProjectBuilder(), '_share_knowledge')}")
print(f"DonkeyBetzContentExecutor has _share_knowledge: {hasattr(DonkeyBetzContentExecutor(), '_share_knowledge')}")
print(f"LiveLearningOrchestrator has _share_knowledge: {hasattr(LiveLearningOrchestrator(), '_share_knowledge')}")

# Check records
print(f"AgentKnowledgeSource: {AgentKnowledgeSource.objects.count()} records")
print(f"AgentMemory: {AgentMemory.objects.count()} records")
```

---

**Session 307 Complete: 4 Additional Agents Now Have Learning Hooks!**

Total agents with learning infrastructure:
- 11 clean architecture agents (Session 304)
- Legacy agents via BaseContentAgent (Session 305)
- 3 standalone agents (Session 306)
- 4 additional agents (Session 307) - **NEW**

**Learning tables now at:**
- AgentKnowledgeSource: 6 records
- AgentMemory: 3 records
