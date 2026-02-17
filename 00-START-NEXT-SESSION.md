# Session 1021 - Start Here

**Previous Session:** 1020 (Initiative Stage 2 Stall, Dedup, Temporal Awareness)
**Date:** February 16, 2026
**Status:** 92 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **497 BLOGS** | **1,488 SIGNAL CLUSTERS** | **INITIATIVE STAGES 1-5 UNBLOCKED** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 268** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **VIDEO STUDIO: 5 EDIT TOOLS** | **GOVERNMENT PAGE: 3 TABS + ASK A BILL RAG** | **CodeArtifact: PATCH-FIRST WORKFLOW LIVE** | **AGENT TIMEOUTS: FIXED** | **CONVERSATION JUNK: FIXED** | **FAST-TRACK STALL: FIXED** | **CONVERSATION DELEGATION: LIVE** | **INITIATIVE DEDUP: LIVE** | **TEMPORAL AWARENESS: LIVE**

---

## Session 1020 Summary (Just Completed)

### Initiative Stage 2 Stall + Dedup + Temporal Awareness (PRs #1247, #1248)

**Stage 2 stall (19/21 initiatives stuck):** Stage 1 gets a SelfBlog document at initialization, but `handle_stage_task_completion()` never created documents for Stage 2+. The hard invariant `if stage.document:` blocked auto-approval permanently. Fixed by creating SelfBlog documents from task output when stages complete.

**Initiative duplicates (4 "audit integrity" variants):** Added similarity dedup (`find_similar_initiative()`) to `AgentDream.promote_to_initiative()` and `InitiativeIntegrationService`. Added circuit breaker to `HiveMindExecutionPipeline` and `ConversationInitiativePipeline` (both were missing). Archived 5 duplicates on Railway (21 → 16).

**Timeout tuning:** OpenAI client 120→60s, cleanup threshold 120→45min, frequency 30→15min.

**Conversation date hallucination:** Agents citing "Oct 10, 2023" as current. Conversation prompts in `tasks.py` had no date context (unlike individual agent execution). Added `_conversation_temporal_context()` helper, injected into all 4 conversation prompt types.

### PRs: #1247, #1248

---

## Session 1019 Summary

### Conversation Agent Delegation (PRs #1244, #1245)

- `_preflight_gather_agent_data()` scans topic for agent name references, invokes up to 2 agents, injects results as context
- `CONVERSATION_DELEGATION_TOOL` allows LLM to request one mid-conversation delegation
- ThreadPoolExecutor broke Django DB connections — fixed with direct calls

---

## Session 1018 Summary

### Conversation Junk Fix (PR #1239) + Initiative Fast-Track Stall Fix (PR #1240) + E2E Audit

- Excluded `[Learned]` items from conversation topic pickers (junk 19% → 0%)
- Changed initiative auto-creation from `execution_speed='fast'` to `'balanced'`
- Comprehensive 24h audit: 99.94% Celery success, 83.5% agent success

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
| Active Initiatives | 16 (all `balanced` speed, Stage 2 fix deployed) |
| Blogs | 497 (28 published in last 24h) |
| Signal Clusters | 1,488 |
| Spider Data Records | 22,698 |
| Code Artifacts | 35 (all pending review) |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |

---

## Verify Before Starting

### 1. Initiative Stage 2+ Progression (Session 1020 — CRITICAL)
- Stage 2 fix deployed but needs time for new stage tasks to trigger. Check if any have progressed:
  ```
  railway run python manage.py shell -c "
  from core.models import Initiative
  active = Initiative.objects.filter(status='ACTIVE')
  for i in active: print(f'Stage {i.current_stage} | {i.execution_speed} | {i.can_auto_progress} | {i.name[:50]}')
  "
  ```
- Look for any at Stage 3+ (proves the fix is working)

