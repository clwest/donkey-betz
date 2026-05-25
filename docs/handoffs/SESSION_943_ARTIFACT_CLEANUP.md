---
originating_session: 943
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 943: Artifact Extraction Cleanup & Operations Tab Fix

**Date:** February 5, 2026
**Status:** Complete
**PRs:** #879, #880, #881, #882, #883, #884, #886, #888, #889, #890, #891, #892

## Summary

Fixed seven major issues:
1. **Operations Tab not creating WorkspaceOperations** for financial agent reports
2. **42K+ pending ExtractedArtifacts backlog** from automated brainstorming conversations
3. **PA/Boardroom couldn't access brainstorming insights** after disabling extraction
4. **PA couldn't access content (blogs, reports) awaiting human review**
5. **PA lacked awareness of system docs** (CLAUDE.md, recent sessions, architecture)
6. **PA had no visibility into initiatives/projects** in the 5-stage pipeline
7. **Frontend using wrong PA class + LLM reformatting tool results** instead of structured format

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

## Problem 3: PA Couldn't Access Brainstorming Insights

### Root Cause
After disabling artifact extraction for Discussion/Panel conversations, the PA and Boardroom had no way to search through brainstorming content. The value of these conversations is in their conclusions and ideas - we just don't want them creating pending review items.

### Solution: BrainstormSearchService (PR #886)

Created a new service that enables on-demand search of brainstorming conversations without creating artifacts.

#### 1. New Service (`core/services/brainstorm_search_service.py`)
```python
class BrainstormSearchService:
    """Search Discussion/Panel conversations for insights on demand."""

    def search(query, days_back=30, limit=10, conversation_type=None)
    def get_conversation_insights(conversation_id, include_full_content=False)
    def get_recent_summaries(days=7, limit=20)
    def get_ideas_by_category(category, days_back=30, limit=10)
    def get_stats(days=30)
```

Categories: `competitor`, `customer`, `pricing`, `content`, `product`, `technical`, `marketing`

#### 2. Tool Registration (`core/services/tool_dispatcher.py`)
```python
self.register("brainstorm_tool", self._handle_brainstorm)
# Actions: search, recent, details, by_category, stats
```

#### 3. PA Routing (`core/services/unified_pa_entrypoint.py`)
```python
# Intent detection keywords:
'brainstorm', 'discussion', 'panel', 'ideas from',
'what did agents', 'agent ideas', 'think tank',
'past conversations', 'previous discussion'
```

### Example PA Queries
- "What brainstorming has been done about competitor pricing?"
- "Show me recent discussion summaries"
- "Get ideas from panels about customer acquisition"
- "Brainstorming stats for the last 30 days"

## Problem 4: PA Couldn't Access Content Ready for Review

### Root Cause
No tool existed for the PA to access Deliverables (blogs, reports, etc.) that are in "ready" status awaiting human review.

### Solution: ContentReviewTool (PR #888)

#### 1. Tool Handler (`core/services/tool_dispatcher.py`)
```python
self.register("content_review_tool", self._handle_content_review)
# Actions: list, stats, details, publish, archive
```

#### 2. PA Routing
```python
# Intent detection keywords:
'blog', 'deliverable', 'content ready', 'ready for review',
'ready to publish', 'publish content', 'archive content',
'content stats', 'what content', 'review content'
```

### Example PA Queries
- "What content is ready for review?"
- "Show me blog stats"
- "Show details [id]"
- "Publish [id]"
- "Archive [id]"

## Problem 5: PA Lacked System Awareness

### Root Cause
The PA didn't have access to the DocsContextBuilder that agents use. It couldn't answer questions about:
- What we've been working on (recent sessions)
- System architecture and capabilities
- Current priorities (00-START-NEXT-SESSION.md)

### Solution: Docs Context Injection for PA (PR #889)

Added `docs_context_builder` to the PA that injects:
- **CLAUDE.md** (300 lines) - System overview, stats, architecture
- **00-START-NEXT-SESSION.md** (200 lines) - Current priorities
- **Recent session handoffs** - What we've been working on
- **Relevant docs** based on the user's query

```python
# In _build_context:
docs_context = self.docs_context_builder.build_context_for_agent(
    agent_name='personal_assistant',
    task=message,
    include_critical_docs=True
)

# In _generate_direct_response:
if docs_context.get('has_docs'):
    system_prompt += docs_context.get('summary', '')
```

