<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.
> **Note:** content may be stale (last refreshed 2026-02-16) — policy direction is still canonical (cited from CLAUDE.md), but verify specific counts/endpoint patterns against `core/urls.py` before relying on them.

# API Path Standardization Policy

**Created:** Session 871 (January 29, 2026)
**Status:** ACTIVE

---

## Executive Summary

This document establishes the API path conventions for the Donkey Betz platform. Due to historical development patterns, the codebase currently uses two path prefixes:

| Pattern | Usage | Endpoint Count |
|---------|-------|----------------|
| `/api/` | Core endpoints, new features | 1,420+ (81.5%) |
| `/api/v1/` | App module includes, research/reasoning APIs | 322 (18.5%) |

**Standard for new development:** Use `/api/` prefix.

---

## Current Architecture

### Pattern 1: `/api/` (PREFERRED)

Direct endpoints defined in `core/urls.py` and other core files:

```python
# Examples from core/urls.py
path('api/projects/', ...)
path('api/learning/', ...)
path('api/agents/', ...)
path('api/workflows/', ...)
path('api/dashboard/', ...)
```

**Use for:**
- New feature endpoints
- Core functionality
- User-facing APIs
- Integration endpoints

### Pattern 2: `/api/v1/` (LEGACY)

Used for app module includes to avoid path conflicts:

```python
# From core/urls.py lines 2795-2867
path('api/v1/workflows/', include('workflows.urls'))
path('api/v1/agents/', include('agents.urls'))
path('api/v1/content/', include('content.urls'))
path('api/v1/sports/', include('sports.urls'))
path('api/v1/reasoning/', ...)
path('api/v1/research/', ...)
```

**Why it exists:** App modules like `workflows.urls` define paths like `history/`, which would conflict with `core/urls.py`'s `/api/workflows/history/`. The `/api/v1/` prefix provides namespace separation.

---

## Path Namespacing (Not True Conflicts)

The following paths have **different functionality** at different prefixes - this is by design:

| Core Path (`/api/`) | Module Path (`/api/v1/`) | Difference |
|---------------------|--------------------------|------------|
| `/api/workflows/*` (26 endpoints) | `/api/v1/workflows/*` (6 endpoints) | Core: management; Module: orchestration execution |
| `/api/agents/*` (35+ endpoints) | `/api/v1/agents/*` (8 ViewSets) | Core: one-off; Module: full CRUD |
| `/api/dashboard/*` (11 endpoints) | ~~`/api/v1/dashboard/*`~~ | Module removed in Session 872 (unused) |

**Session 872 Analysis:** These are complementary endpoint sets, not duplicates. Both are required.

---

## Guidelines for New Development

### 1. New Endpoints

Always use `/api/` prefix:

```python
# CORRECT
path('api/new-feature/', my_view, name='new-feature')

# INCORRECT
path('api/v1/new-feature/', my_view, name='new-feature')
```

### 2. New App Modules

If creating a new Django app with its own `urls.py`:

```python
# In core/urls.py - use /api/ prefix
path('api/my-new-app/', include('my_new_app.urls'))
```

Ensure your app's URL paths don't conflict with existing `/api/` endpoints.

### 3. Frontend API Calls

Check which prefix the endpoint uses:

```typescript
// Research/Reasoning APIs use /api/v1/
fetch('/api/v1/reasoning/thoughts/')
fetch('/api/v1/research/self-blog/')

// Most other APIs use /api/
fetch('/api/learning/journeys/')
fetch('/api/projects/')
```

---

## Migration Roadmap

### Phase 1: Documentation (COMPLETE - Session 871)
- [x] Document current patterns
- [x] Establish policy for new development
- [x] Identify conflicts

### Phase 2: Non-Conflicting Migrations (COMPLETE - Session 871)

The following endpoints were migrated from `/api/v1/` to `/api/`:

| Endpoint | Status | Frontend Updates |
|----------|--------|------------------|
| `/api/llm-routing/*` | MIGRATED | InfrastructureTab.tsx (3 calls) |
| `/api/style-memory/*` | REMOVED (Session 1009) | None needed |
| `/api/coleadership/*` | REMOVED (Session 1009) | None needed |
| `/api/render-jobs/*` | REMOVED (Session 1009) | None needed |
| `/api/pipelines/*` | MIGRATED | None needed |
| `/api/mythology/*` | MIGRATED | IntelligenceTab.tsx (2 calls) |
| `/api/odds-calc/*` | REMOVED (Session 1009) | None needed |
| `/api/initiatives/*` | MIGRATED | None needed |
| `/api/code-artifacts/*` | NEW (Session 1012) | None needed |

**Note:** Research and Reasoning APIs remain at `/api/v1/` due to heavy frontend usage - will require dedicated migration session.

### Phase 3: Conflict Resolution (COMPLETE - Session 872)

Analysis revealed these are **not true conflicts** but **different endpoint sets** serving different purposes:

| Module | `/api/` (core) | `/api/v1/` (module) | Status |
|--------|----------------|---------------------|--------|
| `workflows` | 26 endpoints for workflow management | 6 endpoints for agent orchestration execution | Keep both (different purposes) |
| `agents` | 35+ one-off endpoints | 8 DRF ViewSets for CRUD | Keep both (frontend uses v1 heavily - 47 refs) |
| `dashboard` | 11 endpoints (revenue, learning, health) | 3 endpoints (embeddings stats) | **Module REMOVED** - unused |

**Actions Taken:**
- Removed `dashboard.urls` include - endpoints unused by frontend or backend
- Documented that workflows/agents modules are NOT duplicates but complementary

**Remaining at `/api/v1/` (Required):**
- `workflows.urls` - Used by `personal_assistant_agent.py`
- `agents.urls` - 47 frontend references in `api.ts`
- `sports.urls`, `content.urls`, `self_awareness.urls` - Active modules

---

## File Reference

### URL Configuration Files

| File | `/api/` | `/api/v1/` | Notes |
|------|---------|-----------|-------|
| `core/urls.py` | 1,313 | 316 | Main routing |
| `persistence/urls.py` | 0 | 6 | All v1 |
| `ai_platform/urls.py` | 10 | 0 | All direct |
| `ai_core/urls.py` | 3 | 0 | All direct |
| `sports_betting/urls.py` | 4 | 0 | All direct |

### Frontend API References

| File | `/api/v1/` calls | Notes |
|------|------------------|-------|
| `IntelligenceTab.tsx` | 6 | reasoning, mythology, collective |
| `ContentStudioTab.tsx` | 6 | research/self-blog |
| `InfrastructureTab.tsx` | 3 | llm-routing |
| `BlogViewerPage.tsx` | 2 | research/self-blog |
| `ContentChannelsPage.tsx` | 1 | research/self-blog |

---

## Verification Commands

```bash
# Count /api/v1/ endpoints in backend
grep -r "path('api/v1/" core/urls.py | wc -l

# Count /api/ (non-v1) endpoints
grep -r "path('api/" core/urls.py | grep -v "api/v1" | wc -l

# Check frontend v1 references
grep -r "api/v1/" frontend/src --include="*.tsx" | wc -l

# Check frontend direct api references
grep -r "'/api/" frontend/src --include="*.tsx" | grep -v "api/v1" | wc -l
```

---

## Summary

| Aspect | Guideline |
|--------|-----------|
| **New endpoints** | Use `/api/` |
| **Existing `/api/v1/`** | Keep until conflicts resolved |
| **Frontend changes** | Match backend pattern |
| **Documentation** | Update this file when migrating |

---

*Policy established by Claude Code - Session 871*
