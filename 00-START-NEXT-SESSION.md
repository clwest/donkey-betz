# Session 1016 - Start Here

**Previous Session:** 1015 (Government Page + Image Studio Fix + DNS)
**Date:** February 16, 2026
**Status:** 82 Agents (routable) | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **40+ PUBLISHED BLOGS** | **1,131 SIGNAL CLUSTERS** | **INITIATIVE STAGES 1-5 ACTIVE** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 241** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **VIDEO STUDIO: 5 EDIT TOOLS** | **GOVERNMENT PAGE: 3 TABS + ASK A BILL RAG**

---

## Session 1015 Summary (Just Completed)

### Government & Legislation Page (PRs #1226-#1229)

Full-stack `/government` page with Hub, Bills, and Ask A Bill tabs.

**Backend:**
- `views_government.py` — REST hub endpoint with stats, topics, recent bills
- `tool_dispatcher.py` — `ask` action: RAG over bill embeddings + keyword fallback with stopword filtering
- `unified_pa_entrypoint.py` — legislation ask intent, payload builder, formatter with source citations
- Handles flat, spider-network envelope, and Celery bundle data formats

**Frontend:**
- Hub tab: stat cards, recent bills, top topics, Ask A Bill sidebar
- Bills tab: filterable list with chamber/status filters, expandable cards
- Ask A Bill tab: full PA chat with suggested questions

**Data fixes:** Flattened nested spider data, fixed `embedding_text`, rewrote keyword extraction

### Image Studio Cloudinary Fix (PR #1230)

Images were generated but never saved to gallery. Root cause: `default_storage.path()` fails on Cloudinary backend. Fixed `save_watermarked_image` to return `default_storage.url()` directly, and `save_to_history` to handle cloud URLs.

### Custom Domain DNS (IN PROGRESS)

`www.donkeybetz.com` custom domain added to Railway. CNAME updated to `7sce0gjg.up.railway.app`. SSL cert provisioning pending — Railway DNS cache was still stale at session end. Should auto-resolve.

**PRs:** #1226, #1227, #1228, #1229, #1230

---

## Session 1014 Summary

### Stock Intelligence Hub Polish (PR #1222)
- News tab with source diversity scoring
- Deduped predictions, styled cards, adaptive layout

### Agent Failure Fix (PR #1224)
- Fixed `AgentResult.metadata` crash (correct field: `.data`) — eliminated 70% of daily failures

### Image/Video/Audio Pipeline (PR #1223)
- Connected Image Studio → Video Studio → ElevenLabs audio
- Voice and SFX tool tabs in Video Studio

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 82 routable, 25 non-routable, 26+ provenance-tracked |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 395+ |
| Services | 134 |
| Celery Tasks | 241 |
| Intelligence Desks | 4 (Stocks, Sports, Blockchain, Narrative) — ALL RUNNING |
| Workspace Tabs | 9 |
| Frontend Routes | 27 (added `/government`) |
| Agents Persisting Output | 43 (via `_save_to_deliverable()`) |
| PA Tools | 97 |
| PA Intents | 39 (added legislation ask) |
| Enrichment Services | 8 |
| Sports Leagues | 6 with predictions (NCAAB, NHL, EPL, La Liga, MLS, NCAAF) |
| Sports Pipeline Tasks | 8 (all scheduled, all verified on Railway) |
| Active Initiatives | 20 (circuit breaker threshold) |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |
| Video Studio Edit Tools | 5 (Text, Color, Audio, Voice, SFX) |
| Standalone Pages | `/stocks`, `/government`, `/advisors`, `/betting`, `/neural-orchestra`, `/conversation-contract`, `/mythology-lab`, `/billing`, `/analytics`, `/docs-index`, `/image-studio`, `/video-studio`, `/documents` |

---

## Verify Before Starting

### 1. Image Studio Fix (PR #1230)
- Go to Image Studio, generate an image
- Should appear in gallery with Cloudinary URL
- If still broken, check Railway logs for `save_watermarked_image` / `save_to_history` errors

