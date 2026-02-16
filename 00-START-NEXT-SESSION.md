# Session 1014 - Start Here

**Previous Session:** 1013 (Image/Video/Audio Pipeline + Agent Failure Fix)
**Date:** February 15, 2026
**Status:** 82 Agents (routable) | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **40+ PUBLISHED BLOGS** | **1,131 SIGNAL CLUSTERS** | **INITIATIVE STAGES 1-5 ACTIVE** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 38+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 241** | **Frontend Routes: 26** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **VIDEO STUDIO: 5 EDIT TOOLS**

---

## Session 1013 Summary (Just Completed)

### Seamless Image → Video → Audio Pipeline (PR #1223)

Connected Image Studio, Video Studio, and ElevenLabs audio into a single creative workflow.

**Backend:**
- New `POST /api/tool/add-sfx-to-video/` — generates SFX via ElevenLabs `text_to_sound()`, mixes with video via FFmpeg `amix` filter, falls back to simple overlay if video has no audio track

**Frontend API:**
- `contentApi.addVoiceoverToVideo()` — wraps existing voiceover endpoint
- `contentApi.addSfxToVideo()` — wraps new SFX endpoint

**Frontend UI (VideoStudioPage):**
- **Image Gallery Picker** — "Browse" button in Image-to-Video mode opens modal showing `ImageHistory` thumbnails
- **Voice Tool Tab** — Script textarea, 12 ElevenLabs voice presets, volume slider
- **SFX Tool Tab** — Description input, duration slider (0.5–22s), volume slider
- Edit tools expanded: `text | color | audio | voice | sfx`

### Agent Failure Fix + Spinner Fix (PR #1224)

- **Root cause:** `execute_agent_task()` in `tasks.py:1349` accessed `result.metadata` on `AgentResult` which has no `.metadata` field (correct field: `.data`). Fixed to `getattr(result, 'data', {})`.
- **Impact:** This single bug caused **154 of 221 daily failures (70%)**, hitting `OpportunityScoringAgent` (79 failures) and `SystemIntelligenceAgent` (75 failures)
- **Post-fix:** Zero metadata errors in all subsequent agent runs. Failure rate expected to drop from ~15.6% to ~4.7%.
- **Spinner fix:** Replaced perpetual `Loader2` spinner with static `Workflow` icon in Command Center Active Work card

**PRs:** #1223, #1224

---

## Session 1012 Summary

### Betting Dashboard Polish & Bug Fixes (PRs #1215-#1219)

Comprehensive overhaul of all 12 betting tabs plus bug fixes for console errors.

**PR #1215 — Sharp Action Redesign:**
- Backend: Added `home_team`/`away_team` to signal dict, improved LLM prompt with structured recommendations (side/book/urgency)
- Frontend: Expanded sport filter (4 → 13 sports: NFL, NBA, MLB, NHL, NCAAB, NCAAF, EPL, La Liga, Bundesliga, Serie A, MLS, Champions League, UFC)
- Redesigned signal cards: recommendation box, game times, stale line diffs with pts-off-market, markdown LLM analysis

**PR #1216 — Betting Tabs Overhaul (6 improvements):**
1. **Today's Games** — ESPN score merge for period/clock/quarter, expandable per-bookmaker odds comparison grid
2. **Live Odds** — Full redesign with scores, LIVE/FINAL badges, period info, per-bookmaker odds grid
3. **Bankroll** — Replaced 100% hardcoded mock data with real PlacedWager queries (total wagered, net P/L, ROI, at risk, win rate, avg bet, biggest win/loss, Kelly criterion)
4. **My Wagers** — Manual "Log Wager" entry form (matchup, pick, odds, stake, sport, bookmaker, payout calculator)
5. **Arbitrage** — Stake calculator (enter total stake, see per-leg amounts + guaranteed profit)
6. **Today's Games** — `h2h_odds` passed to frontend for comparison grid

**PR #1217 — Console Error Fixes (4 bugs):**
- `/api/orchestration/active-work/` 500: `completion_percentage` is a `@property`, not DB field — `.values()` threw FieldError
- `/api/agent-learning/stats/` 404: URL removed in Session 1009 but frontend still called it
- `/api/learning/patterns/` 401: Returns empty data for unauthenticated instead of 401
- `/api/learning/insights/` 401: Same fix

**PR #1218 — Today's Games Crash Fix:**
- `eid` undefined variable → replaced with `game.event_id` in bookmaker toggle

**PR #1219 — AI Track Record Dedup:**
- Prediction task creates multiple MLPredictions per game (different days). Deduped by `game_id` via `Max('id')` — fixes inflated W/L stats and duplicate pending rows

---

## Session 1011 Summary

### Sports Prediction Pipeline — Full Automation (PRs #1208-#1212)

Closed the entire sports prediction loop. 8 scheduled tasks fully automated.

**Results verified on Railway:**
- 47 games updated with final scores
- 47 predictions evaluated: **33 correct, 14 incorrect (70.2% accuracy)**
- NCAAB: 69.6% (32/46), Soccer: 100% (1/1)
- 99 new predictions generated, 88 stored

**PRs:** #1208-#1212

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
| Video Studio Edit Tools | 5 (Text, Color, Audio, Voice, SFX) |
| Standalone Pages | `/stocks`, `/advisors`, `/betting`, `/neural-orchestra`, `/conversation-contract`, `/mythology-lab`, `/billing`, `/analytics`, `/docs-index`, `/image-studio`, `/video-studio`, `/documents` |

---

## Known Issues / Open Items

### Remaining Agent Failures (~4.7% rate) — INVESTIGATE
Post-metadata-fix, ~67 failures/day remain from other agents:
- ContentWriterAgent (15), AudioAgent (12), ResearchAgent (10), WorkflowAgent (6), TrendAnalysisAgent (4), VideoAgent (4)
- Each has a different root cause — needs individual investigation

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
