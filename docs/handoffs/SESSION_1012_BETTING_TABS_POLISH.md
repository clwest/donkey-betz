---
originating_session: 1012
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1012 — Betting Dashboard Polish & Bug Fixes

**Date:** February 15, 2026
**PRs:** #1215-#1219

## Overview

Comprehensive overhaul of all 12 betting dashboard tabs plus 4 console error fixes and AI track record dedup. Goal: make the betting section impressive for demo to sports bettors.

## Changes

### PR #1215 — Sharp Action Tab Redesign

**Backend (`core/agents/markets/sharp_action_detector.py`):**
- Added `home_team`/`away_team` to signal dict for frontend recommendation rendering
- Improved LLM prompt: asks for which side to bet, best bookmaker, why, urgency (ACT NOW / MONITOR / WAIT)
- Includes stale line details in prompt text

**Frontend (`frontend/src/pages/BettingPage.tsx`):**
- Expanded sport filter from 4 to 13 (added NCAAB, NCAAF, EPL, La Liga, Bundesliga, Serie A, MLS, Champions League, UFC)
- Redesigned signal cards with recommendation box, game times, stale line diffs
- LLM analysis rendered with markdown formatting

### PR #1216 — Betting Tabs Overhaul (6 improvements)

**Backend (`core/views_odds_sports.py`):**
- `get_todays_games()`: ESPN score merge for period/clock/quarter, `h2h_odds` in response
- `get_bankroll_management()`: Real PlacedWager queries replacing hardcoded mock data
- `get_bankroll_stats()`: Real queries (total, at_risk, available, roi, win_rate, avg_bet, etc.)

**Frontend (`frontend/src/pages/BettingPage.tsx`):**
1. Today's Games — period/clock display, expandable per-bookmaker comparison grid
2. Live Odds — full redesign with scores, LIVE/FINAL badges, per-bookmaker grid
3. Bankroll — real data display (total wagered, net P/L, ROI, Kelly criterion)
4. My Wagers — "Log Wager" manual entry form with payout calculator
5. Arbitrage — stake calculator with per-leg amounts and guaranteed profit
6. Today's Games — bookmaker comparison grid

### PR #1217 — Console Error Fixes (4 bugs)

| Endpoint | Error | Root Cause | Fix |
|----------|-------|-----------|-----|
| `/api/orchestration/active-work/` | 500 | `completion_percentage` is `@property`, not DB field | Compute in Python loop |
| `/api/agent-learning/stats/` | 404 | URL deleted Session 1009, frontend still called it | Point to `/api/learning/stats/` |
| `/api/learning/patterns/` | 401 | Auth check returned 401 for unauthenticated | Return empty data |
| `/api/learning/insights/` | 401 | Same auth check | Return empty data |

### PR #1218 — Today's Games Crash Fix

- `eid` undefined variable in bookmaker toggle → replaced with `game.event_id`

### PR #1219 — AI Track Record Dedup

- MLPrediction task creates multiple rows per game across runs. Deduped by `game_id` via `Max('id')` — only latest prediction per game counts for W/L stats and pending list.

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/markets/sharp_action_detector.py` | home_team/away_team fields, improved LLM prompt |
| `core/views_odds_sports.py` | ESPN merge, real bankroll, h2h_odds, track record dedup |
| `core/views_orchestration.py` | Fix completion_percentage @property in .values() |
| `core/views_learning_loop.py` | Return empty data instead of 401 for unauthenticated |
| `frontend/src/pages/BettingPage.tsx` | All 12 tabs overhauled |
| `frontend/src/lib/api.ts` | Fix agent-learning/stats → learning/stats |
