---
originating_session: 860
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 860 - Initiative Pipeline Fixes

**Date:** January 28, 2026
**Focus:** Fix Initiative Pipeline tracking issues - documents not linking to initiatives
**Status:** COMPLETED

---

## Problem Statement

The Initiative Pipeline was implemented in Session 847, but documents weren't being linked to initiatives properly. Investigation revealed:

1. **`[Report]` documents** had no `parent_topic` in `stats_snapshot`
2. **`[Research]` documents** had no `parent_topic` in `stats_snapshot`
3. **Many documents with `parent_topic`** were never linked despite existing initiatives
4. **Stage overwrites** happened silently without logging

---

## Root Cause Analysis

### Issue 1: Missing parent_topic in Report Documents

`_execute_create_report()` in `autonomous_action_executor.py` created SelfBlog with:
```python
stats_snapshot={
    'auto_generated': True,
    'reasoning': reasoning,
    # NO parent_topic!
}
```

When `_link_to_initiative()` tried to link, `_extract_topic_from_document()` fell back to the title `[Report] System Insights`, which didn't match any real initiative.

### Issue 2: Missing parent_topic in Research Documents

Same issue in `_execute_request_research()` - the research SelfBlog lacked `parent_topic`.

### Issue 3: Existing Documents Not Backfilled

Documents created before Session 847 that had `parent_topic` in `stats_snapshot` were never linked to initiatives because there was no backfill mechanism.

---

## Fixes Applied

### Fix 1: Add parent_topic to Reports (autonomous_action_executor.py:414-430)

```python
# Session 860: Added parent_topic for Initiative linking
stats_snapshot={
    'auto_generated': True,
    'parent_topic': topic,  # Session 860: Required for Initiative linking
    'reasoning': reasoning,
    ...
}
```

### Fix 2: Add parent_topic to Research (autonomous_action_executor.py:607-623)

```python
# Session 860: Added parent_topic for Initiative linking
stats_snapshot={
    'auto_generated': True,
    'parent_topic': topic,  # Session 860: Required for Initiative linking
    'action_type': 'request_research',
    ...
}
```

### Fix 3: Improve Stage Document Handling (initiative_integration_service.py:229-241)

Added logging when replacing existing stage documents and prevented status downgrade:
```python
# Session 860: Check if stage already has a document
if old_document_id and old_document_id != document.id:
    self.logger.info(f"[Session 860] Replacing existing document...")

# Session 860: Don't downgrade status if stage was already APPROVED
if stage.status != InitiativeStage.StageStatus.APPROVED:
    stage.status = InitiativeStage.StageStatus.DRAFT
```

### Fix 4: Backfill Function (initiative_integration_service.py:609-695)

New method `backfill_unlinked_documents()` that:
- Finds all SelfBlogs with `parent_topic` not linked to any InitiativeStage
- Links them to the appropriate initiative and stage
- Supports dry_run mode for preview

---

## Files Changed

| File | Changes |
|------|---------|
| `core/services/autonomous_action_executor.py` | Added `parent_topic` to Report and Research stats_snapshot |
| `core/services/initiative_integration_service.py` | Improved stage linking with logging, added `backfill_unlinked_documents()` |

---

## Results

### Before
- Stages with documents: 15
- Many `[Report]` and `[Research]` documents not linked

### After
- Stages with documents: 31 (+16)
- All documents with `parent_topic` now linked
- Future Reports and Research will auto-link correctly

### Backfill Stats
```
Total unlinked: 25
Linked: 25
Skipped: 0
Errors: 0
```

---

## Usage

### Run Backfill (if needed in future)

```python
from core.services.initiative_integration_service import get_initiative_integration_service

svc = get_initiative_integration_service()

# Preview
results = svc.backfill_unlinked_documents(dry_run=True)
print(f"Would link {len(results['linked'])} documents")

# Execute
results = svc.backfill_unlinked_documents(dry_run=False)
print(f"Linked {len(results['linked'])} documents")
```

---

## Next Steps

1. **Monitor initiative linking** - Check that new actions create proper initiative links
2. **Add UI indicator** - Show when a document is linked to an initiative
3. **Stage promotion automation** - Auto-promote stages when documents are approved

---

**Session 860 Complete - Initiative Pipeline now tracking properly**
