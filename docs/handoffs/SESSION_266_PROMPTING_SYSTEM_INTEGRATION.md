# Session 266: Prompting System Integration Blueprint

**Date:** November 28, 2025
**Session:** 266
**Status:** IN PROGRESS
**Priority:** CRITICAL - Core Platform Integration

---

## Executive Summary

This document defines the complete integration plan for connecting the **Super Platform infrastructure** (built in Sessions 264-265) to the **active prompting system** (EnhancedPersonalAIAssistant + LLMEnforcer).

### The Problem

We have TWO prompting systems that are NOT connected:

| System | Status | Location | Purpose |
|--------|--------|----------|---------|
| **Active** | WORKING | `personal_ai_assistant_enhanced.py` | Static prompts, GPT-5.1 tool calling |
| **Dormant** | BUILT, NOT WIRED | `core/super_platform/` | Dynamic prompts, context aggregation |

### The Solution

**Hybrid Integration** - Keep the working GPT-5.1 tool calling system but inject dynamic context from Super Platform.

---

## Architecture Overview

### Current Flow (What Works)

```
User Message
    │
    ▼
views_assistant_bypass.py:90
    │
    ▼
EnhancedPersonalAIAssistant(user)
    │
    ▼
process_message(message, context)
    │
    ├── Static ~150 line system prompt
    ├── Tool definitions (10+ agent tools)
    └── GPT-5.1 Responses API call
    │
    ▼
LLMEnforcer.enforce_real_ai()
    │
    ▼
Response with tool_calls
```

### Target Flow (After Integration)

```
User Message
    │
    ▼
views_assistant_bypass.py
    │
    ▼
EnhancedPersonalAIAssistant(user)
    │
    ├── NEW: QueryClassifier.classify(message)
    │       → Determines intent (creation, question, workflow, etc.)
    │
    ├── NEW: ContextAggregator.aggregate(classification, message)
    │       → Gathers spider data, memories, mood, opportunities
    │
    ├── NEW: DynamicPromptBuilder.build(context)
    │       → Builds context-aware system prompt
    │
    ├── KEEP: Tool definitions (10+ agent tools)
    │
    └── KEEP: GPT-5.1 Responses API call via LLMEnforcer
    │
    ▼
Response with tool_calls + context-aware intelligence
```

---

## Component Inventory

### Super Platform Components (Ready to Use)

| Component | File | Status | Purpose |
|-----------|------|--------|---------|
| QueryClassifier | `core/super_platform/query_classifier.py` | READY | 9 query types, pattern matching, entity detection |
| DynamicPromptBuilder | `core/super_platform/prompt_builder.py` | READY | Context-aware prompt construction |
| ContextAggregator | `core/super_platform/context_aggregator.py` | READY | Multi-source context gathering |
| SuperPlatformCoordinator | `core/super_platform/coordinator.py` | READY | Unified brain (optional full replacement) |
| AgentContextService | `core/super_platform/agent_context_service.py` | READY | Spider data for agents |
| SciFiIntegrationService | `core/super_platform/scifi_integration.py` | READY | Mood, memory, evolution |
| RevenueIntegrationService | `core/super_platform/revenue_integration.py` | READY | Opportunity discovery |
| LearningLoopService | `core/super_platform/learning_loop.py` | READY | Outcome recording, adaptive selection |
| AutonomyEngine | `core/super_platform/autonomy_engine.py` | READY | Self-operating intelligence |

### Active System Components (Keep Working)

| Component | File | Status | Purpose |
|-----------|------|--------|---------|
| EnhancedPersonalAIAssistant | `core/personal_ai_assistant_enhanced.py` | WORKING | Main assistant class |
| LLMEnforcer | `core/llm_enforcer.py` | WORKING | GPT-5.1 Responses API |
| Tool Definitions | `personal_ai_assistant_enhanced.py:66-500` | WORKING | 10+ agent tools |
| views_assistant_bypass | `core/views_assistant_bypass.py` | WORKING | Entry point |

---

## Integration Plan

### Phase 1: Inject Classification (30 min)

**Goal:** Add query classification to understand user intent before processing.

**File to Modify:** `core/personal_ai_assistant_enhanced.py`

**Changes:**

```python
# At top of file, add import:
from core.super_platform import QueryClassifier, ClassificationResult

# In __init__, add:
self.query_classifier = QueryClassifier()

# In process_message(), add at start:
classification = self.query_classifier.classify(message)
logger.info(f"Query classified as {classification.primary_type.value} (confidence: {classification.confidence:.2f})")
```

