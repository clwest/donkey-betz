---
originating_session: 976
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 976 — Fix SKIN Layer Auto-Generated Files Polluting Git Repo

**Date:** February 9, 2026
**Previous Session:** 975 (Stock Intelligence Dashboard)
**Branch:** `main`

---

## Problem

SKIN Layer Celery tasks (Sessions 695/778) write auto-generated files (status reports, blog drafts, daily summaries) directly into the git repository root. The `_get_workspace_for_skin_layer()` helper in `core/tasks.py` returned the "Donkey Betz" `ProjectWorkspace` whose `root_path` points to the project directory. This caused 61+ auto-generated files to be committed to git across `reports/`, `summaries/`, and `content/blog_*.md`, with new untracked files appearing every 4-8 hours.

Meanwhile, `_ensure_system_workspace()` in `core/services/workspace_manager.py` already creates a "System Autonomous Workspace" rooted at `generated_content/` — which IS already gitignored.

## Solution

Made `_get_workspace_for_skin_layer()` prefer the "System Autonomous Workspace" (rooted at `generated_content/`) instead of cascading through workspaces that ultimately select the project root. Added gitignore patterns. Removed 59 already-committed auto-generated files from git tracking.

---

## Changes

### Files Modified (2)

| File | Changes |
|------|---------|
| `core/tasks.py` | Rewrote `_get_workspace_for_skin_layer()` — now looks up "System Autonomous Workspace" first, falls back to creating one at `generated_content/`. Removed old 4-step cascade that selected project-root workspace. |
| `.gitignore` | Added `/reports/`, `/summaries/`, `/content/blog_*.md` patterns as safety net |

### Files Created (1)

| File | Purpose |
|------|---------|
| `docs/handoffs/SESSION_976_SKIN_LAYER_GITIGNORE_FIX.md` | This handoff document |

### Git Index Changes

59 auto-generated files removed from tracking via `git rm --cached` (files remain on disk):
- 44 status reports (`reports/system_status_*.md`)
- 1 session review (`reports/session_970_production_review.md`)
- 13 blog drafts (`content/blog_*.md`)
- 1 summary (`summaries/daily_2026-01-18.md`)
- 1 gitkeep (`summaries/.gitkeep`)

No migrations needed.

---

## Technical Details

### Before (old cascade)

```python
def _get_workspace_for_skin_layer():
    # 1. Primary workspace from platform_config (default: "Donkey Betz" → project root)
    # 2. Codebase workspace (type='codebase')
    # 3. Any active workspace with allow_file_write=True
    # 4. Superuser's workspace
```

All paths led to a workspace rooted at the project directory, causing files to land in the git repo.

### After (targeted lookup)

```python
def _get_workspace_for_skin_layer():
    # 1. "System Autonomous Workspace" (generated_content/ — gitignored)
    # 2. Fallback: create one at generated_content/
```

The 5 SKIN layer tasks (`agent_workspace_status_report`, `agent_workspace_blog_creation`, `agent_workspace_daily_summary`, `agent_workspace_research_compilation`, `agent_workspace_content_updates`) all call this one helper, so no call-site changes were needed.

### Safety Net

Even if something writes to the old locations, the new `.gitignore` patterns prevent tracking:
- `/reports/` — catches `system_status_*.md` and any other reports
- `/summaries/` — catches `daily_*.md`
- `/content/blog_*.md` — catches auto-generated blog drafts (preserves other content/ files)

---

## Verification

1. `python -c "import py_compile; py_compile.compile('core/tasks.py')"` — syntax OK
2. `git status` — 59 deleted files (from index only), files remain on disk
3. `generated_content/` already exists and is gitignored (line 57 of `.gitignore`)
4. Untracked `reports/system_status_2026-02-09_*.md` and `content/blog_*_2026-02-08_*.md` no longer appear in `git status`
