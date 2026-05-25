---
originating_session: 998
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 998: System Governance Hardening

**Date:** February 12, 2026
**Focus:** PublishGate enforcement, author tracking, reviewer role

## Problem

Three governance gaps: (1) PublishGate could be bypassed — content published even when `publish_ready=False`; (2) No tracking of who/what created content; (3) No read-only role for reviewers.

## What Was Built

### 1. PublishGate Enforcement (`tool_dispatcher.py`, `views_research_demo.py`)
- PublishGate now blocks publishing when `publish_ready=False` in both API and PA paths
- Returns clear error message explaining why content can't be published

### 2. Author Tracking (`models_unified_system.py`, `content_deliberation_runner.py`, `tasks.py`)
- `SelfBlog.author` field tracks creation source: ContentDeliberation, ScheduledTask, InitiativePipeline
- Set automatically at all creation paths
- Migration: `0240_session_998_governance`

### 3. Reviewer Role (`models/base/models.py`, `auth_middleware.py`, `auth_views.py`)
- New `platform_role` choices: added 'reviewer' alongside existing roles
- Read-only middleware enforcement: reviewer role can only perform GET/HEAD/OPTIONS
- Auth responses include `platform_role` field
- Frontend: Sidebar hides Admin link for reviewer-role users

## Files Changed (12)

| File | Change |
|------|--------|
| `core/models/base/models.py` | Added 'reviewer' to platform_role choices |
| `core/models_unified_system.py` | SelfBlog.author field |
| `core/auth_middleware.py` | Read-only enforcement for reviewer role |
| `core/auth_views.py` | Include platform_role in auth response |
| `core/services/content_deliberation_runner.py` | Set author on content creation |
| `core/services/tool_dispatcher.py` | PublishGate enforcement in PA path |
| `core/views_research_demo.py` | PublishGate enforcement in API path |
| `core/tasks.py` | Set author on scheduled content creation |
| `core/migrations/0240_session_998_governance.py` | Migration for author + reviewer fields |
| `frontend/src/components/layout/Sidebar.tsx` | Hide Admin for reviewers |
| `frontend/src/stores/authStore.ts` | Store platform_role |
| `frontend/dist/index.html` | Build output |

## Migration

`0240_session_998_governance` — adds `author` CharField to SelfBlog, adds 'reviewer' choice to platform_role.
