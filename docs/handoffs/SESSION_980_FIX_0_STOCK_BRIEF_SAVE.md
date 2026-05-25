---
originating_session: 980
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 980 — Stock Intelligence Production Hardening

**Date:** February 9, 2026
**Previous Session:** 979 (Stock Intelligence PA Routing)
**Branch:** `session-980/fix-0-stock-brief-save` (+ multiple follow-up PRs)
**PRs:** #1030-#1038 (9 PRs)

---

## Problems Addressed

### 1. Market Brief "0 stocks analyzed"
The Stock Intelligence dashboard showed **"0 stocks analyzed"** on the latest brief (Feb 9, Monday) while older briefs (Feb 7-8) showed 10 stocks. The bull/bear agent pipeline silently failed and the coordinator saved an empty brief, overwriting good data via `update_or_create`.

### 2. Prediction duplicates showing "+0.0%" predicted move
1,310 duplicate PredictionOutcome rows (should have been ~120). Target parsing returned `0.0` for inputs like `"25%+"` or `"-25% or more"`. No unique constraint prevented re-creation.

### 3. Railway deploy blocked by migration lock
Migration 0234 (adding UniqueConstraint to PredictionOutcome) hung during blue-green deploy — old instance held connections preventing exclusive lock.

### 4. Market Briefs showing raw JSON
`JsonSection` component dumped `JSON.stringify(item)` instead of rendering structured stock opportunity cards.

### 5. All 402 alerts were "momentum_shift" type
Yahoo Finance threshold (>5%) was too high (almost never triggers), `'rally'` keyword was too common in news, and no dedup mechanism existed.

---

## Solutions & PRs

### PR #1030 — Market Brief Save Guard
**File:** `core/agents/stocks/market_intelligence_coordinator.py`

1. **Save guard** — `_save_brief_for_tomorrow` skips saving when `total_stocks_analyzed == 0`
2. **Agent failure logging** — Explicit warnings when BullCase/BearCase agents return errors
3. **Weekend fallback** — `_load_previous_brief` falls back to most recent brief within 5 days with `total_stocks_analyzed > 0`

### PR #1031 — Prediction Dedup + Target Parsing
**File:** `core/agents/stocks/market_intelligence_coordinator.py`

1. **`_parse_target_move` static method** — Regex-based parser handles `"25%+"`, `"+15-20%"`, `"-25% or more"`, `"10% upside"` etc.
2. **`_record_predictions_for_learning`** — Switched to `update_or_create` keyed on `(brief, ticker, prediction_type)`

### PR #1032 — Migration: UniqueConstraint + Blockchain Models
**File:** `core/migrations/0234_prediction_outcome_unique_constraint.py`

- Creates `BlockchainMonitoringSession`, `BlockchainSecurityAlert`, `MarketMonitoringSession`, `StockMarketAlert` models
- `RunPython` with raw SQL `DISTINCT ON` dedup before `AddConstraint`
- Also adds `UniqueConstraint` to `PredictionOutcome` model in `core/models_unified_system.py`

### PRs #1033-1036 — Railway Deploy Fixes
- **#1033-1034:** Empty commits to trigger redeploy with 600s healthcheck timeout (set via Railway GraphQL API) — both failed because migration hung on lock
- **#1035:** Removed `migrate` from Railway start command — failed: `$PORT` not expanded without `sh -c` wrapper
- **#1036:** Fixed start command to `sh -c 'daphne -b 0.0.0.0 -p $PORT core.asgi:application'` — **deploy succeeded**
- **Post-deploy:** Manually ran dedup SQL + added constraint via `railway run`, then faked migration 0234, then restored original start command with migrate

### PR #1037 — Market Brief Detail UI
**File:** `frontend/src/pages/StockIntelligencePage.tsx`

Replaced `JsonSection` raw JSON dump with structured cards showing ticker, recommendation badge (color-coded BULLISH/BEARISH/DEBATE), confidence, target prices, bull/bear arguments (max 3 each), and risk factors.

### PR #1038 — Alert Quality + Dedup
**File:** `core/tasks.py` (`run_stock_market_intelligence`)

1. **Dedup tracking** — `seen_titles` set + recent 12h DB title check before creating alerts
2. **Yahoo Finance threshold** — Lowered from 5% to 2% (enables bull/bear/debate alerts)
3. **News noise reduction** — Removed `'rally'` keyword, reduced items per spider from 5 to 3
4. **Production cleanup** — Deleted 319 duplicate alerts via `railway run`, 84 unique remain

---

## Railway Deploy Lessons

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Healthcheck timeout | Default 300s too short for migration | Increased to 600s via Railway GraphQL API |
| Migration hung | Blue-green deploy: old instance holds connections, new migration needs exclusive lock for `AddConstraint` | Temporarily removed `migrate` from start command, ran migration manually after deploy |
| `$PORT` not expanded | Start command `daphne -b 0.0.0.0 -p $PORT` without shell wrapper | Wrap in `sh -c '...'` for variable expansion |
| Railway service config | `startCommand` in Railway GraphQL, NOT `entrypoint.sh` or `railway.toml` | Use `serviceInstanceUpdate` mutation |

---

## Verification

- All 9 PRs merged to main and deployed to Railway
- Migration 0234 applied (faked) with constraint verified in production
- Predictions now have unique constraint — no more duplicates
- Market Briefs render structured cards instead of raw JSON
- Alerts diversified: 84 unique (was 402 duplicates of same type)
- Save guard prevents 0-stock briefs from overwriting good data
- Weekend fallback loads Friday's brief on Monday morning

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/stocks/market_intelligence_coordinator.py` | Save guard, failure logging, weekend fallback, `_parse_target_move`, `update_or_create` for predictions |
| `core/models_unified_system.py` | UniqueConstraint on PredictionOutcome `(brief, ticker, prediction_type)` |
| `core/migrations/0234_prediction_outcome_unique_constraint.py` | New migration with dedup SQL + constraint + 4 new models |
| `frontend/src/pages/StockIntelligencePage.tsx` | JsonSection → structured stock cards |
| `core/tasks.py` | Alert dedup, lower Yahoo threshold, reduced news noise |
