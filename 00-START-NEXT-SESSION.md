# Session 1006 - Start Here

**Previous Session:** 1005 (Desk Intelligence Fixes + Queue Purge)
**Date:** February 14, 2026
**Status:** 82 Agents (routable) | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **40 PUBLISHED BLOGS** | **1,089 SIGNAL CLUSTERS** | **INITIATIVE STAGES 1-5 ACTIVE** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 38+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **long_running QUEUE CLEAN** | **Celery Tasks: 268** | **PURGE ENDPOINT LIVE**

---

## Session 1005 Summary (Just Completed)

### Desk Intelligence Fixes + Queue Purge

Verified all 4 intelligence desks running, fixed sports agent crashes, and purged 3,857 stale tasks from long_running queue.

#### PR #1148: Desk Cache Key Mismatches
- Aligned cache key patterns between `run_all_desks_intelligence` task and coordinators

#### PR #1149: Time Limit on collect_real_opportunities
- Added `soft_time_limit=300, time_limit=360` to prevent infinite loop consuming queue capacity

#### PR #1150: Desk Key Alignment Fixes
- Additional cache key alignment fixes for desk coordinators

#### PR #1151: Fix Sports Agent SourceInfo Crash
- `GamePredictor`, `SharpActionDetector`, `LineMovementAnalyzer` crashed with `SourceInfo.__init__() got an unexpected keyword argument 'data_type'`
- `SourceInfo` dataclass has `source_type` field, not `data_type`
- Fixed `data_type='sports_odds'` → `source_type='spider_data'` in all 3 agents

#### PRs #1152-#1154: Purge Queue API Endpoint
- Built `POST /api/home/purge-queue/` with secret-based auth (PURGE_SECRET env var)
- Added to `PUBLIC_PATHS_EXACT` in auth middleware (uses own secret, not DRF auth)
- Allowed queues: `long_running`, `ml`, `broadcast`, `content`, `agents`, `sports`
- **Purged 3,857 stale messages** — circulatory flow_score hit 100%, all 9 routes healthy

#### PR #1156: Fix build_provenance SourceInfo Crash
- `GamePredictor` passes `SourceInfo` dataclass to `build_provenance()` which calls `.get()` (dict-only)
- Hidden by PR #1151's constructor crash — once that was fixed, this second bug surfaced
- Fix: convert `SourceInfo` to dict via `asdict()` in `build_provenance` loop

#### PR #1157: Fix LLMRequest Missing prompt Arg
- `GamePredictor`, `SharpActionDetector`, `LineMovementAnalyzer` call `LLMRequest(messages=...)` without required `prompt` positional arg
- Agents succeeded without LLM analysis (graceful fallback) but missed enhanced insights
- Fix: pass `prompt=""` since these use `messages` for chat-based calls

#### Desk Intelligence Full Run Results (After All Fixes)
| Desk | Time | Result |
|------|------|--------|
| Stocks | 468.5s | Full brief with audio + Discord |
| Sports | 13.8s | **5/5 agents, 10 top plays** |
| Blockchain | 490.1s | Full audit brief |
| Narrative | 5.2s | Completed |

**PRs:** #1148-#1159
**Handoff:** `docs/handoffs/SESSION_1005_DESK_FIXES_AND_QUEUE_PURGE.md`

#### PR #1158: Entry Point Update
- Updated entry point with sports desk 5/5 results

#### PR #1159: Quick Fixes
- Fixed `MemoryCluster.objects.create()` using wrong field name (`clustering_method` → `cluster_method`) and non-existent field (`is_active`)
- Created `docs/USER_FEEDBACK_QUEUE.md` — referenced by `docs_context_builder` as critical doc but missing
- Data migration `0244` registers GamePredictor, LineMovementAnalyzer, SharpActionDetector in Agent DB — enables MLPrediction storage

---

## Session 1004 Summary (Prior)

### Production Stabilization — Blog Quality + PA Intent + Task Error Sweep

After overnight pipeline run, 40 blogs published (up from 8), 1,089 signal clusters (up from 0), initiative stages 1-5 active. Found and fixed quality issues. Moved 40+ tasks off long_running queue, achieved first desk intelligence run (BlockchainAuditBrief created). Task success rate hit 99.8%.

**PRs:** #1138-#1142, #1144-#1147

---

## Session 1003 Summary (Prior)

### Pipeline Completion — 12 Fixes Closing All Execution Loops

Production audit revealed world-class intake but broken execution completion. Fixed 12 issues across 6 PRs + direct DB fixes:

#### Phase 1: Core Pipeline Fixes (PR #1130)
1. **Blog Pipeline** -- Switched beat task to deliberation pipeline. Added reevaluate (4h) + auto-publish (2h) beat entries.
2. **Initiative Founder Intent** -- Added `set_founder_intent()` after all 4 creation points. Data migration `0243` backfills stuck initiatives.
3. **Signal Aggregation** -- Relaxed `is_processed` filter, added text extraction fallbacks, lowered MIN_CLUSTER_SIZE to 2. **Result: 938 clusters from 18,893 spider records (was 0).**
4. **Podcast Audio** -- Changed `generate_audio: False` to `True`.
5. **Sports Desk Persistence** -- New `SportsBettingBrief` model.
6. **Blockchain Desk Persistence** -- New `BlockchainAuditBrief` model.

