# Session 306: Legacy Agent Learning Expansion + Database Fix

**Date:** December 1, 2025
**Previous Session:** 305 (AudioHistory + Learning Infrastructure for Legacy Agents)
**Status:** COMPLETE

**Part 2 Added:** Fixed AgentMemory database schema issue (missing `tags` column)

---

## Problem Statement

Session 305 added learning hooks to `BaseContentAgent` (the legacy base class), but only `WorkflowOrchestrationAgent` was explicitly wired. Three key standalone agents needed learning capabilities:

1. `BookmakerAgent` - Sports/financial analysis (standalone class)
2. `CreationAgent` - Image generation (standalone class)
3. `OpportunityPipelineOrchestrator` - Multi-stage workflow (standalone async class)

These agents don't inherit from `BaseContentAgent`, so they needed their own learning infrastructure.

---

## Solution Implemented

### Created Learning Mixins

Since these agents are standalone classes with different architectures, we created **learning mixins** for each:

| Agent | Mixin | Location |
|-------|-------|----------|
| BookmakerAgent | `LearningMixin` | `agents/bookmaker_agent.py` |
| CreationAgent | `CreationLearningMixin` | `agents/creation_agent.py` |
| OpportunityPipelineOrchestrator | `PipelineLearningMixin` | `agents/opportunity_pipeline_orchestrator.py` |

### Each Mixin Provides:

| Method | Purpose |
|--------|---------|
| `learning_loop` property | Lazy-load LearningLoopService |
| `memory_service` property | Lazy-load MemoryEmbeddingService |
| `agent_model` property | Lazy-load/create Agent model instance |
| `_record_learning_outcome()` | Record execution for XP and patterns |
| `_create_execution_memory()` | Create memories from interactions |
| `_share_knowledge()` | Share learned patterns cross-agent |
| `_get_shared_knowledge()` | Retrieve knowledge from other agents |

---

## Wiring Details

### BookmakerAgent

Wired in `analyze_game()` method:
- Records learning outcomes for all game analyses
- Creates high-importance (0.7) memories for analysis
- Shares sharp money predictions when probability > 0.6
- Shares top 2 value bet discoveries

```python
# Example knowledge shared
self._share_knowledge(
    knowledge_type='prediction',
    title=f"Sharp money on {side} - {game_id}",
    knowledge_value={...}
)
```

### CreationAgent

Wired in `execute()` method:
- Records learning outcomes for all image generations
- Creates success memories (0.6 importance)
- Shares successful style/prompt combinations

```python
# Example knowledge shared
self._share_knowledge(
    knowledge_type='style',
    title=f"Style works: {style} for {prompt[:50]}",
    knowledge_value={...}
)
```

### OpportunityPipelineOrchestrator

Wired in `orchestrate_opportunity_pipeline()` method:
- Records learning outcomes with execution time
- Creates high-importance (0.8) memories for pipelines
- Shares pipeline patterns when value multiplication > 1.5x

```python
# Example knowledge shared
self._share_knowledge(
    knowledge_type='pipeline',
    title=f"High-value pipeline: {mult:.1f}x",
    knowledge_value={
        'agents_used': [...],
        'value_multiplication': mult,
    }
)
```

---

## Test Results

### Knowledge Sharing Verified

```
AgentKnowledgeSource: 0 → 4 records ✅
  - Creation Agent: Cyberpunk style works great... (content_idea)
  - OpportunityPipelineOrchestrator: Multi-stage pipeline... (tool_discovery)
  - Vegas AI: Test Knowledge - Session 306... (market)
  - Vegas AI: Test betting pattern... (pricing)
```

### Agent Model Created

```
Agent records: 160 → 161 (new: "Vegas AI")
```

### Database Fix (Part 2)

The `AgentMemory` table was missing the `tags` column despite migration 0054 being marked as applied.

**Root Cause:** Migration state mismatch (marked applied but column didn't exist)

**Fix Applied:**
1. Fake-unapplied migration 0054 and later: `migrate core 0053 --fake`
2. Applied 0054 for real: `migrate core 0054`
3. Fake-applied remaining migrations: `migrate core --fake`

**Additional Fix:** Changed `metadata` parameter to `tags` in all three agents' `_create_execution_memory()` methods to match the `MemoryEmbeddingService.create_memory()` signature.

---

## Files Modified

| File | Changes |
|------|---------|
| `agents/bookmaker_agent.py` | +190 lines: LearningMixin + wiring in analyze_game() |
| `agents/creation_agent.py` | +200 lines: CreationLearningMixin + wiring in execute() |
| `agents/opportunity_pipeline_orchestrator.py` | +200 lines: PipelineLearningMixin + wiring in orchestrate_opportunity_pipeline() |
| `docs/handoffs/SESSION_306_LEGACY_AGENT_LEARNING_EXPANSION.md` | This file |

---

## Learning Infrastructure Status

### Clean Architecture Agents (11) - Sessions 304

All connected via `core/agents/base_agent.py`:
- ImageAgent, VideoAgent, AudioAgent, ThreeDAgent
- ResearchAgent, ImageEditingAgent, VideoEditingAgent
- WorkflowAgent, CompetitorAnalysisAgent, CustomerResearchAgent, PersonalAssistantAgent

### Legacy Agents - Sessions 305-306

**Session 305 (BaseContentAgent):**
- WorkflowOrchestrationAgent (explicitly wired)
- All other legacy agents inherit hooks but need explicit calls

**Session 306 (Standalone Mixins):**
- BookmakerAgent ✅
- CreationAgent ✅
- OpportunityPipelineOrchestrator ✅

### Remaining Legacy Agents

Could benefit from learning wiring in future sessions:
- Other agents in `agents/` directory that don't inherit BaseContentAgent

---

## Quick Verification

```python
from agents.bookmaker_agent import BookmakerAgent
from agents.creation_agent import CreationAgent
from agents.opportunity_pipeline_orchestrator import OpportunityPipelineOrchestrator
from core.models_unified_system import AgentKnowledgeSource, AgentMemory

# Verify learning hooks work
print(f"BookmakerAgent has _share_knowledge: {hasattr(BookmakerAgent(), '_share_knowledge')}")
print(f"CreationAgent has _share_knowledge: {hasattr(CreationAgent(user), '_share_knowledge')}")
print(f"OPO has _share_knowledge: {hasattr(OpportunityPipelineOrchestrator(), '_share_knowledge')}")

# Check records
print(f"AgentKnowledgeSource: {AgentKnowledgeSource.objects.count()} records")
print(f"AgentMemory: {AgentMemory.objects.count()} records")
```

## Final Test Results (After Both Fixes)

```
AgentKnowledgeSource: 4 records ✅
AgentMemory: 3 records ✅
Agent: 163 agents (3 new standalone agents created)

Knowledge Entries:
  - Creation Agent: Cyberpunk style works great... (content_idea)
  - OpportunityPipelineOrchestrator: Multi-stage pipeline... (tool_discovery)
  - Vegas AI: Test Knowledge - Session 306... (market)
  - Vegas AI: Test betting pattern... (pricing)

Memory Entries:
  - OpportunityPipelineOrchestrator: Pipeline execution... tags=['pipeline', 'orchestration', 'success']
  - Vegas AI: Game analysis... tags=['sports_analysis', 'bookmaker', 'success']
  - Creation Agent: Image generation... tags=['image_generation', 'creation', 'success']
```

---

**Session 306 Complete: Learning Infrastructure Extended + Database Fixed!**
