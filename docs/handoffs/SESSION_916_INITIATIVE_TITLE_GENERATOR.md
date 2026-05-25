---
originating_session: 916
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 916: Initiative Title Generator Integration

## Summary

Fixed junk initiative titles by integrating the `initiative_title_generator` service into all initiative creation paths. Also added an API endpoint to fix existing bad titles in production.

## Problem

Initiatives were being created with junk titles like:
- "A 'Research Enhancement' pipeline that ingests agent conversation logs..."
- Raw technical descriptions used as names instead of clean titles

## Changes Made

### PRs Merged

| PR | Title | Description |
|----|-------|-------------|
| #765 | Use title generator for all initiative creation | Integrated title generator into all creation paths |

### Key Files Modified

1. **core/models_unified_system.py** (lines 9059-9077) - `promote_to_initiative()` now uses title generator:
   ```python
   from core.services.initiative_title_generator import generate_initiative_title

   initiative_name = generate_initiative_title(
       content=self.content or '',
       topic_hint=self.title,
       max_length=80,
       use_llm=True
   )

   initiative = Initiative.objects.create(
       name=initiative_name,  # Clean title instead of raw self.title
       ...
   )
   ```

2. **core/services/autonomous_action_executor.py** (lines 1086-1095) - Initiative creation now uses title generator:
   ```python
   from core.services.initiative_title_generator import generate_initiative_title
   initiative_name = generate_initiative_title(
       content=reasoning[:1000] if reasoning else '',
       topic_hint=topic,
       max_length=80,
       use_llm=True
   )
   initiative = Initiative.objects.create(name=initiative_name, ...)
   ```

3. **core/views_initiative_kickstart.py** (lines 830-929) - Added `fix_initiative_titles` API endpoint:
   - Finds initiatives with bad titles using `_is_valid_title()` check
   - Generates new titles using LLM with heuristic fallback
   - Supports dry_run mode to preview changes
   - Processes up to 50 initiatives per call

4. **core/urls.py** (line 2858) - Added route:
   ```python
   path('api/initiatives/fix-titles/', views_initiative_kickstart.fix_initiative_titles, name='initiatives-fix-titles'),
   ```

## How Title Generator Works

The `initiative_title_generator.py` service:
1. Uses LLM to extract a clean 3-5 word title from content
2. Falls back to heuristic extraction (first sentence, keyword extraction)
3. Validates title quality before accepting:
   - Not too long (max 80 chars)
   - No code snippets or technical junk
   - No incomplete sentences

## Deployment Instructions

After web service deploys:

1. **Dry run to preview** (in browser or curl):
   ```
   GET /api/initiatives/fix-titles/?limit=50
   ```

2. **Actually fix titles**:
   ```bash
   curl -X POST "https://donkey-betz-production.up.railway.app/api/initiatives/fix-titles/" \
        -H "Authorization: Token YOUR_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"dry_run": false, "limit": 100}'
   ```

## New Initiatives

All new initiatives created after this deploy will automatically get clean titles:
- Dreams promoted to initiatives via `promote_to_initiative()`
- Initiatives created by `AutonomousActionExecutor`

## Related Session Work

- Session 915: Stage document backfill pipeline (PRs #759-764)
- This session builds on Session 915's work to complete the initiative quality improvements

## Next Steps

1. Run fix-titles endpoint on production after deploy
2. Monitor for any remaining bad title patterns
3. Research Briefs will become viewable once backfill task creates documents
