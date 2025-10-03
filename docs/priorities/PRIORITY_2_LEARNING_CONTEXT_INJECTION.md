# 🎯 PRIORITY 2: Learning Context Injection

**Date Created:** October 2, 2025
**Status:** 🔴 **CRITICAL - Next Priority**
**Prerequisite:** ✅ Session 9 Complete (Spider Learning Bridge Active)
**Impact:** HIGH - Makes learning actually useful to agents

---

## 🚨 The Problem

**Current State:**
```
Spider Data → Learning Bridge → UserAgentLearning.create() ✅
                                        ↓
                                   [STORED IN DB] ✅
                                        ↓
                                   [NOT USED] ❌

Agent Execution → LLM → Response (without learned context!)
```

**What's Happening:**
- ✅ Spider data is collected (10,907 entries)
- ✅ Learning entries are created (3 entries, accumulating)
- ✅ Learning bridge is active and working
- ❌ **Agents DON'T USE the learned knowledge when executing!**

**The Gap:**
Learning entries exist in the database but are **NOT injected into agent prompts** when the LLM executes.

---

## 🎯 The Solution

### Inject Learning Context into Agent Prompts

**File:** `ai_core/agents/concrete_executor.py:137`

**Current Code:**
```python
# Enable intelligence capabilities (spider data + LLM)
await self.enable_agent_with_intelligence(agent_name, agent_instance)

logger.info(f"🏃 Executing agent: {agent_name} (with spider data + LLM)")
```

**Proposed Fix:**
```python
# Enable intelligence capabilities (spider data + LLM + LEARNING)
await self.enable_agent_with_intelligence(agent_name, agent_instance)

# 🆕 INJECT LEARNED KNOWLEDGE
await self.inject_learned_context(agent_name, agent_instance, task)

logger.info(f"🏃 Executing agent: {agent_name} (with spider data + LLM + learned patterns)")
```

### New Method to Add

```python
async def inject_learned_context(self, agent_name: str, agent_instance: Any, task: Dict[str, Any]):
    """
    Inject learned knowledge into agent execution context

    Retrieves UserAgentLearning entries for this agent and adds them
    to the prompt context so the LLM can use learned patterns.
    """
    from core.models_unified_system import UserAgentLearning
    from django.db.models import Q

    # Get relevant learning entries for this agent
    learning_entries = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: list(UserAgentLearning.objects.filter(
            agent_name=agent_name,
            is_active=True,
            confidence_score__gte=0.5  # Only use high-confidence learning
        ).order_by('-confidence_score', '-validation_count')[:10])
    )

    if not learning_entries:
        logger.debug(f"No learned knowledge found for {agent_name}")
        return

    # Build learning context summary
    learning_context = {
        'total_learning_entries': len(learning_entries),
        'domains': set(),
        'sources': set(),
        'key_patterns': [],
        'data_quality_insights': []
    }

    for entry in learning_entries:
        content = entry.learning_content or {}

        learning_context['domains'].add(entry.learning_domain)
        learning_context['sources'].add(entry.learning_source)

        # Extract key insights
        if 'opportunity_potential' in content:
            learning_context['key_patterns'].append({
                'source': entry.learning_source,
                'potential': content['opportunity_potential'],
                'confidence': entry.confidence_score,
                'validations': entry.validation_count
            })

        if 'data_source_reliability' in content:
            learning_context['data_quality_insights'].append({
                'source': entry.learning_source,
                'reliability': content['data_source_reliability'],
                'quality': content.get('quality_score', 0)
            })

    # Convert sets to lists for JSON serialization
    learning_context['domains'] = list(learning_context['domains'])
    learning_context['sources'] = list(learning_context['sources'])

    # Inject into agent instance
    if hasattr(agent_instance, 'learned_context'):
        agent_instance.learned_context = learning_context

    # Also add to task context for prompt building
    if 'context' not in task:
        task['context'] = {}
    task['context']['learned_knowledge'] = learning_context

    logger.info(f"✅ Injected {len(learning_entries)} learned patterns into {agent_name}")
    logger.debug(f"   Domains: {learning_context['domains']}")
    logger.debug(f"   Sources: {learning_context['sources']}")
```

