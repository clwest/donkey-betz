# Session 1018 - Start Here

**Previous Session:** 1017 (Agent Execution Pipeline Audit — Timeouts + .metadata Fix)
**Date:** February 16, 2026
**Status:** 92 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **40+ PUBLISHED BLOGS** | **1,131 SIGNAL CLUSTERS** | **INITIATIVE STAGES 1-5 ACTIVE** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 268** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **VIDEO STUDIO: 5 EDIT TOOLS** | **GOVERNMENT PAGE: 3 TABS + ASK A BILL RAG** | **CodeArtifact: PATCH-FIRST WORKFLOW LIVE** | **AGENT TIMEOUTS: FIXED**

---

## Session 1017 Summary (Just Completed)

### AgentResult `.metadata` Backward-Compat Fix (PR #1236)

`AgentResult` has `.data` but NOT `.metadata`. Some code path was calling `.metadata` causing `AttributeError` crashes on OpportunityScoringAgent and SystemIntelligenceAgent (~67 failures/day).

**Fix:** Added `.metadata` property alias on `AgentResult` in `core/agents/base_agent.py` that returns `.data`.

**Exhaustive search:** Searched all code paths (`agent_router.py`, `tasks.py`, `tool_dispatcher.py`, all BaseAgent methods) — couldn't find the `.metadata` access in current code. The property is a permanent defensive fix.

### Agent Timeout Pipeline Fix (PR #1237)

Investigated 28 agent timeouts across 15 agents in 24 hours. Found two root causes:

**Root Cause 1 — No Celery time limits:** Three agent dispatch tasks (`execute_agent_task`, `execute_initiative_stage_task`, `universal_agent_workspace_output`) had no `time_limit` or `soft_time_limit`. Hung agents ran indefinitely until the cleanup task caught them, leaving orphaned `in_progress` execution records.

**Root Cause 2 — Cleanup threshold bug:** `cleanup_stale_agent_executions` had a 30-min default, but the Beat schedule intended 120 min via kwargs that weren't being passed. The 30-min threshold was too aggressive for legitimately slow agents:
- WorkflowAgent: avg 6 min, max 22 min
- MeetingCoordinatorAgent: avg 9 min, max 24 min

**Two categories of timed-out agents identified:**
| Category | Agents | Diagnosis |
|----------|--------|-----------|
| Legitimately slow | WorkflowAgent, MeetingCoordinatorAgent | Max runtime close to 30-min threshold — false positives |
| Genuinely hung | CTOAgent (max 33s), CompetitorAnalysisAgent (max 37s) | Stuck on LLM API calls — true hangs |

**Fixes applied:**
1. Added `soft_time_limit=2700` (45 min) + `time_limit=3000` (50 min) to all 3 dispatch tasks
2. Added `SoftTimeLimitExceeded` handlers that properly update `AgentExecution` records with `status='failed'`
3. Changed cleanup default from 30 to 60 minutes

**Deployed & verified on Railway:** New Celery workers confirmed running with updated thresholds. WorkflowAgent at 21 min no longer falsely killed.

### PRs: #1236, #1237

---

## Session 1016 Summary

### CodeArtifact: Patch-First Workflow (PRs #1232, #1233)
When agents generate code on Railway (no writable workspace), the output was silently lost. Now captured as reviewable `CodeArtifact` records.

### Deep Agent Audit + Fixes (PR #1234)
Audited all 92 agents for silent failure patterns. Found 5 agents beyond CodeGeneratorAgent silently losing output. Added CodeArtifact capture to BaseAgent.

### Activity Feed Gap Root Cause
`can_auto_progress` returns False for `execution_speed='fast'` at stage >= 2. All initiatives default to `fast`, so nothing auto-progresses past Stage 2.

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
| Agents with CodeArtifact Capture | 6 (CodeGenerator, FullStack, DevOps, TechDoc, CodeReview + all BaseAgent subclasses) |
| PA Tools | 97 |
| PA Intents | 39 |
| Enrichment Services | 8 |
| Sports Leagues | 6 with predictions (NCAAB, NHL, EPL, La Liga, MLS, NCAAF) |
| Active Initiatives | ~34 (most stalled at Stage 2 — fast-track gate) |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |

