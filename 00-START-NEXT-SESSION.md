# Session 1011 - Start Here

**Previous Session:** 1010 (Sports Predictions, Sharp Action Fix & System Cleanup)
**Date:** February 15, 2026
**Status:** 82 Agents (routable) | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **40+ PUBLISHED BLOGS** | **1,131 SIGNAL CLUSTERS** | **INITIATIVE STAGES 1-5 ACTIVE** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 38+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 238** | **Frontend Routes: 26** | **6 Sports Leagues w/ Predictions**

---

## Session 1010 Summary (Just Completed)

### Sports Prediction Persistence (PRs #1198-#1202)
- **Fixed MLPrediction storage:** GamePredictor._store_predictions() was silently failing (wrong fields, string vs FK, empty tables). Rewrote to auto-create League → Team → Game → MLPrediction chain.
- **Fixed sport key mapping:** `split('_')[-1]` produced wrong values for multi-word keys (soccer_epl→"epl", mma_mixed_martial_arts→"arts"). Replaced `LEAGUE_MAP` with `SPORT_KEY_LEAGUE` (21 full key mappings) + `SPORT_PREFIX_MAP` fallback.
- **Added NBA All-Stars** to spider SPORTS dict
- **Added 14-day filter** — no far-future predictions (NCAAF Aug/Sep)
- **Result:** 108 predictions across 6 leagues (NCAAB: 53, EPL: 21, La Liga: 23, NHL: 8, MLS: 3)

### Sharp Action Divergence Fix (PR #1203)
Filtered extreme odds (abs > 10000) from divergence calculation. Was showing 100K+ pts from junk -100000 bookmaker values.

### Initiative Spam Fix (PRs #1204-#1205)
- Circuit breaker: counts ALL active/triage (was only no-activity), threshold 50→20, dedup includes TRIAGE
- Topic generator: stopword filter prevents "Developing before and developer and trending skills" word salad
- Quality gate: skip clusters with all-stopword keywords

### Full System Database Cleanup (~26,868 rows deleted)
| Table | Before | After | Deleted |
|-------|--------|-------|---------|
| Initiatives | 971 | 28 | 943 |
| InitiativeStages | 4,852 | 140 | 4,712 |
| AutoTopics | 490 | 0 | 490 |
| HiveMindSessions | 606 | 231 | 375 |
| AgentDreams | 5,553 | 935 | 4,618 |
| AgentExecutions | 14,945 | 6,505 | 8,440 |
| Deliverables | 14,284 | 7,436 | 6,848 |
| SelfBlogs | 1,151 | 344 | 807 |

### Other Fixes
- Matchup display: full team names instead of abbreviations (PR #1199)
- Celery-content OOM: max-tasks-per-child 30→10 (PR #1200)

**PRs:** #1198-#1205

---

## Session 1009 Summary

### Deliverables Tab + Orphan Cleanup + celery-content OOM Fix
- **Deliverables Tab**: New Content Studio sub-tab with list/detail views, filtering, pagination, save/clone/templateize/export (PR #1188)
- **Orphan Cleanup**: Removed ~65 orphaned API endpoints from `core/urls.py` across 12 groups
- **celery-content OOM Fix** (PR #1190): Moved 7 heavy tasks from `content` → `long_running` queue, reduced content worker from `-c 2` → `-c 1`

**PRs:** #1186-#1190

---

## Session 1008 Summary

### Campaign Orchestrator + ToolCall Analytics Frontend
Connected Campaign Orchestrator and ToolCall Analytics dashboards to frontend (PR #1186). Removed dead `synthetic_user_generator` service (PR #1187).

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 82 routable, 25 non-routable, 26+ provenance-tracked |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 395+ |
| Services | 134 |
| Celery Tasks | 238 |
| Intelligence Desks | 4 (Stocks, Sports, Blockchain, Narrative) — ALL RUNNING |
| Workspace Tabs | 9 |
| Frontend Routes | 26 (Image Studio, Video Studio, Documents added) |
| Agents Persisting Output | 43 (via `_save_to_deliverable()`) |
| PA Tools | 97 |
| PA Intents | 38 |
| Enrichment Services | 8 |
| Sports Leagues | 6 with predictions (NCAAB, NHL, EPL, La Liga, MLS, NCAAF) |
| Active Initiatives | 20 (circuit breaker threshold) |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |
| Standalone Pages | `/stocks`, `/advisors`, `/betting`, `/neural-orchestra`, `/conversation-contract`, `/mythology-lab`, `/billing`, `/analytics`, `/docs-index`, `/image-studio`, `/video-studio`, `/documents` |

---

## Known Issues / Open Items

### Initiative Circuit Breaker — DEPLOYED
Threshold at 20 active initiatives. Stopword filter + quality gate on auto-topics. Monitor to ensure meaningful initiatives still get created.

### Sports Prediction Evaluation — NOT YET AUTOMATED
MLPredictions are stored but `was_correct` is never set. Need to implement automated evaluation via `PredictionEvaluator` after games complete (using TheOddsSpider.fetch_scores()).

### NBA All-Star Break
`basketball_nba` returns 0 events (All-Star break). `basketball_nba_all_stars` was added. Regular NBA season should resume soon.

### Blog Topic Diversity -- Monitor
19/40 published blogs about Security/Homeland due to weak novelty scoring. PR #1141 strengthens scoring — verify after next batch.

### collect_real_opportunities — MITIGATED
Time limits (PR #1149) + dedup via `get_or_create` (PR #1160).

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
- Status values are UPPERCASE: `'ACTIVE'`, `'ARCHIVED'`, `'COMPLETED'`, `'TRIAGE'`
- Import from `core.models` (NOT `core.models_unified_system`)
- Field `name` (NOT `title`)

**Sports models (Session 1010):**
- `League`: name (unique), abbreviation (unique), sport_type, current_season
- `Team`: name, abbreviation, league (FK), city. unique_together: `(league, abbreviation)`
- `Game`: external_id (unique), league (FK), home_team (FK), away_team (FK), scheduled_start, season
- `MLPrediction`: game (FK), predicted_winner (FK to Team), confidence (0-100), sport_type, model_used
- `SPORT_KEY_LEAGUE` in game_predictor.py maps full Odds API keys to league tuples

**SelfBlog model:**
- Import from `core.models_unified_system`
- Has `created_at` but NO `updated_at`
- Status flow: `draft -> pending_review -> needs_enhancement -> approved -> published`

**SignalCluster model:**
- Import from `core.models`
- Timestamp field is `detected_at`

**SportsBettingBrief model:**
- Timestamp field is `generated_at` (NOT `created_at`)
- Predictions in `predictions` field (NOT `top_plays`)

**Railway multi-service deployment:**
- Each Procfile process is a SEPARATE Railway service
- `railway up` deploys only the linked service
- `railway redeploy` during a build cancels build and redeploys OLD code
- GitHub push auto-deploys ALL services

**Model registration:** Use `core/models/__init__.py` (NOT `core/models.py`). New model imports: `from ..models_xxx import ClassName` with `app_label = 'core'`.

**Celery pool on Railway:** `--pool=prefork -c 1` (Linux), `--pool=threads` (macOS).

**ML imports:** Always lazy (inside methods). Module-level loads ~800MB.

**Auth for production API:** `Token 0cdc1c72dba99ea637485076ee952d571440aa30` (User: Donkeyking)
