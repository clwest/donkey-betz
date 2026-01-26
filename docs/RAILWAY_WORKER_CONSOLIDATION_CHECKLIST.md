# Railway Worker Consolidation Checklist

**Created:** Session 829 - January 25, 2026
**Updated:** Session 830 - January 25, 2026 (added env var verification)
**Goal:** Reduce duplicate Celery workers to save ~40-50% on compute costs
**Risk Level:** Low (if following pause-then-delete approach)

---

## Pre-Flight Checks

- [ ] Log into Railway dashboard: https://railway.app/dashboard
- [ ] Navigate to your project (unified-donkey-betz or similar)
- [ ] Take a screenshot of current services for reference

---

## Step 1: Audit Current Services (15 min)

For each Celery service, record the start command AND key environment variables.

**Use the detailed audit template:** `docs/RAILWAY_WORKER_CONSOLIDATION_AUDIT.md`

### How to find start command:
1. Click on the service
2. Go to **Settings** tab
3. Look under **Deploy** section
4. Find "Start Command" or "Custom Start Command"

### How to find environment variables:
1. Click on the service
2. Go to **Variables** tab
3. Look for these key variables that affect worker behavior:

| Variable | Purpose | Example |
|----------|---------|---------|
| `CELERY_QUEUES` | Override queues from env | `default,agents` |
| `CELERY_CONCURRENCY` | Override concurrency | `4` |
| `CELERY_POOL` | Worker pool type | `threads`, `prefork` |
| `WORKER_QUEUES` | Alternative queue config | `default,agents` |
| `QUEUES` | Alternative queue config | `default,agents` |
| `CONCURRENCY` | Alternative concurrency | `4` |
| `DJANGO_SETTINGS_MODULE` | Settings module | `core.settings` |

### Expected commands (from Procfile):
```
celery-default:      celery -A core worker -l info --pool=threads -c 4 -Q default,agents,sports,content,ml
celery-long-running: celery -A core worker -l info --pool=threads -c 2 -Q long_running
celery-broadcast:    celery -A core worker -l info --pool=threads -c 2 -Q broadcast
celery-beat:         celery -A core beat -l info
```

### Verify from running workers (recommended):
```bash
# SSH into Railway or run locally with prod env vars:
python manage.py celery_inspect_report

# Or manually:
celery -A core inspect active_queues
celery -A core inspect ping
```

---

## Step 2: Identify Duplicates (10 min)

A service is a **confirmed duplicate** if ANY of these are true:

### Duplicate Indicators:
- [ ] **Same queues** as another service (especially `default,agents,sports,content,ml`)
- [ ] **Generic command** like `celery -A core worker -l info` without `-Q` flag
- [ ] **No `-Q` flag** AND no `CELERY_QUEUES` env var (defaults to all queues)
- [ ] **Service name** doesn't match any Procfile entry
- [ ] **Env vars override** to same queues as another service

### Effective Queue Resolution:
The effective queues are determined by this priority:
1. `-Q` flag in start command (highest priority)
2. `CELERY_QUEUES` or `WORKER_QUEUES` env var
3. Default: ALL queues (if neither specified) - **this is likely a duplicate!**

### Likely duplicates based on Session 829 analysis:
- `celery-worker` - probably generic, duplicating celery-default
- `worker-default` - probably generic, duplicating celery-default

### Use the CLI to verify:
```bash
python manage.py celery_inspect_report
# Check docs/ops/celery_inspect_<timestamp>.json for actual queue assignments
```

---

## Step 3: Pause Suspected Duplicates (5 min)

**DO NOT DELETE YET!** Pause first to verify nothing breaks.

For each suspected duplicate:

### Pausing `celery-worker`:
- [ ] Click on `celery-worker` service
- [ ] Go to Settings tab
- [ ] Find "Replicas" or use the three-dot menu
- [ ] Select "Scale to 0" or "Pause deployment"
- [ ] Note the time: ____________

### Pausing `worker-default`:
- [ ] Click on `worker-default` service
- [ ] Go to Settings tab
- [ ] Find "Replicas" or use the three-dot menu
- [ ] Select "Scale to 0" or "Pause deployment"
- [ ] Note the time: ____________

---

## Step 4: Verification Period (24-48 hours)

Monitor these over the next 24-48 hours:

### Day 1 Checks (after 1 hour):
- [ ] Visit https://your-domain/ai-studio/ - site loads
- [ ] Go to Workspace > Integration tab - Celery shows connected
- [ ] Go to Workspace > Governance tab - Self-healing still shows progress
- [ ] Check Railway logs for `celery-default` - tasks are being processed

### Day 1 Checks (after 4 hours):
- [ ] No error emails or alerts received
- [ ] Self-healing remediation tasks still completing
- [ ] No queue backlog visible in logs

### Day 2 Checks:
- [ ] Platform still fully functional
- [ ] Celery Beat scheduled tasks running (check logs)
- [ ] No degraded performance noticed

---

## Step 5: Delete Confirmed Duplicates (5 min)

**Only proceed if Step 4 verification passed!**

### Deleting `celery-worker`:
- [ ] Click on `celery-worker` service
- [ ] Go to Settings tab
- [ ] Scroll to bottom, find "Delete Service"
- [ ] Type the service name to confirm
- [ ] Click Delete

### Deleting `worker-default`:
- [ ] Click on `worker-default` service
- [ ] Go to Settings tab
- [ ] Scroll to bottom, find "Delete Service"
- [ ] Type the service name to confirm
- [ ] Click Delete

---

## Step 6: Post-Consolidation Verification

- [ ] Check billing page - compute costs should decrease
- [ ] Run a test task from the UI (Workspace > Governance > Run Remediation)
- [ ] Verify task completes successfully

---

## Rollback Plan

If something breaks after pausing:

1. Go to the paused service
2. Scale back to 1 replica or "Resume deployment"
3. Wait 2-3 minutes for it to start
4. Verify functionality restored

---

## Final Service Architecture

After consolidation, you should have **7 services**:

| Service | Purpose | Monthly Cost Estimate |
|---------|---------|----------------------|
| Redis | Cache + Celery broker | ~$5-10 |
| Pgvector | PostgreSQL database | ~$10-20 |
| donkey-betz-platform | Daphne web server | ~$10-20 |
| celery-default | Main task worker | ~$10-15 |
| celery-long-running | Long task worker | ~$5-10 |
| celery-broadcast | Broadcast worker | ~$5-10 |
| celery-beat | Task scheduler | ~$5-10 |

**Estimated savings:** ~$15-30/month by removing 2 duplicate workers

---

## Notes

- If you're unsure about a service, DON'T delete it - just pause it
- You can always un-pause a service if needed
- Railway billing is usage-based, so paused services cost nothing
- Keep this checklist updated with your findings

---

**Checklist completed:** ______________________ (date)
**Verified by:** ______________________
