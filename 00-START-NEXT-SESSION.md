# Session 1017 - Start Here

**Previous Session:** 1016 (CodeArtifact Patch-First Workflow + Deep Agent Audit)
**Date:** February 16, 2026
**Status:** 92 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **40+ PUBLISHED BLOGS** | **1,131 SIGNAL CLUSTERS** | **INITIATIVE STAGES 1-5 ACTIVE** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 268** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **VIDEO STUDIO: 5 EDIT TOOLS** | **GOVERNMENT PAGE: 3 TABS + ASK A BILL RAG** | **CodeArtifact: PATCH-FIRST WORKFLOW LIVE**

---

## Session 1016 Summary (Just Completed)

### CodeArtifact: Patch-First Workflow (PRs #1232, #1233)

When agents generate code on Railway (no writable workspace), the output was silently lost. Now captured as reviewable `CodeArtifact` records.

**New model:** `CodeArtifact` (`core/models_code_artifacts.py`)
- Fields: agent_name, kind (file_create/file_edit/patch), status (pending/approved/rejected/applied/stale), target_path, content, content_before, description
- FKs: agent_execution, initiative, reviewed_by (all nullable)
- Migration: `0246_code_artifact_model` — applied on Railway

**New API:** `/api/code-artifacts/`
- `GET /` — list with `?status=`, `?agent_name=`, `?initiative=`, `?kind=` filters
- `GET /{id}/` — full detail with code content
- `POST /{id}/approve/` — approve with optional review_note
- `POST /{id}/reject/` — reject with optional review_note

**CodeGeneratorAgent:** `_write_file()` and `_edit_file()` capture artifacts at all workspace-unavailability failure points. NOT captured for logic errors (file-not-found, old_text-not-found).

### Deep Agent Audit + Fixes (PR #1234)

Audited all 92 agents for silent failure patterns. Found 5 agents beyond CodeGeneratorAgent silently losing output on Railway.

**Fix 1 — BaseAgent._write_files_to_workspace():** Added CodeArtifact capture at all 3 failure points (no manager, no workspace, no write permission) + individual file write failures. Covers: FullStackDeveloperAgent, DevOpsAgent, TechnicalDocumentAgent, CodeReviewAgent.

**Fix 2 — CodeReviewAgent._read_file():** Now tries WorkspaceManager first before falling back to direct `open()`. Works on Railway where filesystem is empty.

**Fix 3 — BaseAgent._regenerate_docs_index():** Replaced `subprocess.run(['.venv/bin/python', ...])` with `django.core.management.call_command()`. Works on any environment.

### Activity Feed Gap Root Cause

Investigated 11-hour gap in Activity Feed. Root cause: `can_auto_progress` returns `False` when `execution_speed == 'fast' AND current_stage >= 2`. Since ALL initiatives default to `fast`, nothing auto-progresses past Stage 2. Celery tasks ran fine (2000/hour) but found nothing eligible. Documented in `docs/topics/initiative-pipeline.md`.

### Docs Updated (PR #1233)
- `docs/topics/agent-system.md` — CodeArtifact section, agent count to 92
- `docs/topics/initiative-pipeline.md` — fast-track stall behavior documented
- `docs/DATABASE_MODEL_REFERENCE.md` — CodeArtifact model section
- `docs/API_PATH_POLICY.md` — `/api/code-artifacts/` endpoint
- `docs/BACKEND_REFERENCE.md` — Code Artifacts endpoints
- `docs/INDEX.md` — regenerated

**PRs:** #1232, #1233, #1234

---

## Session 1015 Summary

### Government & Legislation Page (PRs #1226-#1229)
Full-stack `/government` page with Hub, Bills, and Ask A Bill tabs.

### Image Studio Cloudinary Fix (PR #1230)
Images were generated but never saved to gallery. Fixed `save_watermarked_image` to return `default_storage.url()` directly.

### Custom Domain DNS (IN PROGRESS)
`www.donkeybetz.com` custom domain added to Railway. SSL cert provisioning pending.

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 92 (54 routable, 25 non-routable, 26+ provenance-tracked) |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 396+ (added CodeArtifact) |
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

### 1. CodeArtifact API
- `curl $RAILWAY_URL/api/code-artifacts/ -H "Authorization: Token 0cdc1c72dba99ea637485076ee952d571440aa30"` — should return JSON list
- After an autonomous agent chain runs, check for new artifacts

### 2. Custom Domain SSL
- Try `https://www.donkeybetz.com` — should show login page with valid cert
- If still cert error: delete domain in Railway dashboard → re-add → update CNAME

### 3. Initiative Fast-Track Gate
- 8 ACTIVE initiatives stuck at Stage 2 with `execution_speed='fast'`
- Decision needed: relax the gate, change default execution_speed, or add manual promotion flow

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

### Remaining Agent Failures (~4.7% rate) — INVESTIGATE
Post-metadata-fix, ~67 failures/day remain from other agents:
- ContentWriterAgent (15), AudioAgent (12), ResearchAgent (10), WorkflowAgent (6), TrendAnalysisAgent (4), VideoAgent (4)

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

**AgentResult fields (Session 1013):**
- `success`, `message`, `data`, `error`, `agent_name`, `execution_time_ms`, `tool_calls`, `tokens_used`, `cost`
- `.content` is a @property alias for `.message`
- **NO `.metadata` field** — use `.data` instead

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

**Model registration:** Use `core/models/__init__.py` (NOT `core/models.py`). New model imports: `from ..models_xxx import ClassName` with `app_label = 'core'`.

**Celery pool on Railway:** `--pool=prefork -c 1` (Linux), `--pool=threads` (macOS).

**ML imports:** Always lazy (inside methods). Module-level loads ~800MB.

**Auth for production API:** `Token 0cdc1c72dba99ea637485076ee952d571440aa30` (User: Donkeyking)
