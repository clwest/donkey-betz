# Session 1019 - Start Here

**Previous Session:** 1018 (End-to-End Audit + Conversation Junk Fix + Initiative Fast-Track Fix)
**Date:** February 16, 2026
**Status:** 92 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **497 BLOGS** | **1,488 SIGNAL CLUSTERS** | **INITIATIVE STAGES 1-5 UNBLOCKED** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 268** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **VIDEO STUDIO: 5 EDIT TOOLS** | **GOVERNMENT PAGE: 3 TABS + ASK A BILL RAG** | **CodeArtifact: PATCH-FIRST WORKFLOW LIVE** | **AGENT TIMEOUTS: FIXED** | **CONVERSATION JUNK: FIXED** | **FAST-TRACK STALL: FIXED**

---

## Session 1018 Summary (Just Completed)

### Conversation Topic Junk Fix (PR #1239)

20% of agent conversations (61/310 in 24h) were circular meta-discussions where agents discussed their own instructions as topics. Root cause: 751 `AgentKnowledgeSource` items with `[Learned]` prefix containing raw agent instructions were being selected as conversation topics.

**Fix:**
1. Excluded `[Learned]` and `EXTERNAL sources` items from knowledge source queries in both `run_agent_conversation` and `run_multi_agent_conversation` topic pickers
2. Added instruction marker filter to reject topics containing `DO NOT`, `web_search`, `spider_query`, `[Synthesis]`, etc.
3. Added cleanup of junk `AgentConversation` records to `cleanup_boardroom_junk` task

**Result:** Junk topics dropped from 61 (19%) to 0 post-fix.

### Initiative Fast-Track Stall Fix (PR #1240)

All 4 initiative auto-creation paths set `execution_speed='fast'`, which is designed to stop at Stage 2. Since every auto-created initiative got `fast`, 100% stalled at Stage 2.

**Root cause:** `can_auto_progress` returns False for `fast` speed at `stage >= 2`. All 4 creation services (ConversationInitiativePipeline, AutonomousActionExecutor, HiveMindExecutionPipeline, InitiativeIntegrationService) were hardcoding `execution_speed='fast'`.

**Fix:**
1. Changed all 4 creation paths from `'fast'` to `'balanced'` (normal 5-stage flow)
2. Batch-updated 21 existing stalled initiatives (10 ACTIVE + 11 TRIAGE) from fast → balanced on Railway

**Result:** All 10 active initiatives now show `can_auto_progress=True`. Stages 3-5 should start progressing.

### End-to-End System Audit

Comprehensive 24-hour audit of all autonomous subsystems:

| Subsystem | 24h Activity | Health |
|-----------|-------------|--------|
| Agent Executions | 437 total, 83.5% success | Timeouts: 0 post-fix, .metadata: 0 post-fix |
| Agent Conversations | 310 total, 309 legitimate | Junk topics: 0 post-fix (was 19%) |
| Agent Dreams | 43 new, 949/982 promoted | Healthy |
| Initiatives | 38 total, 10 ACTIVE unblocked | Fixed (was 100% stalled) |
| Signal Clusters | 328 new (1,488 total) | Healthy |
| Spider Data | 1,694 new (22,698 total) | All spider types active |
| Celery Tasks | 49,676 events, 99.94% success | 0 failures |
| Content Pipeline | 97 new blogs, 28 published | 101 deliberation sessions |
| Body Systems | 1,431 heartbeats, 100% healthy | All 7 components green |
| Code Artifacts | 35 pending review | Capture working |

### PRs: #1239, #1240

---

## Session 1017 Summary

### AgentResult `.metadata` Fix (PR #1236) + Agent Timeout Fix (PR #1237)

