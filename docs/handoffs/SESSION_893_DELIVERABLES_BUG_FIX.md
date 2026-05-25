---
originating_session: 893
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 893 - Deliverables String Bug Fix

**Date:** January 31, 2026
**Focus:** Fix single-letter document titles caused by LLM output format bug
**Status:** Complete

---

## Problem Statement

User reported the Technical sub-tab was showing documents with single-letter titles like:
- `[Stage 1 - Research Brief] n`
- `[Stage 1 - Research Brief] o`
- `[Stage 1 - Research Brief] s`
- etc.

These letters spelled out "summary.json" when read in sequence.

---

## Root Cause

**Location:** `core/services/autonomous_action_executor.py` line 497

The `ThinkingAgent` generates actions via an LLM. When the LLM outputs:
```json
{
  "action_type": "request_research",
  "params": {
    "deliverables": "summary.json"  // STRING - incorrect
  }
}
```

Instead of:
```json
{
  "action_type": "request_research",
  "params": {
    "deliverables": ["summary.json"]  // LIST - correct
  }
}
```

The code then iterates over the string character by character:
```python
for i, deliverable in enumerate(deliverables, 1):  # Iterates: 's', 'u', 'm', ...
    logger.info(f"Synthesizing deliverable {i}/{len(deliverables)}: {deliverable}")
```

Each character becomes a document title, creating 12 documents with single-letter titles.

---

## Solution

### 1. Added Validation (2 locations)

**File:** `core/services/autonomous_action_executor.py`

**At parameter extraction (line 499-504):**
```python
deliverables = params.get('deliverables', [])

# Session 893: Fix LLM output bug - ensure deliverables is always a list
if isinstance(deliverables, str):
    deliverables = [deliverables] if deliverables else []
    logger.warning(f"[Session 893] Converted deliverables string to list: {deliverables}")
```

**At synthesis loop (line 711-714):**
```python
if synthesize_deliverables and deliverables and research_successful:
    # Session 893: Double-check deliverables is a list before iteration
    if isinstance(deliverables, str):
        deliverables = [deliverables] if deliverables else []
```

### 2. Created Cleanup Command

**File:** `core/management/commands/cleanup_single_letter_docs.py`

```bash
# Dry run - see what would be deleted
python manage.py cleanup_single_letter_docs --dry-run

# Actually delete
python manage.py cleanup_single_letter_docs
```

---

## Files Modified

| File | Changes |
|------|---------|
| `core/services/autonomous_action_executor.py` | Added string-to-list validation at 2 locations |
| `core/management/commands/cleanup_single_letter_docs.py` | NEW - cleanup command for bad production data |

---

## Testing

```bash
# Verify the fix is in place
grep -A5 "Session 893" core/services/autonomous_action_executor.py

# Run cleanup on production (after deploying)
python manage.py cleanup_single_letter_docs --dry-run
python manage.py cleanup_single_letter_docs
```

---

## Why "summary.json"?

The ThinkingAgent was instructed to create a research deliverable and the LLM decided to name it "summary.json". This is a common pattern for research outputs. The bug was not in the name itself, but in how it was formatted (string vs list).

---

## Prevention

The fix ensures that even if an LLM outputs `"deliverables": "filename"`, it will be automatically wrapped in a list. This is a defensive pattern for any LLM-generated JSON where arrays might be output as strings.

---

**Session 893 Complete. Single-letter title bug fixed with defensive validation.**
