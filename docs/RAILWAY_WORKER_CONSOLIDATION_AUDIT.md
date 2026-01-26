# Railway Worker Consolidation Audit

**Session:** 830
**Date:** ____________________
**Auditor:** ____________________

---

## Instructions

Fill out this table by inspecting each service in the Railway dashboard:

1. **Start Command**: Settings > Deploy > Start Command
2. **Replicas**: Settings > Deploy > Replicas (or Scaling section)
3. **Key Env Vars**: Variables tab - look for CELERY_*, WORKER_*, QUEUES, CONCURRENCY
4. **Effective Queues**: Derived from -Q flag OR env var OR "ALL (default)"
5. **Concurrency**: From -c flag OR env var OR default (usually CPU count)
6. **Duplicate?**: YES if queues overlap with another service
7. **Action**: KEEP / PAUSE / DELETE

---

## Service Audit Table

| Service | Start Command | Replicas | Key Env Vars | Effective Queues | Concurrency | Duplicate? | Action |
|---------|---------------|----------|--------------|------------------|-------------|------------|--------|
| celery-default | | | | | | NO | KEEP |
| celery-long-running | | | | | | NO | KEEP |
| celery-broadcast | | | | | | NO | KEEP |
| celery-beat | | | | | | NO | KEEP |
| celery-worker | | | | | | ? | CHECK |
| worker-default | | | | | | ? | CHECK |

---

## Expected Values (from Procfile)

| Service | Expected Start Command | Expected Queues | Expected Concurrency |
|---------|------------------------|-----------------|---------------------|
| celery-default | `celery -A core worker -l info --pool=threads -c 4 -Q default,agents,sports,content,ml` | default,agents,sports,content,ml | 4 |
| celery-long-running | `celery -A core worker -l info --pool=threads -c 2 -Q long_running` | long_running | 2 |
| celery-broadcast | `celery -A core worker -l info --pool=threads -c 2 -Q broadcast` | broadcast | 2 |
| celery-beat | `celery -A core beat -l info` | N/A (scheduler) | N/A |

---

## Environment Variables to Check

For each service, check if these env vars exist (they can override command-line flags):

| Variable | Found In | Value |
|----------|----------|-------|
| `CELERY_QUEUES` | | |
| `CELERY_CONCURRENCY` | | |
| `CELERY_POOL` | | |
| `WORKER_QUEUES` | | |
| `QUEUES` | | |
| `CONCURRENCY` | | |
| `DJANGO_SETTINGS_MODULE` | | |
| `REDIS_URL` | | |
| `DATABASE_URL` | | |

---

## Duplicate Analysis

### celery-worker
- **Start Command matches**: [ ] celery-default / [ ] celery-long-running / [ ] celery-broadcast / [ ] None
- **Queues overlap with**: ____________________
- **Verdict**: [ ] DUPLICATE - Safe to pause/delete / [ ] UNIQUE - Keep

### worker-default
- **Start Command matches**: [ ] celery-default / [ ] celery-long-running / [ ] celery-broadcast / [ ] None
- **Queues overlap with**: ____________________
- **Verdict**: [ ] DUPLICATE - Safe to pause/delete / [ ] UNIQUE - Keep

---

## CLI Verification (Optional but Recommended)

Run this command to verify active queues from running workers:

```bash
python manage.py celery_inspect_report
```

Results file: `docs/ops/celery_inspect_<timestamp>.json`

### CLI Output Summary:
```
(paste output here)
```

---

## Decision Summary

| Service | Decision | Reason | Date Actioned |
|---------|----------|--------|---------------|
| celery-worker | | | |
| worker-default | | | |

---

## Rollback Notes

If issues occur after pausing/deleting:

1. **Which service was affected?** ____________________
2. **What broke?** ____________________
3. **Rollback action taken:** ____________________
4. **Time to recovery:** ____________________

---

**Audit completed:** ______________________ (date/time)
**Signed off by:** ______________________
