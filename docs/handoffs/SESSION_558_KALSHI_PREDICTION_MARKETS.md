# Session 558: Prediction Markets & Sports Odds Integration

**Date:** December 26-27, 2025
**Status:** COMPLETE
**Focus:** Full integration of Kalshi prediction markets AND The Odds API sports betting

---

## Overview

Added comprehensive market intelligence integrations:

**Part 1: Kalshi Prediction Markets**
- Public API spider for market data
- Authenticated service for trading operations
- Celery tasks for automated data collection
- Market Intelligence Desk integration
- Discord `/predictions` command

**Part 2: The Odds API Sports Betting**
- Sports odds spider for 40+ bookmakers
- NFL, NBA, MLB, NHL, Soccer, UFC/MMA coverage
- Celery tasks for hourly collection
- Web UI panel with sports section

**Unified Web UI:** Markets sub-tab in Intelligence Command Center

---

## Part 1: Kalshi Prediction Markets

### 1. Kalshi Spider
**File:** `ai_core/spiders/specialized/kalshi_spider.py`

Public API spider that fetches prediction market data without authentication.

```python
class KalshiSpider:
    name = "kalshi"
    base_url = "https://api.elections.kalshi.com/trade-api/v2"

    # Categories: economics, politics, weather, tech, entertainment, finance, science

    def fetch_data(max_results=100)      # Main entry point
    def _fetch_markets(limit, status)     # Get markets list
    def _fetch_trending_markets(limit)    # High-volume markets
    def _fetch_series(limit)              # Market categories
    def _fetch_events(limit)              # Event collections
    def _fetch_market_orderbook(ticker)   # Order book depth
    def _fetch_market_candlesticks(ticker) # OHLC price data
    def get_market_details(ticker)        # Full market info
    def search_markets(query, limit)      # Search by keyword
    def get_markets_by_category(category) # Filter by category
```

**Data Transform:**
- Calculates `implied_probability` from yes_bid/yes_ask midpoint
- Extracts category from title patterns
- Adds tags: `high_volume`, `active`, `likely`, `unlikely`, `uncertain`, `tradeable`

### 2. Kalshi Service
**File:** `core/services/kalshi_service.py`

Authenticated service with RSA-PSS SHA-256 signing for trading operations.

```python
class KalshiService:
    # Authentication
    def _sign_request(timestamp_ms, method, path) -> str
    def _get_auth_headers(method, path) -> Dict

    # Portfolio (requires auth)
    def get_balance() -> Dict           # Account balance
    def get_positions() -> Dict         # Current positions
    def get_orders(ticker=None) -> Dict # Active orders

    # Trading (requires auth)
    def place_order(ticker, side, count, type, yes_price, no_price) -> Dict
    def cancel_order(order_id) -> Dict

    # Market Intelligence (uses spider)
    def get_market_intelligence(categories=None) -> Dict
```

### 3. Discord Command
**File:** `core/services/discord_bot.py`

```
/predictions                      # Top 5 markets by volume
/predictions category:economics   # Filter by category
/predictions category:politics limit:10  # Combined filters
```

---

## Part 2: The Odds API Sports Betting

### 4. The Odds Spider
**File:** `ai_core/spiders/specialized/theodds_spider.py` (NEW - 448 lines)

Sports betting odds aggregator fetching from 40+ bookmakers.

```python
class TheOddsSpider:
    name = "theodds"
    base_url = "https://api.the-odds-api.com/v4"

    # Sports covered (priority 1 = fetched by default)
    SPORTS = {
        'americanfootball_nfl': {'name': 'NFL', 'priority': 1},
        'basketball_nba': {'name': 'NBA', 'priority': 1},
        'baseball_mlb': {'name': 'MLB', 'priority': 1},
        'icehockey_nhl': {'name': 'NHL', 'priority': 1},
        'soccer_epl': {'name': 'English Premier League', 'priority': 1},
        'soccer_uefa_champs_league': {'name': 'Champions League', 'priority': 1},
        'mma_mixed_martial_arts': {'name': 'UFC/MMA', 'priority': 1},
        # + college sports, other soccer leagues, tennis, golf, boxing
    }

    # Preferred US bookmakers
    PREFERRED_BOOKMAKERS = ['draftkings', 'fanduel', 'betmgm', 'caesars', 'bovada']

    def fetch_data(sports=None, max_results=100)  # Main entry point
    def get_sport_odds(sport_key)                  # Single sport
    def get_upcoming_events(hours=24)              # Next 24 hours
    def get_best_bets()                            # Toss-up games (45-55%)
    def get_api_usage()                            # Track quota
```

