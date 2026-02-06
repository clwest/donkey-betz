# Session 943: Artifact Extraction Cleanup & Operations Tab Fix

**Date:** February 5, 2026
**Status:** Complete
**PRs:** #879, #880, #881, #882, #883, #884

## Summary

Fixed two major issues:
1. **Operations Tab not creating WorkspaceOperations** for financial agent reports
2. **42K+ pending ExtractedArtifacts backlog** from automated brainstorming conversations

## Problem 1: Operations Tab Empty

### Root Cause
Two bugs in `BaseAgent.execute_with_workspace()`:
1. Report file dicts used `'path'` key but `_write_files_to_workspace()` expected `'filename'`
2. Detection required `'##'` markdown headers but StockAnalystAgent reports use `**bold**` and `---`

### Fix (PR #880)
```python
# Changed 'path' to 'filename':
files_to_write.append({
    'filename': f"{category}/{filename}",  # Was 'path'
    'content': str(structured_report),
})

# Expanded detection markers:
has_formatting = any(marker in result.message for marker in [
    '##', '**', '---', '•', '- ', '1)', '1.', ':',
])

# Added fallback for known report-producing agents
report_agents = {'stock', 'bull', 'bear', 'market', 'analyst', 'research', 'prediction', 'crypto', 'trend'}
```

## Problem 2: 42K+ Pending Artifacts Backlog

### Root Cause
The `ArtifactExtractionService` was extracting artifacts from **every** conversation, including automated multi-agent brainstorming sessions (`Discussion:` and `Panel:` conversations). These conversations generate ~2,500 artifacts/day - hypothetical ideas that were never meant for human review.

### Analysis
- 35K+ artifacts from `Discussion:` conversations (automated competitor analysis, customer research)
- 6K+ artifacts from `Panel:` conversations (ConceptForge think tank panels)
- All had high scores (0.5-0.96) because the extraction scored brainstorming ideas highly
- Zero decisions made, zero executions - the queue was just accumulating

### Fix

#### 1. Disable Extraction for Automated Conversations (PR #883, #884)
```python
# core/services/artifact_extraction.py
topic = conversation.topic or ''
if topic.startswith('Discussion:') or topic.startswith('Panel:'):
    logger.debug(f"Skipping extraction for automated conversation")
    return []
```

#### 2. Cleanup Task for Existing Backlog
```python
# core/tasks.py
@shared_task
def cleanup_automated_conversation_artifacts(batch_size=5000, prefix=None):
    """Bulk-reject pending artifacts from Discussion/Panel conversations."""
    prefixes = [prefix] if prefix else ['Discussion:', 'Panel:']
    # ... rejects artifacts with status='rejected'
```

#### 3. Aggressive Auto-Processing (PR #881, #882)
Updated `auto_process_extracted_artifacts` with lower thresholds:
- `stale_days`: 14 → 7 days
- `archive_days`: 30 → 14 days
- `proposal_cutoff`: 21 → 10 days
- Added rules for risks (score < 0.4) and action_items (> 14 days, score < 0.5)

### Results
| Metric | Before | After |
|--------|--------|-------|
| Pending artifacts | 42,348 | 0 |
| Discussion artifacts | 29,592 | 0 (rejected) |
| Panel artifacts | 5,984 | 0 (rejected) |

**All artifacts preserved** - just moved from `pending` to `rejected` status. Conversations, initiatives, and deliverables are untouched.

## Files Changed

| File | Changes |
|------|---------|
| `core/agents/base_agent.py` | Fixed path→filename key, expanded format detection |
| `core/services/artifact_extraction.py` | Skip Discussion/Panel conversations |
| `core/tasks.py` | Lower thresholds, add cleanup_automated_conversation_artifacts |
| `core/celery.py` | Updated schedule with aggressive=True |

## Going Forward

- No more artifact extraction from automated brainstorming conversations
- Weekly Synthesis reports will show meaningful metrics
- Pending queue is clean for legitimate human-initiated artifacts
- Auto-processing runs every 6 hours to keep queue manageable

## Testing

```bash
# Verify no pending artifacts
railway run python manage.py shell -c "
from core.models_conversation_artifacts import ExtractedArtifact
print(f'Pending: {ExtractedArtifact.objects.filter(status=\"pending\").count()}')
"

# Verify Operations Tab works
# Run StockAnalystAgent and check WorkspaceOperation is created
```