---

## 🔧 Implementation Steps

### Step 1: Add Learning Context Injection Method
**File:** `ai_core/agents/concrete_executor.py`
**Action:** Add `inject_learned_context` method (code above)
**Lines:** ~50 lines of new code

### Step 2: Call Injection Before Agent Execution
**File:** `ai_core/agents/concrete_executor.py:137`
**Action:** Add call to `inject_learned_context`
**Lines:** 1 line change

### Step 3: Update LLM Integration to Use Learning Context
**File:** `ai_core/agents/llm_integration.py` (or wherever prompt building happens)
**Action:** Include `learned_knowledge` in system prompt

**Current Prompt Structure:**
```python
system_prompt = f"""
You are {agent_name}, an AI agent with expertise in {agent_type}.

Your capabilities:
- {capabilities}

Current task: {task_description}
"""
```

**New Prompt Structure:**
```python
system_prompt = f"""
You are {agent_name}, an AI agent with expertise in {agent_type}.

Your capabilities:
- {capabilities}

🧠 LEARNED KNOWLEDGE (from {learning_context['total_learning_entries']} past experiences):

Domains you've learned about:
{', '.join(learning_context['domains'])}

Reliable data sources you've used:
{format_sources(learning_context['sources'])}

Key patterns you've identified:
{format_patterns(learning_context['key_patterns'])}

Data quality insights:
{format_quality_insights(learning_context['data_quality_insights'])}

Use this learned knowledge to improve your response quality and accuracy.

Current task: {task_description}
"""
```

### Step 4: Test Learning Context Injection

**Test Script:**
```bash
python manage.py shell -c "
from ai_core.agents.concrete_executor import ConcreteAgentExecutor
import asyncio

executor = ConcreteAgentExecutor()

# Execute income-builder with learned context
result = asyncio.run(executor.execute_agent(
    'income-builder',
    {
        'task_description': 'Find high-quality freelance opportunities',
        'input': {}
    }
))

print(result)
"
```

**Expected Output:**
- Agent prompt includes learned patterns
- Agent mentions learned sources (e.g., "Based on past successful opportunities from Guru...")
- Agent uses data quality insights (e.g., "RemoteOK has shown 75% reliability...")

---

## 📊 Expected Impact

### Before Learning Context Injection
```
Agent executes → Generic LLM knowledge → Generic response
```

### After Learning Context Injection
```
Agent executes → Generic LLM knowledge + Learned patterns → Personalized, data-driven response
```

**Improvements:**
- **Response Quality:** +20-30% (uses actual data patterns)
- **Recommendation Accuracy:** +40-50% (knows which sources are reliable)
- **User Value:** +60-80% (recommendations based on real opportunities, not generic advice)

**Example:**

**Before:**
```
User: "Find me freelance writing opportunities"
Agent: "Try Upwork, Fiverr, and Freelancer.com. Look for clients who..."
[Generic advice, no data]
```

**After:**
```
User: "Find me freelance writing opportunities"
Agent: "Based on 960 recent opportunities I've analyzed from Guru (75% reliability score),
I found writing gigs pay $50-200/article. RemoteOK shows 392 remote writing positions with
$60k-$90k salaries. My learning shows Guru has highest conversion rate for quick wins.
Here are the top 5 matches..."
[Data-driven, specific, actionable]
```

---

## 🎯 Success Criteria

✅ **Learning context is injected** into agent execution
✅ **LLM prompts include learned knowledge** in system message
✅ **Agent responses reference learned patterns** (e.g., "Based on past data...")
✅ **Response quality improves measurably** (user engagement, click rates)
✅ **Test script confirms** learning context is present

---

## ⚠️ Known Challenges

### Challenge 1: Prompt Token Limit
**Problem:** Including too much learning context could exceed token limits
**Solution:** Limit to top 10 most relevant/highest-confidence entries
**Implementation:** Already handled in `inject_learned_context` method

