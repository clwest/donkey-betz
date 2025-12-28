# Session 561: Line Movement Charts

**Date:** December 27, 2025
**Status:** COMPLETE
**Branch:** feature/session-52-ai-assistant

---

## Summary

Implemented Line Movement Charts feature for the Betting Dashboard, enabling users to track how odds change over time for games. This is a critical tool for sharp bettors who want to identify steam moves, reverse line movement, and optimal betting timing.

---

## Features Implemented

### 1. Data Models (`core/models_odds_history.py`)
- **OddsSnapshot**: Stores individual odds captures with timestamp
  - game_id, sport_key, bookmaker, market type
  - price (American odds), point (spread/total value)
  - captured_at timestamp with db_index

- **GameLineHistory**: Aggregated line tracking per game
  - Opening and current spreads/totals
  - Movement deltas (current - opening)
  - Snapshot count for trend depth

### 2. Celery Task (`core/tasks.py`)
- `snapshot_odds_for_line_movement()` - runs every 20 minutes
- Fetches live odds from TheOddsSpider
- Creates OddsSnapshot records for h2h, spreads, totals
- Updates GameLineHistory with movement calculations
- Tested: 177 snapshots from 45 games successfully captured

### 3. API Endpoints (`core/views_odds_sports.py`)
- `GET /api/v1/betting/line-movement/` - All games with movement data
- `GET /api/v1/betting/line-movement/<game_id>/` - Specific game history
- `GET /api/v1/betting/movers/` - Games with significant movement (>0.5 spread or >1 total)

Parameters supported:
- `sport` - Filter by sport key
- `market` - Filter by market type (h2h, spreads, totals)
- `bookmaker` - Filter by sportsbook
- `hours` - Limit to recent N hours

### 4. Frontend Component (`ai_core/templates/components/panels/betting/betting_line_movement.html`)
- 7th sub-tab in Betting Dashboard
- Sport dropdown filter
- Movement threshold slider
- Stats row: Games tracked, Movers count, Avg movement
- Chart.js line chart for visualizing historical movement
- Table of games with significant line changes
- Click-to-chart functionality for any game

---

## Bug Fixes

### Console Errors Fixed
1. **`game.bookmakers[0].markets?.find is not a function`**
   - File: `betting_odds.html`
   - Fix: Changed from `.find()` to direct property access since `markets` is an object keyed by market type

2. **`/api/sessions/active/` 500 error**
   - File: `views_session_handoff.py`
   - Fix: Added missing `from django.db import models` import

### Spider Data Structure Issues
3. **`sport` parameter error**
   - Spider uses `sports` (list) not `sport` (string)

4. **Field name mismatch**
   - Spider returns `event_id` not `id`
   - Spider returns pre-aggregated odds (`home_odds`, `home_spread`) not `bookmakers` array

---

## Database

### Migration
- `0126_session_561_odds_history.py` - Creates OddsSnapshot and GameLineHistory tables

### Current Data
- 177 OddsSnapshot records
- 45 GameLineHistory records
- Tracking: NHL, NBA, NFL, NCAAB, NCAAF

---

## Files Modified/Created

### New Files
| File | Purpose |
|------|---------|
| `core/models_odds_history.py` | OddsSnapshot and GameLineHistory models |
| `core/migrations/0126_session_561_odds_history.py` | Database migration |
| `ai_core/templates/components/panels/betting/betting_line_movement.html` | Frontend component |
| `docs/handoffs/SESSION_561_LINE_MOVEMENT_CHARTS.md` | This handoff |

### Modified Files
| File | Changes |
|------|---------|
| `core/models.py` | Import odds history models |
| `core/tasks.py` | Added `snapshot_odds_for_line_movement()` task |
| `core/celery.py` | Added beat schedule for every 20 minutes |
| `core/views_odds_sports.py` | Added `get_line_movement()` and `get_games_with_movement()` |
| `core/urls.py` | Added line movement routes |
| `core/auth_middleware.py` | Added paths to PUBLIC_PATHS |
| `ai_core/templates/components/panels/betting_dashboard_panel.html` | Added Line Movement tab |
| `ai_core/templates/components/panels/betting/betting_odds.html` | Fixed markets access bug |
| `core/views_session_handoff.py` | Fixed missing models import |

---

## Testing

```bash
# Verify data collection
.venv/bin/python manage.py shell -c "from core.models_odds_history import *; print(f'Snapshots: {OddsSnapshot.objects.count()}, Games: {GameLineHistory.objects.count()}')"
# Output: Snapshots: 177, Games: 45

# Test APIs
curl http://localhost:8000/api/v1/betting/line-movement/ | jq '.games | length'
# Output: 45

curl http://localhost:8000/api/v1/betting/movers/ | jq '.movers | length'
# Output: 0 (no significant movement yet - need multiple snapshots)

# Manually trigger snapshot
.venv/bin/celery -A core call core.tasks.snapshot_odds_for_line_movement
```

---

## Session 562 Priorities

From Session 561 roadmap, remaining items:
1. **Push Notifications for Arb Alerts** - WebSocket or browser push when arb detected
2. **Mobile-Responsive Improvements** - Better touch UI for betting dashboard
3. **Betting Patterns Analysis** - Historical win/loss tracking
4. **Export Functionality** - CSV/PDF export for bet history

---

## Architecture Notes

### Data Flow
```
TheOddsSpider.fetch_data()
    ↓
snapshot_odds_for_line_movement() [Celery, every 20min]
    ↓
OddsSnapshot (raw captures)
GameLineHistory (aggregated movement)
    ↓
/api/v1/betting/line-movement/
/api/v1/betting/movers/
    ↓
betting_line_movement.html (Chart.js visualization)
```

### Movement Detection
- Spread movement > 0.5 points = significant
- Total movement > 1.0 points = significant
- Sharp money indication when line moves against public betting

---

## Notes

- Line movement tracking requires time to build data. Initial snapshot shows no movement since we only have 1 data point per game.
- After 24-48 hours of snapshots (72-144 captures), meaningful movement patterns will emerge.
- Celery Beat must be running for automatic snapshots: `make celery`
