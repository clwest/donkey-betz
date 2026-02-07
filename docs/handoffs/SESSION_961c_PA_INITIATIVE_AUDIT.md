# Session 961c: PA Initiative Audit & Cleanup

**Date:** February 7, 2026
**Status:** Complete
**PR:** #960
**Branch:** main

---

## Problem Statement

With 568 initiatives (almost all Stage 1, no activity, auto-generated names), asking the PA to "audit all initiatives and classify them" produced a useless flat list. The PA needed to actually **analyze and classify** when asked to audit.

---

## What Was Built

### 1. PA Initiative Audit Action

Added `audit` action to `_handle_initiative()` in tool_dispatcher.py that classifies initiatives into four categories:

| Category | Criteria | Purpose |
|----------|----------|---------|
| **Real** | `current_stage > 1` OR `last_activity_at is not None` | Progressing initiatives worth keeping |
| **Stalled** | Stage 1, no activity, created > 14 days ago | Old initiatives that never started |
| **Noise** | Stage 1, no activity, created <= 14 days ago | Recent auto-generated clutter |
| **Duplicates** | Jaccard similarity >= 0.6 via BFS clustering | Reuses Session 906 `find_duplicate_clusters()` |

### 2. Keyword Routing

Routes `audit`, `classify`, `classification`, `triage`, `cleanup` keywords to the audit action (first in condition chain, before `stats`).

### 3. Structured Formatter

Formats audit results as a breakdown with counts, sample items per category, duplicate cluster info, and cleanup recommendation.

---

## Production Cleanup Results

After deploying the audit feature, ran cleanup on Railway:

### Duplicate Consolidation (`consolidate_duplicate_initiatives --fix`)

| Cluster | Merged | Description |
|---------|--------|-------------|
| Cluster 6 | **78** | "Auto-created From Conversation Decision" spam |
| Cluster 3 | 4 | Customer behavior/research duplicates |
| 12 other clusters | 1 each | Various content/enhancement duplicates |
| **Total** | **94** | Merged into 14 primary initiatives |

### Noise Archival

Archived 420 Stage 1/no-activity initiatives (status: ACTIVE -> ARCHIVED).

### Before/After

| Metric | Before | After |
|--------|--------|-------|
| Total | 568 | 474 |
| Active | 566 | **52** |
| Completed | 2 | 2 |
| Archived | 0 | **420** |
| Duplicates merged | - | **94** |

---

## Files Modified

| File | Changes |
|------|---------|
| `core/services/tool_dispatcher.py` | Added `elif action == 'audit':` block (~70 lines) |
| `core/services/unified_pa_entrypoint.py` | Audit keyword routing + formatter (~38 lines) |

## Reused Code (no modifications)

| File | Import |
|------|--------|
| `core/management/commands/consolidate_duplicate_initiatives.py` | `find_duplicate_clusters()` (Session 906) |

---

## Testing

- 16/16 PA tests pass
- 6 voice test failures are pre-existing (unrelated `OpenAI` mock issue)
- Verified on Railway production: structured audit response confirmed
