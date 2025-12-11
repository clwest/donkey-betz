# Session 413: Agent Conversation Fix + Reasoning Model Timeouts

**Date:** December 10, 2025
**Status:** Complete

---

## Issues Fixed

### 1. Agent Conversation Duplicate Replies Bug

**Problem:** Conversations showed the same agent replying multiple times in a row (e.g., CreativeDirectorAgent starts, then ImageAgent replies 3x consecutively).

**Root Cause:** In `core/tasks.py:3919-3928`, when an agent returned empty content:
1. Code swapped speakers AND called `continue`
2. At end of successful message, code also swapped speakers
3. This double-swap corrupted the turn order

**Fix:** Removed the swap on empty response. Now if an agent returns empty, we just `continue` to the next iteration where the SAME speaker retries with a different diversity prompt. The swap only happens after successful messages.

**File:** `core/tasks.py:3918-3934`

### 2. GPT-5 Reasoning Model Timeouts

**Problem:** GPT-5-mini is a reasoning model that needs extra time for internal "thinking" before producing output. Without explicit timeouts, calls could hang.

**Fix:** Added explicit timeouts to all agent conversation GPT calls:

| Location | Timeout | Token Limit |
|----------|---------|-------------|
| Conversation messages | 120s | 1000 |
| Conversation conclusion | 90s | 600 |
| Multi-agent panel messages | 120s | 2000 |
| Dream generation | 120s | 1000 |
| Dream title generation | 60s | 500 |

---

## Database Recovery

Also performed database restore from Dec 7 backup after discovering data loss:
- Restored 1,725 conversations (was 671)
- Restored 1,851 dreams (was 793)
- Restored 11,735 spider data (was 10,600)
- Restored 50 shared knowledge (was 0)
- Ran migrations for Sessions 403-410 (Legal Assistant)

Created daily backup script: `scripts/daily_backup.sh`

---

## Files Changed

| File | Change |
|------|--------|
| `core/tasks.py` | Fixed empty response handling, added timeouts |
| `scripts/daily_backup.sh` | NEW - Daily backup script |

---

## Conversation Settings

Sweet spot for 2-agent conversations: **6 messages** (3 turns each)
- Substantive exchange without being too long
- Cost-effective (6 GPT calls per conversation)
- Enough depth for insights

Multi-agent panels: **12 messages** (4 agents × 3 rounds)

---

## Next Priorities

1. Test Legal Assistant with denied motion (ensure document context flows correctly)
2. Add PA keywords for system features (spiders, conversations, boardroom)
3. Monitor conversation quality after fix
