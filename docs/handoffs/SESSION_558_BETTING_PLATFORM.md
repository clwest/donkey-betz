# Session 558: Complete Betting Platform

**Date:** December 27, 2025
**Status:** COMPLETE ✅
**Focus:** Sports betting and prediction markets integration

---

## Overview

Built a comprehensive betting intelligence platform integrating The Odds API for sports betting and Kalshi API for prediction markets. Includes 8 major features with Discord commands, autonomous scanning, and arbitrage detection.

---

## Features Implemented

### 1. Sports Odds Lookup (`/odds`)
- Real-time odds from 40+ bookmakers via The Odds API
- Supports NFL, NBA, MLB, NHL, NCAAF, NCAAB, Soccer, UFC, Tennis, Golf
- Shows moneyline, spread, and totals
- Displays implied probabilities and identifies favorites

### 2. Daily Betting Digest (Celery Task)
- **Schedule:** 8:30 AM daily
- **Task:** `core.tasks.daily_betting_digest`
- Posts to Discord #opportunities channel:
  - Top prediction market opportunities from Kalshi
  - Best sports betting value plays
  - Toss-up games (45-55% implied probability)
  - Heavy favorites and high-volume markets

### 3. Arbitrage Detector (`/arb`)
- Cross-bookmaker arbitrage detection
- **Fixes applied this session:**
  - 3-way market handling (soccer with draw)
  - Fuzzy team name matching (LA Chargers = Los Angeles Chargers)
  - Sanity checks: total prob ≥85%, profit ≤10%
  - None value handling for missing odds
- Shows stake calculations for guaranteed profit
- Ratings: HOT (1.5%+), GOOD (1-1.5%), MARGINAL (0.5-1%)

### 4. Bankroll Tracker (`/bankroll`, `/bet`, `/resolve`)
- **Models:** `Bankroll`, `Wager`, `BettingSession`
- Track balance, P/L, ROI, win rate
- Unit-based betting with configurable unit size
- Streak tracking (hot/cold)
- Pending wager management

### 5. Market Intelligence Feed (Celery Task)
- **Schedule:** Every 2 hours
- **Task:** `core.tasks.market_intelligence_scan`
- Runs market analyst agents
- Posts findings to Discord

### 6. Futures Championship Tracker (`/futures`)
- Super Bowl, NBA Championship, World Series, Stanley Cup
- CFP Champion, March Madness Winner
- Shows top contenders with odds and implied probabilities

### 7. Bet Slip Generator (`/slip`)
- Create single bets or parlays
- Calculates potential payouts
- Shows risk vs reward analysis

### 8. Real-Time Alert System (Celery Task)
- **Schedule:** Every 30 minutes
- **Task:** `core.tasks.market_movement_alerts`
- Monitors for significant odds changes
- Alerts on line movements >10%

---

## Files Created

| File | Purpose |
|------|---------|
| `core/agents/markets/arbitrage_detector.py` | Arbitrage detection agent (~500 lines) |
| `core/models_bankroll.py` | Bankroll tracking models (~280 lines) |
| `core/migrations/0125_session_558_bankroll_tracker.py` | Database migration |
| `run_discord_bot.py` | Helper script to run Discord bot |

---

## Files Modified

| File | Changes |
|------|---------|
| `ai_core/spiders/specialized/theodds_spider.py` | Added `h2h_odds` array, `_teams_match()` fuzzy matching |
| `core/services/discord_notifications.py` | Added `send_betting_digest()` method |
| `core/services/discord_bot.py` | Added 7 slash commands, disabled 4 cogs for command limit |
| `core/tasks.py` | Added 3 new Celery tasks |
| `core/celery.py` | Added 3 beat schedules |
| `core/agent_router.py` | Registered ArbitrageDetector |
| `core/agents/__init__.py` | Export ArbitrageDetector |
| `core/models/__init__.py` | Import bankroll models |

---

## Discord Commands Added

