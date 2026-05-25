# Session 405: Legal Agent Learning Audit & Fix

**Date:** December 9, 2025
**Session:** 405
**Focus:** Audit and FIX collective intelligence integration for LegalDocDrafterAgent

---

## Executive Summary

GPT correctly identified that the platform has the primitives for inter-agent learning. This audit verified which parts were actively firing and identified critical gaps. **All gaps have now been fixed.**

**Status: FIXED** - The LegalDocDrafterAgent now fully participates in collective intelligence:
- ✅ Agent registered in database
- ✅ Learning hooks fire during denied motion processing
- ✅ AgentKnowledgeSource records created
- ✅ LegalMemory records created
- ✅ Every motion filed makes the system smarter!

---

## What GPT Said vs. Reality

| GPT's Claim | Reality | Status |
|-------------|---------|--------|
| Agents have reflection logs | `AgentReflection` model exists | ✅ Verified |
| Agents have memory entries | `AgentMemory`, `MemoryCluster` exist | ✅ Verified |
| Agents have vector embeddings | pgvector integration works | ✅ Verified |
| Inter-agent knowledge transfer | 924 `AgentKnowledgeSource` records | ✅ Verified |
| **Legal agent shares knowledge** | **0 records from LegalDocDrafterAgent** | ❌ **GAP** |
| Cross-user cluster pollination | Not implemented | ❌ Future |

---

## Architecture Analysis

### BaseAgent Learning Infrastructure (Session 304/400)

The `BaseAgent` class at `core/agents/base_agent.py` provides these learning methods:

```python
# Knowledge retrieval (Session 400)
_get_relevant_knowledge_for_task(task, limit=5)  # Lines 315-402
_get_fresh_spider_intelligence(categories, hours, limit)  # Lines 246-313
_build_knowledge_attribution(knowledge_items)  # Lines 404-459

# Learning hooks (Session 304)
_record_learning_outcome(result, task, context, ...)  # Lines 1009-1061
_create_execution_memory(result, task, memory_type, importance)  # Lines 1077-1137
_share_knowledge(knowledge_type, title, knowledge_value, confidence)  # Lines 1181-1255
_get_shared_knowledge(knowledge_type, title_contains, from_agents)  # Lines 1257-1326
```

### LegalDocDrafterAgent Implementation

Location: `core/agents/legal/legal_doc_drafter_agent.py`

**Learning hooks ARE present:**
- Line 979: `_record_learning_outcome()` - Called in standard execute()
- Line 989: `_create_execution_memory()` - Called when documents generated
- Line 998: `_share_legal_knowledge()` - Called to share patterns
- Line 1934: `_share_knowledge()` - Called inside `_share_legal_knowledge()`

**CRITICAL GAP:** The `_execute_denied_motion_pipeline()` method (lines 2062-2224) does **NOT** call any learning hooks!

```python
def _execute_denied_motion_pipeline(self, task, context, start_time):
    """
    Session 404: This bypasses GPT and DIRECTLY calls:
    1. analyze_denied_motion
    2. check_non_party_issues
    3. rewrite_motion
    4. generate_evidence_checklist
    """
    # ... 160 lines of processing ...

    return AgentResult(
        success=True,
        message="\n".join(output_parts),
        data={...}
    )
    # ❌ NO LEARNING HOOKS CALLED!
```

---

## Database Evidence

### AgentKnowledgeSource by Agent (Top 10)

| Agent | Knowledge Records |
|-------|-------------------|
| ContentStrategyAgent | 202 |
| ResearchAgent | 70 |
| TrendAnalysisAgent | 67 |
| WorkflowAgent | 56 |
| SocialMediaAgent | 51 |
| SEOOptimizerAgent | 49 |
| OpportunityScoringAgent | 48 |
| CTOAgent | 40 |
| VideoAgent | 39 |
| COOAgent | 36 |
| **LegalDocDrafterAgent** | **0** |

### Legal-Specific Database Tables

| Table | Records | Notes |
|-------|---------|-------|
| LegalMemory | 0 | No legal patterns stored |
| LegalDocument | 1 | Only 1 document saved |
| LegalResearchResult | 0 | No research cached |
| LegalCase | 0 | No cases tracked |

### Agent Registration

**LegalDocDrafterAgent is NOT in the Agent database table!**

This means `self.agent_model` returns `None`, which causes:
- `_share_knowledge()` to silently fail
- `_create_execution_memory()` to silently fail
- `_track_contribution()` to silently fail

---

## Learning Flow Comparison

### Other Agents (Working)
```
User Request
    ↓
Agent.execute()
    ↓
Process task with tools
    ↓
_record_learning_outcome() ✅
    ↓
_create_execution_memory() ✅
    ↓
_share_knowledge() ✅
    ↓
AgentKnowledgeSource created ✅
    ↓
Other agents can retrieve via _get_relevant_knowledge_for_task()
```

