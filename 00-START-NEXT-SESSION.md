# Session 898 - Start Here

**Previous Session:** 897 (Experiment Pipeline Fix)
**Date:** February 1, 2026
**Status:** 76 Agents | 77 Spiders | 25 Advisors | 139 Personas | **EXPERIMENT PIPELINE: CLEARED** | **820 SUCCESSFUL EXPERIMENTS**

---

## What Was Accomplished in Session 897

### Experiment Pipeline Fix - 604 Running → 0

Fixed the completely stuck experiment pipeline that had 68.3% of experiments in "running" status.

**Root Cause:** All 875 running pilots had `started_at = NULL`, making them invisible to the evaluation task's filter.

**Solution:** Created `fix_pilot_started_at` command to backfill started_at values.

**Results:**
| Metric | Before | After |
|--------|--------|-------|
| Running experiments | 604 | **0** |
| Running pilots | 875 | **0** |
| Stuck >24h | 511 | **0** |
| Successful experiments | 33 | **820** |
| Learnings created | - | **658** |

**PRs:** #660, #661, #662, #663 | **Handoff:** `SESSION_897_EXPERIMENT_PIPELINE_FIX.md`

---

## New Management Commands

| Command | Purpose |
|---------|---------|
| `check_experiment_status` | Diagnose experiment/pilot pipeline issues |
| `fix_pilot_started_at` | Backfill NULL started_at values |
| `trigger_pilot_evaluation` | Manually trigger evaluation task |

---

## Current Celery Architecture

```
celery-worker: -Q default,agents,sports,ml (4 concurrency)
celery-content: -Q content (4 concurrency)        # Workspace writing tasks
celery-long-running: -Q long_running (2 concurrency)
celery-beat: scheduler
celery-broadcast: -Q broadcast (2 concurrency)
```

---

## TOP PRIORITY for Session 898

### 1. Monitor New Experiment Creation
Verify that newly created pilots get `started_at` populated:
```bash
railway ssh -s donkey-betz-platform python manage.py check_experiment_status
```

### 2. Check CodeGeneratorAgent Tasks
Verify agents are producing real code (Session 896 codebase workspace fix):
```bash
railway ssh -s donkey-betz-platform python manage.py shell -c "
from core.models import AgentExecution
for e in AgentExecution.objects.filter(agent_name='CodeGeneratorAgent').order_by('-created_at')[:5]:
    print(f'{e.status}: {e.task[:50]}...')
"
```

---

## Quick Commands

```bash
# Start platform
make start && make celery

# Check experiment status on production
railway ssh -s donkey-betz-platform python manage.py check_experiment_status

# Fix any NULL started_at (if needed)
railway ssh -s donkey-betz-platform python manage.py fix_pilot_started_at

# Trigger pilot evaluation manually
railway ssh -s donkey-betz-platform python manage.py trigger_pilot_evaluation
```

---

## Recent PRs

| PR | Description |
|----|-------------|
| #663 | Add trigger_pilot_evaluation command |
| #662 | Fix pilots with NULL started_at (root cause) |
| #661 | Enhanced experiment pipeline diagnostics |
| #660 | Add experiment status diagnostic command |
| #658 | PDF Export - Download initiative documents as professional PDFs |
| #657 | Codebase Workspace Fix - CodeGeneratorAgent can access real code |

---

## Recent Session History

| Session | Focus | Handoff |
|---------|-------|---------|
| **897** | Experiment Pipeline Fix - 604 stuck experiments → 0 | `SESSION_897_EXPERIMENT_PIPELINE_FIX.md` |
| **896** | Codebase Workspace Fix + PDF Export for Initiative Documents | `SESSION_896_CODEBASE_WORKSPACE_FIX.md` |
| **895** | Coordinator Timeout Protection (8 coordinators, 2-tier timeout) | `SESSION_895_COORDINATOR_TIMEOUT_PROTECTION.md` |
| **894** | Voice Mode for AI Assistant (Whisper + ElevenLabs) | Previous START file |
| **893** | 4 Bug Fixes: Deliverables, Intel 401, Social Modal, Workspace Context | `SESSION_893_*.md` |

---

## System Stats

| Component | Count |
|-----------|-------|
| Agents | 76 |
| Spiders | 77 |
| Advisors | 25 |
| Personas | 139 |
| Database Models | 379+ |
| Celery Tasks | 281 |
| Services | 128 |
| Experiments (Success) | 820 |
| Experiments (Partial) | 91 |
| Learnings | 658+ |

---

## Workspace Architecture

| Workspace | Path | Purpose |
|-----------|------|---------|
| `donkey-betz-codebase` | `/app` (production) | CodeGeneratorAgent access to source code |
| `System Autonomous Workspace` | `/app/workspace` | Generated content storage |
| `{username}-personal` | `/generated_content/users/{username}` | Per-user generated files |

---

**Experiment pipeline is now healthy - 820 successful experiments!**