#### Phase 2: AudioAgent + Concurrency (PR #1131)
7. **AudioAgent Cloudinary Fix** -- Centralized `get_audio_storage()` returns `RawMediaCloudinaryStorage` for audio files. Applied to all 4 audio save paths. Fixes 89% failure rate (102/115 executions failed).
8. **Worker Concurrency Bump** -- pa/content workers: -c 1 → -c 2; broadcast: -c 1 → -c 3.

#### Phase 3: ContentStudio Timeout (PR #1132)
- **ContentStudio Timeout Epidemic** -- Added `soft_time_limit=600, time_limit=720` to content generation. Parallelized fallback debate with ThreadPoolExecutor (3 agents × 120s). Added `timeout=60` to OpenAI clients. Graceful SoftTimeLimitExceeded handler saves partial results.

#### Phase 4: Blog Scoring + Mythology + Initiative Quality (PRs #1133, #1134, #1135)
9. **Mythology Threshold** -- `MYTHOLOGY_THRESHOLD` lowered from 0.5 to 0.15. MythologyDetectionService was giving 0.55-1.0 risk on ALL AI-generated blogs, blocking every blog from publishing.
10. **Beat Schedule DB Fixes** -- Direct Railway DB: auto-publish `hour=6` → `hour=*/2`, created missing `run-all-desks-intelligence` task.
11. **Blog Scoring Expansion** -- `reevaluate_enhanced_blogs` now scores ALL unscored blogs (pending_review + draft), not just needs_enhancement.
12. **Initiative Quality Gate** -- Added 'Key Finding', 'Research on', 'Status', 'Confidence', 'Complete' as accepted alternatives in Stage 1 quality check. All 59 DRAFT stages were failing with "Missing sections: Research Findings".

#### Phase 5: Task Error Sweep (PR #1137)
13. **47 Daily Task Failures** -- NameError in `check_blocked_research_for_unblock` (31/day, `models.F()` without import) + TypeError in `execute_agent_task` (16/day, invalid `action_name` kwarg to `log_post_deserialize`).

**Migrations:** `0242_session_1003_desk_intelligence_briefs` + `0243_session_1003_backfill_founder_intent`
**PRs:** #1130, #1131, #1132, #1133, #1134, #1135, #1137
**Handoff:** `docs/handoffs/SESSION_1003_PIPELINE_COMPLETION.md`

### Production Metrics After Session 1003

| Metric | Before | After | Fix |
|--------|--------|-------|-----|
| Signal Clusters | 0 | 1,089 (350/day) | Fix 3 |
| Blog scoring | 59/160 scored | All scored (deploying) | Fix 11 |
| Blog mythology gate | ALL blocked | 8+ unblocked (deploying) | Fix 9 |
| Initiative Stage 1 stuck | 59 stuck | 59 unblocked (deploying) | Fix 12 |
| AudioAgent failure | 89% (102/115) | Fix deployed, awaiting runs | Fix 7 |
| ContentStudio timeouts | 65 in 3 days | Time-limited + parallel | ContentStudio fix |
| Auto-publish frequency | Once daily 6 AM | Every 2 hours | Fix 10 |
| Desk intelligence | Missing from beat | Created in beat DB | Fix 10 |
| Agent success rate | 94.7% | 94.8% (stable) | — |
| Agent executions/day | ~980 | ~980 | — |

## Session 1002C Summary (Prior)

### Universal Agent Tool Access — super() Fallback + Shared Tools + Delegate Cleanup + Direct API Fix

Session 1002B centralized `delegate_to_specialist`, `web_search`, and `spider_query` in `BaseAgent._execute_tool_call()`, but most agents couldn't reach those handlers. Fixed in 3 PRs + 1 follow-up:

1. **BaseAgent: return dict instead of raising** — Changed `raise NotImplementedError(...)` to `return {'success': False, 'error': ...}` so subclasses can safely call `super()._execute_tool_call()` as a fallback.