**Data Transform:**
- Calculates implied probabilities from American odds
- Identifies favorite team
- Extracts spread and total lines
- Tags: `heavy_favorite`, `favorite`, `toss_up`, `has_spread`, `has_totals`, `live`

**Sample Output:**
```json
{
    "event_id": "832c36c4b6d5132e88cf11391797c194",
    "sport_name": "NFL",
    "title": "Houston Texans @ Los Angeles Chargers",
    "home_team": "Los Angeles Chargers",
    "away_team": "Houston Texans",
    "home_odds": 102,
    "away_odds": -122,
    "home_implied_prob": 49.5,
    "home_spread": 1.5,
    "total_line": 40.5,
    "favorite": "Houston Texans",
    "best_bookmaker": "draftkings"
}
```

### 5. Spider Registry
**File:** `ai_core/spiders/spider_registry.py`

```python
# Kalshi
self.register_spider('kalshi', KalshiSpider, {
    'category': 'prediction_markets',
    'priority': 1,
    'requires_auth': False,
    'api_key_env': 'KALSHI_API_KEY',
})

# The Odds API
self.register_spider('theodds', TheOddsSpider, {
    'category': 'sports_odds',
    'priority': 1,
    'requires_auth': True,
    'api_key_env': 'THE_ODDS_API_KEY',
})
```

---

## Celery Tasks & Schedules

### Tasks
**File:** `core/tasks.py`

```python
# Kalshi (existing)
@shared_task
def collect_kalshi_prediction_markets():
    """Fetches 200 markets, stores in SpiderData. Every 30 min."""

@shared_task
def collect_kalshi_market_intelligence():
    """Posts trending markets to Discord. Every 4 hours."""

# The Odds API (new)
@shared_task
def collect_sports_odds():
    """Fetches odds for NFL, NBA, MLB, NHL, Soccer, UFC. Every hour."""

@shared_task
def collect_sports_odds_intelligence():
    """Posts upcoming games to Discord. Every 6 hours."""
```

### Beat Schedules
**File:** `core/celery.py`

```python
'collect-kalshi-prediction-markets': {
    'schedule': crontab(minute='*/30'),  # Every 30 minutes
},
'collect-kalshi-market-intelligence': {
    'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
},
'collect-sports-odds': {
    'schedule': crontab(minute='*/60'),  # Every hour (conserve API quota)
},
'collect-sports-odds-intelligence': {
    'schedule': crontab(minute=30, hour='*/6'),  # Every 6 hours
},
```

---

## Web UI: Markets Tab

**Files:**
- `ai_core/templates/components/panels/intelligence_command_center.html`
- `ai_core/templates/partials/js/intelligence_command_center.html`
- `core/views_spider_intelligence.py`
- `core/urls.py`

**Access:** AI Studio → Intelligence Command Center → 🎲 Markets tab

### Prediction Markets Section (Purple Theme)
- Stats row: Likely (>80%), Uncertain (40-60%), Unlikely (<20%), Total Volume
- Trending Markets (top 5 by volume >10k)
- All Prediction Markets list
- Category filter: economics, politics, finance, tech, weather, entertainment, science

### Sports Betting Section (Green Theme)
- Stats row: Upcoming (24h), Toss-ups (45-55%), Active Leagues
- Sport filter: NFL, NBA, MLB, NHL, College, Soccer, UFC
- Game cards showing:
  - Teams with favorite in bold
  - Moneyline odds (color-coded)
  - Spread and O/U lines
  - Implied probabilities

**API Endpoints:**
```
GET /api/prediction-markets/
GET /api/prediction-markets/?category=economics
GET /api/sports-odds/
GET /api/sports-odds/?sport=nfl
GET /api/sports-odds/?sport=nba&limit=20
```

---

## Environment Variables

Required in `.env`:
```bash
# Kalshi (prediction markets)
KALSHI_API_KEY=your_api_key_here
KALSHI_PRIVATE_KEY=your_rsa_private_key_here

# The Odds API (sports betting)
THE_ODDS_API_KEY=your_api_key_here
```

**API Quotas:**
- Kalshi: Unlimited public API
- The Odds API: 20,000 requests/month (paid tier)

---

## Testing

