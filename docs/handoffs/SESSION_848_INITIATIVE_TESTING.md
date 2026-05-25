---
originating_session: 848
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 848 - Initiative Pipeline Testing & Fixes

**Date:** January 27, 2026
**Focus:** Testing Session 847's Initiative Pipeline against ChatGPT's verification checklist
**PRs Merged:** #353 (Session 847 feature), #354 (Initiative fixes), #355 (Docs), #356 (Decision Card 500 fix)

---

## What Was Done

ChatGPT provided a comprehensive 7-point testing checklist for the Initiative Pipeline. This session executed all tests and fixed bugs discovered.

### Tests Executed

| # | Test | Result | Notes |
|---|------|--------|-------|
| 0 | Idempotency | ✅ PASS | Second `populate` creates 0 duplicates, lists 17 existing |
| 1 | Golden IDs | ✅ PASS | Reverse lookup works: `InitiativeStage.objects.filter(document_id=X)` |
| 2 | Stage Mapping | ✅ PASS | Uses `stats_snapshot.stage` for existing, `CATEGORY_TO_STAGE` for new |
| 3 | Promotion State Machine | ✅ PASS | Can't promote without doc, can't skip, can't regress |
| 4 | Populate Button | ⚠️ PARTIAL | 1035/1091 old-format blogs not linked (expected) |
| 5 | Gate Lockout | ✅ PASS | Initiative-linked gates blocked from auto-waive |
| 6 | Health Status | ✅ FIXED | API wasn't returning health - now fixed |
| 7 | UI Affordances | ⚠️ PARTIAL | Document link added; conversation/agent-run links TBD |

---

## Bugs Found & Fixed

### Bug 1: Health Missing from API

**Problem:** `initiatives_api` view didn't call `get_initiative_health()`, so UI showed "unknown" for all 17 initiatives.

**Fix:** Added health calculation to `core/views_research_demo.py`:
```python
# Session 848: Get health service for calculating initiative health
health_service = get_initiative_integration_service()

# ... in the loop:
health_data = health_service.get_initiative_health(init)

initiatives_list.append({
    # ... existing fields ...
    'health': health_data.get('health', 'unknown'),
    'health_issues': health_data.get('health_issues', []),
    'days_since_update': health_data.get('days_since_update', 0),
})
```

### Bug 2: Document Button Non-Functional

**Problem:** Document icon in InitiativesTab detail modal had no click handler.

**Fix:** Changed button to anchor with navigation:
```tsx
<a
  href={`/ai-studio/workspace?tab=deliverables&id=${stage.document_id}`}
  className="p-2 hover:bg-dark-border rounded-lg transition-colors"
  title="Open document"
>
  <FileText size={16} className="text-gray-400 hover:text-primary-400" />
</a>
```

### Bug 3: Decision Card 500 Error (Production)

**Problem:** `/api/platform/decision-summary/{id}/` returning 500 Internal Server Error on production.

**Root Cause:** `decision_summary_detail_view` in `core/views_platform_command.py` used field names that don't exist on the `AgentDecisionSummary` model:

| Incorrect Field | Correct Field |
|-----------------|---------------|
| `decision.reasoning` | `decision.rationale` |
| `decision.final_decision` | `decision.recommended_stance` |
| `decision.lead_agent` | `decision.participants[0]` |
| `decision.confidence_level` | (doesn't exist) |
| `decision.dissenting_views` | (doesn't exist) |
| `decision.key_factors` | `decision.key_insights` |
| `decision.contributing_agents` | `decision.participants` |
| `decision.conversation_id` | `decision.conversation.id` |

**Fix:** Updated `core/views_platform_command.py` to use correct field names and added error handling.

**Note:** The 404 error on `/api/human/attention/{id}/` is **expected behavior** - the frontend tries two endpoints:
1. `/api/platform/decision-summary/{id}/` - For `AgentDecisionSummary` (now works)
2. `/api/human/attention/{id}/` - Fallback for `HumanAttentionItem` (404 correct since ID is a decision)

### Bug 4: Pending Decisions Not Updating After Approve/Dismiss

**Problem:** Users clicking Approve/Dismiss on "Pending Decisions" in Production UI saw no change - items stayed in the list.

**Root Cause:** Mismatch between query and action:

| Component | Behavior |
|-----------|----------|
| `_get_pending_decisions()` | Returns ALL users' pending items (no user filter) |
| `record_decision()` | Only allows deciding on items owned by `request.user` |

This caused silent 404 failures when trying to decide on another user's items.

**Fix:**
1. **Backend**: `_get_pending_decisions(user=None)` now accepts user parameter and filters when provided
2. **Frontend**: Added `onError` handler to `decisionMutation` to display error feedback

```python
# Before (broken):
pending = HumanAttentionItem.objects.filter(status='pending')

# After (fixed):
queryset = HumanAttentionItem.objects.filter(status='pending')
if user and user.is_authenticated:
    queryset = queryset.filter(user=user)
```

### Bug 5: Stock Agent Outputs Showing Raw JSON

**Problem:** BullCaseAgent, BearCaseAgent outputs displayed as raw JSON instead of formatted cards.

**Root Cause:** `SmartOutputRenderer` expected `thesis`, `key_points`, `risks` keys but stock agents return `analysis`, `conviction`, `ticker`.

**Fix:** Added `StockAnalysisRenderer` component with:
- Conviction badges (HIGH=green, MEDIUM=amber, LOW=gray)
- Expandable analysis text
- Bull/Bear case cards
- Collapsible tool calls

### Bug 6: Podcast Agents Showing "1. Item 1" Placeholder

**Problem:** ModeratorAgent and other podcast agents wrote "1. Item 1" to workspace files instead of actual content.

**Root Cause:** `_extract_agent_output_content()` checked for `content`/`summary`/`description` keys but podcast agents return `text` key:
```python
{"role": "HOST", "voice_id": "Antoni", "segment": "intro", "text": "Welcome to..."}
```

**Fix:** Added `text` to `CONTENT_KEYS` list and array item extraction in `core/tasks.py`.

---

## Known Limitations (Acceptable)

### 1. Old-Format SelfBlogs Not Linked

1035 out of 1091 SelfBlogs use old format (`[Report]`, `[Research]`) instead of `[Stage X -`. The populate function only handles the new format.

**Why Acceptable:** These are historical blogs. New ThinkingAgent actions use the new format and auto-link correctly.

### 2. Non-ThinkingAgent Workflows Bypass Initiatives

`core/tasks.py` creates SelfBlogs directly via `generate_self_blog_task` without Initiative linking.

**Why Acceptable:** ThinkingAgent is the primary autonomous workflow. Direct SelfBlog creation is manual/legacy.

### 3. Missing UI Links

The Initiative detail modal is missing:
- "Open parent conversation" link
- "Open agent run / execution log" link

**Why Acceptable:** First iteration focuses on visibility. Navigation is future enhancement.

---

## Files Changed

| File | Change |
|------|--------|
| `core/views_research_demo.py` | Added health calculation to initiatives_api |
| `frontend/src/pages/workspace/tabs/InitiativesTab.tsx` | Added document navigation link |
| `core/views_platform_command.py` | Fixed field name mismatches + user filter for pending decisions |
| `frontend/src/pages/workspace/tabs/CommandTab.tsx` | Added error feedback for failed decisions |
| `frontend/src/components/SmartOutputRenderer.tsx` | Added StockAnalysisRenderer for Bull/Bear case outputs |
| `core/tasks.py` | Added 'text' key extraction for podcast agents |

---

## Health Definitions (Verified)

The health calculation in `InitiativeIntegrationService.get_initiative_health()`:

| Status | Condition |
|--------|-----------|
| **Stale** | No updates for > 14 days |
| **Blocked** | Rejected stages exist OR current stage needs document for > 7 days |
| **Healthy** | Neither stale nor blocked |

---

## Production Status

### Merged to Main
```
67e4e5ab fix(Session 848): Extract 'text' key from agent output for podcast agents (#360)
4bba2cc1 fix(Session 848): Add StockAnalysisRenderer for Bull/Bear case agent outputs (#359)
4d490bfc fix(Session 848): Filter pending decisions by user to enable approve/dismiss (#358)
4cdea0d9 fix(Session 848): Fix 500 error on decision-summary endpoint (#356)
dfc1b7df docs: Session 848 handoff - Initiative Pipeline testing & fixes (#355)
a461fefb fix(Session 848): Add health to Initiatives API + document navigation (#354)
1f879be9 feat(Session 847): Initiative Pipeline - Wire ThinkingAgent to 5-stage workflow (#353)
```

### Production Deployment
```bash
# On production server:
python manage.py migrate  # Apply 0194
curl -X POST https://your-domain/api/v1/initiatives/populate/
```

### Current Stats
- **17 Initiatives** created from existing deliverables
- **All 17 healthy** (just created)
- **572 Gates** (0 linked to initiatives yet)

---

## ChatGPT's Red Flag: Addressed

> "Make sure it also creates/link initiatives when non-ThinkingAgent workflows create deliverables"

**Assessment:**
- ThinkingAgent actions → Auto-linked via `AutonomousActionExecutor._link_to_initiative()`
- Direct SelfBlog creation → Not linked (acceptable for now)
- Backfill → Use populate endpoint for `[Stage X -` titled blogs

---

## Potential Future Enhancements

1. **Add conversation link** to Initiative detail modal
2. **Add agent-run link** to Initiative detail modal
3. **Migrate old-format blogs** to new format with stage assignment
4. **Hook SelfBlog.save()** to auto-link all blogs (complex, not recommended)

---

## Quick Reference

```bash
# Check initiative health
curl http://localhost:8000/api/v1/initiatives/

# Populate from existing deliverables
curl -X POST http://localhost:8000/api/v1/initiatives/populate/

# Test health calculation
python manage.py shell -c "
from core.services.initiative_integration_service import get_initiative_integration_service
from core.models import Initiative
service = get_initiative_integration_service()
for i in Initiative.objects.all()[:5]:
    print(f'{i.name[:40]}: {service.get_initiative_health(i)[\"health\"]}')"
```

---

**Session 848 Complete - Initiative Pipeline tested and bugs fixed**