### LegalDocDrafterAgent (Standard Path)
```
User Request (non-denied motion)
    ↓
execute()
    ↓
_build_legal_prompt()
    ↓
_call_openai()
    ↓
Process tool calls
    ↓
_record_learning_outcome() ✅ (line 979)
    ↓
_create_execution_memory() ✅ (line 989)
    ↓
_share_legal_knowledge() ✅ (line 998)
    ↓
❌ FAILS because agent_model is None
```

### LegalDocDrafterAgent (Denied Motion Path)
```
User Request (denied motion detected)
    ↓
execute()
    ↓
_detect_denied_motion_mode() → True
    ↓
_execute_denied_motion_pipeline()
    ↓
analyze_denied_motion
check_non_party_issues
rewrite_motion
generate_evidence_checklist
    ↓
return AgentResult
    ↓
❌ NO LEARNING HOOKS CALLED AT ALL
```

---

## Impact Assessment

### What This Means

1. **No Cross-Learning:** When the legal agent successfully rewrites a denied motion, other agents cannot learn from that success.

2. **No Pattern Detection:** The system cannot detect patterns like "motions with these characteristics get denied" or "this JDF form combination works."

3. **No Collective Memory:** Each legal request starts from scratch - the agent doesn't remember what worked before.

4. **Isolated Knowledge:** The legal agent cannot benefit from knowledge shared by ResearchAgent, TrendAnalysisAgent, or other agents.

### The Lost Opportunity

GPT was right - every motion filed SHOULD make the system smarter:

```
Motion Filed → Success/Failure
                    ↓
            Record Pattern
                    ↓
        Share with Collective
                    ↓
    Future Motions Benefit
```

~~Currently: **Nothing is recorded or shared from denied motion processing.**~~

**UPDATE: FIXED** - Learning hooks now fire for every denied motion rewrite!

---

## Fixes Implemented (Session 405)

### Fix 1: Agent Registration

**File:** `core/agents/legal/legal_doc_drafter_agent.py`

Added `_ensure_agent_registered()` method that runs on `__init__`:

```python
def _ensure_agent_registered(self):
    """Ensure LegalDocDrafterAgent is registered in the Agent database."""
    try:
        from core.models_unified_system import Agent
        if self._agent_model is None:
            self._agent_model, created = Agent.objects.get_or_create(
                name=self.name,
                defaults={
                    'agent_type': 'legal',
                    'description': 'Pro Se Legal Assistant for Colorado Family Law...',
                    'is_active': True
                }
            )
    except Exception as e:
        logger.warning(f"Could not ensure agent registration: {e}")
```

### Fix 2: Learning Hooks in Denied Motion Pipeline

**File:** `core/agents/legal/legal_doc_drafter_agent.py` (lines 2259-2311)

Added learning hooks at end of `_execute_denied_motion_pipeline()`:

```python
# Session 405: LEARNING HOOKS - Every motion makes the system smarter!

# 1. Record learning outcome (XP, pattern detection)
self._record_learning_outcome(
    result=result,
    task=task,
    context=context,
    spider_data_used=False,
    scifi_context_used=False
)

# 2. Create execution memory
self._create_execution_memory(
    result=result,
    task=f"Denied Motion Rewrite: {relief_type}",
    memory_type="success",
    importance=0.9
)

# 3. Share with collective intelligence
self._share_knowledge(
    knowledge_type='content_idea',
    title=f"Legal Motion Pattern: {relief_type.replace('_', ' ').title()}",
    knowledge_value={
        'document_type': 'denied_motion_rewrite',
        'relief_type': relief_type,
        'jurisdiction': 'Colorado',
        'facts_count': len(facts),
        ...
    },
    confidence=0.85
)

# 4. Save legal-specific memory
self._save_legal_memory(
    task=task,
    relief_type=relief_type,
    facts=facts,
    success=True,
    execution_time_ms=execution_time
)
```

### Fix 3: Legal Memory Helper

Added `_save_legal_memory()` method that creates `LegalMemory` records with:
- Agent FK linkage
- Memory type: 'pattern'
- Case type: 'family_law'
- Document type: 'denied_motion_rewrite'
- Key insights and applicable scenarios

---

## Verification Results

After implementing fixes:

```
=== BEFORE FIXES ===
AgentKnowledgeSource (LegalDocDrafterAgent): 0
LegalMemory: 0
Agent in database: None

=== AFTER FIXES ===
AgentKnowledgeSource (LegalDocDrafterAgent): 1
LegalMemory: 1
Agent in database: LegalDocDrafterAgent (legal)

New Records Created:
- AgentKnowledgeSource: "Legal Motion Pattern: Modify Parenting Time"
  Type: content_idea, Confidence: 0.85

- LegalMemory: "Motion Rewrite: Modify Parenting Time"
  Type: pattern, Case: family_law, Doc: denied_motion_rewrite
  Insights: ['Relief type: modify_parenting_time', 'Facts count: 2', ...]
```

---

## Original Gaps (Now Fixed)

