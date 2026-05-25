# Session 648: Celery Task Scheduling

**Date:** December 31, 2025
**Status:** COMPLETE
**Focus:** Schedule 14 previously unscheduled critical Celery tasks

---

## Summary

Audited all 190 Celery tasks and identified 78 that were defined but never added to Beat schedule. Added schedules for 14 critical recurring tasks.

---

## Task Audit Results

| Category | Count | Action |
|----------|-------|--------|
| Total tasks defined | 190 | - |
| Previously scheduled | 113 | - |
| Now scheduled | 127 | +14 new |
| Manual/event-driven | ~50 | No schedule needed |
| One-time/deprecated | ~13 | Skip |

---

## 14 New Scheduled Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| `collect_spider_data` | Every 4h at :00 | Main spider collection |
| `run_unified_intelligence_pipeline` | Every 6h at :30 | Intelligence aggregation |
| `run_stock_market_intelligence` | M-F 9, 12, 4 PM | Market analysis |
| `run_blockchain_security_monitor` | Every 4h at :15 | On-chain security |
| `run_autonomous_content_studio` | Every 4h at :00 | Content generation |
| `run_narrative_drift_cycle` | Every 6h at :45 | Trend analysis |
| `generate_weekly_intelligence_brief` | Mon 9 AM | Executive summary |
| `unified_pipeline_health_check` | Every 30 min | Health monitoring |
| `track_content_performance` | Daily 8 PM | Content analytics |
| `send_narrative_daily_digest` | Daily 8 AM | Daily narrative |
| `maintain_dream_backlog` | Daily 3 AM | Dream maintenance |
| `cleanup_old_resolve_jobs` | Daily 4 AM | Job cleanup (30 days) |
| `cleanup_expired_uploads` | Daily 4:30 AM | Upload cleanup |
| `aggregate_roi_metrics_daily` | Daily 1 AM | ROI metrics |

---

## Tasks NOT Scheduled (By Design)

These tasks are event-driven or triggered by other tasks:

| Category | Examples | Reason |
|----------|----------|--------|
| Single spider execution | `execute_single_spider*` | Triggered by `collect_spider_data` |
| Processing tasks | `process_*` | Triggered by data arrival |
| Recording tasks | `record_*` | Triggered by user events |
| Async generation | `generate_*_async` | User-initiated |
| Trigger tasks | `trigger_*` | Event-driven |
| One-time setup | `create_default_triggers` | Run manually once |

---

## Files Changed

| File | Change |
|------|--------|
| `core/celery.py` | Added 14 new Beat schedules (lines 1294-1430) |

---

## Schedule Distribution

Tasks are staggered to avoid conflicts:

| Time | Task |
|------|------|
| :00 | `collect_spider_data` (4h), `run_autonomous_content_studio` (4h) |
| :15 | `run_blockchain_security_monitor` (4h) |
| :30 | `run_unified_intelligence_pipeline` (6h), `unified_pipeline_health_check` (30m) |
| :45 | `run_narrative_drift_cycle` (6h) |

Daily tasks (overnight/morning):
- 1 AM: `aggregate_roi_metrics_daily`
- 3 AM: `maintain_dream_backlog`
- 4 AM: `cleanup_old_resolve_jobs`
- 4:30 AM: `cleanup_expired_uploads`
- 8 AM: `send_narrative_daily_digest`
- 8 PM: `track_content_performance`

---

## Verification

```bash
# Count scheduled tasks
grep -c "'task': 'core.tasks" core/celery.py
# Expected: 127

# Verify celery compiles
.venv/bin/python -c "import core.celery; print('OK')"

# Check specific task is scheduled
grep "collect_spider_data" core/celery.py
```

---

## Sessions 647-648 Combined Impact

| Metric | Before | After |
|--------|--------|-------|
| Scheduled tasks | 113 | 127 |
| Orphaned services | 1 (decision_executor) | 0 |
| Discord notifications | - | ThinkingAgent now posts |

---

## Next Session (649)

Focus on **Activating 7 Dead Situations** - autonomous situations that have 0 data.

See `docs/SESSION_ROADMAP_DISCONNECTED_FIXES.md` for details.
