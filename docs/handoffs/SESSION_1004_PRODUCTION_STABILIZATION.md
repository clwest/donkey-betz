---
originating_session: 1004
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1004: Production Stabilization — Blog Quality + PA Intent + Task Error Sweep + Queue Fix

**Date:** February 14, 2026
**Focus:** Fix quality issues discovered after overnight pipeline run + unblock desk intelligence

## Context

Session 1003 deployed 13 fixes to close broken execution loops. After running overnight:
- 40 blogs published (was 8) -- BUT 19/40 about same topic (Security/Homeland)
- 1,089 signal clusters (was 0)
- Initiative stages 1-5 active (was stuck at Stage 1)
- 172 task failures in 12h (retry_blocked_research: 141, execute_agent_task: 24)
- PA didn't use blog tools when user mentioned blog by title
- Beat schedules kept reverting on deploy
- Desk intelligence NEVER ran (long_running queue saturated)

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

### PR #1144: Move Heartbeat + check_nervous off long_running
**Files:** `core/settings.py`, `core/celery.py`

- Moved `run_heartbeat` and `check_nervous` from `long_running` to `broadcast` queue
- Heartbeat runs every 60s, takes 30s = 50% of long_running's concurrency-1 capacity
- `broadcast` worker uses `--pool=threads -c 3`, safe for SentenceTransformer

### PR #1145: Move I/O-bound ai_core tasks off long_running
**Files:** `core/settings.py`, `core/celery.py`

- `collect_real_opportunities`, `refresh_ai_content_opportunities`, `warm_up_spider_network` → `default` queue
- These are I/O-bound web scraping tasks, not memory-bound

### PR #1146: Redistribute 40+ tasks off long_running queue
**Files:** `core/settings.py`, `Procfile`

**Root cause:** `long_running` queue had **55+ tasks** competing for **concurrency 1**. Agent conversations, category rotations, autonomous monitors perpetually blocked desk intelligence.

- Bumped `celery-long-running` from `-c 1` to `-c 3`
- Moved 18 agent rotation tasks → `agents` queue
- Moved 14 autonomous monitor tasks → `agents` queue
- Moved 6 conversation/research tasks → `default` queue
- Moved 4 pipeline execution tasks → `default` queue
- Moved 4 narrative drift tasks → `default` queue
- Moved blog enhancement → `content` queue

**long_running now reserved for 7 truly memory-heavy tasks:**
`run_spider_network`, `generate_agent_dreams`, `run_autonomous_intelligence_loop`,
`run_agent_learning_cycle`, `score_and_promote_dreams`, `process_approved_dreams`,
`run_all_desks_intelligence`

### PR #1147: Add queue override to trigger-desks endpoint
**File:** `core/views_home.py`

- `POST /api/home/trigger-desks/` now accepts `{"queue": "default"}` to override queue
- Defaults to `long_running`
- Needed because celery-long-running had stuck pre-deploy tasks

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
| Task failures/12h | ~47 | ~35 | 172→0 (fixed) |
| Task success rate | 94.7% | 94.8% | 99.8% (6h window) |
| Blog topic diversity | N/A | 19/40 same topic | Fix deployed |
| BlockchainAuditBrief | 0 | 0 | **1** (first ever!) |
| Desk task execution | Never ran | Never ran | **First successful run** |
| Heartbeat queue | long_running | long_running | broadcast |
| long_running task count | 55+ | 55+ | **7** |

## Files Modified

| File | Changes |
|------|---------|
| `Procfile` | `--create-only` flag, long_running -c 1→3 |
| `core/celery.py` | Reevaluate schedule, queue assignments for heartbeat/ai_core/spiders |
| `core/settings.py` | Redistributed 50+ tasks across queues |
| `core/tasks.py` | Limit 20→50, auto_repair_context fix, category→data_type |
| `core/agent_router.py` | auto_repair_context fix |
| `core/services/publish_gate.py` | Strengthened _score_novelty |
| `core/services/unified_pa_entrypoint.py` | Broader blog intent patterns |
| `core/services/human_attention_bridge.py` | hasattr fallback for template/agent |
| `core/views_home.py` | Queue override for trigger-desks endpoint |

## Known Issues (Next Session)

1. **collect_real_opportunities infinite loop**: The task in `ai_core/tasks.py` cycles through jobs endlessly via `JobIncomeBridge.sync_to_income_builder()`. The old pre-deploy instance is still running on the long_running worker. Needs: investigate `sync_to_income_builder` for the infinite loop bug, or add a timeout/job-count limit.

2. **Stocks desk not creating new MarketIntelligenceBrief**: Last brief was at 16:05 UTC, desk task ran at 22:45 UTC but no new brief. MarketIntelligenceCoordinator may have errored silently.

3. **Sports desk not creating SportsBettingBrief**: `SportsBettingCoordinator.generate_brief()` may be failing. Need to check API keys and coordinator health.

4. **Blog factual accuracy**: LLM uses stale training data ("former President Trump"). Need to add current context to blog generation system prompt.

## Verification

1. **Novelty**: Next batch of blogs should show topic diversity (no >3 blogs on same topic) ✅ Deployed, blocking duplicates
2. **PA**: "there is one titled 'X'" routes to content_review with read action ✅ Deployed
3. **Task failures**: `retry_blocked_research` and `execute_agent_task` errors drop to 0 ✅ Verified
4. **Beat schedule**: `auto-publish` runs every 2h, `reevaluate` every 3h ✅ Verified
5. **Desk briefs**: BlockchainAuditBrief populated ✅, SportsBettingBrief still 0 ⚠️
6. **Queue distribution**: Heartbeat on broadcast ✅, 7 tasks on long_running ✅