```bash
# Test Kalshi spider
.venv/bin/python -c "
from ai_core.spiders.specialized.kalshi_spider import KalshiSpider
spider = KalshiSpider()
markets = spider.fetch_data(max_results=5)
for m in markets:
    if m.get('data_type') == 'prediction_market':
        print(f\"{m['title'][:50]} - {m['implied_probability_pct']:.1f}%\")
"

# Test The Odds spider
.venv/bin/python -c "
from ai_core.spiders.specialized.theodds_spider import TheOddsSpider
spider = TheOddsSpider()
events = spider.fetch_data(max_results=5)
for e in events:
    if e.get('data_type') == 'sports_odds':
        print(f\"{e['title']} - {e['favorite']} favored\")
"

# Test API endpoints
curl 'http://localhost:8000/api/prediction-markets/?limit=3'
curl 'http://localhost:8000/api/sports-odds/?sport=nfl&limit=3'

# Run Celery tasks
.venv/bin/celery -A core call core.tasks.collect_kalshi_prediction_markets
.venv/bin/celery -A core call core.tasks.collect_sports_odds
```

---

## Data Model

Both spiders store data in `SpiderData`:

```python
# Prediction markets
SpiderData.objects.filter(spider_name='kalshi', data_type='prediction_market')

# Sports odds
SpiderData.objects.filter(spider_name='theodds', data_type='sports_odds')
```

---

## Bugs Fixed During Session

### 1. Orderbook Parsing (Kalshi)
**Error:** `TypeError: list indices must be integers or slices, not str`
**Fix:** Orderbook format is `[[price, count], ...]` not `[{'price': x, 'count': y}]`

### 2. SpiderData Model Fields
**Error:** `Cannot resolve keyword 'source' into field`
**Fix:** Model uses `source_platform`, not `source`

### 3. Auth Middleware
**Error:** API returns 401 for prediction-markets and sports-odds endpoints
**Fix:** Added both paths to `PUBLIC_PATHS` in `core/auth_middleware.py`

---

## Session 559 Recommendations

1. **Discord `/odds` Command**
   - Add dedicated sports odds command similar to `/predictions`
   - Filter by sport, show upcoming games

2. **Trading Automation**
   - Create trading agent that uses prediction market signals
   - Sports betting analysis agent

3. **Alert System**
   - Discord alerts for significant line movements
   - Notification when odds shift >10%

4. **Historical Analysis**
   - Track prediction accuracy over time
   - Build model for identifying value bets

---

## Files Modified

| File | Changes |
|------|---------|
| `ai_core/spiders/specialized/kalshi_spider.py` | **NEW** - 448 lines |
| `ai_core/spiders/specialized/theodds_spider.py` | **NEW** - 448 lines |
| `core/services/kalshi_service.py` | **NEW** - 350 lines |
| `ai_core/spiders/spider_registry.py` | Added kalshi + theodds registration |
| `core/tasks.py` | Added 4 Celery tasks (~500 lines) |
| `core/celery.py` | Added 4 Beat schedules |
| `core/agents/stocks/market_intelligence_coordinator.py` | Added prediction signals |
| `core/services/discord_bot.py` | Added `/predictions` command |
| `ai_core/templates/.../intelligence_command_center.html` | Markets tab + Sports section (~170 lines) |
| `ai_core/templates/.../js/intelligence_command_center.html` | `loadPredictionMarkets()` + `loadSportsOdds()` (~280 lines) |
| `core/views_spider_intelligence.py` | Added 2 API views |
| `core/urls.py` | Added 2 routes |
| `core/auth_middleware.py` | Added 2 public paths |

---

## Commits

| Commit | Description |
|--------|-------------|
| `e31bece` | Kalshi prediction markets integration |
| `a7e82d4` | Web UI prediction markets panel |
| `139453a` | Handoff document |
| `1504338` | Auth middleware fix |
| `14aa43f` | The Odds API sports betting integration |

---

## Summary

Session 558 delivered complete market intelligence integration:

**Prediction Markets (Kalshi):**
- Spider fetches 200 markets with probabilities, volumes, categories
- RSA-PSS authenticated trading capability
- 30-minute data collection + 4-hour Discord posts
- Market Intelligence Desk integration
- `/predictions` Discord command

**Sports Betting (The Odds API):**
- Spider fetches odds from 40+ bookmakers
- NFL, NBA, MLB, NHL, Soccer, UFC/MMA coverage
- Moneylines, spreads, totals, implied probabilities
- Hourly collection (conserving 20k/month quota)
- 6-hour Discord intelligence posts

**Unified Web UI:**
- Markets tab in Intelligence Command Center
- Prediction Markets section (purple) with category filter
- Sports Betting section (green) with sport filter
- Real-time stats and game cards

The platform now has comprehensive market intelligence covering:
- Political/economic predictions (Kalshi)
- Sports betting odds (The Odds API)
- All accessible via Discord, Web UI, and programmatic API
