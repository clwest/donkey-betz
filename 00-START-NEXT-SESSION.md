# Session 559 - Start Here

**Previous Session:** 558
**Date:** December 27, 2025
**Focus:** UI Updates for Betting Platform + New Features

---

## Session 558 Accomplishments

### Complete Betting Platform (8 Features)

| Feature | Command/Task | Status |
|---------|--------------|--------|
| Sports Odds Lookup | `/odds [sport]` | ✅ |
| Daily Betting Digest | Celery 8:30 AM | ✅ |
| Arbitrage Detector | `/arb` | ✅ |
| Bankroll Tracker | `/bankroll`, `/bet`, `/resolve` | ✅ |
| Market Intelligence | Every 2 hours | ✅ |
| Futures Tracker | `/futures` | ✅ |
| Bet Slip Generator | `/slip` | ✅ |
| Real-Time Alerts | Every 30 min | ✅ |

### Arbitrage Detector Fixes
- 3-way market handling (soccer with draw)
- Fuzzy team name matching
- Sanity checks (prob ≥85%, profit ≤10%)
- None value handling

### New Files
| File | Purpose |
|------|---------|
| `core/agents/markets/arbitrage_detector.py` | Arb detection agent |
| `core/models_bankroll.py` | Bankroll tracking models |
| `run_discord_bot.py` | Discord bot helper script |

**Handoff:** `docs/handoffs/SESSION_558_BETTING_PLATFORM.md`

---

## Session 559 Priorities

### 1. UI Updates for Betting Platform
The Discord commands work great, but the web UI needs updates:

- [ ] **Betting Dashboard Tab** - New tab or sub-tab showing:
  - Live odds from The Odds API
  - Arbitrage opportunities
  - User's bankroll stats
  - Recent wagers

- [ ] **Market Intelligence Panel Update** - Add:
  - Prediction market opportunities (Kalshi)
  - Sports betting insights
  - Value plays identified by agents

- [ ] **Arbitrage Alerts Widget** - Real-time notifications for arbs

- [ ] **Bankroll Visualization** - Charts for P/L over time

### 2. Additional Features to Consider
- Kelly Criterion calculator for optimal bet sizing
- Historical odds tracking / line movement charts
- Betting patterns analysis (win rate by sport/bet type)
- Push notifications for arbs (browser/mobile)

---

## Current System State

| Component | Count | Status |
|-----------|-------|--------|
| **Spiders** | 76 | +Kalshi, TheOdds |
| **Agents** | 55 | +ArbitrageDetector |
| **Discord Commands** | ~96 | 4 cogs disabled for limit |
| **Celery Beat Tasks** | +3 | Betting digest, intelligence, alerts |
| **Knowledge Entries** | 3,379+ | Active |

---

## Quick Start

```bash
# 1. Start all services
make start && make celery

# 2. Run Discord bot
.venv/bin/python run_discord_bot.py

# 3. Test betting commands in Discord
/odds nfl
/arb
/bankroll
/futures

# 4. Access AI Studio
open http://localhost:8000/ai-studio/
```

---

## Key Files (Betting Platform)

| File | Purpose |
|------|---------|
| `ai_core/spiders/specialized/theodds_spider.py` | Sports odds spider |
| `ai_core/spiders/specialized/kalshi_spider.py` | Prediction markets |
| `core/agents/markets/arbitrage_detector.py` | Arb detection |
| `core/models_bankroll.py` | Bankroll models |
| `core/services/discord_bot.py` | Discord commands |
| `core/tasks.py` | Celery tasks |

---

## Environment Variables Required

```bash
THE_ODDS_API_KEY=your_key_here      # Required for sports odds
KALSHI_API_KEY=your_key_here        # Optional for prediction markets
```

---

## Discord Commands Available

### Betting
| Command | Description |
|---------|-------------|
| `/odds [sport]` | Live sports betting odds |
| `/arb [sport]` | Arbitrage opportunities |
| `/bankroll` | View bankroll stats |
| `/bet` | Log a new wager |
| `/resolve` | Resolve pending wager |
| `/futures [league]` | Championship futures |
| `/slip` | Generate bet slip |
| `/predictions` | Kalshi prediction markets |

---

**Betting Platform: COMPLETE** ✅
**Next Focus: Web UI Updates**