### 2. Custom Domain SSL
- Try `https://www.donkeybetz.com` — should show login page with valid cert
- If still cert error: delete domain in Railway dashboard → re-add → update CNAME in Squarespace

### 3. Ask A Bill Embeddings
- Run: `railway run python manage.py shell -c "from core.models_unified_system import SpiderData; print(SpiderData.objects.filter(spider_name='legislation', embedding__isnull=False).count())"`
- If 0, trigger: `railway run python manage.py shell -c "from core.tasks import backfill_spider_embeddings; backfill_spider_embeddings.delay()"`

---

## Known Issues / Open Items

### PA Context Awareness — NEEDS WORK
PA doesn't understand page context. When user says "I just created an image but it's not displaying" from Image Studio, PA asks generic clarifying questions instead of checking ImageHistory or knowing the user was on Image Studio. Needs:
- Page-context awareness (which page the user is on)
- Image-specific intent/enrichment to check recent ImageHistory
- Potentially a new `image_studio` intent in PA

### Remaining Agent Failures (~4.7% rate) — INVESTIGATE
Post-metadata-fix, ~67 failures/day remain from other agents:
- ContentWriterAgent (15), AudioAgent (12), ResearchAgent (10), WorkflowAgent (6), TrendAnalysisAgent (4), VideoAgent (4)

### Initiative Circuit Breaker — DEPLOYED
Threshold at 20 active initiatives. Monitor to ensure meaningful initiatives still get created.

### NBA All-Star Break
`basketball_nba` returns 0 events (All-Star break). Regular NBA season should resume soon.

### Blog Topic Diversity — Monitor
19/40 published blogs about Security/Homeland due to weak novelty scoring. PR #1141 strengthens scoring — verify after next batch.

### Sports Prediction Accuracy — MONITOR
Initial accuracy is 70.2% (mostly NCAAB). Monitor by sport/model as more leagues return data.

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

**Sports models (Session 1010):**
- `League`: name (unique), abbreviation (unique), sport_type, current_season
- `Team`: name, abbreviation, league (FK), city. unique_together: `(league, abbreviation)`
- `Game`: external_id (unique), league (FK), home_team (FK), away_team (FK), scheduled_start, season
- `MLPrediction`: game (FK, related_name='ml_predictions'), predicted_winner (FK to Team), confidence (0-100), sport_type, model_used, was_correct, evaluated_at

**MLPrediction gotchas (Session 1011):**
- `evaluated_at` (NOT `evaluation_date`)
- `metadata` for evaluation data (inherited from UnifiedBaseModel, NOT `evaluation_metadata`)
- Reverse relation from Game: `ml_predictions` (NOT `mlprediction`)

**SelfBlog model:**
- Import from `core.models_unified_system`
- Has `created_at` but NO `updated_at`

**Cloudinary storage (Session 1015):**
- `DEFAULT_FILE_STORAGE` is `cloudinary_storage.storage.MediaCloudinaryStorage` on Railway
- `default_storage.save()` uploads directly to Cloudinary
- `default_storage.url()` returns `https://res.cloudinary.com/...` URLs
- `default_storage.path()` RAISES `This backend doesn't support absolute paths` — NEVER use on Railway
- Image `file_path` in DB may be a Cloudinary URL (starts with `http`) or relative local path

**Railway multi-service deployment:**
- Each Procfile process is a SEPARATE Railway service
- `railway up` deploys only the linked service
- `railway redeploy` during a build cancels build and redeploys OLD code
- GitHub push auto-deploys ALL services

**Model registration:** Use `core/models/__init__.py` (NOT `core/models.py`). New model imports: `from ..models_xxx import ClassName` with `app_label = 'core'`.

**Celery pool on Railway:** `--pool=prefork -c 1` (Linux), `--pool=threads` (macOS).

**ML imports:** Always lazy (inside methods). Module-level loads ~800MB.

**Auth for production API:** `Token 0cdc1c72dba99ea637485076ee952d571440aa30` (User: Donkeyking)
