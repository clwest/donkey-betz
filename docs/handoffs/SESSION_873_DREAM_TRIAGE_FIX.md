---
originating_session: 873
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 873 - Dream Triage Emergency Fix

**Date:** January 29, 2026
**Previous Session:** 872 (API Fixes + Celery Sync + ChatGPT Feedback Implementation)
**Status:** COMPLETE

---

## Problem Identified

ThinkingAgent system insights report revealed the actual dream backlog is far worse than initially reported:

| Metric | Reported | Actual |
|--------|----------|--------|
| **Pending Dreams** | 538 | **2,130** |
| **Oldest Pending** | 72.3 hours | **62 days (1,493 hours)** |
| **Gate Waiver Rate** | N/A | **79.4%** |

---

## Root Cause

The `dream-auto-triage` Celery Beat task was configured with insufficient capacity:

```python
# BEFORE (insufficient)
'dream-auto-triage': {
    'schedule': crontab(hour='*/4', minute=30),  # Every 4 hours
    'max_promote': 20,   # Default
    'max_archive': 50,   # Default
    'archive_age_days': 7,  # Default
}
# Rate: ~70 dreams cleared per 4 hours = 420/day
```

With 2,130 pending dreams, this would take **5+ days** to clear.

---

## Solution Implemented

**PR #536:** `fix(Session 873): Increase dream triage frequency and capacity`

```python
# AFTER (aggressive)
'dream-auto-triage': {
    'schedule': crontab(minute=30),  # Every hour (6x increase)
    'kwargs': {
        'max_promote': 200,    # 10x increase
        'max_archive': 500,    # 10x increase
        'archive_age_days': 3, # More aggressive (was 7)
    }
}
# Rate: ~700 dreams/hour = 4,200/day
```

**Expected:** Clear 2,130 dream backlog in ~12 hours.

---

## Files Changed

| File | Change |
|------|--------|
| `core/celery.py` | Updated `dream-auto-triage` schedule and kwargs |

---

## Session 872 Recap (Context)

Session 872 implemented "Executive Function" improvements based on ChatGPT feedback:

1. **DecisionEnforcerAgent** (PR #531) - "Prefrontal Cortex" that forces decisions
2. **SynthesisContract** (PR #532) - Structured debate outputs with binary categorization
3. **AutoSpawnerService** (PR #533) - Data insufficiency reflexes
4. **Prompt Sharpening** (PR #534) - Transform hedging to decisive language

---

## Session 873 PRs

| PR | Title |
|----|-------|
| #536 | fix(Session 873): Increase dream triage frequency and capacity |

---

## Monitoring

After deploy, verify dream backlog is clearing:

```bash
# Check dream stats
curl https://donkey-betz-platform-production.up.railway.app/api/mythology/dreams/stats/

# Watch Celery logs for triage activity
# Look for: "[DREAM-TRIAGE] Promoted:" and "[DREAM-TRIAGE] Archived:"
```

---

## Next Steps (Optional)

1. **Monitor backlog clearance** - Should see ~700 dreams/hour being processed
2. **Address 79.4% gate waiver rate** - Investigate why so many gates are being waived
3. **Integrate Executive Function components** - Wire DecisionEnforcerAgent into conversation_orchestrator
4. **Apply prompt sharpening** - Add SHARP_DEBATE_RULES to agent system prompts