**Why:** Classification tells us what kind of prompt context to build.

**Test:**
```python
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()
assistant = EnhancedPersonalAIAssistant(user)
# Should log classification for any message
```

---

### Phase 2: Inject Context Aggregation (45 min)

**Goal:** Gather spider intelligence, memories, and mood before building prompts.

**File to Modify:** `core/personal_ai_assistant_enhanced.py`

**Changes:**

```python
# At top of file, add import:
from core.super_platform import ContextAggregator, AggregatedContext

# In __init__, add:
self.context_aggregator = ContextAggregator(user)

# In process_message(), after classification:
aggregated_context = self.context_aggregator.aggregate(classification, message)
logger.info(f"Aggregated context from: {aggregated_context.sources_used}")
```

**What Gets Aggregated:**
- `spider_data` - Trends, news, market data, job listings
- `memories` - Past interactions from Memory Palace
- `agent_mood` - Current mood influencing creativity
- `available_agents` - List of ready agents
- `user_preferences` - Personalization settings
- `active_opportunities` - Revenue opportunities

**Test:**
```python
# After phase 2, check context gathering works
# Should see spider data, memories, etc. in logs
```

---

### Phase 3: Dynamic Prompt Injection (1 hour)

**Goal:** Replace static system prompt with dynamic, context-aware prompt.

**File to Modify:** `core/personal_ai_assistant_enhanced.py`

**Current State (Static Prompt):**
The `_build_system_prompt()` method builds a ~150 line static prompt.

**New State (Dynamic Prompt):**

```python
# At top of file, add import:
from core.super_platform import DynamicPromptBuilder, PromptContext

# In __init__, add:
self.prompt_builder = DynamicPromptBuilder()

# Create new method:
def _build_dynamic_system_prompt(self, message: str, classification: ClassificationResult, context: AggregatedContext) -> str:
    """Build a dynamic system prompt using Super Platform infrastructure."""

    # Build prompt context
    prompt_context = PromptContext(
        classification=classification,
        spider_data=context.spider_data,
        memories=context.memories,
        agent_mood=context.agent_mood,
        user_preferences=context.user_preferences,
        available_agents=context.available_agents,
    )

    # Get dynamic base prompt
    dynamic_prompt = self.prompt_builder.build(prompt_context)

    # CRITICAL: Append existing tool instructions
    # These are essential for GPT-5.1 to use tools correctly
    tool_instructions = self._get_tool_usage_instructions()

    # CRITICAL: Append user personalization
    user_context = self._get_user_personalization_context()

    # Combine all sections
    full_prompt = f"""{dynamic_prompt}

## Tool Usage Instructions
{tool_instructions}

## User Context
{user_context}

## Current Assets
{self._get_recent_assets_context()}
"""

    return full_prompt
```

**Key Preservation:**
- Keep tool usage instructions (essential for function calling)
- Keep user personalization (learned preferences)
- Keep asset context (for intelligent chaining)
- Keep conversation history handling

---

### Phase 4: Spider Data in Prompts (30 min)

**Goal:** Format spider intelligence for GPT consumption.

**File to Modify:** `core/super_platform/prompt_builder.py`

**Enhance `_build_spider_section()`:**

```python
def _build_spider_section(self, spider_data: Dict[str, Any]) -> str:
    """Build rich spider intelligence section for GPT."""
    context_parts = []

    # Trending topics with actionable framing
    if spider_data.get('trends'):
        trends = spider_data['trends'][:5]
        trend_text = "\n".join(f"- **{t.get('title', t)}** (trending now)" for t in trends)
        context_parts.append(f"### Trending Topics\n{trend_text}\n*Use these trends to make content more relevant.*")

    # Recent news for research context
    if spider_data.get('news'):
        news = spider_data['news'][:3]
        news_text = "\n".join(f"- {n.get('title', 'Article')}" for n in news)
        context_parts.append(f"### Latest News\n{news_text}")

    # Market data for financial context
    if spider_data.get('market'):
        market = spider_data['market']
        if market.get('crypto'):
            crypto = market['crypto'][:3]
            crypto_text = ", ".join(f"{c.get('symbol', '?')}: ${c.get('price', 0):,.2f}" for c in crypto)
            context_parts.append(f"### Market Snapshot\n{crypto_text}")

    # Job market for opportunity context
    if spider_data.get('jobs'):
        jobs = spider_data['jobs']
        if jobs.get('hot_skills'):
            context_parts.append(f"### Hot Skills in Demand\n{', '.join(jobs['hot_skills'][:5])}")

    spider_context = "\n\n".join(context_parts) if context_parts else "Real-time data available on request."

    return self.PROMPT_SECTIONS['spider_intelligence'].format(spider_context=spider_context)
```

