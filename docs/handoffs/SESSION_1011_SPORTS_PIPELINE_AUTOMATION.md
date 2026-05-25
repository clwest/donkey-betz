---
originating_session: 1011
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1011: Sports Prediction Pipeline — Full Automation

**Date:** February 15, 2026
**PRs:** #1208-#1212

---

## Context

Session 1010 stored 108 MLPredictions across 6 leagues, but `was_correct` was never set because game scores were never fetched. The `update_game_scores` task was a placeholder returning `not_implemented`, and it wasn't in the beat schedule. The evaluation pipeline existed but couldn't run without final scores.

## Implement update_game_scores (PR #1208)

Replaced the placeholder in `sports/tasks.py` with real implementation:
- Builds reverse map from `League.abbreviation` → Odds API `sport_key` using `GamePredictor.SPORT_KEY_LEAGUE`
- Queries non-FINAL Games from last 3 days that have predictions (`ml_predictions__isnull=False`)
- Groups by sport_key, calls `TheOddsSpider.fetch_scores()` per group
- Matches by `external_id`, updates `home_score`, `away_score`, `status=FINAL`
- Registered in beat schedule (every 30 min)

**Result:** 47 games updated with final scores (1 La Liga + 46 NCAAB) from 5 API calls.

## Fix related_name (PR #1209)

MLPrediction's FK to Game uses `related_name='ml_predictions'`, not the default `mlprediction`. The filter query was using `mlprediction__isnull=False` which threw `FieldError`.

## Fix PredictionEvaluator bugs (PR #1208)

Two bugs in `sports/prediction_evaluator.py`:
1. `prediction.evaluation_date` → `prediction.evaluated_at` (correct model field)
2. `prediction.evaluation_metadata` → `prediction.metadata` (uses inherited `UnifiedBaseModel.metadata` JSONField; `evaluation_metadata` doesn't exist as a field, data was silently lost)

**Result:** 47 predictions evaluated — 33 correct, 14 incorrect (70.2% accuracy). NCAAB: 69.6%, Soccer: 100%.

## Fix SportsBettingLearningBridge (PRs #1210-#1211)

Two bugs preventing learning loop integration:
1. `prediction.game_date` → `prediction.game.scheduled_start` (MLPrediction has no `game_date` field)
2. `FeedbackItem()` missing required `id` and `timestamp` positional args (dataclass)

Also fixed: `predicted_winner` (FK object, not JSON-serializable) → `.name`, `prediction.id` (UUID) → `str()`.

## Schedule prediction generation & outcome verification (PR #1212)

Two tasks were missing from the automated pipeline:
- `generate_game_predictions` (every 2h at :15) — runs `GamePredictor.execute()` to create MLPrediction rows from current odds. Without this, predictions were only created manually.
- `verify_betting_outcomes` (every 30m) — runs `BettingOutcomeVerifier.verify_all_pending()` to settle `PlacedWagerLeg` records and verify arb `HumanAttentionItem` records.

**Result:** 99 predictions generated, 88 stored (11 duplicates skipped). Verification runs cleanly (0 pending wagers currently — kicks in when users place bets).

---

## Complete Automated Sports Pipeline

| Step | Task | Schedule | Source |
|------|------|----------|--------|
| Odds ingestion | `collect_sports_odds` | Every 20 min | Pre-existing |
| Prediction generation | `generate_game_predictions` | Every 2h | **NEW (PR #1212)** |
| Score fetching | `update_game_scores` | Every 30 min | **NEW (PR #1208)** |
| Prediction evaluation | `evaluate_completed_predictions` | Hourly | Fixed (PR #1208) |
| Wager verification | `verify_betting_outcomes` | Every 30 min | **NEW (PR #1212)** |
| Bet settlement | `settle_user_bets` | Every 15 min | Pre-existing |
| Accuracy report | `generate_accuracy_report` | Daily 9 AM | Pre-existing |
| Cleanup | `cleanup_old_predictions` | Weekly Mon 3 AM | Pre-existing |

All 8 tasks are registered in `core/celery.py` beat schedule and verified on Railway.

---

## Files Changed

| File | Changes |
|------|---------|
| `sports/tasks.py` | Replaced `update_game_scores` placeholder; added `generate_game_predictions` and `verify_betting_outcomes` |
| `core/celery.py` | Added 3 beat schedule entries |
| `sports/prediction_evaluator.py` | Fixed `evaluation_date` → `evaluated_at`, `evaluation_metadata` → `metadata` |
| `core/learning_bridges/sports_betting_bridge.py` | Fixed `game_date`, `FeedbackItem` constructor, serialization |

## Branch Cleanup

Deleted 63 merged local branches + 4 squash-merged session branches. Pruned 55 stale remote tracking refs.
