---
originating_session: 997
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 997B: Podcast Cleanup + Boardroom Preview + Betting Sidebar + Initiative Owner Backfill

**Date:** February 12, 2026
**Focus:** Three UI improvements + PA routing fix + management command

## What Was Built

### 1. Podcast Tab Cleanup (`ContentStudioTab.tsx`, `views_podcast.py`)
- Removed ChannelEpisode noise from Podcast sub-tab display
- Added inline episode generation capability directly from the Podcast tab
- Cleaned up API to return only relevant podcast episodes

### 2. Boardroom Summary Preview + Betting Sidebar (`Sidebar.tsx`, `tool_dispatcher.py`, `unified_pa_entrypoint.py`)
- Boardroom summary preview shown in workspace sidebar
- Betting sidebar link added to navigation
- PA intent detection: added betting-related context

### 3. Backfill Initiative Owners (`backfill_initiative_owners.py`)
- Management command: `python manage.py backfill_initiative_owners`
- Applies `PROGRAM_OWNER_MAP` and `created_by` rules to all 169 existing unowned initiatives
- Uses same logic as Session 996 auto-assignment

### 4. PA Review Keyword Fix (`unified_pa_entrypoint.py`)
- Refined 'review' keyword routing to avoid false boardroom intent matches
- "review my content" no longer misroutes to boardroom actions
- More specific pattern matching for boardroom-related queries

## Files Changed (7)

| File | Change |
|------|--------|
| `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx` | Podcast tab cleanup + inline generation |
| `core/views_podcast.py` | Cleaner podcast episode API |
| `frontend/src/components/layout/Sidebar.tsx` | Boardroom preview + betting sidebar link |
| `core/services/tool_dispatcher.py` | Boardroom summary support |
| `core/services/unified_pa_entrypoint.py` | Review keyword fix + betting context |
| `core/management/commands/backfill_initiative_owners.py` | New management command |
| `frontend/src/lib/api.ts` | API endpoint additions |

## PA Routing Fix Detail

Before: "review my latest blog" → matched boardroom intent (false positive)
After: "review" only matches boardroom when paired with boardroom-specific context (e.g., "boardroom review", "review session")