---

### Phase 5: Learning Loop Integration (30 min)

**Goal:** Record outcomes and use adaptive agent selection.

**File to Modify:** `core/personal_ai_assistant_enhanced.py`

**Changes:**

```python
# At top of file, add import:
from core.super_platform import get_learning_loop_service

# In __init__, add:
self._learning_service = None

@property
def learning_service(self):
    if self._learning_service is None:
        try:
            self._learning_service = get_learning_loop_service(self.user)
        except Exception as e:
            logger.warning(f"Could not load learning service: {e}")
    return self._learning_service

# After successful response, record outcome:
def _record_learning_outcome(self, message, classification, response, success, agents_used, execution_time_ms):
    if self.learning_service:
        try:
            self.learning_service.record_outcome(
                query_type=classification.primary_type.value,
                query_text=message,
                execution_mode='assistant',
                agents_used=agents_used,
                response=response[:500],  # Truncate for storage
                execution_time_ms=execution_time_ms,
                success=success,
                classification_confidence=classification.confidence,
                spider_data_used=classification.requires_spider_data,
            )
        except Exception as e:
            logger.warning(f"Failed to record learning outcome: {e}")
```

---

### Phase 6: Sci-Fi Context (Optional, 20 min)

**Goal:** Add mood and personality to agent interactions.

**File to Modify:** `core/personal_ai_assistant_enhanced.py`

**Changes:**

```python
# At top of file, add import:
from core.super_platform import get_scifi_integration_service

# In __init__, add:
self._scifi_service = None

@property
def scifi_service(self):
    if self._scifi_service is None:
        try:
            self._scifi_service = get_scifi_integration_service()
        except Exception as e:
            logger.warning(f"Could not load sci-fi service: {e}")
    return self._scifi_service

# When preparing agent context:
def _get_agent_personality_context(self, agent_name: str, task: str) -> str:
    if not self.scifi_service:
        return ""

    try:
        scifi_ctx = self.scifi_service.get_scifi_context(agent_name, task, self.user)
        parts = []

        if scifi_ctx.mood:
            parts.append(f"Agent mood: {scifi_ctx.mood.mood_type} - {scifi_ctx.mood.description}")

        if scifi_ctx.evolution:
            parts.append(f"Experience: Level {scifi_ctx.evolution.level} ({scifi_ctx.evolution.title})")

        return "\n".join(parts)
    except Exception:
        return ""
```

---

## File Change Summary

### Files to MODIFY:

| File | Changes | Priority |
|------|---------|----------|
| `core/personal_ai_assistant_enhanced.py` | Add classification, aggregation, dynamic prompts | P0 |
| `core/super_platform/prompt_builder.py` | Enhance spider data formatting | P1 |

### Files to KEEP AS-IS:

| File | Reason |
|------|--------|
| `core/llm_enforcer.py` | Working GPT-5.1 integration |
| `core/views_assistant_bypass.py` | Entry point works fine |
| `core/super_platform/query_classifier.py` | Ready to use |
| `core/super_platform/context_aggregator.py` | Ready to use |
| `core/super_platform/coordinator.py` | Optional full replacement |

### Files NOT NEEDED:

| File | Reason |
|------|--------|
| None | All Super Platform components are useful |

---

## Testing Plan

### Unit Tests

```python
# tests/test_prompting_integration.py

def test_query_classification():
    """Test that queries are classified correctly."""
    from core.super_platform import QueryClassifier
    classifier = QueryClassifier()

    # Test creation request
    result = classifier.classify("Create a logo for my coffee shop")
    assert result.primary_type.value == "creation"
    assert result.confidence > 0.7

    # Test question
    result = classifier.classify("What is trending in AI?")
    assert result.primary_type.value == "question"
    assert result.requires_spider_data == True

def test_context_aggregation():
    """Test that context is gathered from all sources."""
    from core.super_platform import ContextAggregator, QueryClassifier
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.first()

    classifier = QueryClassifier()
    aggregator = ContextAggregator(user)

    classification = classifier.classify("What are the latest tech trends?")
    context = aggregator.aggregate(classification, "What are the latest tech trends?")

    assert 'spider_intelligence' in context.sources_used
    assert context.spider_data is not None

def test_dynamic_prompt_building():
    """Test that dynamic prompts include all sections."""
    from core.super_platform import DynamicPromptBuilder, QueryClassifier, PromptContext

    classifier = QueryClassifier()
    builder = DynamicPromptBuilder()

    classification = classifier.classify("Create a logo")

    prompt_context = PromptContext(
        classification=classification,
        spider_data={'trends': [{'title': 'AI logos'}]},
    )

    prompt = builder.build(prompt_context)

    assert "Super Platform Intelligence Hub" in prompt
    assert "Content Creation Capabilities" in prompt
```

