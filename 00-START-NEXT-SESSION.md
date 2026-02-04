# Session 923 - Start Here

**Previous Session:** 922 (Stage Generation Bug Fix)
**Date:** February 3, 2026
**Status:** 76 Agents | 77 Spiders | 25 Advisors | 139 Personas | **315 INITIATIVES** | **PIPELINE HEALTH: RECOVERING** | **565 Transition Logs**

---

## Session 922 Complete: Fixed Critical Stage Generation Bug

Found and fixed the ROOT CAUSE of why 192 initiatives were stuck at Stage 1 DRAFT with no documents.

### Root Cause Discovered

The `generate_initiative_stage_document` Celery task was calling `router.execute_agent()` which **doesn't exist** on `AgentRouter`. This caused all Stage 1 document generations to fail silently.

### What Was Fixed

| Fix | File | Description |
|-----|------|-------------|
| Stage Gen Method | `core/tasks.py` | Changed `router.execute_agent()` to `router.route()` |
| Parameter Name | `core/tasks.py` | Changed `query=prompt` to `task=prompt` |
| Result Access | `core/tasks.py` | Changed `result.get('response')` to `result.message` |
| Backfill Endpoint | `views_initiative_kickstart.py` | Added `/api/initiatives/trigger-backfill/` endpoint |

**PRs:** #811 (Backfill Endpoint), #812 (Stage Gen Fix)

### Backfill Results

| Metric | Before | After |
|--------|--------|-------|
| Stage 1 WITH documents | 8 | 58 |
| Stage 1 WITHOUT docs | 192 | 257 |
| Document coverage | 4% | 18% |

### How to Continue Backfill

```bash
# Dry run - see what would be triggered
railway run python manage.py shell -c "
from core.models_document_registry import InitiativeStage
count = InitiativeStage.objects.filter(
    stage=1, document__isnull=True, initiative__status='ACTIVE'
).count()
print(f'{count} initiatives need Stage 1 documents')
"

# Run backfill batch (processes ~50% success rate due to malformed names)
railway run python manage.py backfill_stage_documents --stage=1 --limit=30
```

---

## Current Production State

| Metric | Value |
|--------|-------|
| Total Initiatives | 315 |
| Stage 1 with documents | 58 (18%) |
| Stage 1 without docs | 257 (need backfill) |
| Transition Logs | 565+ |

---

## NEXT PRIORITIES for Session 923+

### 1. Continue Stage 1 Backfill
~257 initiatives still need Stage 1 documents. Run more batches:
```bash
railway run python manage.py backfill_stage_documents --stage=1 --limit=50
```

### 2. Fix Malformed Initiative Names
Many initiatives have truncated/garbage names that cause agent failures:
- "Back Engine:"
- "Agent Discussion Outputs and Generates Priori..."
- Names ending in "..."

### 3. Integrate Dedupe into Pipeline (from 920)
```python
from core.services.deduplication_service import get_deduplication_service
dedup = get_deduplication_service()
clean_text, _ = dedup.dedupe_decision_summary_blocks(raw_output)
```

### 4. Monitor Pipeline Health
Check the Health tab to verify transitions are increasing as documents are generated.

---

## Recent Session History

| Session | Focus | Handoff |
|---------|-------|---------|
| **922** | Stage Generation Bug Fix | `docs/handoffs/SESSION_922_STAGE_GEN_FIX.md` |
| 921 | Pipeline Health Monitoring | `docs/handoffs/SESSION_921_PIPELINE_HEALTH_MONITORING.md` |
| 920 | Panel/Advisor System Improvements | `docs/handoffs/SESSION_920_PANEL_ADVISOR_IMPROVEMENTS.md` |
| 918 | Report Provenance + PDF Export | `docs/handoffs/SESSION_918_REPORT_PROVENANCE.md` |
| 916 | Hard Invariants - StageTransitionLog | `docs/handoffs/SESSION_916_HARD_INVARIANTS.md` |

---

## System Stats

| Component | Count |
|-----------|-------|
| Agents | 76 |
| Spiders | 77 |
| Advisors | 25 |
| Personas | 139 |
| Database Models | 387+ |
| Celery Tasks | 262 |
| Services | 131 |
| **Initiatives** | **315** |
| **Transition Logs** | **565+** |
| SignalClusters | 22 |
| AutoTopics | 10 |

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| `docs/handoffs/SESSION_922_STAGE_GEN_FIX.md` | Stage generation bug fix |
| `docs/handoffs/SESSION_921_PIPELINE_HEALTH_MONITORING.md` | Health monitoring implementation |
| `docs/DREAM_INITIATIVE_WORKFLOW.md` | Complete pipeline documentation |
| `CLAUDE.md` | AI session entry point |

---

**Session 922 Complete - Stage Generation Bug Fixed! 50 new documents created, pipeline is recovering.**
