# Session 786: DecisionSummary Generation Fix

**Date:** January 21, 2026
**Focus:** Fix KeyError bug preventing DecisionSummary blocks in new conversations
**Status:** COMPLETE

## Summary

Fixed a critical bug where new conversations were not generating DecisionSummary blocks despite the backfill successfully updating 94.7% of historical conversations. The root cause was a KeyError in `tasks.py` that was failing silently.

## Problem Statement

After running the DecisionSummary backfill command which updated 5,411 of 5,711 conversations (94.7%), the Conversation Contract API was still reporting 0% summary rate. Investigation revealed:

1. The API returns the most recent 100 conversations
2. Recent conversations (created after backfill) were missing DecisionSummary
3. New conversations were not generating DecisionSummary blocks because Celery tasks bypass the `ConversationOrchestrator`

## Root Cause Analysis

The Celery tasks in `core/tasks.py` have their own conversation generation code that doesn't use the `ConversationOrchestrator`. Three code paths create conversations:

1. **Standard Discussion Conversations** (~line 6057)
2. **Multi-Agent Panel Conversations** (~line 6725)
3. **Project Conversations** (~line 7771)

### The Bug

At all three locations, the code to create the synthesis message was failing due to a KeyError:

```python
# BUGGY CODE
final_seq = (messages[-1]['sequence'] if messages else 0) + 1 if messages else 1
```

The `messages` list only contains `agent`, `content`, and `type` keys - NOT a `sequence` key. This caused a KeyError that was caught by exception handlers, preventing the synthesis message from being created.

## Solution

### Fix Applied (Commit 733e5a82)

Changed all three locations to use `len(messages) + 1` instead:

```python
# FIXED CODE
final_seq = len(messages) + 1  # Session 786 fix: use len() since messages dict doesn't have 'sequence' key
```

### Files Modified

1. **core/tasks.py** (3 locations):
   - Line 6145: Standard discussion conversations
   - Line 6831: Multi-agent panel conversations
   - Line 7894: Project conversations

2. **core/views_agent_learning.py** (1 location):
   - Line 5180: Changed message ordering from `-created_at` to `-sequence_number` for consistency with backfill command

## Verification

After the fix was deployed:

```
Conversations with synthesis message type in last hour: 3

14:19:16 | HasDS=True | Discussion: [Learned] Mobihealthnews - Healthtech...
14:18:58 | HasDS=True | Discussion: [Learned] Crunchbase - Startups Intell...
14:13:53 | HasDS=True | Discussion: [Learned] Venturebeat - Startups Intel...
```

API now reports:
- `summary_rate: 5.0%` (up from 0%)
- `valid_summary_rate: 100%` (all summaries that exist are valid)

The rate will continue to improve as more conversations are generated with the fixed code.

## DecisionSummary Format

Each conversation conclusion now includes:

```
=== DecisionSummary ===
Insights:
1. [First key insight from the conversation - be specific]
2. [Second insight about approach or implementation]
3. [Third insight about considerations or trade-offs]

Proposed Feature:
- Name: [Specific feature name that emerged from the discussion]
- Inputs: [What data or content it needs]
- Outputs: [What it produces or enables]
- Where it plugs into the system: [Component: dashboard, API, workflow, agent, etc.]

Next Steps:
1. [Agent1: specific action]
2. [Agent2: specific action]
```

## Backfill Status (Prior Work)

The backfill command was run successfully:
- **Legacy Conversations:** 96.4% coverage (5,230/5,424)
- **HiveMind Sessions:** 63.1% coverage (181/287) - remaining have empty synthesis fields
- **Combined:** 94.7% coverage (5,411/5,711)

## Related Files

- `core/tasks.py` - Main Celery tasks with conversation generation
- `core/views_agent_learning.py` - Conversation Contract API
- `core/conversation_orchestrator.py` - ConversationOrchestrator (used by WebSocket consumer, not Celery)
- `core/management/commands/backfill_decision_summaries.py` - Backfill command

## Testing Commands

```bash
# Check recent conversations for DecisionSummary
.venv/bin/python manage.py shell -c "
from core.models import AgentConversation
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(hours=1)
for conv in AgentConversation.objects.filter(started_at__gte=cutoff, status='concluded')[:10]:
    final_msg = conv.messages.order_by('-sequence_number').first()
    has_ds = '=== DecisionSummary ===' in (final_msg.content if final_msg else '')
    print(f'{conv.started_at.strftime(\"%H:%M:%S\")} | HasDS={has_ds} | {conv.topic[:50]}')
"

# Check API summary rate
curl -s http://localhost:8000/api/conversation-contract/overview/ | python3 -m json.tool | grep summary_rate
```

## Commits

- `733e5a82` - fix(Session 786): Fix KeyError bug preventing DecisionSummary in new conversations

## Next Steps

1. Monitor summary_rate over time - should increase as new conversations are generated
2. Consider running another backfill for any conversations created between the initial backfill and this fix
3. The 106 HiveMind sessions with empty synthesis remain unfilled (they have no content to generate from)
