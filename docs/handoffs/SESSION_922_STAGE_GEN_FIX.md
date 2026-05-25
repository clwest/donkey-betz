---
originating_session: 922
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 922: Stage Generation Bug Fix

**Date:** February 3, 2026
**Focus:** Fix critical bug preventing Stage 1 document generation

---

## Problem Statement

Diagnostic revealed that **192 out of 200 Stage 1 DRAFT initiatives (96%)** had no document attached. This was the root cause of why initiatives appeared "stuck" at 0/5 stages in the UI.

---

## Root Cause

The `generate_initiative_stage_document` Celery task in `core/tasks.py` was calling:

```python
result = router.execute_agent(
    agent_name=agent_model.name,
    query=prompt,
    context={'initiative_id': str(initiative_id), 'stage': stage_num}
)
```

**Problem:** `AgentRouter.execute_agent()` doesn't exist! The correct method is `route()`.

This caused every Stage 1 document generation to fail with:
```
'AgentRouter' object has no attribute 'execute_agent'
```

---

## Fix Applied

**PR #812:** Changed to correct method signature:

```python
result = router.route(
    agent_name=agent_model.name,
    task=prompt,  # was: query=prompt
    context={'initiative_id': str(initiative_id), 'stage': stage_num}
)

# AgentResult has .success, .message, .data - not .get('response')
if not result or not result.success or not result.message:
    raise ValueError(f"Agent returned empty response: {result.error if result else 'No result'}")

document_content = result.message  # was: result.get('response', '')
```

---

## Backfill Executed

Ran manual backfill to generate Stage 1 documents for stuck initiatives:

| Metric | Before | After |
|--------|--------|-------|
| Stage 1 WITH documents | 8 | 58 |
| Stage 1 WITHOUT docs | 192 | 257 |
| Document coverage | 4% | 18% |

**Note:** ~50% of initiatives fail during backfill due to malformed/truncated names that confuse the ResearchAgent.

---

## PRs Merged

| PR | Description |
|----|-------------|
| #811 | Add `/api/initiatives/trigger-backfill/` endpoint |
| #812 | Fix `generate_initiative_stage_document` using `router.route()` |

---

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py:32344-32357` | Fixed method call and result handling |
| `core/views_initiative_kickstart.py` | Added `trigger_stage_backfill` endpoint |
| `core/urls.py` | Added URL route for backfill endpoint |

---

## How to Continue Backfill

```bash
# Check how many still need documents
railway run python manage.py shell -c "
from core.models_document_registry import InitiativeStage
count = InitiativeStage.objects.filter(
    stage=1, document__isnull=True, initiative__status='ACTIVE'
).count()
print(f'{count} initiatives need Stage 1 documents')
"

# Run backfill in batches
railway run python manage.py backfill_stage_documents --stage=1 --limit=30
```

---

## Known Issues

1. **Malformed initiative names** cause ~50% failure rate during backfill:
   - "Back Engine:"
   - "Agent Discussion Outputs and Generates Priori..."
   - Names that are just fragments

2. **Railway deployment** may lag behind git - `railway run` pulls local code but production server needs explicit redeploy.

---

## Next Steps for Session 923+

1. Continue running backfill batches until coverage >80%
2. Clean up malformed initiative names
3. Verify auto-progression starts working (initiatives should move from Stage 1 → Stage 2 once they have documents)
4. Monitor Pipeline Health tab for increasing transitions
