# Session 796 - Context Preservation Document

**Purpose:** Preserve critical context for Human-AI Assistant connection overhaul.

---

## THE PROBLEM

Human and AI Assistant are disconnected:
- PA chat exists but doesn't surface Human decisions
- Human Page shows decisions but no natural language interaction
- PA doesn't consult human before autonomous actions
- 373 waived gates = system bypassing human entirely

---

## PROGRESS TRACKER

| Phase | Status | PR |
|-------|--------|-----|
| Phase 1: PA Surfaces Decisions | ✅ MERGED | #14 |
| Phase 2: Smart Decisions | ✅ PR CREATED | #15 |
| Phase 3: Consultation Loop | ✅ PR CREATED | #16 |

---

## OPTION A IMPLEMENTATION PLAN

### Goal: Enhance Assistant Page so PA surfaces decisions in chat

### Phase 1: PA Surfaces Pending Decisions ✅ COMPLETE

**Backend Changes:** (PR #14)
- Added `human_decisions_tool` to tool_definitions.py
- Added `_handle_human_decisions_tool()` handler with actions: list, get, decide, stats
- Integrated with HumanInterfaceService for decision recording

**Frontend Changes:** (PR #14)
- Added pending decisions query (30s refresh)
- PA greeting shows pending count
- "Review pending decisions" quick action highlighted
- Pending Decisions sidebar card with urgency emojis

### Phase 2: Chat-Based Decision Making ✅ COMPLETE

**Backend Changes:** (PR #15)
- Added `batch_decide` action - apply decision to multiple items by filter
- Added `auto_execute` action - auto-approve low-risk with ML confidence ≥ 85%
- Added `consult` action - creates consultation item for human approval
- Added parameters: type_filter, confidence_threshold, consultation_context

User can now say:
- "Approve all low priority items" → PA batch approves
- "Auto-execute high confidence decisions" → PA auto-executes
- "Defer all policy decisions" → PA batch defers

### Phase 3: Human Consultation Loop ✅ COMPLETE

**Backend Changes:** (PR #16)
- Added `_check_consultation_response()` - Detects user responses to consultations
  - Pattern matching for affirmative (yes, proceed, go ahead, etc.)
  - Pattern matching for negative (no, stop, cancel, etc.)
  - Pattern matching for info requests (tell me more, explain, etc.)
- Added `_execute_consultation_action()` - Executes approved actions
  - Supports: start_workflow, execute_pilot, process_opportunity
  - Falls back to generic approval acknowledgment
- Integrated into `process_message()` flow
  - Checks for pending consultations before normal processing
  - Returns early if message is a consultation response

**Example Flow:**
```
PA: "I found a podcast opportunity. Should I proceed? [Yes/No/Details]"
User: "yes"
PA: "Great! Proceeding with: podcast opportunity... Action initiated."
```

---

## KEY FILES TO MODIFY

### Backend
| File | Change |
|------|--------|
| `core/agents/personal_assistant_agent.py` | Add decision tools |
| `core/assistant/tool_definitions.py` | Add tool schemas |
| `core/personal_ai_assistant_enhanced.py` | Add human decision methods |
| `core/views_personal_assistant.py` | Add chat-based decision endpoints |

### Frontend
| File | Change |
|------|--------|
| `frontend/src/pages/AssistantPage.tsx` | Add decision cards, proactive greeting |
| `frontend/src/lib/api.ts` | Add decision-via-chat endpoints |

---

## EXISTING CODE PATTERNS

### Current Chat Flow
```
User types → assistantApi.chat(message)
  → POST /v1/assistant/chat/
  → PersonalAIAssistant.process_message(message, context)
  → AgentRouter routes to specialized agent
  → Response returned
```

### Current Decision Flow (Human Page)
```
HumanAttentionItem created → Human Page shows it
User clicks Approve/Reject → POST /api/human/attention/{id}/decide/
HumanInterfaceService.record_decision()
```

### Target Chat-Decision Flow
```
User: "What needs my attention?"
PA: "You have 3 pending items:
     1. 🚨 Arbitrage opportunity (critical)
     2. ⚠️ Policy decision (medium)
     3. ℹ️ Content review (info)"
User: "Approve the arbitrage one"
PA: "Done! Approved the arbitrage opportunity.
     Remaining: 2 items."
```

---

## DATABASE MODELS

### HumanAttentionItem (core/models_human_interface.py)
```python
class HumanAttentionItem(TimeStampedModel):
    user = ForeignKey(User)
    source_type = CharField()  # 'pilot', 'opportunity', 'concern', etc.
    source_id = CharField()
    item_type = CharField()    # 'approval', 'verification', 'review'
    title = CharField()
    summary = TextField()
    urgency = CharField()      # 'critical', 'high', 'medium', 'low'
    priority_score = IntegerField()
    status = CharField()       # 'pending', 'viewed', 'decided', 'deferred'
    decision = CharField()     # 'approve', 'reject', etc.
    payload = JSONField()      # Extra context
```

---

## QUICK COMMANDS

```bash
# Check pending decisions
.venv/bin/python manage.py shell -c "
from core.models_human_interface import HumanAttentionItem
print(f'Pending: {HumanAttentionItem.objects.filter(status=\"pending\").count()}')"

# Test PA chat
curl -X POST http://localhost:8000/api/v1/assistant/chat/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What needs my attention?"}'
```

---

## SUCCESS CRITERIA

- [ ] PA greets user with pending decision count
- [ ] User can say "show pending decisions" and see them in chat
- [ ] User can approve/reject/defer via natural language
- [ ] PA confirms actions and shows remaining items
- [ ] Works on both localhost and Railway production
