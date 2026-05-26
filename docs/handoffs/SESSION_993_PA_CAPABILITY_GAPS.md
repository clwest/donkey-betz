---
originating_session: 993
provenance_confidence: HIGH
provenance_note: Hand-authored handoff. Cited by Session 1158 narrative D (Personal Assistant) milestone 3 as the wiring-completion + capability-gap audit that prepared the input list for Session 1035-W2's 11 new tools.
---

# Session 993 — PA Capability Gaps: Write Actions + Blog Triage + V2 Generation

**Date:** February 12, 2026
**Previous:** Session 992 (Wire 3 Remaining Unwired Services)

## Summary

Added 3 PA capability gaps: bulk blog triage with publish/archive, V2 blog generation via the deliberation pipeline, and write actions for 3 read-only tools (initiative, opportunity, spider).

## Changes

### 1. Bulk Blog Triage + Publish/Archive (`tool_dispatcher.py` — `_handle_blog_query`)

5 new actions added after `batch_enhance`:

| Action | Behavior |
|--------|----------|
| `triage` | Groups ALL blogs into 3 quality tiers: publish-ready (gate-passed + approved/pending_review), needs-revision (draft/needs_enhancement), archive-candidates (draft, >30d old, quality<0.4). Returns counts, items, avg_quality. |
| `publish` | Publishes a single SelfBlog. Requires approved/pending_review status. Records content feedback. |
| `archive` | Archives a blog by setting status→draft, publish_ready→False (safe, reversible — SelfBlog has no 'archived' status). Records content feedback. |
| `batch_publish` | Publishes all publish-ready blogs. Capped at 50 per call. Records feedback for each. |
| `batch_archive` | Archives old low-quality drafts. Configurable via `days_old` (default 30) and `max_quality` (default 0.4). Capped at 50. |

### 2. V2 Blog Generation via PA (`tool_dispatcher.py` — new `_handle_generate_blog`)

New handler registered as `generate_blog_tool`:
- **With topic:** Calls `ContentDeliberationRunner().run_blog(topic, voice=tone)` synchronously. Returns blog_id, decision, summary.
- **Without topic:** Dispatches `generate_self_blog_deliberation_task.delay(tone=tone)` to Celery. Returns task_id.

New intent in `unified_pa_entrypoint.py`:
- Triggers: "generate a blog", "generate blog", "v2 blog", "deliberated blog", "generate content", etc.
- Routes to `('generate_blog', 'generate_blog_tool')`

### 3. Write Actions for Read-Only Tools

**Initiative tool** (`_handle_initiative`) — 3 new actions:
| Action | Behavior |
|--------|----------|
| `update_status` | Changes initiative status: ACTIVE/ON_HOLD/COMPLETED/ARCHIVED |
| `advance` | Calls `initiative.advance_stage()` model method. Returns old→new stage. |
| `complete_action_item` | Calls `item.complete(by='PA')` on InitiativeActionItem |

**Opportunity tool** (`_handle_opportunity_manager`) — 1 new action:
| Action | Behavior |
|--------|----------|
| `update_status` | Changes opportunity status: active/pending/applied/accepted/rejected/expired |

**Spider tool** (`_handle_spider_data`) — 1 new action:
| Action | Behavior |
|--------|----------|
| `trigger` | Dispatches `run_spider_by_category.delay(category=...)` to Celery. Returns task_id. |

### 4. New Intent Phrases (`unified_pa_entrypoint.py`)

Added to `content_review` block: `triage content`, `triage blogs`, `summarize all blogs`, `blog triage`, `review all blogs`, `publish all`, `batch publish`, `batch archive`

New `generate_blog` intent (between content_review and brainstorming): 9 trigger phrases

## Files Changed

| File | Changes |
|------|---------|
| `core/services/tool_dispatcher.py` | 5 blog actions, 1 new handler + registration, 3 initiative actions, 1 opportunity action, 1 spider action |
| `core/services/unified_pa_entrypoint.py` | 8 new content_review phrases, 1 new generate_blog intent |

## What We Did NOT Change

- No new models, migrations, or Celery tasks
- No frontend changes
- No changes to existing action behavior
- SelfBlog has no 'archived' status → archive uses 'draft' (safe, reversible)

## PA Tool Count Update

- **Intents:** 36 → 37 (added generate_blog)
- **Tool handlers:** 50 → 51 (added generate_blog_tool)
- **Total actions across all tools:** +11 new write actions

## Testing

```
"Triage all the blogs"          → tiered summary with publish-ready/needs-revision/archive-candidates
"Generate a blog about AI"      → triggers v2 deliberation pipeline synchronously
"Generate a blog"               → queues async blog generation via Celery
"Mark initiative X completed"   → updates initiative status
"Advance initiative X"          → moves to next pipeline stage
"Trigger the crypto spiders"    → queues spider run
"Mark opportunity X as applied" → updates opportunity status
```
