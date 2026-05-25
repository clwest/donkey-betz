---
originating_session: 995
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 995: Betting Outcome Verification + Learning Loop

**Date:** February 12, 2026
**Focus:** Close the feedback loop for sports betting — verify outcomes, settle wagers, feed learning

## Problem

The system detects arbitrage opportunities (ArbitrageDetector) and tracks placed wagers (PlacedWager/PlacedWagerLeg), but never checks if they won or lost. PlacedWagers sit in `pending` status forever. HumanAttentionItems with `decision='watch'` never get verified. No outcomes feed into the learning loop.

## Changes

### 1. TheOddsSpider: `fetch_scores()` (theodds_spider.py)
- New method fetches completed game scores from The Odds API `/v4/sports/{sport}/scores` endpoint
- Reuses existing `_make_request()` for auth, rate limits, timeout handling
- Returns normalized list: `{event_id, sport_key, home_team, away_team, home_score, away_score, completed}`
- Same `event_id` as odds data — no fuzzy team matching needed for joining scores to wagers

### 2. BettingOutcomeVerifier Service (NEW: core/services/betting_outcome_verifier.py)
Main service with 5 public/private methods:

- **`verify_all_pending()`** — Entry point. Finds pending PlacedWagerLeg records (commence_time > 3h ago) and HumanAttentionItems in `watching` status. Batch-fetches scores per sport. Settles wagers, verifies arb items, creates learning records. Returns summary dict.
- **`_settle_wager(wager, score_lookup)`** — Iterates legs, determines outcome per leg, handles single vs parlay logic (all-must-win for parlays, any loss = lost). Calls `wager.settle()`.
- **`_determine_leg_outcome(leg, score_data)`** — Dispatches to market-specific evaluation (h2h, spreads, totals). Handles push on exact line matches.
- **`_verify_arb_item(item, score_lookup)`** — Extracts event_id from item payload, calculates actual profit from arb stakes/odds, calls `item.record_verification()`.
- **`_create_learning_records()`** — Calls SportsBettingLearningBridge for each settled wager and verified arb item.

Team matching uses substring + word overlap (consistent API team names). Line parsing from pick strings via regex.

### 3. Celery Task: `verify_betting_outcomes` (core/tasks.py)
- `@shared_task(bind=True, max_retries=2, default_retry_delay=300, queue='default')`
- Calls `BettingOutcomeVerifier.verify_all_pending()`
- Also recalculates `BettingStats` for affected users after settlement
- Idempotent — checks status before settling/verifying

### 4. Beat Schedule (core/settings.py)
- `'verify-betting-outcomes'`: every 2 hours at :15 — `crontab(hour='*/2', minute='15')`

### 5. SportsBettingLearningBridge: Two New Methods (sports_betting_bridge.py)

**`record_wager_outcome(wager)`:**
- Creates/updates `UserAgentLearning` for agent `SportsOddsAnalyst`, domain `sports_betting_{sport}`
- Calls `record_success()` or `record_failure()` based on wager status
- Creates `AgentMemory` with outcome details, tags, importance (0.8 for failures, 0.6 for successes)

**`record_arbitrage_outcome(arb_item)`:**
- Creates/updates `UserAgentLearning` for agent `ArbitrageDetector`, domain `general`
- Calls `record_success()` or `record_failure()`
- Creates `AgentMemory` with predicted vs actual profit, bookmaker pair, sport

## Files Changed

| File | Action | Lines |
|------|--------|-------|
| `ai_core/spiders/specialized/theodds_spider.py` | Modified — added `fetch_scores()` | +55 |
| `core/services/betting_outcome_verifier.py` | **Created** | ~340 |
| `core/tasks.py` | Modified — added `verify_betting_outcomes` task | +50 |
| `core/settings.py` | Modified — added beat schedule entry | +6 |
| `core/learning_bridges/sports_betting_bridge.py` | Modified — added 2 methods | +130 |

No new models. No migrations. 1 new Celery task. 1 new beat schedule entry.

## Data Flow

```
Celery Beat (every 2h at :15)
  → verify_betting_outcomes task
    → BettingOutcomeVerifier.verify_all_pending()
      → Find pending PlacedWagerLeg (commence_time > 3h ago)
      → Find HumanAttentionItem (status=watching, type=arbitrage)
      → TheOddsSpider.fetch_scores(sport) per unique sport
      → Match event_id → settle legs → settle wagers
      → Match event_id → verify arb items
      → SportsBettingLearningBridge.record_wager_outcome()
        → UserAgentLearning (SportsOddsAnalyst)
        → AgentMemory (success/failure + tags)
      → SportsBettingLearningBridge.record_arbitrage_outcome()
        → UserAgentLearning (ArbitrageDetector)
        → AgentMemory (predicted vs actual profit)
      → BettingStats.recalculate() for affected users
```

## Verification

```bash
# Syntax check
python -c "import ast; ast.parse(open('core/services/betting_outcome_verifier.py').read())"

# Import check
python -c "import django; django.setup(); from core.services.betting_outcome_verifier import BettingOutcomeVerifier"

# Manual run
python manage.py shell -c "from core.services.betting_outcome_verifier import BettingOutcomeVerifier; v = BettingOutcomeVerifier(); print(v.verify_all_pending())"
```