Added `.metadata` property alias on `AgentResult`. Added `soft_time_limit=2700` + `time_limit=3000` to all 3 agent dispatch tasks. Changed cleanup default from 30 to 60 minutes.

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 92 (54 routable, 25 non-routable, 26+ provenance-tracked) |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 396+ |
| Services | 134 |
| Celery Tasks | 268 |
| Intelligence Desks | 4 (Stocks, Sports, Blockchain, Narrative) — ALL RUNNING |
| Workspace Tabs | 9 |
| Frontend Routes | 27 |
| Agents Persisting Output | 43 (via `_save_to_deliverable()`) |
| PA Tools | 97 |
| PA Intents | 39 |
| Enrichment Services | 8 |
| Sports Leagues | 6 with predictions (NCAAB, NHL, EPL, La Liga, MLS, NCAAF) |
| Active Initiatives | 10 (all `balanced` speed, unblocked) |
| Blogs | 497 (28 published in last 24h) |
| Signal Clusters | 1,488 |
| Spider Data Records | 22,698 |
| Code Artifacts | 35 (all pending review) |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |

---

## Verify Before Starting

### 1. Initiative Progression (Session 1018)
- Initiatives should be progressing past Stage 2 now:
  ```
  railway run python manage.py shell -c "
  from core.models import Initiative
  active = Initiative.objects.filter(status='ACTIVE')
  for i in active: print(f'Stage {i.current_stage} | {i.execution_speed} | {i.can_auto_progress} | {i.name[:50]}')
  "
  ```
- Look for any at Stage 3+ (proves auto-progression is working)

