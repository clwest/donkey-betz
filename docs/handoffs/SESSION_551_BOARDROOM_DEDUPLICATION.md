# Session 551: Boardroom Deduplication + Pending Dreams Tracking

**Date:** December 25, 2025
**Commit:** `aecc2f0`
**Status:** COMPLETE

---

## Overview

Session 551 addressed critical issues with the Boardroom Decisions system:
1. Massive duplicate decisions (614 duplicates deleted)
2. Missing tracking for "Dreams Awaiting Decisions"
3. Added prevention to stop future duplicates

---

## Problems Identified

### Problem 1: Duplicate Boardroom Decisions

Agent conversations were creating duplicate decisions for the same topics:

| Topic | Duplicates |
|-------|------------|
| Crunchbase - Startups Intelligence | 75 |
| Securityweek - Cybersecurity Intelligence | 63 |
| Indiehackers - Community Intelligence | 59 |
| Mobihealthnews - Healthtech Intelligence | 55 |
| Venturebeat - Startups Intelligence | 50 |
| + 80 more topics... | |

**Root Cause:** Different agent pairs discussing the same `[Learned]` knowledge created separate decisions. No deduplication check existed.

### Problem 2: Dreams Awaiting Decisions Not Tracked

The ThinkingAgent monitored general dream stats but NOT:
- How many dreams were promoted and pending human decision
- How old the oldest pending dream was
- Whether a backlog was forming

Found: 14 dreams pending, oldest was 19.9 days old!

---

## Solutions Implemented

### 1. Cleanup: Deleted 614 Duplicates

```python
# Before cleanup: 990 decisions
# After cleanup:  376 decisions
# Deleted:        614 duplicates
```

Kept canonical decisions or most recent for each unique topic.

### 2. Prevention: Topic-Based Deduplication

**File:** `core/services/decision_extractor.py`

Added `normalize_topic()` function:
```python
def normalize_topic(topic: str) -> str:
    # Strips [Learned], Discussion:, special chars
    # "Discussion: [Learned] Crunchbase - Startups Intelligence"
    # -> "crunchbase startups intelligence"
```

Added `_has_recent_decision_for_topic()` method:
```python
def _has_recent_decision_for_topic(self, topic: str) -> bool:
    # Checks if similar topic was decided within 24 hours
    # Returns True to skip, False to create
```

Applied to both:
- `create_decision_from_conversation()` (legacy AgentConversation)
- `create_decision_from_hive_session()` (new HiveMindSession)

### 3. Pending Dreams Tracking

**File:** `core/agents/thinking_agent.py`

Added to dream stats context:
```python
context['dream_stats'] = {
    'total': total_dreams,
    'count_24h': dreams_24h,
    'pending_decision': pending_dreams,      # NEW
    'oldest_pending_hours': oldest_hours,    # NEW
    'recent_dreams': [...]
}
```

Added to prompt generation:
```
### Agent Dreams
- Total Dreams: 498
- Dreams (24h): 12
- Dreams Awaiting Decision: 0     # NEW
- Oldest Pending: 0.0 hours       # NEW (if any pending)
```

Added backlog assessment guidance:
```
**IMPORTANT - Dream Backlog Assessment:**
Flag as a concern if:
- More than 10 dreams are pending (decision bottleneck)
- Oldest pending dream is over 48 hours old (stale backlog)
```

### 4. Dream Backlog Concern Category

**File:** `core/services/concern_tracker.py`

```python
CATEGORY_KEYWORDS = {
    # ... existing ...
    # Session 551: Dream backlog category
    'dream': 'dream_backlog',
    'pending dream': 'dream_backlog',
    'awaiting decision': 'dream_backlog',
    'dream backlog': 'dream_backlog',
}

VERIFICATION_METRICS = {
    # ... existing ...
    'dream_backlog': 'pending_dreams_count',  # Session 551
}
```

---

## Celery Schedule Sync

Also synced 80 missing scheduled tasks from `celery.py` to the database scheduler:

```
Before: 62 tasks in database
After:  142 tasks in database
Added:  80 tasks
```

This ensures all autonomous tasks run properly with `DatabaseScheduler`.

---

## Two Boardroom Sections Clarified

| Section | Source | Model |
|---------|--------|-------|
| **Boardroom Decisions** | Agent conversations | `AgentDecisionSummary` |
| **Dreams Awaiting Decisions** | High-scoring promoted dreams | `AgentDream` |

Both are now properly tracked by the ThinkingAgent.

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/thinking_agent.py` | Added `pending_decision`, `oldest_pending_hours` to dream stats; added backlog assessment guidance |
| `core/services/concern_tracker.py` | Added `dream_backlog` category and keywords |
| `core/services/decision_extractor.py` | Added `normalize_topic()`, `_has_recent_decision_for_topic()`, 24h dedup window |

---

## Verification

```python
# Test normalize_topic
normalize_topic("[Learned] Crunchbase - Startups Intelligence")
# -> "crunchbase startups intelligence"

normalize_topic("Discussion: [Learned] Crunchbase - Startups Intelligence")
# -> "crunchbase startups intelligence"

# Both normalize to same value = deduplication works!
```

Log output when duplicate is skipped:
```
INFO Session 551: Skipping duplicate decision for topic 'Discussion: [Learned] Crunchbase...' - similar decision exists within 24h
```

---

## Current State After Cleanup

| Metric | Value |
|--------|-------|
| Boardroom Decisions | 376 (was 990) |
| Pending Dreams | 0 (cleared by user) |
| Approved Dreams | 9 |
| Deferred Dreams | 3 |
| Rejected Dreams | 8 |
| Scheduled Tasks | 142 (was 62) |

---

## Session 552 Priorities

1. **Monitor deduplication** - Verify no new duplicates appear overnight
2. **ThinkingAgent insights** - Check that dream backlog is reported correctly
3. **Continue Boardroom review** - User may want to review the 376 remaining decisions

---

## Key Insight

The Boardroom was being flooded because:
1. Spiders collect data → stored as `[Learned]` knowledge
2. Multiple agent pairs discuss the same knowledge
3. Each conversation created a new decision
4. No deduplication = 75 decisions for one topic!

Now with 24-hour topic-based deduplication, only the first conversation creates a decision. Subsequent conversations on the same topic within 24 hours are skipped.
