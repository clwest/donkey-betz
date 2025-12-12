# Session 429: Discord Conversation Notifications + Cost Optimization

**Date:** December 12, 2025
**Status:** COMPLETE

---

## Summary

Investigated OpenAI credit consumption and discovered agent conversations and multi-agent panels were consuming significant API credits without posting to Discord. Added Discord notifications to both tasks and reduced their frequencies to save costs.

---

## Problem Identified

User noticed $3 in OpenAI charges but only dreams were appearing in Discord for 12+ hours.

### Investigation Results

| Task | Old Frequency | API Calls/Run | Daily Runs | Daily Calls |
|------|---------------|---------------|------------|-------------|
| `run_agent_conversation` | Every 5 min | 6-8+ | 288 | ~2,300 |
| `run_multi_agent_conversation` | Every 20 min | 12+ | 72 | ~860 |
| **Total** | - | - | 360 | **~3,160** |

**Root Cause:** Both tasks were saving to database and broadcasting via WebSocket/Redis, but never posting to Discord. Only `generate_agent_dreams` had Discord integration.

---

## Changes Made

### 1. Added Discord Notifications

**File:** `core/tasks.py`

#### run_agent_conversation (line 4392)
```python
# Session 429: Send Discord notification for completed conversation
try:
    from core.services.discord_notifications import discord_notify
    discord_notify.send_conversation(
        participants=[initiator.name, responder.name],
        topic=topic,
        synthesis=conclusion,
        mode=template['type'].replace('_', ' ')
    )
except Exception as discord_err:
    logger.debug(f"Discord notification failed: {discord_err}")
```

#### run_multi_agent_conversation (line 4951)
```python
# Session 429: Send Discord notification for multi-agent panel
try:
    from core.services.discord_notifications import discord_notify
    discord_notify.send_conversation(
        participants=[a.name for a in panel_agents],
        topic=topic,
        synthesis=conclusion,
        mode=template['type'].replace('_', ' ')
    )
except Exception as discord_err:
    logger.debug(f"Discord notification failed: {discord_err}")
```

### 2. Reduced Task Frequencies

**File:** `core/celery.py`

| Task | Before | After | Change |
|------|--------|-------|--------|
| `agent-conversation-cycle` | `*/5` (every 5 min) | `*/30` (every 30 min) | 6x reduction |
| `multi-agent-panel-cycle` | `*/20` (every 20 min) | `minute=0` (hourly) | 3x reduction |

```python
# Session 429: Reduced from 5 to 30 min to save OpenAI credits (DB already populated)
'agent-conversation-cycle': {
    'task': 'core.tasks.run_agent_conversation',
    'schedule': crontab(minute='*/30'),  # Every 30 minutes (was 5 min before Session 429)
    'options': {
        'expires': 1800,  # 30 minutes
    }
},

# Session 429: Reduced from 20 to 60 min to save OpenAI credits
'multi-agent-panel-cycle': {
    'task': 'core.tasks.run_multi_agent_conversation',
    'schedule': crontab(minute=0),  # Every hour at :00 (was every 20 min before Session 429)
    'options': {
        'expires': 3600,  # 60 minutes
    },
    ...
},
```

---

## Cost Savings

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Conversation runs/day | 288 | 48 | 83% |
| Panel runs/day | 72 | 24 | 67% |
| Est. API calls/day | ~3,160 | ~580 | **82%** |

---

## Discord Channel Usage

Agent conversations now post to **#agent-conversations** (Channel ID: 1448809914783895583)

The `send_conversation()` method creates a pink embed with:
- Topic as title
- Synthesis/conclusion as description
- Participant list
- Conversation mode (brainstorm, debate, critical review, etc.)

---

## Technical Notes

### Why Reduce Frequency?

The original high frequency (every 5 minutes) was designed to quickly populate the database with agent conversations and establish learning patterns. Now that the database has:
- 117+ HiveMind sessions
- 2,080+ dreams
- 940+ knowledge sources

...the aggressive frequency is no longer needed. Agents can continue learning at a more sustainable pace.

### Celery Beat Restart Required

After deploying these changes, restart Celery Beat to pick up the new schedule:

```bash
# Stop existing Celery processes
pkill -f celery

# Restart
make celery
```

---

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | Added Discord notifications to `run_agent_conversation` and `run_multi_agent_conversation` |
| `core/celery.py` | Reduced frequencies: conversations 5->30 min, panels 20->60 min |
| `00-START-NEXT-SESSION.md` | Updated for Session 429 |

---

## OpenAI Tasks Summary (for future reference)

Tasks that use OpenAI API (found via grep for `openai.OpenAI`):

| Task | Frequency | Posts to Discord? |
|------|-----------|-------------------|
| `run_agent_conversation` | Every 30 min | YES (Session 429) |
| `run_multi_agent_conversation` | Every 60 min | YES (Session 429) |
| `generate_agent_dreams` | Every 15 min | YES |
| `trigger_conversations_from_spider_data` | Internal | No |
| `propagate_policy_to_agents` | On demand | No |
| `agent_think_and_synthesize` | Every 30 min | No (WebSocket only) |
| `run_agent_learning_cycle` | Every 10 min | No (WebSocket only) |

---

## Next Session: 430

**Focus: Discord Workflow Triggers**
- Add `/workflow` command to trigger multi-step workflows
- `/brand <company>` - Run full brand research workflow
- `/content <topic>` - Generate content package
- Consider reaction-based approvals for workflow steps

---

**Session 429 COMPLETE - Agent conversations now post to Discord with 82% cost reduction!**
