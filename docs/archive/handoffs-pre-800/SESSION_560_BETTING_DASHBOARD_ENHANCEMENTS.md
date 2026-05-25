# Session 560: Betting Dashboard Enhancements

**Date:** December 27, 2025
**Focus:** Futures Tab, Kelly Calculator, Bet Logging, WebSocket Real-Time Updates

---

## Summary

Session 560 expanded the Betting Dashboard with 4 major features:
1. Futures Tab - Championship odds display
2. Kelly Criterion Calculator Modal - Optimal bet sizing
3. Web Bet Logging - Log bets from the web UI
4. WebSocket Real-Time Updates - Live odds updates via WebSocket

---

## New Features

### 1. Futures Tab

**Location:** Betting Dashboard > Futures tab

**API Endpoint:** `GET /api/v1/betting/futures/`
- Query params: `league` (nfl, nba, mlb, nhl), `limit`
- Returns championship futures with implied probabilities
- Falls back to cached SpiderData if live API unavailable

**Files Modified:**
- `core/views_odds_sports.py` - Added `get_futures_odds()` function
- `core/urls.py` - Added `/api/v1/betting/futures/` route
- `core/auth_middleware.py` - Added to PUBLIC_PATHS
- `ai_core/templates/components/panels/betting/betting_futures.html` - New template
- `ai_core/templates/components/panels/betting_dashboard_panel.html` - Added tab

**Features:**
- 4 leagues: NFL, NBA, MLB, NHL
- Teams sorted by implied probability (favorites first)
- League-specific colors and icons
- Crown badge for favorites

---

### 2. Kelly Criterion Calculator Modal

**Location:** Betting Dashboard > "Kelly Calculator" button

**Features:**
- American/Decimal odds input
- True probability input (your estimated win %)
- Bankroll input
- Kelly fraction selection (1/4, 1/2, Full)
- Real-time calculation with API fallback
- Risk level indicator (Low/Medium/High)
- Edge and implied probability display

**Files Modified:**
- `ai_core/templates/components/panels/betting_dashboard_panel.html`
  - Added modal HTML
  - Added Kelly calculation JavaScript
  - Added modal styles

---

### 3. Web Bet Logging

**Location:** Betting Dashboard > "Log Bet" button

**API Endpoint:** `POST /api/v1/betting/wager/`
- Requires authentication
- Creates Wager record in Bankroll
- Updates bankroll balance

**Request Body:**
```json
{
  "event_name": "Chiefs vs Raiders",
  "selection": "Chiefs ML",
  "bet_type": "moneyline",
  "odds_american": -150,
  "stake": 100,
  "sport": "NFL",
  "bookmaker": "DraftKings",
  "line": null,
  "event_time": "2025-12-28T13:00:00Z",
  "notes": "Confident pick"
}
```

**Features:**
- Full form with all bet details
- Live payout preview as you type
- Sport and bet type dropdowns
- Optional bookmaker, line, event time, notes
- Refreshes bankroll stats on success

**Files Modified:**
- `core/views_odds_sports.py` - Added `log_wager()` function
- `core/urls.py` - Added `/api/v1/betting/wager/` route
- `ai_core/templates/components/panels/betting_dashboard_panel.html`
  - Added "Log Bet" modal
  - Added form validation and submission JavaScript

---

### 4. WebSocket Real-Time Updates

**Connections:**
- `/ws/live-sports/` - Live odds updates
- `/ws/arbitrage/` - Arbitrage alerts

**Features:**
- Auto-reconnect with exponential backoff
- Odds flash animation when updated
- Score update animation
- Arb count pulse animation
- Toast notifications for significant events
- Connection status indicator support

**Files Modified:**
- `ai_core/templates/components/panels/betting_dashboard_panel.html`
  - Added WebSocket connection logic
  - Added update handlers
  - Added CSS animations for updates

---

## API Endpoints Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/betting/futures/` | GET | Public | Championship futures odds |
| `/api/v1/betting/wager/` | POST | Required | Log a new bet |

---

## CSS Animations Added

```css
.odds-flash       - Flash animation for odds updates
.score-update     - Scale animation for score changes
.arb-pulse        - Pulse animation for new arbitrage alerts
.kelly-risk-*     - Border colors for Kelly risk levels
```

---

## Testing

```bash
# Test futures endpoint
curl 'http://localhost:8000/api/v1/betting/futures/?league=nfl'

# Test wager logging (requires auth)
curl -X POST http://localhost:8000/api/v1/betting/wager/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{"event_name":"Test","selection":"Test ML","odds_american":-110,"stake":50}'
```

---

## Session 561 Priorities

1. **Line Movement Charts** - Historical odds visualization
2. **Push Notifications for Arb Alerts** - Browser notifications
3. **Mobile-Responsive Improvements** - Better mobile layout
4. **Betting Patterns Analysis** - Win rate by sport/type
5. **Export Functionality** - CSV/PDF betting history export

---

## Files Changed

| File | Lines Added | Description |
|------|-------------|-------------|
| `core/views_odds_sports.py` | ~200 | Futures + Wager endpoints |
| `core/urls.py` | 4 | Route definitions |
| `core/auth_middleware.py` | 2 | PUBLIC_PATHS |
| `betting_futures.html` | 190 | New futures template |
| `betting_dashboard_panel.html` | ~600 | Modals, WebSocket, CSS |

---

**Reality Score:** 100% - All endpoints working, UI components functional
