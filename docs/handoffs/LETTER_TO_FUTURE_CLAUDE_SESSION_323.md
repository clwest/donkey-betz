---
originating_session: 324
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Letter to Future Claude: Session 323 - Boardroom Decisions Implementation

**From:** Claude (Session 322)
**To:** Claude (Session 323+)
**Date:** December 2, 2025
**Subject:** Implementing the Boardroom Decisions System

---

## Dear Future Claude,

I've just completed Session 322 where we fixed the Live Agent Learning Activity and created a comprehensive blueprint for the next major feature: **Boardroom Decisions**. This letter will help you hit the ground running.

---

## What Just Happened (Session 322)

### Fixes Applied
1. **Live Agent Learning Activity UI** - There were two `updateLearningFeed` functions in the JavaScript that were conflicting. Removed the duplicate and switched to API-based loading.

2. **Learning Cycle Duplicate Detection** - The learning cycle was making 0 transfers because it was matching knowledge by just the first word of titles (e.g., "Session"). Changed to 30-character prefix matching. After the fix, 7 transfers happened immediately.

### Current State
- All Social tab components are now working
- Agent Learning, Dreams, Conversations, Slack - all operational
- The system is stable and ready for new features

---

## Your Mission: Implement Boardroom Decisions

The user wants to capture valuable insights from agent conversations and turn them into actionable policies. I've created a detailed blueprint at:

**`docs/handoffs/SESSION_322_BOARDROOM_DECISIONS_BLUEPRINT.md`**

Read this file first - it has everything: models, services, APIs, UI components, and testing checklists.

---

## Recommended Implementation Order

### Phase 1: Data Model + Extraction (Do This First)

1. **Create the model** in `core/models_unified_system.py`:
   - `AgentDecisionSummary` - stores structured decisions
   - Fields: topic, decision_type, impact_area, key_insights, recommended_stance, is_canonical, etc.

2. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create the extractor service** at `core/services/decision_extractor.py`:
   - Uses GPT to parse conversation conclusions into structured decisions
   - The prompt is in the blueprint

4. **Hook into conversation conclude** in `core/tasks.py`:
   - Find where conversations are marked as `concluded`
   - Add a call to extract and save the decision

5. **Test with existing data**:
   ```bash
   python manage.py shell
   >>> from core.models import AgentConversation
   >>> conv = AgentConversation.objects.filter(status='concluded', conclusion__isnull=False).first()
   >>> from core.services.decision_extractor import get_decision_extractor
   >>> extractor = get_decision_extractor()
   >>> decision = extractor.create_decision_from_conversation(conv)
   >>> print(decision)
   ```

### Phase 2: API + UI

1. **Add API endpoints** to `core/views_agent_learning.py`:
   - `GET /api/boardroom/decisions/` - list decisions
   - `POST /api/boardroom/decisions/{id}/promote/` - promote to canonical
   - `POST /api/boardroom/decisions/{id}/reject/` - reject

2. **Add URL routes** to `core/urls.py`

3. **Add UI component** to `ai_core/templates/ai_image_studio.html`:
   - Goes in the Social tab after Agent Dreams
   - Gold/amber color scheme (#f59e0b)
   - Cards showing decisions with Promote/Reject buttons

4. **Add JavaScript** for loading and actions

### Phase 3: Policy Feedback Loop (Advanced)

1. **Create policy context service** at `core/services/policy_context.py`
2. **Inject canonical policies into agent prompts**
3. **Test that agents reference policies in responses**

---

## Key Files to Reference

| File | Purpose |
|------|---------|
| `docs/handoffs/SESSION_322_BOARDROOM_DECISIONS_BLUEPRINT.md` | **THE BLUEPRINT - READ THIS** |
| `core/models_unified_system.py` | Where to add the new model |
| `core/tasks.py` | Find `run_agent_conversation` for hook point |
| `core/views_agent_learning.py` | Add API endpoints here |
| `ai_core/templates/ai_image_studio.html` | Add UI here (after line ~7700 in Social tab) |

---

## Quick Commands

```bash
# Start the platform
make start && make celery

# Check current state
curl -s http://localhost:8000/api/agent-learning/activity/ | python3 -m json.tool | head -20

# Test a conversation has conclusions
python manage.py shell -c "
from core.models import AgentConversation
convs = AgentConversation.objects.filter(status='concluded', conclusion__isnull=False)[:3]
for c in convs:
    print(f'{c.topic[:50]}...')
    print(f'  Conclusion: {c.conclusion[:100]}...')
    print()
"
```

---

## Potential Gotchas

1. **GPT model for extraction**: Use `gpt-4o-mini` for cost efficiency. The extraction prompt is simple.

2. **JSON response format**: Use `response_format={"type": "json_object"}` to ensure valid JSON from GPT.

3. **Empty conclusions**: Some conversations may have empty or None conclusions. Skip these.

4. **Foreign key to conversation**: Make sure the `AgentConversation` import is correct in the model.

5. **CSRF tokens**: The promote/reject buttons need CSRF tokens. There's a pattern in the existing code.

---

## What Success Looks Like

After Phase 1:
- New `AgentDecisionSummary` records are created when conversations conclude
- You can query them: `AgentDecisionSummary.objects.all()`

After Phase 2:
- Boardroom Decisions panel visible in Social tab
- Gold cards showing decisions with insights
- Promote button makes `is_canonical=True`
- Badge shows count of canonical policies

After Phase 3:
- Agent prompts include canonical policies
- Agents reference policies in their responses
- The system becomes self-governing!

---

## The User's Vision

The user (working with ChatGPT analysis) identified that agent conversations are generating real governance value:
- **Prompt Engineering Policy** from BookmakerAgent + CTOAgent
- **Memory Isolation Architecture** from MemoryIsolationAgent + CreationAgent
- **Image Pipeline Spec** from ImageEditingAgent + CreativeDirectorAgent

The goal is to capture these insights, let the human promote them to "canonical policies", and then feed them back into agent behavior. This closes the loop on agent intelligence.

---

## Final Notes

The user is excited about this feature. They called the ChatGPT analysis "god-tier" and want to implement it properly. Take your time with Phase 1 to get the foundation right.

The blueprint has complete code samples - you can largely copy-paste and adapt. Test each piece before moving on.

Good luck! This is going to be a great addition to the platform.

Warm regards,
Claude (Session 322)

---

**P.S.** The Social tab is finally working perfectly after sessions 320-322 of fixes. Don't break it! 😄
