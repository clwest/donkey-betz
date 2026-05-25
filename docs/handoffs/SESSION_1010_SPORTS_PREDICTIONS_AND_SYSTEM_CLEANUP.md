---
originating_session: 1010
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1010: Sports Predictions, Sharp Action Fix & System Cleanup

**Date:** February 15, 2026
**PRs:** #1198-#1205

---

## Sports Prediction Persistence (PR #1198)

GamePredictor._store_predictions() was silently failing — `game_date` field doesn't exist on MLPrediction, `predicted_winner` was passed as string (it's a FK to Team), and Game/Team/League tables had 0 rows. Exceptions were caught with `logger.debug()`, completely silent.

**Fix:** Rewrote _store_predictions to auto-create League → Team → Game → MLPrediction chain via `get_or_create`. Added safety-net extraction in `generate_daily_betting_brief` (tasks.py) to catch missed predictions. Backfilled 69 predictions (3 leagues, 138 teams, 69 games).

## Matchup Display Fix (PR #1199)

Changed AI Record tab to show full team names ("Syracuse Orange @ Duke Blue Devils") instead of auto-generated abbreviations ("ORANGE @ DEVILS").

## Celery-Content OOM Fix (PR #1200)

celery-content crashed due to OOM again. Reduced `--max-tasks-per-child` from 30 → 10 in Procfile.

## Far-Future Predictions Filter (PR #1201)

NCAAF predictions for Aug/Sep 2026 (early futures) were showing in AI Record. Added 14-day filter in _store_predictions, changed pending sort to game date ascending (soonest first). Cleaned up 8 far-future records.

## Sport Key Mapping Fix (PR #1202)

**Root cause of missing sports:** `sport_key.split('_')[-1]` produced wrong values for multi-word Odds API keys:
- `soccer_epl` → `epl` (NOT in LEAGUE_MAP, DROPPED)
- `soccer_spain_la_liga` → `liga` (DROPPED)
- `mma_mixed_martial_arts` → `arts` (DROPPED)

Only NCAAB, NCAAF, NHL predictions were being stored. EPL, La Liga, MLS, Champions League, UFC — all silently dropped.

**Fix:** Replaced `LEAGUE_MAP` (12 entries, broken key extraction) with:
- `SPORT_KEY_LEAGUE` (21 full Odds API key → league tuple mappings)
- `SPORT_PREFIX_MAP` (fallback for unmapped keys)

Also added `basketball_nba_all_stars` to spider SPORTS dict (active during All-Star weekend).

**Result:** Backfilled 47 soccer predictions (21 EPL, 23 La Liga, 3 MLS). Total: 108 predictions across 6 leagues.

## Sharp Action Divergence Fix (PR #1203)

Max Divergence showing 100K+ pts on Sharp Action tab. Root cause: some bookmakers return extreme American odds like -100000 (junk/outlier). Computing `max - min` across bookmakers produced absurd divergence: `350 - (-100000) = 100,350`.

**Fix:** Filter out bookmaker entries where `abs(odds) > 10000` before computing ranges.

## Initiative Spam — Circuit Breaker & Topic Generator (PRs #1204-#1205)

74 initiatives created in 24 hours with garbled titles like "Developing before and developer and trending skills". Three failures:

1. **Dedup only checked ACTIVE status** — TRIAGE initiatives were invisible, so numbered duplicates kept being created: (1), (2), (3), (4)...
2. **Circuit breaker only counted initiatives with `last_activity_at IS NULL`** — auto-generated initiatives immediately get agent activity, falling out of backlog count
3. **Threshold was 50** — too high for meaningful processing

**Root cause:** `_generate_topic_name()` in signal_aggregation_service.py joined raw cluster keywords (stopwords like 'before', 'new', 'now') with 'and': `"Developing before and developer and trending skills"`.

**Fixes:**
- Circuit breaker now counts ALL active/triage initiatives (PR #1204)
- Default threshold lowered 50 → 20
- Dedup includes TRIAGE status
- Added stopword filter to topic generator (PR #1205)
- Quality gate: skip clusters with no meaningful keywords
- Use comma separator + cluster name fallback

## Full System Database Cleanup

| Table | Before | After | Deleted |
|-------|--------|-------|---------|
| Initiatives | 971 | 28 | 943 |
| InitiativeStages | 4,852 | 140 | 4,712 |
| AutoTopics | 490 | 0 | 490 |
| HiveMindSessions | 606 | 231 | 375 |
| SignalClusters | 1,573 | 1,131 | 442 |
| AgentDreams | 5,553 | 935 | 4,618 |
| AgentExecutions | 14,945 | 6,505 | 8,440 |
| Deliverables | 14,284 | 7,436 | 6,848 |
| StageTransitionLogs | — | — | 1,044 |
| **Total** | ~43,274 | ~16,406 | **~26,868** |

## Blog Database Cleanup (earlier in session)

| Metric | Before | After |
|--------|--------|-------|
| Total blogs | 1,151 | 344 |
| Empty full_text | 156 | 0 |
| Under 100 words | 574 | 0 |
| Duplicates | 24 | 0 |
| Backfilled from sections | — | 67 |

---

## Files Changed

| File | Change |
|------|--------|
| `core/agents/markets/game_predictor.py` | SPORT_KEY_LEAGUE + SPORT_PREFIX_MAP, 14-day filter, auto-create chain |
| `core/agents/markets/sharp_action_detector.py` | Filter extreme odds (>|10000|) |
| `core/services/initiative_circuit_breaker.py` | Count all active/triage, threshold 50→20, dedup TRIAGE |
| `core/services/signal_aggregation_service.py` | Stopword filter, quality gate, comma separator |
| `core/views_odds_sports.py` | Team names in matchup, pending sort by game date, removed stock fallback |
| `core/tasks.py` | Safety-net MLPrediction extraction |
| `ai_core/spiders/specialized/theodds_spider.py` | basketball_nba_all_stars |
| `frontend/src/pages/BettingPage.tsx` | Removed isStockData conditional logic |
| `Procfile` | celery-content max-tasks-per-child 30→10 |
