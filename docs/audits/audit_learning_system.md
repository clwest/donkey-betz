# Agent 2.5: Learning System Audit

**Date:** December 21, 2025
**Status:** Complete
**Priority:** P0 - Critical
**Auditor:** Claude (Session 525)

---

## Executive Summary

The Learning System **IS WORKING** - agents are actively sharing knowledge and gaining XP. However, there's a significant gap between knowledge CREATION and knowledge CONSUMPTION.

### Key Findings

| Metric | Value | Status |
|--------|-------|--------|
| AgentKnowledgeSource records | **1,960** | Working |
| AgentMemory records | **292** | Working |
| AgentEvolution records | **49** | Working |
| Agents sharing knowledge | **38** | Good |
| Knowledge updated (24h) | **59** | Active |
| Knowledge retrieved in prompts | **2 files** | **GAP** |

---

## Learning System Architecture

### Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    LEARNING SYSTEM OVERVIEW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. KNOWLEDGE SHARING (Working)                                  │
│     ├── BaseAgent._share_knowledge() → AgentKnowledgeSource     │
│     ├── 1,960 knowledge records stored                          │
│     ├── 38 agents actively sharing                              │
│     └── 59 updates in last 24 hours                             │
│                                                                  │
│  2. MEMORY CREATION (Working)                                    │
│     ├── BaseAgent._create_execution_memory() → AgentMemory      │
│     ├── 292 memories stored                                     │
│     └── Most recent: Today                                      │
│                                                                  │
│  3. EVOLUTION/XP (Working)                                       │
│     ├── LearningLoopService.record_outcome() → AgentEvolution   │
│     ├── 49 agents with evolution data                           │
│     └── ResearchAgent leads at Level 4 (960 XP)                 │
│                                                                  │
│  4. KNOWLEDGE RETRIEVAL (GAP)                                    │
│     ├── BaseAgent._get_relevant_knowledge_for_task()            │
│     ├── Only 2 files call retrieval methods                     │
│     └── Most agents don't use retrieved knowledge               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Findings

### 1. Knowledge Sharing is Active

**Top Knowledge Contributors:**

| Agent | Knowledge Items | Specialization |
|-------|-----------------|----------------|
| ResearchAgent | 522 | Web research intelligence |
| ContentStrategyAgent | 395 | Content planning insights |
| TrendAnalysisAgent | 96 | Trend detection |
| OpportunityScoringAgent | 76 | Opportunity scoring |
| WorkflowAgent | 66 | Workflow patterns |
| VideoAgent | 61 | Video creation insights |
| SocialMediaAgent | 60 | Social media patterns |
| SEOOptimizerAgent | 58 | SEO optimization |
| ImageAgent | 54 | Image creation insights |
| CTOAgent | 49 | Technical planning |

**Knowledge Types:**

| Type | Count | Percentage |
|------|-------|------------|
| trend | 1,241 | 63% |
| market | 310 | 16% |
| best_practice | 307 | 16% |
| tool_discovery | 34 | 2% |
| content_idea | 31 | 2% |
| opportunity | 25 | 1% |
| user_behavior | 12 | <1% |

### 2. Agent Evolution is Working

**Top Evolved Agents:**

| Agent | Level | XP | Status |
|-------|-------|-----|--------|
| ResearchAgent | 4 | 960 | Senior |
| ContentWriterAgent | 3 | 555 | Experienced |
| ImageAgent | 3 | 380 | Experienced |
| AudioAgent | 2 | 270 | Developing |
| AISeriesWorkflowAgent | 2 | 260 | Developing |

### 3. Knowledge Freshness

| Time Period | Count | Percentage |
|-------------|-------|------------|
| Last 24 hours | 59 | 3% |
| Last 7 days | 568 | 28% |
| Older than 7 days | 1,392 | 72% |

### 4. The Gap: Knowledge Retrieval

**Files that retrieve knowledge:**
- `core/agents/base_agent.py` - Defines `_get_relevant_knowledge_for_task()` and `_get_shared_knowledge()`
- `core/agents/personal_assistant_agent.py` - Uses knowledge in routing

**Problem:** While BaseAgent DEFINES knowledge retrieval methods, most agents don't actively call them. The `_build_prompt()` method does include retrieved knowledge, but:

1. Many agents override `_build_prompt()` with simpler versions
2. Some agents build prompts manually without calling base methods
3. Knowledge injection happens but isn't optimized for each agent's domain

---

## Learning Hooks Analysis

### Hooks Available in BaseAgent (Session 304)