### Integration Test

```python
# Test full flow in Django shell
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

assistant = EnhancedPersonalAIAssistant(user)
response = assistant.process_message("What's trending in AI right now?")

# Should see:
# 1. Classification logged
# 2. Context aggregation logged
# 3. Dynamic prompt used
# 4. Spider data in response
print(response)
```

---

## Rollback Plan

If integration causes issues:

```bash
# 1. Revert personal_ai_assistant_enhanced.py
git checkout HEAD -- core/personal_ai_assistant_enhanced.py

# 2. Restart server
make start

# 3. Verify original behavior works
curl -X POST http://localhost:8000/api/assistant/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

---

## Success Criteria

### Phase 1 Complete When:
- [ ] QueryClassifier imported and initialized
- [ ] Classification logged for every message
- [ ] No errors in classification

### Phase 2 Complete When:
- [ ] ContextAggregator imported and initialized
- [ ] Spider data gathered for questions
- [ ] Memories gathered for recall requests
- [ ] Sources logged

### Phase 3 Complete When:
- [ ] Dynamic prompts replace static prompts
- [ ] Tool instructions preserved
- [ ] User context preserved
- [ ] GPT-5.1 tool calling still works

### Phase 4 Complete When:
- [ ] Spider trends appear in responses
- [ ] News data used for research queries
- [ ] Market data available for financial queries

### Phase 5 Complete When:
- [ ] Outcomes recorded to database
- [ ] Agent performance tracked
- [ ] Learning patterns detectable

### Phase 6 Complete When:
- [ ] Agent mood influences responses
- [ ] Agent level/experience shown
- [ ] Personality adds character

---

## Historical Context

### Session 25 (October 2025)
- Discovered GPT-5-mini needed explicit "FINAL ANSWER:" markers
- Fixed llm_enforcer.py with output instructions
- All 196 agents affected

### Session 129
- Upgraded from GPT-5-mini to GPT-5.1
- Migrated to Responses API
- Added reasoning effort configuration
- Tool calling via Responses API format

### Sessions 264-265 (November 2025)
- Built Super Platform infrastructure (6 phases)
- QueryClassifier, PromptBuilder, ContextAggregator
- Spider-Agent Bridge, Sci-Fi Integration
- Revenue Pipeline, Learning Loop, Autonomy Engine
- **All built but NOT connected to main entry point**

### Session 266 (Current)
- This integration plan created
- Goal: Connect dormant infrastructure to active system

---

## Notes for Future Sessions

1. **The llm_enforcer.py is CORRECT** - Don't modify it, the GPT-5.1 Responses API integration works.

2. **Keep tool definitions as-is** - The 10+ agent tools in personal_ai_assistant_enhanced.py are well-designed.

3. **Integration is additive** - We're adding new capabilities, not replacing working code.

4. **Spider data is the key value-add** - The 70 spiders collecting real-time data should enhance every response.

5. **Learning loop enables improvement** - Recording outcomes lets the system get smarter over time.

---

## Quick Reference

### Key Imports
```python
from core.super_platform import (
    QueryClassifier,
    ClassificationResult,
    DynamicPromptBuilder,
    PromptContext,
    ContextAggregator,
    AggregatedContext,
    get_learning_loop_service,
    get_scifi_integration_service,
)
```

### Key Files
- Entry point: `core/views_assistant_bypass.py`
- Main assistant: `core/personal_ai_assistant_enhanced.py`
- LLM layer: `core/llm_enforcer.py`
- Super Platform: `core/super_platform/`

### Key Commands
```bash
# Start platform
make start && make celery

# Test assistant
python manage.py shell -c "
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()
assistant = EnhancedPersonalAIAssistant(user)
print(assistant.process_message('Hello'))
"
```

---

**Document Status:** IMPLEMENTATION COMPLETE

**Completed Actions:**
- Phase 1: QueryClassifier injected
- Phase 2: ContextAggregator injected
- Phase 3: Spider intelligence in prompts
- Phase 4: Learning Loop outcome recording
- Phase 5: Sci-Fi agent personality

**Session 266 Completion Time:** ~2 hours
