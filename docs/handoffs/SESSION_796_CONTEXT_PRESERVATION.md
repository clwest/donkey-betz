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

## OPTION A IMPLEMENTATION PLAN

### Goal: Enhance Assistant Page so PA surfaces decisions in chat

### Phase 1: PA Surfaces Pending Decisions

**Backend Changes:**
1. Add `get_pending_human_items()` to PersonalAIAssistant that fetches HumanAttentionItems
2. Add PA tool `review_pending_decisions` that returns pending items formatted for chat
3. Add PA tool `handle_decision` that interprets "approve", "reject", "defer" commands

**Frontend Changes:**
1. On load, PA proactively shows pending decisions count
2. Add quick action "Review pending decisions"
3. Decision cards can be clicked to act via chat

### Phase 2: Chat-Based Decision Making

User can say:
- "Approve the first one" → PA calls `handle_decision(item_id, 'approve')`
- "Tell me more about the arbitrage opportunity" → PA provides details
- "Defer all policy decisions" → PA batch defers

### Phase 3: Human Consultation Loop

Before significant actions, PA asks:
- "I found a podcast opportunity. Should I start the workflow? [Yes/No/Details]"
- User responds in natural language
- PA interprets and acts

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