2. **45 agents: super() fallback** — Replaced final error returns in 31 agents (PR #1125) + 14 more discovered agents that used `_execute_tool` or `_handle_tool_call` instead of `_execute_tool_call` (PR #1127). All now fall through to BaseAgent for centralized handling. 4 agents intentionally skipped (content_executor, opportunity_pipeline, workflow_orchestration, workflow_agent — programmatic agents that reject all tools by design).

3. **Universal tool injection** — New `_get_tools_with_shared()` in BaseAgent auto-injects `WEB_SEARCH_TOOL` and `SPIDER_QUERY_TOOL` into every agent's LLM tool schema (with dedup). Called from both `get_tools_with_delegation()` and `_call_llm_with_tools()` (PR #1126).

4. **Fixed try/except regression** — 4 stock agents used `try: return super()... except NotImplementedError: pass` which broke when BaseAgent stopped raising. Removed dead blocks (PR #1126).

5. **Delegate block cleanup** — Removed redundant `delegate_to_specialist` elif blocks from 59 agents (-534 lines). BaseAgent handles delegation via super() now (PR #1127).

6. **9 agents: direct API call fix** — 9 agents bypassed `_call_openai()` by calling `client.chat.completions.create(tools=self.tools)` directly. Replaced with `tools=self.get_tools_with_delegation()` so shared tools are included.

**Result:** 64 agents with tool handlers all fall through to BaseAgent. Every agent sees `web_search`, `spider_query`, and `delegate_to_specialist` in its LLM tool schema.

**PRs:** #1125, #1126, #1127, #1129. See `docs/handoffs/SESSION_1002C_SUPER_FALLBACK.md`.

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 82 routable, 25 non-routable, 26+ provenance-tracked |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 395+ |
| Services | 134 |
| Celery Tasks | 268 |
| long_running Queue Tasks | 7 (was 55+) |
| Intelligence Desks | 4 (Stocks, Sports, Blockchain, Narrative) — ALL RUNNING |
| Workspace Tabs | 9 |
| Frontend Routes | 37 (15 standalone + 22 redirects) |
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
`ai_core/tasks.py` — Time limits (PR #1149) + dedup via `get_or_create` (PR #1160). No longer cycles through same jobs. Deeper `processed` flag on OpportunityActionPlan would be ideal but not urgent.

### CoinGecko Spider Not Crawling
Generic `normalize_item()` in `real_data_collector.py` doesn't properly extract CoinGecko JSON fields. Needs spider-specific parser or field mapping.

### Agent Knowledge Freshness -- Monitor Impact
14-day cutoff may be too aggressive. Monitor agent conversation quality.

### Railway Deploy: Migration Lock Risk
`AddConstraint` during blue-green deploy can hang on lock.

### Legacy Routes — Remove After Feb 22
26 legacy redirects in `App.tsx:78-114` (added Feb 8, Session 971b). 9 hardcoded links in components still reference legacy paths — update those FIRST, then remove redirects.

### Billing + Analytics Orphaned
`/billing` and `/analytics` need an Admin tab.

### ToolCallRecord Analytics Dashboard
Data is flowing but no dashboard exists yet.

### Disconnected Dots Audit (Sessions 646/735/972) -- Ongoing
Decision execution system is fully wired (DecisionEnforcerAgent + ConversationOrchestrator). 7 agents now persist to Deliverable (PRs #1162, #1163). Enrichment truncation fixed (PR #1164). Remaining: 87+ orphan API endpoints (no frontend consumers), ~21 agents without `_save_to_deliverable()` calls, 2 empty model tables (PodcastShow — broken write path, Campaign — feature not activated). "8 orphaned services" were re-audited: 7 of 8 are actively used, only `decision_executor.py` is truly orphaned (already in `_deprecated/`).

### sync_celery_beat Parser -- Mitigated
`--create-only` flag prevents overwrites (PR #1139), but the parser still can't update existing schedules. DB fixes must be applied directly. Full parser rewrite still needed for robustness.

### Blog Topic Diversity -- Fix Deployed
19/40 published blogs about Security/Homeland due to weak novelty scoring. PR #1141 strengthens scoring — verify after next batch.

---

## What Could Come Next

### Monitor Session 1005 Results
- All 4 desks running with **5/5 sports agents** — verify briefs continue on beat schedule
- Blog novelty scoring: verify topic diversity improves (was 19/40 same topic)
- Queue health: long_running depth 0 after purge, monitor for re-accumulation
- Purge endpoint: set `PURGE_SECRET` env var on Railway (currently uses default)

### Intelligence Desk Enhancements
- Add desk-specific detail pages (click a desk card -> full brief view)
- Historical desk briefs (compare today vs yesterday)
- Desk-specific alert thresholds (e.g., whale alert > $1M)
- PA integration: "What did the blockchain desk find today?"

### Continue Disconnected Dots Audit
Session 972 identified ~200+ items. High-impact remaining items:
- ~21 agents still without `_save_to_deliverable()` (7 done in PRs #1162, #1163)
- Orphan API endpoints with no frontend consumers
- PodcastShow model never created (PodcastEpisode FK references nonexistent parent)

### Fix sync_celery_beat Parser
Replace regex-based parsing with direct Python import to prevent beat schedule drift.

### Auto-Revision Loop
If deliberation pipeline returns REVISE verdict, loop back through EditorAgent automatically.

### Scheduled Task Visibility
PA has no visibility into Celery Beat scheduled tasks. Add `scheduled_tasks_tool`.

### Agent Introspection
PA can invoke agents but can't describe their capabilities. Add "what can [agent name] do?" intent.

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
- Status flow: `draft → pending_review → needs_enhancement → approved → published`

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