---

## Verify Before Starting

### 1. Agent Timeout Fix
- `railway run python manage.py shell -c "from core.tasks import execute_agent_task; print(execute_agent_task.soft_time_limit)"` — should return `2700`
- Check for `soft_time_limit` errors: `AgentExecution.objects.filter(error_message__icontains='soft_time_limit').count()` — any > 0 means a hung agent was properly killed
- Cleanup threshold: `from core.tasks import cleanup_stale_agent_executions; import inspect; print(inspect.signature(cleanup_stale_agent_executions).parameters['minutes_threshold'].default)` — should return `60`

### 2. CodeArtifact API
- `curl $RAILWAY_URL/api/code-artifacts/ -H "Authorization: Token 0cdc1c72dba99ea637485076ee952d571440aa30"` — should return JSON list

### 3. Custom Domain SSL
- Try `https://www.donkeybetz.com` — should show login page with valid cert
- If still cert error: delete domain in Railway dashboard → re-add → update CNAME

---

## Known Issues / Open Items

### Initiative Fast-Track Stall — DECISION NEEDED
`can_auto_progress` blocks ALL fast-track initiatives at Stage 2. Since every initiative defaults to `fast`, nothing auto-progresses beyond Stage 1→2. Options:
1. Change default `execution_speed` for new initiatives (e.g. to `standard`)
2. Relax the gate so `fast` doesn't block at Stage 2
3. Add PA command to batch-promote eligible initiatives
4. Keep as-is (human must explicitly advance each one)

### PA Context Awareness — NEEDS WORK
PA doesn't understand page context. When user says "I just created an image but it's not displaying" from Image Studio, PA asks generic clarifying questions instead of checking ImageHistory.

### Remaining Agent Failures — REDUCED
Post-.metadata-fix and timeout-fix, failure rate should drop significantly. Monitor:
- `.metadata` crashes: should be 0 (PR #1236 fixed)
- False-positive timeouts: should be 0 (PR #1237 fixed)
- Remaining failures: ContentWriterAgent, AudioAgent, VideoAgent (likely ElevenLabs quota / external API issues)

### Genuinely Hung Agents — INVESTIGATE
CTOAgent (max 33s normally) and CompetitorAnalysisAgent (max 37s) occasionally hang for 30+ min. Now properly killed by `soft_time_limit` at 45 min. Root cause likely: stuck on LLM API call or infinite tool loop. Investigate `httpx` timeout settings in LLM provider clients.

### CodeArtifact v2 — DEFERRED
- **PatchApplier service**: Auto-applying approved artifacts to git tree
- **Frontend UI**: Dedicated code review panel in workspace
- **Initiative FK wiring**: Auto-linking artifacts to triggering initiative

### Initiative Circuit Breaker — DEPLOYED
Threshold at 20 active initiatives. Monitor to ensure meaningful initiatives still get created.

### Blog Topic Diversity — Monitor
19/40 published blogs about Security/Homeland due to weak novelty scoring. PR #1141 strengthens scoring — verify after next batch.

### Sports Prediction Accuracy — MONITOR
Initial accuracy is 70.2% (mostly NCAAB). Monitor by sport/model as more leagues return data.

---

## Critical Patterns & Gotchas

**Django settings module:** `core.settings` (NOT `config.settings`).

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

**CodeArtifact model (Session 1016):**
- Import from `core.models_code_artifacts` (or `core.models`)
- `kind`: file_create, file_edit, patch
- `status`: pending, approved, rejected, applied, stale
- BaseAgent captures via `_capture_files_as_artifacts()` / `_capture_single_file_artifact()`
- CodeGeneratorAgent captures via `_capture_code_artifact()`

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