### Example PA Queries Now Supported
- "What have we been working on?"
- "What's the system architecture?"
- "What are the current priorities?"
- "How many agents do we have?"

## Problem 6: PA Had No Initiative Visibility

### Root Cause
The PA had no tool to access the Initiative model. Users couldn't ask about:
- Active projects and their status
- Pipeline overview (how many in each stage)
- Action items needing attention
- Details of specific initiatives

### Solution: InitiativeTool (PR #890)

#### Tool Actions
- `list` - List initiatives with filters (status, stage, purpose, program)
- `stats` - Pipeline overview (by stage, by status, action item counts)
- `details` - Full details of a specific initiative
- `action_items` - List pending action items across all initiatives

#### PA Routing
```python
# Intent detection keywords:
'initiative', 'initiatives', 'project', 'projects',
'pipeline', 'stage', 'action item', 'action items',
'what are we working on', 'active projects', 'current projects'
```

### Example PA Queries
- "What initiatives are active?"
- "Show me the pipeline overview"
- "What action items need attention?"
- "Details about [project name]"
- "Show stage 3 initiatives"
- "What's the status of the monetization project?"

## Problem 7: Frontend Using Wrong PA Class + LLM Reformatting Tool Results

### Root Cause
Two issues preventing the new PA tools from working in production:
1. `views_assistant_bypass.py` was still using `EnhancedPersonalAIAssistant` instead of `UnifiedPAEntrypoint`
2. Tool results were being passed through LLM for "summarization", producing verbose text instead of structured format

### Solution: Wire Frontend + Structured Formatting (PR #891, #892)

#### 1. Wire Frontend to UnifiedPAEntrypoint
```python
# core/views_assistant_bypass.py
from core.services.unified_pa_entrypoint import get_unified_pa
from asgiref.sync import async_to_sync

pa = get_unified_pa(user)
pa_response = async_to_sync(pa.process_message)(message, context)

response_data = {
    'response': pa_response.content,
    'trace_id': pa_response.trace_id,
    'intent': pa_response.intent,
    'tool_runs': pa_response.tool_runs,
    # ...
}
```

#### 2. Use Structured Formatting Directly for New Tools
```python
# core/services/unified_pa_entrypoint.py
async def _generate_response_from_tool(self, message, intent, tool_result, context, trace_id):
    # Use structured formatting directly for these intents
    structured_format_intents = [
        'initiatives', 'brainstorming', 'content_review',
        'boardroom', 'decision_management'
    ]

    if intent in structured_format_intents:
        return self._format_tool_result(tool_result, intent, user_name)

    # For other intents, use LLM to interpret results
    # ...
```

### Example Output After Fix
```
📊 **Initiatives Overview**

🟢 **Monetization Strategy** (Stage 3/5, revenue) - 2 action items
🔵 **Content Pipeline Optimization** (Stage 2/5, stability) - 0 action items
🟠 **New Agent Development** (Stage 1/5, expansion) - 1 action item
```

## Files Changed

| File | Changes |
|------|---------|
| `core/agents/base_agent.py` | Fixed path→filename key, expanded format detection |
| `core/services/artifact_extraction.py` | Skip Discussion/Panel conversations |
| `core/tasks.py` | Lower thresholds, add cleanup_automated_conversation_artifacts |
| `core/celery.py` | Updated schedule with aggressive=True |
| `core/services/brainstorm_search_service.py` | **NEW** - Search Discussion/Panel conversations |
| `core/services/tool_dispatcher.py` | Added brainstorm, content_review, initiative tool handlers |
| `core/services/unified_pa_entrypoint.py` | Added all tool routing + docs context injection + structured formatting bypass |
| `core/views_assistant_bypass.py` | Wire frontend to UnifiedPAEntrypoint with async_to_sync |

## Going Forward

- No more artifact extraction from automated brainstorming conversations
- Weekly Synthesis reports will show meaningful metrics
- Pending queue is clean for legitimate human-initiated artifacts
- Auto-processing runs every 6 hours to keep queue manageable
- PA and Boardroom can search brainstorming insights on demand via `brainstorm_tool`
- PA can access content ready for review via `content_review_tool`
- PA now has full system awareness via docs injection (CLAUDE.md, sessions, architecture)
- PA can access initiative pipeline and action items via `initiative_tool`

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
