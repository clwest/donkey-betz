# Session 897 - Experiment Pipeline Fix

**Date:** February 1, 2026
**Focus:** Fixed stuck experiment pipeline - 604 experiments cleared
**PRs:** #660, #661, #662, #663

---

## Problem

ThinkingAgent reported 68.3% of experiments stuck in "running" status:
- **604 experiments** in "running" status (out of 884)
- **511 experiments** running for >24 hours
- Oldest experiment: **167+ hours** old (almost 7 days!)

---

## Root Cause Analysis

Used enhanced diagnostics (`check_experiment_status`) to discover:

```
=== Pilot Pipeline Blockers ===
  Pilots with NULL started_at: 875
  Running pilots by outcome:
    pending: 875
  Eligible for evaluation (>1h, pending): 0
```

**Root Cause:** All 875 running pilots had `started_at = NULL`

The `evaluate_and_complete_pilots` task filters on:
```python
eligible_pilots = PilotExecution.objects.filter(
    status='running',
    started_at__lte=cutoff,  # <-- This filter matched NOTHING!
    outcome='pending'
)
```

Since `started_at` was NULL, no pilots passed the filter, and the pipeline was completely blocked.

---

## Solution

Created `fix_pilot_started_at` management command to backfill `started_at`:

```bash
# Dry run (preview)
python manage.py fix_pilot_started_at --dry-run

# Apply fix
python manage.py fix_pilot_started_at
```

The command backfills `started_at` from:
1. Linked experiment's `started_at` (preferred)
2. Pilot's `created_at` timestamp (fallback)

---

## Results

**Before Fix:**
| Metric | Value |
|--------|-------|
| Running experiments | 604 (68.3%) |
| Running pilots | 875 |
| Pilots with NULL started_at | 875 |
| Eligible for evaluation | 0 |
| Stuck >24h | 511 |

**After Fix:**
| Metric | Value |
|--------|-------|
| Running experiments | 0 |
| Running pilots | 0 |
| Pilots with NULL started_at | 0 |
| Successful experiments | 820 |
| Partial experiments | 91 |
| Learnings created | 658 |

---

## Commands Added

| Command | Purpose |
|---------|---------|
| `check_experiment_status` | Diagnose experiment/pilot pipeline issues |
| `fix_pilot_started_at` | Backfill NULL started_at values |
| `trigger_pilot_evaluation` | Manually trigger evaluation task |

---

## Prevention

The root cause was pilots being created without `started_at` being set. To prevent recurrence:

1. The pilot creation code should always set `started_at = timezone.now()` when status is set to 'running'
2. Celery Beat runs `evaluate_and_complete_pilots` every 2 hours to process eligible pilots
3. New diagnostic command can detect issues early

---

## Files Changed

| File | Changes |
|------|---------|
| `core/management/commands/check_experiment_status.py` | Added pipeline blocker diagnostics |
| `core/management/commands/fix_pilot_started_at.py` | New - backfill started_at |
| `core/management/commands/trigger_pilot_evaluation.py` | New - manual task trigger |

---

## Verification Commands

```bash
# Check current status
railway ssh -s donkey-betz-platform python manage.py check_experiment_status

# Fix any new NULL started_at (if needed)
railway ssh -s donkey-betz-platform python manage.py fix_pilot_started_at

# Trigger evaluation manually
railway ssh -s donkey-betz-platform python manage.py trigger_pilot_evaluation
```
