---
originating_session: 1070
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1070 — Decision Gates: Classification Before Execution

**Date:** February 23, 2026
**PR:** #1440 (merged & deployed to Railway)
**Branch:** `feat/decision-gates` (merged to main)

---

## Problem

The core semantic bug: **the system treated "insight exists" as "action should follow"** without a human decision in between. The PA demonstrated governance instincts when analyzing agent-generated initiatives (correctly identifying scope drift, proposing policy gates), but the pipeline didn't enforce this. Insights were auto-approved by `triage_extracted_artifacts` in `core/tasks.py`, bypassing any human classification.

ChatGPT analysis identified this as a "decision-extraction problem" — the intelligence layer is ahead of the control surface.

## Solution: 4-Question Classification Gate

Every artifact/initiative now needs classification answers before agents can execute:

1. **What is this?** — `research_finding` | `actionable_recommendation` | `scope_change` | `risk_flag` | `informational`
2. **Who is it for?** — `platform` | `end_users` | `founder` | `agents` | `public`
3. **What data is allowed?** — `public_only` | `internal_ops` | `api_data` | `user_data` | `all`
4. **What phase is approved?** — `research` | `prototype` | `pilot` | `production` | `none`

---

## Changes by File

### 1. ExtractedArtifact Model (`core/models_conversation_artifacts.py`)

**New fields** (after `composite_score`, before `class Meta`):
- `classified` (BooleanField, default=False)
- `classified_at` (DateTimeField, nullable)
- `classified_by` (FK to UnifiedUser, nullable)
- `classification` (JSONField, default=dict) — stores the 4 answers

**New method:** `classify(classification: dict, user=None)` — sets all 4 fields + saves with `update_fields`.

**New index:** `(status, classified)` for efficient unclassified queries.

### 2. Initiative Model (`core/models_document_registry.py`)

**New fields** (after `blocking_reason`, ~line 435):
- `target_audience` (CharField, max_length=50, blank/default='')
- `data_scope` (CharField, max_length=50, blank/default='')

**Updated `can_auto_progress`** (~line 893): blocks at Stage 2+ if `target_audience` or `data_scope` is empty.

**Updated `progression_blocked_reason`** (~line 920): returns descriptive message listing which classification fields are missing.

### 3. Auto-Approve Removed (`core/tasks.py`, lines 842-867)

**Before:** Auto-approved ALL insights (aggressive) or low-score insights (standard).

**After:** Only auto-rejects very low-score noise (`composite_score < 0.3`). All other insights stay `pending` until a human classifies and approves them. The `stats['insights_approved']` key is reused for backwards compat.

### 4. Execution Gate (`core/services/artifact_execution.py`, after line 109)

In `execute_artifact()`, after status validation: if `not artifact.classified` AND artifact was approved after gate activation date (2026-02-24), raises `ValueError`. This grandfathers all existing approved artifacts.

### 5. API Endpoints (`core/views_artifacts.py`)

Two new view functions (before Phase B section):

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `api/artifacts/<uuid>/classify/` | POST | Classify artifact with 4 fields + optional `auto_approve` |
| `api/artifacts/needs-classification/` | GET | List pending, unclassified artifacts (score >= 0.4) |

**Validation constants:** `VALID_WHAT_IS_THIS`, `VALID_WHO_IS_IT_FOR`, `VALID_DATA_ALLOWED`, `VALID_PHASE_APPROVED` — all validated server-side.

**Serializer updated:** `_serialize_artifact()` now always includes `classified` and `classification` fields. Full mode adds `classified_at` and `classified_by`.

### 6. URL Routes (`core/urls.py`, after line 3775)

Two new routes added before the Review Documents section.

### 7. PA Tool Schema (`core/services/pa_tool_schemas.py`)

`boardroom_tool` action enum extended with `list_unclassified` and `classify_suggest`. New `artifact_id` parameter added.

### 8. PA Tool Handlers (`core/services/tool_dispatcher.py`)

Two new handlers in `_handle_boardroom` (before the `else` block):

- **`list_unclassified`**: Queries `ExtractedArtifact(status='pending', classified=False, composite_score__gte=0.4)`, returns items with note about required fields.
- **`classify_suggest`**: Deterministic heuristic based on `artifact_type` and keyword matching. Returns suggestions dict — does NOT apply them. Human must confirm.

### 9. Frontend API (`frontend/src/lib/api.ts`)

New `classificationApi` export (before `decisionsApi`):
- `listUnclassified(limit?)` — GET
- `classifyArtifact(artifactId, classification, autoApprove?)` — POST

### 10. BoardroomPage (`frontend/src/pages/BoardroomPage.tsx`)

- **New tab:** "Needs Classification" (amber-themed) alongside Inbox and Draft Decisions
- **Summary card:** Replaced ML Accuracy (usually `--`) with "Needs Classification" count (clickable, navigates to tab)
- **Classification form:** Inline 4-dropdown form per artifact with "Classify & Approve" and "Classify Only" buttons
- **New types:** `UnclassifiedArtifact` interface, option arrays for each dropdown
- **New state:** `classificationForms` record, `classifyMutation`, `unclassifiedData` query

### 11. Migration (`core/migrations/0256_decision_gates.py`)

- Schema: 4 fields on ExtractedArtifact, 2 on Initiative, 1 index
- Data migration: `grandfather_existing_artifacts()` marks all `status in ('approved', 'implemented')` as `classified=True`
- **Result on Railway:** 324 artifacts grandfathered, 2339 pending artifacts now need classification

---

## Verification on Railway

```bash
# Needs-classification endpoint working:
curl -s "https://donkey-betz-platform-production.up.railway.app/api/artifacts/needs-classification/?limit=3" | python -m json.tool

# Migration applied:
railway run python manage.py showmigrations core | grep 0256
# [X] 0256_decision_gates
```

---

## Key Numbers

| Metric | Value |
|--------|-------|
| Artifacts grandfathered | 324 |
| Pending needing classification | 2,339 |
| Gate activation date | 2026-02-24 |
| Noise threshold (auto-reject) | composite_score < 0.3 |
| Unclassified query threshold | composite_score >= 0.4 |

---

## Architecture Decisions

1. **Grandfather clause via date, not flag**: Artifacts approved before 2026-02-24 skip the classification gate in `execute_artifact()`. Data migration separately marks them `classified=True` for query consistency.

2. **Classification is decoupled from approval**: `classify()` and `approve()` are separate operations. The `auto_approve` parameter in the API is a convenience shortcut, not a coupling.

3. **Heuristic suggestions only**: `classify_suggest` returns suggestions based on artifact_type and keywords but NEVER applies them. Human confirmation is always required.

4. **Initiative gates are additive**: `target_audience` and `data_scope` add to existing `can_auto_progress` checks (founder_intent, boardroom_approval, fast-track). They don't replace anything.

5. **Noise threshold is conservative**: Only composite_score < 0.3 is auto-rejected (previously all insights were auto-approved). The 0.3-0.4 gap stays pending but doesn't appear in the classification UI (threshold is 0.4).