| Hook | Purpose | Usage Count |
|------|---------|-------------|
| `_record_learning_outcome()` | Record execution outcome for XP | 222 occurrences across 64 files |
| `_create_execution_memory()` | Create persistent memory | 222 occurrences across 64 files |
| `_share_knowledge()` | Share learned knowledge | 222 occurrences across 64 files |
| `_get_shared_knowledge()` | Retrieve others' knowledge | 2 files only |
| `_get_relevant_knowledge_for_task()` | Semantic knowledge search | 2 files only |

### What This Means

1. **Storage is widespread** - All agents CAN create memories and share knowledge (222 occurrences)
2. **Retrieval is limited** - Only 2 files actively retrieve and use knowledge
3. **Learning is ONE-WAY** - Agents learn and share, but don't learn FROM each other effectively

---

## Services Involved

| Service | File | Purpose |
|---------|------|---------|
| LearningLoopService | `core/super_platform/learning_loop.py` | Outcome recording, XP, pattern detection |
| AgentLearningService | `core/services/agent_learning_service.py` | Interaction tracking, preference learning |
| MemoryEmbeddingService | `core/services/memory_embedding_service.py` | Memory creation with embeddings |
| CollectiveIntelligence | `core/services/collective_intelligence.py` | Cross-agent knowledge sharing |

---

## Gap Analysis

### What's Working Well

1. **Knowledge Creation** - 1,960 records from 38 agents
2. **Memory Storage** - 292 memories stored
3. **Evolution System** - 49 agents leveling up
4. **Hook Infrastructure** - All agents have access to learning hooks
5. **Recent Activity** - 59 knowledge updates in 24 hours

### What Needs Improvement

| Issue | Impact | Priority |
|-------|--------|----------|
| Knowledge retrieval limited to 2 files | Agents don't learn from each other | P0 |
| 72% of knowledge >7 days old | Some knowledge may be stale | P1 |
| Only 12% high-confidence knowledge | Low confidence limits usefulness | P2 |
| Many agents override _build_prompt() | Skip knowledge injection | P0 |

---

## Recommendations

### Immediate (P0)

1. **Enforce Knowledge Injection in BaseAgent**
   - Modify `_build_prompt()` to ALWAYS include relevant knowledge
   - Add knowledge retrieval to `_call_openai()` as fallback
   - Prevent agents from bypassing knowledge context

2. **Add Domain-Specific Knowledge Retrieval**
   - ImageAgent should retrieve image-related knowledge
   - ResearchAgent should retrieve research patterns
   - Filter knowledge by agent domain

### Short-Term (P1)

3. **Implement Knowledge Decay**
   - Reduce confidence of stale knowledge over time
   - Archive knowledge older than 30 days with low usage

4. **Add Cross-Agent Learning Triggers**
   - When one agent succeeds, share pattern with related agents
   - When one agent fails, warn related agents

### Long-Term (P2)

5. **Knowledge Quality Scoring**
   - Track which knowledge leads to successful outcomes
   - Boost high-quality knowledge in prompts

---

## Verification Commands

```bash
# Check knowledge count
.venv/bin/python manage.py shell -c "from core.models_unified_system import AgentKnowledgeSource; print(AgentKnowledgeSource.objects.count())"

# Check recent memories
.venv/bin/python manage.py shell -c "from core.models_unified_system import AgentMemory; print(AgentMemory.objects.order_by('-created_at')[:5].values('memory_type', 'created_at'))"

# Check agent evolution
.venv/bin/python manage.py shell -c "from core.models_unified_system import AgentEvolution; print(AgentEvolution.objects.order_by('-total_xp')[:5].values('agent__name', 'current_level', 'total_xp'))"
```

---

## Comparison with Prompting System (Agent 2.1)

| Aspect | Prompting System | Learning System |
|--------|------------------|-----------------|
| Infrastructure | Complete | Complete |
| Data Storage | PLATFORM_CONTEXT static | 1,960 dynamic records |
| Usage Rate | 1/42 agents | 38/42 agents create, 2/42 consume |
| Gap Type | Not imported/called | Created but not retrieved |

Both systems have the same fundamental problem: **Infrastructure exists but agents don't use it.**

---

## Files Referenced

| File | Purpose |
|------|---------|
| `core/agents/base_agent.py` | Learning hooks (lines 1241-1549) |
| `core/super_platform/learning_loop.py` | LearningLoopService |
| `core/services/agent_learning_service.py` | AgentLearningService |
| `core/services/collective_intelligence.py` | Cross-agent sharing |
| `core/models_unified_system.py` | AgentKnowledgeSource, AgentMemory, AgentEvolution models |

---

*Generated by Agent 2.5: Learning System Audit - December 21, 2025*