### Gap 1: Agent Not Registered in Database

**Problem:** LegalDocDrafterAgent is not in the `Agent` table.

**Fix:** Add agent to database or ensure `agent_model` property creates it.

```python
# In BaseAgent.__init__ or first use
from core.models_unified_system import Agent
self._agent_model, _ = Agent.objects.get_or_create(
    name='LegalDocDrafterAgent',
    defaults={
        'agent_type': 'legal',
        'description': 'Pro Se Legal Assistant for Colorado Family Law',
        'is_active': True
    }
)
```

### Gap 2: Denied Motion Pipeline Missing Learning Hooks

**Problem:** `_execute_denied_motion_pipeline()` doesn't call learning hooks.

**Fix:** Add learning hooks at end of pipeline:

```python
def _execute_denied_motion_pipeline(self, task, context, start_time):
    # ... existing code ...

    execution_time = int((time.time() - start_time) * 1000)

    result = AgentResult(
        success=True,
        message="\n".join(output_parts),
        # ...
    )

    # ADD THESE LINES:
    # Record learning outcome
    self._record_learning_outcome(
        result=result,
        task=task,
        context=context,
        spider_data_used=False,
        scifi_context_used=False
    )

    # Create execution memory for successful motion rewrite
    self._create_execution_memory(
        result=result,
        task=task,
        memory_type="success",
        importance=0.9  # High importance for legal work
    )

    # Share learned pattern
    self._share_knowledge(
        knowledge_type='content_idea',
        title=f"Colorado Motion Pattern: {relief_type}",
        knowledge_value={
            'relief_type': relief_type,
            'facts_count': len(facts),
            'non_party_issues': non_party_result.get('has_non_party_issues'),
            'case_type': context.get('case_type', 'family_law'),
            'success': True,
        },
        confidence=0.85
    )

    return result
```

### Gap 3: Legal-Specific Knowledge Types

**Problem:** Using generic `content_idea` type for legal patterns.

**Suggestion:** Add legal-specific knowledge types to the model:
- `legal_motion_pattern`
- `legal_form_mapping`
- `legal_deficiency_pattern`
- `legal_success_pattern`

---

## Verification Commands

```bash
# Check if LegalDocDrafterAgent is in database
.venv/bin/python manage.py shell -c "
from core.models_unified_system import Agent
agent = Agent.objects.filter(name='LegalDocDrafterAgent').first()
print(f'Agent exists: {agent is not None}')
"

# Check legal knowledge records
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentKnowledgeSource
legal = AgentKnowledgeSource.objects.filter(agent__name='LegalDocDrafterAgent').count()
print(f'Legal knowledge records: {legal}')
"

# Check LegalMemory records
.venv/bin/python manage.py shell -c "
from core.models_unified_system import LegalMemory
print(f'Legal memories: {LegalMemory.objects.count()}')
"
```

---

## Recommended Next Steps

### Immediate (Session 405)

1. **Register LegalDocDrafterAgent in database**
2. **Add learning hooks to `_execute_denied_motion_pipeline()`**
3. **Test that knowledge is created after motion rewrite**

### Future Sessions

4. Add legal-specific knowledge types
5. Create legal spider → agent knowledge bridge
6. Implement legal pattern clustering
7. Add cross-user knowledge sharing (opt-in)

---

## Conclusion

GPT's analysis was correct about the system's potential. The primitives exist:
- 924 knowledge records from other agents
- Learning hooks in BaseAgent
- Memory and reflection infrastructure

**UPDATE: ALL FIXES IMPLEMENTED AND VERIFIED!**

The LegalDocDrafterAgent now fully participates in collective intelligence:
- ✅ Agent registered in database
- ✅ Learning hooks fire during denied motion processing
- ✅ AgentKnowledgeSource records created
- ✅ LegalMemory records created
- ✅ Text cleanup patches applied (4D-4H)
- ✅ Frontend bullet formatting working
- ✅ Every motion filed makes the system smarter!

---

## Files Referenced

| File | Purpose |
|------|---------|
| `core/agents/base_agent.py` | Learning infrastructure |
| `core/agents/legal/legal_doc_drafter_agent.py` | Legal agent with learning hooks |
| `core/models_unified_system.py` | Database models |
| `ai_core/templates/components/panels/legal_assistant_panel.html` | Frontend formatting |

---

## Session 405 Patches Summary

| Patch | Description |
|-------|-------------|
| 4D | Pre-extraction cleanup patterns for PDF artifacts |
| 4D.5 | `postprocess_extracted_facts()` and `cleanup_generated_facts_block()` |
| 4D.7 | "Immediate Emergency Basis" removal, grammar fixes |
| 4E | Complete rewrite of `_build_clean_allegations()` |
| 4F | Bullet formatting in `cleanup_generated_facts_block()` |
| 4G | "Today's Incident" → "The Incident on [date]" |
| 4H | Frontend HTML formatting for bullets and newlines |

---

**End of Session 405 - COMPLETE ✅**