| Command | Description |
|---------|-------------|
| `/odds [sport]` | Get live sports betting odds |
| `/arb [sport] [min_profit]` | Scan for arbitrage opportunities |
| `/bankroll` | View your betting bankroll |
| `/bet <event> <selection> <odds> <stake>` | Log a new wager |
| `/resolve <wager_id> <result>` | Resolve a pending wager |
| `/futures [league]` | Get championship futures odds |
| `/slip <type> <events>` | Generate a bet slip |
| `/predictions` | Get Kalshi prediction market data |

---

## Celery Schedules Added

```python
'daily-betting-digest': {
    'task': 'core.tasks.daily_betting_digest',
    'schedule': crontab(hour=8, minute=30),
},
'market-intelligence-scan': {
    'task': 'core.tasks.market_intelligence_scan',
    'schedule': crontab(minute=0, hour='*/2'),
},
'market-movement-alerts': {
    'task': 'core.tasks.market_movement_alerts',
    'schedule': crontab(minute='*/30'),
},
```

---

## Bug Fixes

### 1. Discord 100 Command Limit
- **Problem:** Bot had 112 commands, Discord max is 100
- **Fix:** Disabled 4 less-critical cogs:
  - VoiceMarketplaceCommands
  - PipelineLearningCommands
  - NarrativeCommands
  - ROICommands

### 2. Arbitrage False Positives
- **Problem:** Showing 40-100% fake arbs
- **Root causes:**
  - Soccer 3-way markets treated as 2-way
  - Team names mismatched between bookmakers
  - Stale/bad API data not filtered
- **Fixes:**
  - Separate 2-way vs 3-way detection
  - `_teams_match()` fuzzy matching
  - Sanity checks (prob ≥85%, profit ≤10%)

### 3. None Odds Handling
- **Problem:** `'>' not supported between NoneType and int`
- **Fix:** Added None check in `_american_to_decimal()`

---

## API Integrations

### The Odds API
- **Endpoint:** `https://api.the-odds-api.com/v4`
- **Key:** `THE_ODDS_API_KEY` env var
- **Quota:** 20,000 requests/month
- **Sports:** 40+ leagues, 40+ bookmakers

### Kalshi API
- **Endpoint:** `https://api.elections.kalshi.com/trade-api/v2`
- **Key:** `KALSHI_API_KEY` env var
- **Markets:** Politics, economics, weather, events

---

## Testing Done

- [x] `/odds` returns live odds with bookmaker names
- [x] `/arb` shows realistic 2-5% arbs (not 100%+)
- [x] `/bankroll` displays user balance and stats
- [x] `/bet` logs wagers correctly
- [x] `/futures` shows championship contenders
- [x] Bot stays under 100 command limit
- [x] Celery tasks registered in beat schedule

---

## Commits

| Hash | Message |
|------|---------|
| `9157341` | feat(Session 558): Complete Betting Platform with 8 Features |
| `e123d6f` | fix(Session 558): Arbitrage detector accuracy improvements |

---

## Next Session Priorities

### UI Updates Needed
1. **Betting Dashboard Tab** - Display odds, arbs, bankroll in web UI
2. **Market Intelligence Panel** - Show prediction market opportunities
3. **Arbitrage Alerts Widget** - Real-time arb notifications
4. **Bankroll Visualization** - Charts for P/L over time

### Additional Features to Consider
1. **Kelly Criterion Calculator** - Optimal bet sizing
2. **Historical Odds Tracking** - Line movement charts
3. **Betting Patterns Analysis** - Win rate by sport/bet type
4. **Automated Alerts** - Push notifications for arbs
5. **Multi-user Bankroll** - Per-user tracking (currently uses request.user)

---

## Environment Variables Required

```bash
THE_ODDS_API_KEY=your_key_here
KALSHI_API_KEY=your_key_here  # Optional, for prediction markets
```

---

## How to Test

```bash
# Start services
make start
make celery

# Run Discord bot
.venv/bin/python run_discord_bot.py

# Test in Discord
/odds nfl
/arb
/bankroll
/futures nfl
```

---

**Session 558 Complete** ✅
