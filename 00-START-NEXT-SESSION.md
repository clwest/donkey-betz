# Session 1010 - Start Here

**Previous Session:** 1009 (Deliverables Tab + Orphan Cleanup)
**Date:** February 15, 2026
**Status:** 82 Agents (routable) | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **40 PUBLISHED BLOGS** | **1,089 SIGNAL CLUSTERS** | **INITIATIVE STAGES 1-5 ACTIVE** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 38+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 238** | **Frontend Routes: 24**

---

## Session 1008-1009 Summary (Just Completed)

### Session 1008: Campaign Orchestrator + ToolCall Analytics Frontend
Connected Campaign Orchestrator and ToolCall Analytics dashboards to frontend (PR #1186). Removed dead `synthetic_user_generator` service (PR #1187).

### Session 1009: Deliverables Tab + Orphan Cleanup + celery-content OOM Fix
- **Deliverables Tab**: New Content Studio sub-tab with list/detail views, filtering, pagination, save/clone/templateize/export (PR #1188)
- **Orphan Cleanup**: Removed ~65 orphaned API endpoints from `core/urls.py` across 12 groups (voice-checkout, agent-mood, agent-collab, agent-intelligence, agent-learning, render-jobs, coleadership, agents.urls, style-memory, certifications, agent-analytics, agent-deployment, odds-calc)
- **Deleted**: `core/views_agent_mood.py` (679 lines), dead `agentCollaborationApi` from frontend
- **Docs**: Updated 8 docs with stale reference cleanup, created handoff doc
- **celery-content OOM Fix** (PR #1190): Root cause was `agent_category_rotation` and `full_agent_rotation` routed to `content` queue via `CELERY_TASK_ROUTES`. Views called `.delay()` without explicit queue, so these heavy tasks (running 20-74 agents each) landed on the content worker. With `-c 2`, two heavy tasks simultaneously pushed the 512MB container past its limit.
  - Moved 7 workspace/rotation tasks from `content` → `long_running` queue in `CELERY_TASK_ROUTES`
  - Reduced content worker from `-c 2` → `-c 1` (350MB peak vs 500MB)
  - Removed 6 phantom task routes + 3 phantom beat schedules for tasks that don't exist

**PRs:** #1186-#1190

---

## Session 1007 Summary

### Dead Code Purge & Pipeline Fixes

Massive cleanup session: ~10,350 lines of dead code removed across 8 PRs, plus auto-revision loop fix and ToolCallRecord analytics infrastructure.

#### PR #1177: Auto-Revision Loop Fix
- REVISE blogs now set to `needs_enhancement` (was `draft` — EditorAgent never picked them up)
- Beat schedule: `enhance-content` now every 4h (was daily 3 AM), moved to `content` queue

#### PR #1178: Beat Schedule Dedup + ToolCallAggregate Task
- Removed 11 duplicate beat entries (5 tasks were double-executing)
- Added `aggregate_tool_call_stats` task (daily 2:30 AM) populating `ToolCallAggregate` model

#### PR #1179: Dead Tasks + ToolCallAggregate API
- Removed 2 unreachable tasks (`get_gate_statistics`, `get_content_pipeline_stats`)
- Added `ToolCallAggregateViewSet` at `/api/v1/tool-call-aggregates/`

#### PR #1180: Dead CELERY_BEAT_SCHEDULE (605 lines)
- Removed ~600 lines of dead `CELERY_BEAT_SCHEDULE` from settings.py (overwritten by celery.py)
- Updated 2 views to read from `celery_app.conf.beat_schedule`

#### PR #1181: 30 Dead Tasks (1,672 lines)
- Removed 30 `@shared_task` functions never called, scheduled, or referenced
- Removed 3 unused settings dicts (`AGENT_SYSTEM`, `API_RATE_LIMITS`, `REDIS_KEY_PATTERNS`)

#### PR #1182: 5 Dead Modules (2,534 lines)
- Deleted `views_assistant_intelligent.py`, `views_assistant_rag_enhanced.py`, `views_unified_backend.py`
- Deleted `services/experiment_collision_service.py`, `services/_deprecated/decision_executor.py`
- Fixed duplicate `import os` and duplicate dict keys in `AI_CONFIG`

#### PR #1183: 21 Dead Commands + Dead Models (5,497 lines)
- Deleted 21 management commands (sports/ML, spider, core utilities)
- Deleted `models_spider_aggregation.py` (entirely dead file)

#### PR #1184: Restore DaVinci Resolve Task
- Restored `start_resolve_render` task accidentally removed in #1181

**PRs:** #1177-#1184
**Net lines removed:** ~10,350

---

## Session 1006 Summary

### Systematic Cleanup & Agent Persistence

Rapid-fire session closing disconnected dots: 30 agents now persist output to `Deliverable` model (was 0), enrichment data truncation fixed (was losing 85-95%), and 25 legacy redirect routes removed.

#### PR #1160: Profile Async + Temporal + Opportunity Dedup
- `ExtendedUserProfile` loaded via `asyncio.to_thread()` (was sync blocking)
- PA system prompt now includes current date/time
- `collect_real_opportunities`: `get_or_create` prevents reprocessing

#### PR #1161: Initiative Rate Limit + Stage Backfill
- Rate limit 40 -> 100, stage backfill batch 50 -> 200 every 15 min

#### PRs #1162, #1163, #1166, #1167, #1168: Agent Output Persistence (30 agents)
- All 30 applicable agents now call `_save_to_deliverable()` to persist output
- Established pattern: insert before `return AgentResult(...)` with appropriate tags/metadata
- 3 agents skipped (inherit from BaseBusinessResearchAgent, need parent class edit)

#### PR #1164: Enrichment Truncation Fix
- 3 truncation points caused 85-95% data loss before reaching LLM
- `ENRICHMENT_CAPS` per-section: 300-600 -> 1000-2000 chars
- `max_context_chars` overall: 3,000 -> 12,000 chars
- Tool result cap: 3,000 -> 8,000 chars

#### PR #1165: Legacy Route Links (21 links in 10 files)
- Updated `/body-health`, `/content-channels`, `/spiders`, `/blogs` -> workspace paths

#### PR #1167: Legacy Redirect Removal
- Removed 25 `<Navigate>` redirect routes from `App.tsx`
- Route count: 37 -> 24 (21 pages + 3 redirects)

**PRs:** #1160-#1168
**Handoff:** `docs/handoffs/SESSION_1006_SYSTEMATIC_CLEANUP.md`

---

## Session 1005 Summary (Prior)

### Desk Intelligence Fixes + Queue Purge

Verified all 4 intelligence desks running, fixed sports agent crashes, and purged 3,857 stale tasks from long_running queue.

- **PRs #1148-#1151:** Desk cache key alignment, time limits on `collect_real_opportunities`, sports agent `SourceInfo` crash fix
- **PRs #1152-#1154:** Purge queue API endpoint (`POST /api/home/purge-queue/`)
- **PR #1156:** `build_provenance` SourceInfo-to-dict fix
- **PR #1157:** `LLMRequest` missing `prompt` arg in 3 agents
- **PR #1159:** MemoryCluster bad kwargs, missing feedback queue, 3 unregistered market agents

**Result:** All 4 desks running (Sports: 5/5 agents, 10 top plays). Queue depth 0.
**Handoff:** `docs/handoffs/SESSION_1005_DESK_FIXES_AND_QUEUE_PURGE.md`

---

## Session 1004 Summary (Prior)

### Production Stabilization — Blog Quality + PA Intent + Task Error Sweep

40 blogs published (up from 8), 1,089 signal clusters (up from 0), initiative stages 1-5 active. Task success rate 99.8%.

**PRs:** #1138-#1142, #1144-#1147
**Handoff:** `docs/handoffs/SESSION_1004_PRODUCTION_STABILIZATION.md`

---

## Session 1003 Summary (Prior)

### Pipeline Completion — 12 Fixes Closing All Execution Loops

Fixed blog pipeline (deliberation), initiative founder intent (auto-set), signal aggregation (0 -> 938 clusters), podcast audio, sports/blockchain desk persistence.

**PRs:** #1130-#1135, #1137
**Handoff:** `docs/handoffs/SESSION_1003_PIPELINE_COMPLETION.md`

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 82 routable, 25 non-routable, 26+ provenance-tracked |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 395+ |
| Services | 134 |
| Celery Tasks | 238 (was 268 — 30 dead tasks removed) |
| long_running Queue Tasks | 7 (was 55+) |
| Intelligence Desks | 4 (Stocks, Sports, Blockchain, Narrative) — ALL RUNNING |
| Workspace Tabs | 9 |
| Frontend Routes | 24 (21 pages + 3 redirects) |
| Agents Persisting Output | 43 (via `_save_to_deliverable()`) |
| PA Tools | 97 |
| PA Intents | 38 |
| Enrichment Services | 8 |
| Attention Sections | 7 |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |
| Migrations | Through 0244 |
| Standalone Pages | `/stocks`, `/advisors`, `/betting`, `/neural-orchestra`, `/conversation-contract`, `/mythology-lab`, `/billing`, `/analytics`, `/docs-index` |

---

## Known Issues / Open Items

### collect_real_opportunities — MITIGATED
`ai_core/tasks.py` — Time limits (PR #1149) + dedup via `get_or_create` (PR #1160). No longer cycles through same jobs.

### CoinGecko Spider Not Crawling — FIXED
Added `current_price` to `normalize_item()` field mapping in `real_data_collector.py` (PR #1173). CoinGecko's `current_price` now maps to standard `price` field.

### Agent Knowledge Freshness -- Monitor Impact
14-day cutoff may be too aggressive. Monitor agent conversation quality.

### Railway Deploy: Migration Lock Risk
`AddConstraint` during blue-green deploy can hang on lock.

### Billing + Analytics Orphaned — FIXED
Added Billing and Analytics tabs to Admin page (PR #1176).

### ToolCallRecord Analytics Dashboard -- FIXED
Aggregation task populates `ToolCallAggregate` daily (PR #1178). REST API at `/api/v1/tool-call-aggregates/` (PR #1179). Frontend dashboard built as `ToolCallAnalyticsTab` in System tab (Session 1008).

### sync_celery_beat Parser -- Mitigated
`--create-only` flag prevents overwrites (PR #1139), but parser can't update existing schedules. DB fixes must be applied directly.

### Blog Topic Diversity -- Fix Deployed
19/40 published blogs about Security/Homeland due to weak novelty scoring. PR #1141 strengthens scoring — verify after next batch.

---

## What Could Come Next

### Monitor Session 1006 Results
- Verify Deliverable records accumulating from 30 agents
- Check enrichment quality improvement in PA responses (caps raised 4-6x)
- Monitor queue health (long_running depth was 0 after purge)

### Remaining Disconnected Dots
- v1/ API namespace (185 endpoints): NOT orphaned — it's the primary API surface used by frontend and PA agent. DO NOT remove.
- Remaining orphan API endpoints need careful audit (many are actually consumed via API client, not direct path references)
- PodcastShow model never created (FK nullable, episodes work, Show grouping unused)
- Campaign model empty (feature not activated)

### Intelligence Desk Enhancements
- Add desk-specific detail pages (click a desk card -> full brief view)
- Historical desk briefs (compare today vs yesterday)
- Desk-specific alert thresholds (e.g., whale alert > $1M)
- PA integration: "What did the blockchain desk find today?"

### Auto-Revision Loop -- FIXED
REVISE blogs now set to `needs_enhancement` (was `draft`). EditorAgent picks them up every 4h, PublishGate re-evaluates every 3h, auto-publish every 2h. Full loop: REVISE → needs_enhancement → EditorAgent → PublishGate → approved → published (PR #1177).

### Scheduled Task Visibility -- FIXED
Added `scheduled_tasks_tool` PA intent + handler. Users can ask "what's scheduled?" or "show celery beat tasks" (PR #1176).

### Agent Introspection -- FIXED
Added `agent_introspection` PA intent + handler. Users can ask "what can [agent] do?" (PR #1176).

---

## Critical Patterns & Gotchas

**Django settings module:** `core.settings` (NOT `config.settings`).

**SpiderData actual fields (Session 989):**
- `spider_name`, `source_url`, `data_type`, `raw_data`, `processed_data`, `embedding_text`, `relevance_score`, `insights`, `is_processed`, `is_actionable`, `created_at`, `processed_at`
- DO NOT use `title`, `url`, `category`, `content` (don't exist)

**AgentExecution fields (Session 989):**
- `agent` is FK to Agent -- use `agent__name` in `.values()` and `agent__name__icontains` in filters
- No `success` field -- use `status='completed'` / `status='failed'`
- No `agent_name` field, no `started_at` field -- use `created_at`

**CeleryTaskEvent fields:**
- `duration_seconds`, `error_message`, `error_type`, `finished_at`, `id`, `queue`, `started_at`, `status`, `task_id`, `task_name`, `worker`
- NO `timestamp` field -- use `started_at`

**Initiative model:**
- Status values are UPPERCASE: `'ACTIVE'`, `'ARCHIVED'`, `'COMPLETED'`
- Import from `core.models` (NOT `core.models_unified_system`)
- Field `name` (NOT `title`)

**SelfBlog model:**
- Import from `core.models_unified_system`
- Has `created_at` but NO `updated_at`
- Status flow: `draft -> pending_review -> needs_enhancement -> approved -> published`

**SignalCluster model:**
- Import from `core.models`
- Timestamp field is `detected_at`

**DeliberationSession.participants (Session 989):**
- JSONField containing dicts (not strings)
- Extract `.get('name')` before `', '.join()`

**Initiative ownership (Session 996):**
- `owner` = FK to User (nullable), `owner_agent` = CharField (agent name)
- Only one should be set at a time (assign_owner clears the other)
- Auto-assigned via `PROGRAM_OWNER_MAP` or `created_by` at creation time

**Odds-consensus predictions (Session 998B):**
- `_american_to_probability()` in `views_odds_sports.py` -- converts American odds to implied probability
- Only predicts when implied prob > 55%
- `prediction_correct` field: `True`/`False` for completed, `None` for pending

**Intelligence desk cache keys (Session 1000):**
- `desk:stocks:latest`, `desk:sports:latest`, `desk:blockchain:latest`, `desk:narrative:latest`
- 6-hour TTL, regenerated daily at 6 AM or on-demand via `/api/home/trigger-desks/`
- Trigger endpoint accepts `{"queue": "default"}` to override queue (PR #1147)

**Railway multi-service deployment (Session 989):**
- Each Procfile process is a SEPARATE Railway service
- `railway up` deploys only the linked service
- `railway redeploy` during a build cancels build and redeploys OLD code
- GitHub push auto-deploys ALL services
- To check a specific worker: `railway service link celery-pa` then `railway logs`

**Model registration:** Use `core/models/__init__.py` (NOT `core/models.py`). New model imports: `from ..models_xxx import ClassName` with `app_label = 'core'`.

**Celery pool on Railway:** `--pool=prefork -c 1` (Linux), `--pool=threads` (macOS).

**ML imports:** Always lazy (inside methods). Module-level loads ~800MB.

**LLM Provider Registry:** `from core.services.llm_provider_registry import get_llm_provider_registry, LLMRequest`

**PA intent routing:** More specific patterns BEFORE generic catch-alls. Always test new patterns against likely user questions.

**Model import paths:**
- `HeartBeat`: `core.models_heart` -- `recorded_at`, `overall_status`
- `SpiderData`: `core.models_unified_system`
- `CeleryTaskEvent`: `core.models_celery_telemetry`
- `DeliberationSession`: `core.models_deliberation`

**Purge queue endpoint (Session 1005):**
```bash
curl -X POST https://donkey-betz-platform-production.up.railway.app/api/home/purge-queue/ \
  -H 'Content-Type: application/json' \
  -d '{"queue": "long_running", "secret": "donkey-purge-2026"}'
```
Allowed queues: `long_running`, `ml`, `broadcast`, `content`, `agents`, `sports`. Uses `PURGE_SECRET` env var (default: `donkey-purge-2026`).

**Auth for production API:** `Token 0cdc1c72dba99ea637485076ee952d571440aa30` (User: Donkeyking)
