# Session 1022 - Start Here

**Previous Session:** 1021 (Initiative Pipeline Integrity — DRAFT Approval, No Skip-Ahead, Real Data Gathering)
**Date:** February 16, 2026
**Status:** 92 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **497 BLOGS** | **1,488 SIGNAL CLUSTERS** | **INITIATIVE PIPELINE INTEGRITY: FIXED** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 268** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **VIDEO STUDIO: 5 EDIT TOOLS** | **GOVERNMENT PAGE: 3 TABS + ASK A BILL RAG** | **CodeArtifact: PATCH-FIRST WORKFLOW LIVE** | **AGENT TIMEOUTS: FIXED** | **CONVERSATION JUNK: FIXED** | **FAST-TRACK STALL: FIXED** | **CONVERSATION DELEGATION: LIVE** | **INITIATIVE DEDUP: LIVE** | **TEMPORAL AWARENESS: LIVE** | **REAL DATA GATHERING: LIVE**

---

## Session 1021 Summary (Just Completed)

### Initiative Pipeline Integrity (PRs #1250, #1251, #1252)

**DRAFT stage approval (PR #1250):** `advance_initiative_pipeline` only matched `PENDING` stages without docs. After Session 1020 created SelfBlog docs for Stage 2+, stages with `DRAFT` status + existing document were silently skipped. Fixed by adding DRAFT+document detection path. Result: 2 initiatives reached Stage 5, 6 reached Stage 3 within 30 minutes.

**No stage skip-ahead (PR #1251):** The `range(1, 6)` loop generated documents for ANY pending stage — even future stages beyond `current_stage`. This caused "rubber-stamping" (4 stages approved in 10 min with zero work). Fixed by anchoring to `init.current_stage` with prior stage approval check.

**Real data gathering (PR #1252):** Deep audit revealed ALL Stage 1/2 documents contained garbage — parroted prompt instructions or random blog summaries. `TechnicalDocumentAgent` had no `topic`, no `research_context`, and no tools. Added `_gather_initiative_research()` that queries SpiderData, SignalClusters, AgentConversations, and Deliverables for real data before calling the agent. Also passes `topic` and `research_context` to agent context.

### PRs: #1250, #1251, #1252

---

## Session 1020 Summary

### Initiative Stage 2 Stall + Dedup + Temporal Awareness (PRs #1247, #1248)

- Stage 2 stall fixed: `handle_stage_task_completion()` now creates SelfBlog documents for Stage 2+
- Initiative dedup: similarity dedup on all 6 creation paths, circuit breaker on all paths
- Timeout tuning: OpenAI 120→60s, cleanup 120→45min, frequency 30→15min
- Temporal awareness: `_conversation_temporal_context()` injected into all 4 conversation prompt types

---

## Session 1019 Summary

### Conversation Agent Delegation (PRs #1244, #1245)

- `_preflight_gather_agent_data()` scans topic for agent name references, invokes up to 2 agents, injects results as context
- `CONVERSATION_DELEGATION_TOOL` allows LLM to request one mid-conversation delegation
- ThreadPoolExecutor broke Django DB connections — fixed with direct calls

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
| Active Initiatives | ~10 (some reached Stage 5 via rubber-stamp, need audit) |
| Blogs | 497 (28 published in last 24h) |
| Signal Clusters | 1,488 |
| Spider Data Records | 22,698 |
| Code Artifacts | 35 (all pending review) |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |

---

## Verify Before Starting

### 1. Real Data Gathering in Stage Documents (Session 1021 — CRITICAL)
- PR #1252 deployed. Check if new stage documents contain real spider data:
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import SelfBlog
  from django.utils import timezone; from datetime import timedelta
  recent = SelfBlog.objects.filter(
      category='initiative_stage',
      created_at__gte=timezone.now()-timedelta(hours=12)
  ).order_by('-created_at')[:5]
  for b in recent:
      print(f'{b.created_at.strftime(\"%H:%M\")} | {b.title[:60]}')
      print(f'  Content length: {len(b.full_text)} chars')
      has_data = 'Spider Intelligence' in b.full_text or 'Signal Clusters' in b.full_text or 'No data available' in b.full_text
      print(f'  Has real data markers: {has_data}')
      print(f'  First 200 chars: {b.full_text[:200]}')
      print()
  "
  ```
- Look for "Spider Intelligence", "Signal Clusters", or "No data available" markers — NOT parroted prompts or random blog content

### 2. Initiative Stage Progression (Session 1021)
- Verify stages advance one at a time (no skip-ahead):
  ```
  railway run python manage.py shell -c "
  from core.models import Initiative
  active = Initiative.objects.filter(status='ACTIVE')
  for i in active: print(f'Stage {i.current_stage} | {i.execution_speed} | {i.can_auto_progress} | {i.name[:50]}')
  "
  ```
- Initiatives that reached Stage 5 via rubber-stamp may need their Stage 3-5 docs regenerated

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
- Cleanup runs every 15min with 45min threshold:
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import AgentExecution
  from django.utils import timezone; from datetime import timedelta
  hung = AgentExecution.objects.filter(status='running', created_at__lt=timezone.now()-timedelta(minutes=45))
  print(f'Hung executions (>45min): {hung.count()}')
  "
  ```

### 5. Conversation Delegation (Session 1019)
- Check execution count stays modest:
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

### Rubber-Stamped Initiatives — NEEDS AUDIT
Initiatives that reached Stage 5 via the skip-ahead bug (PR #1251) have Stage 3-5 docs that were generated out of order with no real data. Consider:
- Invalidating Stage 3-5 docs for affected initiatives
- Resetting them to Stage 2 (or wherever they last had real work)
- Letting the new pipeline regenerate with real data

### PA Context Awareness — NEEDS WORK
PA doesn't understand page context. When user says "I just created an image but it's not displaying" from Image Studio, PA asks generic clarifying questions instead of checking ImageHistory.

### Remaining Agent Failures — REDUCED
Post all Session 1017-1021 fixes:
- `.metadata` crashes: **0** (PR #1236 fixed)
- False-positive timeouts: **0** (PR #1237 fixed)
- Conversation junk: **0** (PR #1239 fixed)
- Initiative stall: **FIXED** (PRs #1247, #1250 — Stage 2+ doc creation + DRAFT approval)
- Initiative duplicates: **FIXED** (PR #1247 — dedup on all creation paths)
- Initiative skip-ahead: **FIXED** (PR #1251 — current_stage anchoring)
- Initiative garbage docs: **FIXED** (PR #1252 — real data gathering)
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

**Initiative pipeline (Session 1021):**
- `advance_initiative_pipeline` only processes `init.current_stage` — never scans ahead
- Prior stage must be `APPROVED` before current stage is processed
- `_gather_initiative_research()` queries SpiderData, SignalClusters, AgentConversations, Deliverables
- `TechnicalDocumentAgent` has NO tools — only works with data provided in prompt/context
- Must pass `topic` and `research_context` in context dict (were missing before Session 1021)

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
- Has `conclusion` field for summary (NOT `messages_data`)
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

**InitiativeStage model:**
- Import from `core.models_document_registry` (NOT `core.models_unified_system`)

**Deliverable model:**
- Import from `core.models_deliverables` (NOT `core.models_document_registry`)

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