### 2. Temporal Awareness in Conversations (Session 1020)
- Check recent conversations for date context:
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import AgentConversation
  from django.utils import timezone; from datetime import timedelta
  recent = AgentConversation.objects.filter(started_at__gte=timezone.now()-timedelta(hours=12)).order_by('-started_at')[:5]
  for c in recent: print(f'{c.started_at.strftime(\"%H:%M\")} | {c.topic[:60]}')
  "
  ```
- Spot-check messages for "2024" or "2023" date references treated as current

### 3. Initiative Dedup (Session 1020)
- Verify no new duplicates created:
  ```
  railway run python manage.py shell -c "
  from core.models import Initiative
  from collections import Counter
  names = list(Initiative.objects.filter(status__in=['ACTIVE','TRIAGE']).values_list('name', flat=True))
  print(f'Active+Triage: {len(names)}')
  dupes = {k:v for k,v in Counter(names).items() if v > 1}
  if dupes: print(f'DUPLICATES: {dupes}')
  else: print('No exact duplicates')
  "
  ```

### 4. Agent Timeout & Cleanup (Session 1020)
- Cleanup now runs every 15min with 45min threshold:
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import AgentExecution
  from django.utils import timezone; from datetime import timedelta
  hung = AgentExecution.objects.filter(status='running', created_at__lt=timezone.now()-timedelta(minutes=45))
  print(f'Hung executions (>45min): {hung.count()}')
  "
  ```

### 5. Conversation Delegation (Session 1019)
- Check execution count stays modest (not runaway):
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import AgentExecution
  from django.utils import timezone; from datetime import timedelta
  recent = AgentExecution.objects.filter(created_at__gte=timezone.now()-timedelta(hours=24))
  print(f'Total executions (24h): {recent.count()}')
  "
  ```

---

## Known Issues / Open Items

### PA Context Awareness — NEEDS WORK
PA doesn't understand page context. When user says "I just created an image but it's not displaying" from Image Studio, PA asks generic clarifying questions instead of checking ImageHistory.

### Remaining Agent Failures — REDUCED
Post all Session 1017-1020 fixes:
- `.metadata` crashes: **0** (PR #1236 fixed)
- False-positive timeouts: **0** (PR #1237 fixed)
- Conversation junk: **0** (PR #1239 fixed)
- Initiative stall: **FIXED** (PR #1247 — Stage 2+ doc creation)
- Initiative duplicates: **FIXED** (PR #1247 — dedup on all creation paths)
- Conversation date hallucination: **FIXED** (PR #1248 — temporal awareness)
- Remaining: AudioAgent (ElevenLabs quota, ~7/day), assorted others (~18/day)

### CodeArtifact v2 — DEFERRED
- **PatchApplier service**: Auto-applying approved artifacts to git tree
- **Frontend UI**: Dedicated code review panel in workspace
- **Initiative FK wiring**: Auto-linking artifacts to triggering initiative
- **35 artifacts pending review** — no review workflow in frontend yet

### Initiative Circuit Breaker — DEPLOYED
Threshold at 20 active initiatives. All 6 creation paths now have circuit breaker + similarity dedup.

### Blog Topic Diversity — Monitor
19/40 published blogs about Security/Homeland due to weak novelty scoring. PR #1141 strengthens scoring — verify after next batch. Now at 497 total blogs.

### Sports Prediction Accuracy — MONITOR
Initial accuracy is 70.2% (mostly NCAAB). Monitor by sport/model as more leagues return data.

---

## Critical Patterns & Gotchas

**Django settings module:** `core.settings` (NOT `config.settings`).

**Initiative 6 creation paths (Session 1020):**
- `InitiativeIntegrationService` — has similarity dedup + circuit breaker
- `AgentDream.promote_to_initiative()` — has similarity dedup + circuit breaker
- `HiveMindExecutionPipeline` — has circuit breaker (Session 1020)
- `ConversationInitiativePipeline` — has circuit breaker (Session 1020)
- `AutonomousActionExecutor` — has circuit breaker
- `create_initiative_from_deliverables()` — has circuit breaker

**Initiative auto-creation (Session 1018):**
- All paths now use `execution_speed='balanced'` (NOT `'fast'`)
- `fast` is MVP-only, stops at Stage 2 by design
- `balanced` allows normal 5-stage flow

**Agent timeout limits (Session 1017, tuned Session 1020):**
- `execute_agent_task`: `soft_time_limit=2700` (45 min), `time_limit=3000` (50 min)
- OpenAI client timeout: 60s (reduced from 120s in Session 1020)
- `cleanup_stale_agent_executions`: threshold 45min, runs every 15min

**AgentResult fields (Session 1017):**
- `success`, `message`, `data`, `error`, `agent_name`, `execution_time_ms`, `tool_calls`, `tokens_used`, `cost`
- `.content` is a @property alias for `.message`
- `.metadata` is a @property alias for `.data`

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

**ThreadPoolExecutor + Django (Session 1019):**
- Do NOT use `ThreadPoolExecutor` for `AgentRouter.route()` or other Django ORM operations
- Child threads get separate DB connections, results can be silently lost
- Use direct calls instead

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
