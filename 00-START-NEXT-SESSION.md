# Session 1012 - Start Here

**Previous Session:** 1011 (Sports Pipeline Full Automation)
**Date:** February 15, 2026
**Status:** 82 Agents (routable) | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **40+ PUBLISHED BLOGS** | **1,131 SIGNAL CLUSTERS** | **INITIATIVE STAGES 1-5 ACTIVE** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 38+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 241** | **Frontend Routes: 26** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED**

---

## Session 1011 Summary (Just Completed)

### Sports Prediction Pipeline — Full Automation (PRs #1208-#1212)

Closed the entire sports prediction loop. Previously, `update_game_scores` was a placeholder, predictions were never evaluated, and the learning loop was broken.

**What was built/fixed:**
1. **`update_game_scores`** — fetches final scores from TheOddsSpider, marks Games as FINAL (every 30 min)
2. **`generate_game_predictions`** — runs GamePredictor to create MLPredictions from odds (every 2h)
3. **`verify_betting_outcomes`** — settles PlacedWager legs and verifies arb items (every 30 min)
4. **PredictionEvaluator bug fixes** — wrong field names (`evaluation_date`, `evaluation_metadata`)
5. **SportsBettingLearningBridge bug fixes** — `game_date` AttributeError, `FeedbackItem` constructor, serialization

**Results verified on Railway:**
- 47 games updated with final scores
- 47 predictions evaluated: **33 correct, 14 incorrect (70.2% accuracy)**
- NCAAB: 69.6% (32/46), Soccer: 100% (1/1)
- 99 new predictions generated, 88 stored
- Learning loop integration working end-to-end

**Complete automated pipeline (8 scheduled tasks):**
| Step | Task | Schedule |
|------|------|----------|
| Odds ingestion | `collect_sports_odds` | Every 20 min |
| Prediction generation | `generate_game_predictions` | Every 2h |
| Score fetching | `update_game_scores` | Every 30 min |
| Prediction evaluation | `evaluate_completed_predictions` | Hourly |
| Wager verification | `verify_betting_outcomes` | Every 30 min |
| Bet settlement | `settle_user_bets` | Every 15 min |
| Accuracy report | `generate_accuracy_report` | Daily 9 AM |
| Cleanup | `cleanup_old_predictions` | Weekly Mon 3 AM |

**Branch cleanup:** Deleted 67 stale local branches, pruned 55 remote refs.

**PRs:** #1208-#1212

---

## Session 1010 Summary

### Sports Prediction Persistence (PRs #1198-#1202)
- **Fixed MLPrediction storage:** GamePredictor._store_predictions() was silently failing (wrong fields, string vs FK, empty tables). Rewrote to auto-create League → Team → Game → MLPrediction chain.
- **Fixed sport key mapping:** `split('_')[-1]` produced wrong values for multi-word keys. Replaced `LEAGUE_MAP` with `SPORT_KEY_LEAGUE` (21 full key mappings) + `SPORT_PREFIX_MAP` fallback.
- **Result:** 108 predictions across 6 leagues (NCAAB: 53, EPL: 21, La Liga: 23, NHL: 8, MLS: 3)

### Sharp Action Divergence Fix (PR #1203)
Filtered extreme odds (abs > 10000) from divergence calculation.

### Initiative Spam Fix (PRs #1204-#1205)
Circuit breaker threshold 50→20, stopword filter on auto-topics, quality gate on clusters.

**PRs:** #1198-#1205

---

## Session 1009 Summary

### Deliverables Tab + Orphan Cleanup + celery-content OOM Fix
- **Deliverables Tab**: New Content Studio sub-tab with list/detail views, filtering, pagination, save/clone/templateize/export (PR #1188)
- **Orphan Cleanup**: Removed ~65 orphaned API endpoints from `core/urls.py` across 12 groups
- **celery-content OOM Fix** (PR #1190): Moved 7 heavy tasks from `content` → `long_running` queue, reduced content worker from `-c 2` → `-c 1`

**PRs:** #1186-#1190

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
| Frontend Routes | 26 (Image Studio, Video Studio, Documents added) |
| Agents Persisting Output | 43 (via `_save_to_deliverable()`) |
| PA Tools | 97 |
| PA Intents | 38 |
| Enrichment Services | 8 |
| Sports Leagues | 6 with predictions (NCAAB, NHL, EPL, La Liga, MLS, NCAAF) |
| Sports Pipeline Tasks | 8 (all scheduled, all verified on Railway) |
| Active Initiatives | 20 (circuit breaker threshold) |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |
| Standalone Pages | `/stocks`, `/advisors`, `/betting`, `/neural-orchestra`, `/conversation-contract`, `/mythology-lab`, `/billing`, `/analytics`, `/docs-index`, `/image-studio`, `/video-studio`, `/documents` |

---

## Known Issues / Open Items

### Initiative Circuit Breaker — DEPLOYED
Threshold at 20 active initiatives. Stopword filter + quality gate on auto-topics. Monitor to ensure meaningful initiatives still get created.

### NBA All-Star Break
`basketball_nba` returns 0 events (All-Star break). `basketball_nba_all_stars` was added. Regular NBA season should resume soon.

### Blog Topic Diversity — Monitor
19/40 published blogs about Security/Homeland due to weak novelty scoring. PR #1141 strengthens scoring — verify after next batch.

### collect_real_opportunities — MITIGATED
Time limits (PR #1149) + dedup via `get_or_create` (PR #1160).

### Sports Prediction Accuracy — MONITOR
Initial accuracy is 70.2% (mostly NCAAB). As more leagues return data and predictions accumulate, monitor by sport/model. Retraining candidates flagged automatically when accuracy < 55% with 50+ samples.

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
- `MLPrediction`: game (FK, related_name='ml_predictions'), predicted_winner (FK to Team), confidence (0-100), sport_type, model_used, was_correct, evaluated_at
- `SPORT_KEY_LEAGUE` in game_predictor.py maps full Odds API keys to league tuples

**MLPrediction gotchas (Session 1011):**
- `evaluated_at` (NOT `evaluation_date`)
- `metadata` for evaluation data (inherited from UnifiedBaseModel, NOT `evaluation_metadata`)
- Reverse relation from Game: `ml_predictions` (NOT `mlprediction`)

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