### 2. Conversation Junk (Session 1018)
- Should be 0 junk topics in new conversations:
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import AgentConversation
  from django.utils import timezone; from datetime import timedelta
  recent = AgentConversation.objects.filter(started_at__gte=timezone.now()-timedelta(hours=24))
  junk = recent.filter(topic__startswith='[Learned]').count()
  print(f'Junk topics: {junk} / {recent.count()}')
  "
  ```

### 3. Agent Timeout Fix (Session 1017)
- `railway run python manage.py shell -c "from core.tasks import execute_agent_task; print(execute_agent_task.soft_time_limit)"` — should return `2700`

### 4. CodeArtifact API
- `curl $RAILWAY_URL/api/code-artifacts/ -H "Authorization: Token 0cdc1c72dba99ea637485076ee952d571440aa30"` — should return JSON list

---

## Known Issues / Open Items

### PA Context Awareness — NEEDS WORK
PA doesn't understand page context. When user says "I just created an image but it's not displaying" from Image Studio, PA asks generic clarifying questions instead of checking ImageHistory.

### Remaining Agent Failures — REDUCED
Post all Session 1017-1018 fixes:
- `.metadata` crashes: **0** (PR #1236 fixed)
- False-positive timeouts: **0** (PR #1237 fixed)
- Conversation junk: **0** (PR #1239 fixed)
- Initiative stall: **FIXED** (PR #1240)
- Remaining: AudioAgent (ElevenLabs quota, 10/day), VideoAgent (external API), assorted others (~25/day)

### Genuinely Hung Agents — INVESTIGATE
CTOAgent (max 33s normally) and CompetitorAnalysisAgent (max 37s) occasionally hang for 30+ min. Now properly killed by `soft_time_limit` at 45 min. Root cause likely: stuck on LLM API call or infinite tool loop. Investigate `httpx` timeout settings in LLM provider clients.

### CodeArtifact v2 — DEFERRED
- **PatchApplier service**: Auto-applying approved artifacts to git tree
- **Frontend UI**: Dedicated code review panel in workspace
- **Initiative FK wiring**: Auto-linking artifacts to triggering initiative
- **35 artifacts pending review** — no review workflow in frontend yet

### Initiative Circuit Breaker — DEPLOYED
Threshold at 20 active initiatives. Monitor to ensure meaningful initiatives still get created.

### Blog Topic Diversity — Monitor
19/40 published blogs about Security/Homeland due to weak novelty scoring. PR #1141 strengthens scoring — verify after next batch. Now at 497 total blogs.

### Sports Prediction Accuracy — MONITOR
Initial accuracy is 70.2% (mostly NCAAB). Monitor by sport/model as more leagues return data.

---

## Critical Patterns & Gotchas

**Django settings module:** `core.settings` (NOT `config.settings`).

**Initiative auto-creation (Session 1018):**
- All 4 creation paths now use `execution_speed='balanced'` (NOT `'fast'`)
- `fast` is MVP-only, stops at Stage 2 by design
- `balanced` allows normal 5-stage flow
- `can_auto_progress` still blocks at Stage 2+ if `founder_intent_set=False`

**Agent timeout limits (Session 1017):**
- `execute_agent_task`: `soft_time_limit=2700` (45 min), `time_limit=3000` (50 min)
- `execute_initiative_stage_task`: same
- `universal_agent_workspace_output`: same
- `cleanup_stale_agent_executions`: default 60 min (Beat kwargs: 120 min)
- `SoftTimeLimitExceeded` handlers update `AgentExecution` records properly

**AgentResult fields (Session 1017):**
- `success`, `message`, `data`, `error`, `agent_name`, `execution_time_ms`, `tool_calls`, `tokens_used`, `cost`
- `.content` is a @property alias for `.message`
- `.metadata` is a @property alias for `.data` (backward-compat added Session 1017)

**AgentDream fields:**
- Timestamp: `dreamed_at` (NOT `created_at`)
- Type: `dream_type` (NOT `type` or `status`)
- Import from `core.models_unified_system`

**SignalCluster fields:**
- Type: `pattern_type` (NOT `cluster_type`)
- Timestamp: `detected_at`
- Name: `name` (NOT `title`)

**AgentConversation fields:**
- Timestamp: `started_at` (NOT `created_at`)
- Import from `core.models_unified_system`

**ComponentStatus:**
- Import from `core.models_heart` (NOT `core.models`)

**DeliberationSession:**
- Import from `core.models_deliberation` (NOT `core.models_unified_system`)

**CodeArtifact model (Session 1016):**
- Import from `core.models_code_artifacts` (or `core.models`)
- `kind`: file_create, file_edit, patch
- `status`: pending, approved, rejected, applied, stale

**SpiderData actual fields (Session 989):**
- `spider_name`, `source_url`, `data_type`, `raw_data`, `processed_data`, `embedding_text`, `relevance_score`, `insights`, `is_processed`, `is_actionable`, `created_at`, `processed_at`
- DO NOT use `title`, `url`, `category`, `content` (don't exist)

**AgentExecution fields (Session 989):**
- `agent` is FK to Agent -- use `agent__name` in `.values()` and `agent__name__icontains` in filters
- No `success` field -- use `status='completed'` / `status='failed'`
- No `agent_name` field, no `started_at` field -- use `created_at`

**Initiative model:**
- Status values are UPPERCASE: `'ACTIVE'`, `'ARCHIVED'`, `'COMPLETED'`, `'TRIAGE'`
- Import from `core.models` (NOT `core.models_unified_system`)
- Field `name` (NOT `title`)
- `can_auto_progress` returns False for `execution_speed='fast'` at stage >= 2

**Cloudinary storage (Session 1015):**
- `default_storage.save()` uploads directly to Cloudinary
- `default_storage.url()` returns `https://res.cloudinary.com/...` URLs
- `default_storage.path()` RAISES — NEVER use on Railway

**Railway multi-service deployment:**
- Each Procfile process is a SEPARATE Railway service
- `railway up` deploys only the linked service
- `railway redeploy` during a build cancels build and redeploys OLD code
- GitHub push auto-deploys ALL services
- Celery workers can take up to 30 min to go live after push

**Model registration:** Use `core/models/__init__.py` (NOT `core/models.py`). New model imports: `from ..models_xxx import ClassName` with `app_label = 'core'`.

**Celery pool on Railway:** `--pool=prefork -c 1` (Linux), `--pool=threads` (macOS).

**ML imports:** Always lazy (inside methods). Module-level loads ~800MB.

**Auth for production API:** `Token 0cdc1c72dba99ea637485076ee952d571440aa30` (User: Donkeyking)
