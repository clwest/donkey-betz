# Session 1004: Production Stabilization — Blog Quality + PA Intent + Task Error Sweep

**Date:** February 14, 2026
**Focus:** Fix quality issues discovered after overnight pipeline run

## Context

Session 1003 deployed 13 fixes to close broken execution loops. After running overnight:
- 40 blogs published (was 8) -- BUT 19/40 about same topic (Security/Homeland)
- 1,089 signal clusters (was 0)
- Initiative stages 1-5 active (was stuck at Stage 1)
- 172 task failures in 12h (retry_blocked_research: 141, execute_agent_task: 24)
- PA didn't use blog tools when user mentioned blog by title
- Beat schedules kept reverting on deploy

## Changes

### PR #1138: Increase Blog Reevaluate Frequency + Batch Size
**Files:** `core/celery.py`, `core/tasks.py`

- Blog reevaluation: `*/4h limit=20` -> `*/3h limit=50`
- More blogs scored per cycle, more frequent evaluation

### PR #1139: Protect Beat Schedule from Deploy Overwrite
**File:** `Procfile`

- Added `--create-only` flag to `sync_celery_beat --apply` in release command
- Prevents every deploy from reverting DB schedule fixes
- Root cause: `sync_celery_beat --apply` overwrites existing PeriodicTask records

### PR #1140: ContextTracer.auto_repair_context AttributeError
**Files:** `core/tasks.py`, `core/agent_router.py`

- `auto_repair_context` is a module-level function in `core/services/context_tracing.py`
- Two call sites used `ContextTracer.auto_repair_context()` (class method syntax)
- Fixed: `from core.services.context_tracing import ContextTracer, auto_repair_context`

### PR #1141: Strengthen Novelty Scoring + Broaden PA Intent Routing
**Files:** `core/services/publish_gate.py`, `core/services/unified_pa_entrypoint.py`

**Novelty scoring** (`_score_novelty`):
- Old: Started at 0.8, max penalty -0.3, broke after first similar match
- New: Starts at 1.0, counts ALL similar blogs, proportional penalties
  - 1 exact match: score 0.75 (passes 0.6 threshold)
  - 2 exact matches: score 0.60 (borderline)
  - 3+ exact matches: fails (blocked)
- Strips stop words before word overlap comparison

**PA intent routing**:
- Added patterns: `'one titled'`, `'titled "'`, `'inaccuracy'`, `'inaccurate'`, `'factual error'`, `'fix the blog'`, `'edit the blog'`, etc.
- Updated title extraction regex: `(?:blog\s+)?(?:titled|called)` (makes "blog" prefix optional)
- Root cause: User said "one titled 'X'" which didn't match `'blog titled'`

### PR #1142: Fix 165 Daily Task Failures
**Files:** `core/tasks.py`, `core/services/human_attention_bridge.py`

1. `retry_blocked_research` (141/batch): `SpiderData.objects.filter(category__in=...)` -> `data_type__in=...`
2. `execute_agent_task` (24/day): `human_attention_bridge` signal handler accessed `instance.template.name` on deprecated `AgentExecution` model (which uses `.agent` not `.template`). Added `hasattr` fallback.

### Beat Schedule DB Fixes (Direct)
Applied directly to Railway DB:
- `auto-publish-approved-blogs`: `hour=6` -> `hour=*/2`, `queue=content`
- `reevaluate-enhanced-blogs`: `hour=5,11,17,23` -> `hour=*/3`, `limit=50`, `queue=content`

## Production Metrics

| Metric | Session 1003 Start | Session 1003 End | Session 1004 End |
|--------|--------------------|------------------|------------------|
| Published blogs | 8 | 40 | 40 (novelty fix deployed) |
| Signal clusters | 0 | 938 | 1,089 |
| Initiative stages | All Stage 1 | Stage 1-5 | Stage 1-5 active |
| Task failures/12h | ~47 | ~35 | 172 (new bugs found + fixed) |
| Agent success rate | 94.7% | 94.8% | 89.9% (24h) |
| Blog topic diversity | N/A | 19/40 same topic | Fix deployed |

## Files Modified

| File | Changes |
|------|---------|
| `Procfile` | `--create-only` flag on sync_celery_beat |
| `core/celery.py` | Reevaluate schedule */4 -> */3 |
| `core/tasks.py` | Limit 20->50, auto_repair_context fix, category->data_type |
| `core/agent_router.py` | auto_repair_context fix |
| `core/services/publish_gate.py` | Strengthened _score_novelty |
| `core/services/unified_pa_entrypoint.py` | Broader blog intent patterns |
| `core/services/human_attention_bridge.py` | hasattr fallback for template/agent |

## Verification

1. **Novelty**: Next batch of blogs should show topic diversity (no >3 blogs on same topic)
2. **PA**: "there is one titled 'X'" routes to content_review with read action
3. **Task failures**: `retry_blocked_research` and `execute_agent_task` errors drop to 0
4. **Beat schedule**: `auto-publish` runs every 2h, `reevaluate` every 3h
5. **Desk briefs**: `SportsBettingBrief` + `BlockchainAuditBrief` populate after next 6 AM run
