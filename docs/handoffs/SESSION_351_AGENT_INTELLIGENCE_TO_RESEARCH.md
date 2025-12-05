# Session 351: Agent Intelligence → Research Pipeline

**Date:** December 4, 2025
**Status:** COMPLETE
**Branch:** `feature/session-52-ai-assistant`

---

## Summary

Connected the "Agents/Social" tab data (agent conversations, shared knowledge, boardroom decisions) to the business research pipeline. Now when agents discuss ideas, that intelligence is actually used when researching the market.

---

## What Was Built

### 1. AgentIntelligenceContextService (`core/services/agent_intelligence_context.py`)

New service that aggregates intelligence from multiple agent data sources:

**Data Sources:**
- `SharedKnowledge` - What agents have learned (currently 0 items)
- `KnowledgeTransfer` - What agents have taught each other
- `AgentConversation` - What agents have discussed (1,164 conversations)
- `AgentDecisionSummary` - Boardroom decisions and policies (43 decisions)

**Key Methods:**
```python
from core.services.agent_intelligence_context import get_agent_intelligence_context

service = get_agent_intelligence_context()
context = service.get_context_for_research(
    topic="AI fitness coaching app",
    domain="fitness_health",  # Optional domain filter
    max_items_per_category=5
)

# Get formatted prompt text
prompt_text = context.to_prompt_context()
```

**Output Format:**
```
============================================================
AGENT COLLECTIVE INTELLIGENCE (Session 351)
============================================================
The following insights come from agent learning, conversations, and governance decisions.
Consider these when forming your analysis.

## LEARNED INSIGHTS FROM AGENTS
- [AgentName] Knowledge Title
  → Description preview...

## RECENT KNOWLEDGE SHARING
- Teacher taught Student: Knowledge Title

## INSIGHTS FROM AGENT DISCUSSIONS
### Topic: Discussion topic
   Conclusion: Summarized conclusion...
   • Key insight 1
   • Key insight 2

## CANONICAL POLICIES (Boardroom Decisions)
These policies have been established through agent governance:
### Policy Topic
Type: guideline | Area: product
Stance: Recommended stance...
============================================================
```

### 2. CompetitorAnalysisAgent Integration

Modified `core/agents/business/competitor_analysis_agent.py`:

- Added `_agent_intelligence` property for lazy loading
- Injected agent intelligence context into research prompts
- Records decision when context is injected

**Key Changes:**
- Line 289: Added `self._agent_intelligence = None`
- Lines 315-321: Added `agent_intelligence` property
- Lines 553-581: Inject context into `full_prompt`

### 3. CustomerResearchAgent Integration

Modified `core/agents/business/customer_research_agent.py`:

- Same integration pattern as CompetitorAnalysisAgent
- Injects agent intelligence context into customer research prompts

**Key Changes:**
- Line 394: Added `self._agent_intelligence = None`
- Lines 421-427: Added `agent_intelligence` property
- Lines 665-693: Inject context into `full_prompt`

### 4. "Start Research Project" Button

Added to Boardroom Decisions UI for product-type decisions:

**Files Modified:**
- `ai_core/templates/ai_image_studio.html`
  - Lines 46924-46929: Added `researchButton` variable
  - Lines 46931-46946: Added button to action buttons
  - Lines 47015-47067: Added `startResearchFromDecision()` function

**Behavior:**
- Only appears on `decision_type === 'product'` decisions with `suggested_feature`
- Pre-fills chat input with research request referencing the boardroom decision
- Scrolls to chat, highlights input, and prompts user to send

---

## Data Flow

```
Agent Conversations (1,164)     SharedKnowledge (0)
         ↓                              ↓
    AgentDecisionSummary (43)   KnowledgeTransfer
         ↓                              ↓
         └──────────┬──────────────────┘
                    ↓
    AgentIntelligenceContextService
                    ↓
              to_prompt_context()
                    ↓
    CompetitorAnalysisAgent / CustomerResearchAgent
                    ↓
             Enhanced Research Results
```

---

## Testing

```bash
# Test the service
.venv/bin/python manage.py shell -c "
from core.services.agent_intelligence_context import get_agent_intelligence_context

service = get_agent_intelligence_context()
context = service.get_context_for_research('AI content generation')

print('Knowledge:', context.total_knowledge_items)
print('Conversations:', context.total_conversations)
print('Policies:', context.total_policies)
print()
print(context.to_prompt_context()[:1000])
"

# Check database counts
.venv/bin/python manage.py shell -c "
from core.models_unified_system import SharedKnowledge, AgentConversation, AgentDecisionSummary

print('SharedKnowledge:', SharedKnowledge.objects.count())
print('AgentConversation:', AgentConversation.objects.count())
print('AgentDecisionSummary:', AgentDecisionSummary.objects.count())
print('Canonical Policies:', AgentDecisionSummary.objects.filter(is_canonical=True).count())
"
```

---

## Files Changed

### New Files
| File | Purpose |
|------|---------|
| `core/services/agent_intelligence_context.py` | Service to aggregate agent intelligence for research |
| `docs/handoffs/SESSION_351_AGENT_INTELLIGENCE_TO_RESEARCH.md` | This handoff document |

### Modified Files
| File | Lines | Changes |
|------|-------|---------|
| `core/agents/business/competitor_analysis_agent.py` | 289, 315-321, 553-581 | Agent intelligence injection |
| `core/agents/business/customer_research_agent.py` | 394, 421-427, 665-693 | Agent intelligence injection |
| `ai_core/templates/ai_image_studio.html` | 46924-46946, 47015-47067 | Research button + JS function |

---

## Current Data State

```
AgentKnowledgeSource: 732 items (what agents have learned!)
KnowledgeTransfer: Active transfers happening
AgentConversation: 1,164 conversations
AgentDecisionSummary: 43 decisions
Canonical Policies: 0 (none promoted yet)
```

### IMPORTANT: Data Model Clarification

There are TWO knowledge models - the service now uses the CORRECT one:

| Model | Count | Used By |
|-------|-------|---------|
| `AgentKnowledgeSource` | **732** | `run_agent_learning_cycle()` in tasks.py - **THE ACTUAL DATA** |
| `SharedKnowledge` | 0 | Unused legacy model |

The `AgentKnowledgeSource` model stores:
- Knowledge learned from spider data
- Knowledge transferred between agents (prefixed with `[Learned]`)
- Linked to specific Agent via ForeignKey

**Note:** The intelligence pipeline is ready but works best when:
1. Boardroom decisions are promoted to canonical policies

---

## Recommendations for Session 352

1. **Promote Canonical Policies** - Go to Agents/Social → Boardroom Decisions and promote valuable decisions to canonical status. These will then influence all research.

2. **Generate SharedKnowledge** - Trigger agent learning cycles to populate SharedKnowledge table.

3. **Test End-to-End Flow:**
   - Run a business research with agent context
   - Check logs for "🧠 [Session 351] Injected agent intelligence"
   - Verify research references agent insights

4. **Monitor Integration:**
   ```bash
   # Watch for intelligence injection in logs
   tail -f /var/log/celery/*.log | grep "Session 351"
   ```

---

## Architecture Note

The AgentIntelligenceContextService follows the same pattern as:
- `PolicyContextService` - Injects canonical policies
- `UnifiedIntelligenceSearch` - Combines spider + research data

All three now feed into business research agents, creating a comprehensive intelligence pipeline.

---

**Agent conversations are now connected to research! Promote policies to see them influence outcomes.**
