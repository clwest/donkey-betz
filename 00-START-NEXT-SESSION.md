# Session 917 - Start Here

**Previous Session:** 916 (Hard Invariants for Initiative Stage Approval)
**Date:** February 2, 2026
**Status:** 76 Agents | 77 Spiders | 25 Advisors | 139 Personas | **204 INITIATIVES** | **HARD INVARIANTS ACTIVE** | **552 AUDIT LOGS**

---

## Session 916 Complete: Hard Invariants

Data integrity is now enforced at the model level. All 225 initiatives have been audited and fixed.

### What Was Fixed

| Issue | Count | Resolution |
|-------|-------|------------|
| Stage APPROVED without document | 150 | Set to DRAFT |
| Stage 2 approved before Stage 1 | 38 | Sequence corrected |
| Wrong document types attached | 2 | Reassigned |
| Deep sequence violations | 98 | Fixed via unsafe_update |
| **Total Issues Fixed** | **315** | **All resolved** |

### Hard Invariants Now Active

```python
# INVARIANT 1: Cannot approve without document
if stage.status == 'APPROVED' and not stage.document:
    raise ValidationError("INVARIANT VIOLATION: Cannot save as APPROVED without document")

# INVARIANT 2: Cannot approve out of sequence
if stage.stage > 1 and prev_stage.status != 'APPROVED':
    raise ValidationError("INVARIANT VIOLATION: Cannot approve before prior stage")
```

### Audit Trail: StageTransitionLog

Every stage transition is now logged with:
- `from_status` / `to_status`
- `triggered_by` (user, system, Celery task)
- `quality_score` / `confidence_score`
- `checks_passed` (JSON dict)
- 552 transition logs created (including 38 production resets)

### Production Reset: Broken Stage Sequences

38 initiatives were at Stage 2+ but had incomplete Stage 1 (Research Brief). These were reset to Stage 1 to enforce proper sequencing.

---

## Current Production State

| Metric | Value |
|--------|-------|
| Total Initiatives | 204 |
| At Stage 1 | 171 |
| At Stage 2 | 19 |
| At Stage 3 | 12 |
| At Stage 4-5 | 2 |
| With incomplete S1 at Stage 2+ | **0** |
| StageTransitionLog entries | 552 |
| Production resets | 38 |

---

## Quick Reference: Initiative Commands

```bash
# ===== INVARIANT VERIFICATION =====
# Test that invariants are enforced
python manage.py shell -c "
from core.models_document_registry import InitiativeStage
stage = InitiativeStage.objects.filter(document__isnull=True).first()
stage.status = 'APPROVED'
stage.save()  # Should raise ValidationError
"

# ===== AUDIT TRAIL =====
# Check transition logs
python manage.py shell -c "
from core.models_document_registry import StageTransitionLog
print(f'Total logs: {StageTransitionLog.objects.count()}')
print(f'By trigger type:')
for tt in ['auto', 'manual', 'api']:
    print(f'  {tt}: {StageTransitionLog.objects.filter(trigger_type=tt).count()}')
"

# ===== ESCAPE HATCH (for migrations only) =====
# InitiativeStage.unsafe_update_status(stage_id, 'APPROVED', reason='data_migration')

# ===== STAGE DOCUMENT BACKFILL =====
python manage.py fix_initiative_stages --dry-run
python manage.py fix_initiative_stages
```

---

## Governance Pipeline (Sessions 914-914.7)

All governance gates remain active:

```
Initiative Created
    ↓
Stage 1 (Research Brief) - Can auto-progress
    ↓
[GATE] Founder Intent Required
    ↓
[INVARIANT] Must have document to approve ← NEW
    ↓
Stage 2 (Prototype Plan)
    ↓
[INVARIANT] Stage 1 must be APPROVED first ← NEW
    ↓
[GATE] Boardroom Approval (if institutional)
    ↓
[GATE] Semantic Drift Check
    ↓
Stages 3-5
    ↓
Deliverable Published
```

---

## NEXT PRIORITIES for Session 917+

### 1. Unblock Initiative Pipeline
185 initiatives still awaiting founder intent:
```bash
python manage.py set_founder_intent --all-pending --speed=fast
# Or interactive review:
python manage.py set_founder_intent --interactive
```

### 2. Generate Missing Stage Documents
Many stages are now DRAFT awaiting documents:
```bash
# Check how many need documents
python manage.py shell -c "
from core.models_document_registry import InitiativeStage
print(f'DRAFT stages needing docs: {InitiativeStage.objects.filter(status=\"DRAFT\", document__isnull=True).count()}')
"

# Backfill runs automatically via Celery Beat every 30 min
# Or trigger manually:
curl -X POST "https://donkey-betz-production.up.railway.app/api/initiatives/backfill-documents/"
```

### 3. Optional: Implement Soft Invariants
ChatGPT suggested quality gates:
- Minimum `quality_score` threshold for approval
- Weekly integrity report as Celery task
- Regression tests for CI

---

## Recent Session History

| Session | Focus | Handoff |
|---------|-------|---------|
| **916** | Hard Invariants - StageTransitionLog, save() enforcement | `docs/handoffs/SESSION_916_HARD_INVARIANTS.md` |
| 916 | Initiative Title Generator Integration | `docs/handoffs/SESSION_916_INITIATIVE_TITLE_GENERATOR.md` |
| 915 | Stage Document Backfill Pipeline | `docs/handoffs/SESSION_915_STAGE_DOCUMENT_BACKFILL.md` |
| 914.7 | Operating Rhythm - Daily/Weekly cadence | `docs/handoffs/SESSION_914_7_OPERATING_RHYTHM.md` |
| 914-914.6 | Governance Pipeline (Intent, Tracks, Drift, Limits) | (in 914.7 handoff) |

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
| Services | 129 |
| **Initiatives** | **204** |
| **StageTransitionLogs** | **552** |
| SignalClusters | 22 |
| AutoTopics | 10 |

---

## Celery Beat Schedules

| Task | Schedule | Purpose |
|------|----------|---------|
| `backfill_stage_documents` | Every 30 min | Generate missing stage documents |
| `process_initiative_auto_progression` | Every 10 min | Progress stages at 60%+ quality |
| `detect_duplicate_initiatives` | Daily 2 AM | Alert on new duplicate clusters |
| `cleanup_zombie_agent_tasks` | Every 15 min | Clean stuck tasks |

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| `docs/handoffs/SESSION_916_HARD_INVARIANTS.md` | Hard invariants implementation |
| `docs/DREAM_INITIATIVE_WORKFLOW.md` | Complete pipeline documentation |
| `CLAUDE.md` | AI session entry point |

---

**Session 916 Complete - Data Integrity Enforced!**
