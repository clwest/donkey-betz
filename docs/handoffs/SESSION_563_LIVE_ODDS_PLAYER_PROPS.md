# Session 563: Live Odds Enhancements & Player Props

**Date:** December 27, 2025
**Status:** COMPLETE
**Branch:** feature/session-52-ai-assistant

---

## Summary

Enhanced the Live Odds tab with ESPN live scores, player props modal, proper spread/total displays, and automatic dream backlog maintenance. Fixed critical bug where sport filter wasn't working (all sports showed NFL games).

---

## Features Implemented

### 1. Sport Filter Fix (`sports/data_providers.py`)

**Bug:** Regardless of sport selected (NBA, NFL, NCAAF), only NFL games were displayed.

**Root Cause:** Frontend sends full API keys like `basketball_nba` but `SPORT_MAPPING` used short keys (`nba`) as lookup, defaulting to NFL.

**Fix:** Added check for full API keys:
```python
# Session 563: Support both short keys (nfl) and full keys (americanfootball_nfl)
if '_' in sport:
    sport_key = sport
else:
    sport_key = self.SPORT_MAPPING.get(sport, 'americanfootball_nfl')
```

### 2. Live Scores Integration (`core/views_odds_sports.py`)

New endpoint `/api/v1/sports/live-odds-scores/` combines:
- The Odds API for betting odds
- ESPN Scoreboard API for live scores

| Feature | Description |
|---------|-------------|
| Live Score Display | "Orlando Magic 125 - Denver Nuggets 124" |
| Status Detail | "11.9 - 4th", "Halftime", "FINAL" |
| Auto-Refresh | Every 30 seconds when live games exist |
| Visual Indicator | Red border + 🔴 LIVE badge for in-progress games |

### 3. Player Props Modal (`core/views_odds_sports.py`)

New endpoint `/api/v1/sports/events/{event_id}/props/`

| Sport | Available Props |
|-------|-----------------|
| **NBA/NCAAB** | Points, Rebounds, Assists, Threes, Blocks, Steals, PRA, Double-Double |
| **NFL/NCAAF** | Pass TDs, Pass Yds, Rush Yds, Rec Yds, Receptions, Anytime TD, First TD |
| **NHL** | Points, Assists, Shots on Goal, Blocked Shots |
| **MLB** | Hits, Home Runs, RBIs, Total Bases, Pitcher Strikeouts |

**UI Features:**
- Props organized by player name
- Over/Under buttons with best odds from all bookmakers
- Click to add to bet slip
- Sport-appropriate emojis (🏈 football, 🏀 basketball, 🏒 hockey, ⚾ baseball)
- Graceful handling when props unavailable (422 → "No Props Available")

### 4. Spread/Total Point Display

**Before:** "Atlanta Hawks" with odds
**After:** "Atlanta Hawks **+8.5**" with odds (spread line in yellow)

**Before:** "Over" with odds
**After:** "Over **245.5**" with odds (total in yellow)

### 5. Bet Slip Integration

- Click any odds button to add to bet slip
- Parlay odds calculation (American to decimal conversion)
- Click prop Over/Under to add player props
- Visual selection indicator

### 6. Dream Backlog Maintenance (`core/tasks.py`)

New Celery task `maintain_dream_backlog()`:
- Runs daily at 3 AM
- Archives dreams with score < 0.3 older than 7 days
- Archives dreams with score 0.3-0.5 older than 14 days
- Archived 2,004 stale dreams on first run

---

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/sports/live-odds-scores/` | GET | Public | Odds + ESPN live scores |
| `/api/v1/sports/events/{id}/props/` | GET | Public | Player props for event |

### Query Parameters

**live-odds-scores:**
- `sport` - Sport key (e.g., `basketball_nba`, `americanfootball_nfl`)
- `markets` - Market type (`h2h`, `spreads`, `totals`)

**props:**
- `sport` - Sport key for prop market selection

---

## Files Modified

| File | Changes |
|------|---------|
| `sports/data_providers.py` | Fixed sport key handling for full API keys |
| `core/views_odds_sports.py` | Added `live_odds_with_scores()`, `get_player_props()` |
| `core/auth_middleware.py` | Added public paths for new endpoints |
| `core/tasks.py` | Added `maintain_dream_backlog()` task |
| `core/settings.py` | Added Celery Beat schedule for dream maintenance |
| `betting_odds.html` | Complete UI rewrite with live scores, props modal, bet slip |

---

## Frontend Changes (`betting_odds.html`)

### New Components

1. **Live Score Display**
   - Shows current score for in-progress games
   - Green highlight for leading team
   - Status detail (quarter, period, inning)

2. **Props Modal**
   - Bootstrap modal triggered by "📊 Props" button
   - Loading spinner while fetching
   - Empty state for unavailable props
   - Error state with message

3. **Bet Slip Panel**
   - Sticky sidebar showing picks
   - Parlay odds calculation
   - Remove individual picks
   - Clear all button

4. **Point Display for Spreads/Totals**
   - Yellow highlighted point values
   - Formatted with +/- for spreads
   - Included in bet slip description

---

## Testing

```bash
# Test sport filter fix
curl "http://localhost:8000/api/v1/sports/live-odds/?sport=basketball_nba" | jq '.odds | length'

# Test live scores endpoint
curl "http://localhost:8000/api/v1/sports/live-odds-scores/?sport=basketball_nba" | jq '.data[0].live'

# Test player props
curl "http://localhost:8000/api/v1/sports/events/{event_id}/props/?sport=basketball_nba" | jq '.props_by_player | keys'

# Test props unavailable (returns graceful empty response)
curl "http://localhost:8000/api/v1/sports/events/invalid_id/props/?sport=americanfootball_nfl"
```

---

## Celery Beat Schedule

```python
'maintain-dream-backlog': {
    'task': 'core.tasks.maintain_dream_backlog',
    'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
},
```

---

## Session 564 Priorities

1. **Betting History/Tracking** - Record placed bets, track P/L over time
2. **Mobile-Responsive Improvements** - Better touch UI for betting dashboard
3. **Betting Patterns Analysis** - Historical win/loss tracking
4. **Export Functionality** - CSV/PDF export for bet history

---

## Live Odds Tab Features (Complete)

| Feature | Status |
|---------|--------|
| Sport Filter (NBA, NFL, NCAAF, NCAAB) | ✅ Fixed |
| Market Filter (Moneyline, Spread, O/U) | ✅ Working |
| Live Scores | ✅ New |
| Auto-Refresh (30s) | ✅ New |
| Spread Point Display | ✅ New |
| Total Point Display | ✅ New |
| Player Props Modal | ✅ New |
| Bet Slip | ✅ New |
| Sport-Specific Emojis | ✅ New |

---

## Architecture Notes

### Live Scores Flow
```
Frontend (loadLiveOdds)
    ↓
/api/v1/sports/live-odds-scores/
    ↓
┌─────────────────────────────────┐
│  The Odds API (betting odds)    │
│  ESPN Scoreboard API (scores)   │
└─────────────────────────────────┘
    ↓
Merge by team name matching
    ↓
Return combined data with live.is_live, live.home_score, etc.
```

### Props Flow
```
Click "📊 Props" button
    ↓
openPropsModal(eventId, matchup)
    ↓
/api/v1/sports/events/{id}/props/
    ↓
The Odds API /v4/sports/{sport}/events/{id}/odds
    ↓
Parse & organize by player
    ↓
Render modal with Over/Under buttons
    ↓
Click → togglePropPick() → Add to betSlip
```
