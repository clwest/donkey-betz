---
originating_session: 1000
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1000C: Content Review Automation Pipeline

**Date:** February 13, 2026
**Focus:** Wire the content review automation pipeline so blogs don't sit in 'draft' forever

## Problem

1,400+ blogs stuck in 'draft' because the pipeline had all the building blocks but they weren't connected:
- PublishGate scored blogs but never promoted status on 'publish' decision
- EditorAgent enhance task defaulted to `save=False` (useless for scheduled runs)
- No task re-evaluated blogs after enhancement
- No task auto-published approved blogs

## Changes

### Fix 1: PublishGate promotes publish-ready blogs (publish_gate.py)

Added `elif result.decision == 'publish'` in `apply_to_blog()` to set `blog.status = 'approved'` when a blog passes all thresholds. Previously blogs got `publish_ready=True` but status stayed 'draft'.

### Fix 2: enhance_all_blogs_task wired for scheduled use (tasks.py)

- Changed default `save=False` → `save=True` so scheduled runs actually persist changes
- Added enhancement count guard via `stats_snapshot['enhancement_count']` — max 3 rounds per blog to prevent infinite loops

### Fix 3: New task — reevaluate_enhanced_blogs (tasks.py)

Re-runs PublishGate on `needs_enhancement` blogs that already have a `quality_score`. If quality improved enough after EditorAgent enhancement, blog gets promoted to 'approved'.

### Fix 4: New task — auto_publish_approved_blogs (tasks.py)

Final pipeline step. Moves `approved` + `publish_ready=True` blogs to `published` status. Runs daily at 6 AM.

### Fix 5: Task routes + Celery Beat entries (settings.py)

**Routes:**
- `enhance_all_blogs_needing_enhancement` → `long_running` (EditorAgent = LLM calls)
- `reevaluate_enhanced_blogs` → `content` (PublishGate = heuristic only)
- `auto_publish_approved_blogs` → `content` (simple status update)

**Beat schedule:**
- `enhance-blogs-needing-enhancement`: every 6h at :40 (limit 5, save=True)
- `reevaluate-enhanced-blogs`: every 6h at :10, offset 3h from enhance
- `auto-publish-approved-blogs`: daily at 6 AM

## Pipeline Flow

```
draft (unscored)
  │  evaluate_unscored_blogs [every 2h, existing]
  ▼
draft (scored) ──publish──► approved ──auto_publish──► published
  │                                    [daily 6AM]
  │ enhance
  ▼
needs_enhancement
  │  enhance_all_blogs_task [every 6h at :40]
  │  EditorAgent improves structure (max 3 rounds)
  ▼
needs_enhancement (enhanced)
  │  reevaluate_enhanced_blogs [every 6h at :10]
  │  PublishGate re-scores
  ▼
approved / still needs_enhancement
```

## Files Changed (3)

| File | Lines | Change |
|------|-------|--------|
| `core/services/publish_gate.py` | +3 | Promote 'publish' decision to 'approved' status |
| `core/tasks.py` | +~70 | Fix enhance defaults, add count guard, 2 new tasks |
| `core/settings.py` | +~18 | 3 task routes, 3 beat schedule entries |

## Verification

All changes verified:
- `py_compile` passes for all 3 files
- Django shell imports succeed for new tasks and PublishGate
- Beat schedule entries parse correctly