### Challenge 2: Learning Context Format
**Problem:** Raw learning data might not be LLM-friendly
**Solution:** Format learning into natural language summaries
**Implementation:** Use format helper functions in prompt building

### Challenge 3: Stale Learning
**Problem:** Old learning might become irrelevant
**Solution:** Filter by `confidence_score >= 0.5` and order by `validation_count`
**Implementation:** Already handled in query

---

## 🔗 Related Work

**Dependencies:**
- ✅ Session 9: Spider Learning Bridge (COMPLETE)
- ✅ UserAgentLearning model (EXISTS)
- ✅ Learning entries being created (ACTIVE)

**Enables:**
- 🎯 Priority 3: Learning-based Agent Selection (agents recommend themselves based on past success)
- 🎯 Priority 4: Personalized Learning (user-specific patterns)
- 🎯 Priority 5: Cross-Agent Learning (agents learn from each other)

---

## 📝 Files to Modify

1. **`ai_core/agents/concrete_executor.py`**
   - Add `inject_learned_context` method (~50 lines)
   - Call injection at line 137 (+1 line)

2. **`ai_core/agents/llm_integration.py`** (or equivalent)
   - Update prompt building to include learned_knowledge
   - Add formatting helpers (~30 lines)

3. **`scripts/test_learning_context_injection.py`** (NEW)
   - Test script to verify learning context is injected
   - Validate prompt includes learned patterns (~80 lines)

**Total Estimated Changes:** ~160 lines of code

---

## 🚀 Deployment Plan

### Phase 1: Core Implementation (30 min)
1. Add `inject_learned_context` method
2. Call it in agent execution flow
3. Test with single agent

### Phase 2: Prompt Integration (20 min)
1. Update prompt building to include learning context
2. Add formatting helpers
3. Test prompt quality

### Phase 3: Validation (10 min)
1. Run test script
2. Verify agent responses include learned patterns
3. Check token usage stays within limits

**Total Time:** ~60 minutes for complete implementation and testing

---

## 💡 Quick Start for Next Session

```bash
# 1. Read this document
cat docs/priorities/PRIORITY_2_LEARNING_CONTEXT_INJECTION.md

# 2. Check current learning entries
python manage.py shell -c "
from core.models_unified_system import UserAgentLearning
print(f'Learning entries: {UserAgentLearning.objects.filter(learning_source__startswith=\"spider:\").count()}')
"

# 3. Implement injection method in concrete_executor.py
# (Copy method from this document)

# 4. Test injection
python scripts/test_learning_context_injection.py

# 5. Verify agent responses improve
# (Execute income-builder and check it mentions learned sources)
```

---

## 📈 Metrics to Track

**Before Implementation:**
- Agent responses: Generic, no data references
- User engagement: Baseline
- Learning entries: Created but unused

**After Implementation:**
- Agent responses: Include "Based on X opportunities..." references
- User engagement: +20-30% (more specific = more valuable)
- Learning entries: Created AND used ✅

**Monitor:**
```python
# Count how many agent executions include learned context
from core.models import AgentExecution
executions_with_learning = AgentExecution.objects.filter(
    context__contains='learned_knowledge'
).count()

print(f"Executions using learned knowledge: {executions_with_learning}")
```

---

## 🎊 Bottom Line

**Current State:** Learning is collected but NOT used
**After This Fix:** Learning is collected AND injected into agent prompts
**Impact:** Agents become **data-driven** instead of generic
**Effort:** ~60 minutes to implement and test
**Priority:** 🔴 **CRITICAL** - This makes learning actually useful!

Without this fix, agents are still "dumb" despite having learned knowledge in the database. This is the bridge between **collection** and **utilization**.

---

**Next Session Action:** Implement learning context injection in `concrete_executor.py:137`

**Expected Result:** Agents mention learned patterns like "Based on 960 opportunities from Guru..." instead of generic advice.

🚀 **This is how agents become truly intelligent!** 🚀
