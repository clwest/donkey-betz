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

## Part 3: Market Analyst Agents

### 6. PredictionMarketAnalyst
**File:** `core/agents/markets/prediction_market_analyst.py`

Dedicated agent for analyzing Kalshi prediction markets.

```python
class PredictionMarketAnalyst(BaseAgent):
    name = "PredictionMarketAnalyst"

    # Signal Types Generated:
    # - HIGH_CONVICTION: >80% probability with supporting data
    # - UNCERTAIN_VALUE: 40-60% probability (research opportunities)
    # - SMART_MONEY: High volume (>50k) indicating institutional interest

    def execute(task, context):
        markets = self._get_kalshi_markets(context)     # Via KalshiSpider
        analysis = self._analyze_markets(markets, task)  # Pattern detection
        signals = self._generate_signals(markets, analysis)
        response = self._generate_analysis_report(...)   # LLM-powered report
        return AgentResult(...)
```

**Analysis Categories:**
- `high_conviction`: Markets >80% or <20% probability
- `contrarian_opportunities`: Potentially mispriced markets
- `momentum_plays`: Fast-moving probabilities
- `uncertain_markets`: 40-60% probability (toss-ups)
- `high_volume`: >50k volume (smart money signals)

### 7. SportsOddsAnalyst
**File:** `core/agents/markets/sports_odds_analyst.py`

Dedicated agent for analyzing sports betting odds.

```python
class SportsOddsAnalyst(BaseAgent):
    name = "SportsOddsAnalyst"

    # Signal Types Generated:
    # - TOSS_UP: Close games (45-55% implied) - research opportunities
    # - FAVORITE_ANALYSIS: Heavy favorites (>70%) - check spread value
    # - SHARP_MARKET: High book count (8+) - sharp money involved
    # - UPCOMING: Games starting within 24 hours

    def execute(task, context):
        events = self._get_sports_odds(context)       # Via TheOddsSpider
        analysis = self._analyze_odds(events, task)   # Pattern detection
        signals = self._generate_signals(events, analysis)
        response = self._generate_analysis_report(...)  # LLM-powered report
        return AgentResult(...)
```

**Analysis Categories:**
- `value_bets`: Potential +EV opportunities
- `toss_ups`: Close games (45-55% implied)
- `heavy_favorites`: >70% implied probability
- `sharp_indicators`: High book count, unusual lines
- `upcoming_games`: Games in next 24 hours

### Agent Registration
**File:** `core/agent_router.py`

```python
AGENT_MAP = {
    # ... existing agents ...
    'PredictionMarketAnalyst': PredictionMarketAnalyst,
    'SportsOddsAnalyst': SportsOddsAnalyst,
}
```

### Usage Examples

```python
# Via direct import
from core.agents.markets import PredictionMarketAnalyst, SportsOddsAnalyst

pma = PredictionMarketAnalyst()
result = pma.execute('analyze economics markets', context={'category': 'economics'})
# Returns: 100 markets analyzed, 5 signals

soa = SportsOddsAnalyst()
result = soa.execute('analyze NFL games', context={'sport': 'nfl'})
# Returns: 100 events analyzed, 14 signals

# Via AgentRouter
from core.agent_router import AgentRouter
router = AgentRouter(user=request.user)
result = router.route("PredictionMarketAnalyst", "find value bets")
result = router.route("SportsOddsAnalyst", "analyze today's games")
```

---

## Part 4: Session 558 Continued - Bug Fixes & Testing

### 8. Celery SIGSEGV Fix

**Problem:** Celery workers crashing with `signal 11 (SIGSEGV)` when using default prefork pool.

**Error:**
```
Process 'ForkPoolWorker-X' pid:XXXX exited with 'signal 11 (SIGSEGV)'
```

**Solution:** Use threads pool instead of prefork:
```bash
# DON'T USE (crashes)
celery -A core worker --loglevel=info

# USE THIS (works)
celery -A core worker --loglevel=info --pool=threads --concurrency=4
```

### 9. SpiderData Field Names Fix

**Problem:** Kalshi and The Odds tasks using wrong field names for `SpiderData` model.

**Error:**
```
Invalid field name(s) for model SpiderData: 'collected_at', 'raw_data'
Invalid field name(s) for model SpiderData: 'embedding_text', 'processed_data'
```

**Root Cause:** Two different `SpiderData` models exist:
- `persistence.models.SpiderData` - Correct (title, content, structured_data)
- `core.models.SpiderData` - Wrong (raw_data, processed_data)

**Fix in `core/tasks.py`:**
```python
# collect_kalshi_prediction_markets (lines 18458-18477)
# collect_sports_odds (lines 18698-18715)

# Changed to use correct fields:
SpiderData.objects.update_or_create(
    spider_name='kalshi',  # or 'theodds'
    source_url=url,
    defaults={
        'source_platform': 'kalshi',
        'data_type': 'prediction_market',
        'title': title[:500],
        'content': content[:5000],
        'category': category,
        'structured_data': {...},  # Full data goes here
        'relevance_score': 0.80,
        'quality_score': 0.85,
    }
)
```

### 10. Spider Collection Results

Ran comprehensive spider collection for all active spiders:

| Spider | Records | Category |
|--------|---------|----------|
| kalshi | 200 | Prediction Markets |
| theodds | 150 | Sports Betting |
| yahoo_finance | 30 | Finance |
| producthunt | 25 | Tech Products |
| remoteok | 25 | Remote Jobs |
| reddit | 25 | Social Media |
| techcrunch | 25 | Tech News |
| hackernews | 25 | Tech/Dev |
| coingecko | 19 | Crypto |
| axios | 15 | News |
| finnhub | 15 | Financial Data |
| mit_tech_review | 15 | Tech News |
| arstechnica | 15 | Tech News |
| wired | 15 | Tech News |
| devto | 15 | Developer |
| theverge | 15 | Tech News |

**Total: 629 records from 16 spiders**

### 11. Agent Router Enhancement

Added full tool mapping for market analysts:

```python
# core/agent_router.py - TOOL_TO_AGENT_MAP

# Session 558: Markets Agents
'prediction_market_analyst': 'PredictionMarketAnalyst',
'sports_odds_analyst': 'SportsOddsAnalyst',
'market_analysis': 'PredictionMarketAnalyst',
'sports_betting': 'SportsOddsAnalyst',
'kalshi': 'PredictionMarketAnalyst',
'odds': 'SportsOddsAnalyst',
```

Added market keyword detection for spider context:
```python
# _get_spider_context method
if any(word in task.lower() for word in ['betting', 'odds', 'sports', 'prediction', 'kalshi', 'market', 'wager']):
    context['market_analysis'] = True
```

### 12. Market Analyst Test Results

| Agent | Markets/Events | Signals | Time |
|-------|----------------|---------|------|
| PredictionMarketAnalyst | 100 markets | 5 | 10.2s |
| SportsOddsAnalyst | 100 events | 12 | 11.9s |

**PredictionMarketAnalyst Output:**
- Categories: general (88), tech (6), politics (5), weather (1)
- Total volume analyzed: 199,843
- Signal types: HIGH_CONVICTION, UNCERTAIN_VALUE, SMART_MONEY

**SportsOddsAnalyst Output:**
- Sports: NFL (13), NBA (9), NHL (18), EPL (23), UCL (18), UFC (19)
- Games in next 24h: 33
- Signal types: TOSS_UP, FAVORITE_ANALYSIS, SHARP_MARKET, UPCOMING

---

## Session 559 Recommendations

1. **Discord `/odds` Command**
   - Add dedicated sports odds command similar to `/predictions`
   - Filter by sport, show upcoming games

2. **Trading Automation**
   - Wire PredictionMarketAnalyst to actual Kalshi trading
   - Create betting recommendation system using SportsOddsAnalyst

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
| `core/agents/markets/__init__.py` | **NEW** - Package exports |
| `core/agents/markets/prediction_market_analyst.py` | **NEW** - 350 lines |
| `core/agents/markets/sports_odds_analyst.py` | **NEW** - 430 lines |
| `ai_core/spiders/spider_registry.py` | Added kalshi + theodds registration |
| `core/tasks.py` | Added 4 Celery tasks (~500 lines) + Fixed SpiderData fields |
| `core/celery.py` | Added 4 Beat schedules |
| `core/agents/stocks/market_intelligence_coordinator.py` | Added prediction signals |
| `core/agents/__init__.py` | Added markets agents exports |
| `core/agent_router.py` | Added PredictionMarketAnalyst, SportsOddsAnalyst + tool mappings |
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
| `0e18a67` | Handoff update with sports odds |
| `24711d4` | MST timezone fix for sports odds |
| `5ae63be` | Market analyst agents (PredictionMarketAnalyst, SportsOddsAnalyst) |
| `3956413` | Handoff update with market analyst agents |
| `8556a41` | Fix SpiderData field names in Kalshi/Odds tasks |
| `ed5db6c` | Register market analysts in agent router (tool mappings) |

---

## Summary

Session 558 delivered complete market intelligence integration:

**Prediction Markets (Kalshi):**
- Spider fetches 200 markets with probabilities, volumes, categories
- RSA-PSS authenticated trading capability
- 30-minute data collection + 4-hour Discord posts
- Market Intelligence Desk integration
- `/predictions` Discord command
- **PredictionMarketAnalyst agent** for LLM-powered analysis

**Sports Betting (The Odds API):**
- Spider fetches odds from 40+ bookmakers
- NFL, NBA, MLB, NHL, Soccer, UFC/MMA coverage
- Moneylines, spreads, totals, implied probabilities
- Hourly collection (conserving 20k/month quota)
- 6-hour Discord intelligence posts
- **SportsOddsAnalyst agent** for LLM-powered analysis

**Market Analyst Agents:**
- PredictionMarketAnalyst: 100 markets → 5 signals (HIGH_CONVICTION, UNCERTAIN_VALUE, SMART_MONEY)
- SportsOddsAnalyst: 100 events → 14 signals (TOSS_UP, FAVORITE_ANALYSIS, SHARP_MARKET, UPCOMING)
- Both registered in AgentRouter for routing via Personal Assistant

**Unified Web UI:**
- Markets tab in Intelligence Command Center
- Prediction Markets section (purple) with category filter
- Sports Betting section (green) with sport filter
- Real-time stats and game cards

**Bug Fixes & Testing (Part 4):**
- Fixed Celery SIGSEGV crashes (use `--pool=threads`)
- Fixed SpiderData field names in collect tasks
- Collected 629 records from 16 spiders
- Tested market analysts: 100 markets → 5 signals, 100 events → 12 signals
- Added 6 tool mappings for flexible agent invocation

The platform now has comprehensive market intelligence covering:
- Political/economic predictions (Kalshi)
- Sports betting odds (The Odds API)
- LLM-powered market analysis agents
- All accessible via Discord, Web UI, Agents, and programmatic API
- **Total registered agents: 46**

---

## Part 5: Spider Data Expansion

### 13. Kalshi Spider Pagination

**Problem:** Only fetching first page of 200 markets, but Kalshi has thousands of markets available.

**Solution:** Added cursor-based pagination to fetch up to 2000 markets:

```python
# ai_core/spiders/specialized/kalshi_spider.py

def _fetch_markets(self, limit: int = 100, status: str = 'open') -> List[Dict]:
    """Fetch markets from Kalshi API with pagination support."""
    market_data = []
    cursor = None
    max_pages = 10  # Safety limit

    for page in range(max_pages):
        params = {'limit': min(limit, 200), 'status': status}
        if cursor:
            params['cursor'] = cursor

        response = self.session.get(url, params=params, timeout=30)
        data = response.json()
        markets = data.get('markets', [])

        for market in markets:
            market_data.append(self._transform_market(market))

        cursor = data.get('cursor')
        if not cursor or len(market_data) >= limit:
            break

    return market_data[:limit]
```

**Results:**
| Before | After |
|--------|-------|
| 200 markets | 1000+ markets |
| No pagination | Cursor-based pagination |
| max_results=100 default | max_results=500 default |

**Markets by Category (1000 sample):**
- politics: 446
- general: 425
- tech: 65
- economics: 49
- weather: 4
- entertainment: 4
- finance: 4
- science: 3

**Top Volume Markets:**
- Will Trump nominate Kevin Hassett as Fed Chair? (vol: 3,989,510)
- Will Trump nominate Kevin Warsh as Fed Chair? (vol: 2,607,628)
- Will Trump nominate Christopher Waller? (vol: 2,498,180)
- Will Gavin Newsom be Democratic nominee? (vol: 2,222,606)
- Will Trump buy Greenland? (vol: 2,033,989)

### 14. The Odds API Expansion

**Problem:** Only fetching 7 priority-1 sports from 64 available sports. Missing futures, college sports, and additional leagues.

**Solution:** Expanded SPORTS dictionary from 18 → 37 sports with futures support:

```python
# ai_core/spiders/specialized/theodds_spider.py

SPORTS = {
    # US MAJOR LEAGUES (priority 1)
    'americanfootball_nfl': {'name': 'NFL', 'priority': 1},
    'basketball_nba': {'name': 'NBA', 'priority': 1},
    'baseball_mlb': {'name': 'MLB', 'priority': 1},
    'icehockey_nhl': {'name': 'NHL', 'priority': 1},

    # FUTURES / CHAMPIONSHIP WINNERS (priority 1-2) - NEW
    'americanfootball_nfl_super_bowl_winner': {'name': 'Super Bowl Winner', 'priority': 1},
    'basketball_nba_championship_winner': {'name': 'NBA Championship', 'priority': 1},
    'baseball_mlb_world_series_winner': {'name': 'World Series Winner', 'priority': 1},
    'icehockey_nhl_championship_winner': {'name': 'Stanley Cup Winner', 'priority': 1},
    'americanfootball_ncaaf_championship_winner': {'name': 'CFP Champion', 'priority': 2},
    'basketball_ncaab_championship_winner': {'name': 'March Madness Winner', 'priority': 2},

    # COLLEGE SPORTS (elevated to priority 1) - UPDATED
    'americanfootball_ncaaf': {'name': 'NCAAF', 'priority': 1},
    'basketball_ncaab': {'name': 'NCAAB', 'priority': 1},

    # SOCCER - TOP LEAGUES (priority 1-2)
    'soccer_epl': {'name': 'EPL', 'priority': 1},
    'soccer_spain_la_liga': {'name': 'La Liga', 'priority': 1},
    'soccer_uefa_champs_league': {'name': 'Champions League', 'priority': 1},
    'soccer_usa_mls': {'name': 'MLS', 'priority': 1},
    # + Bundesliga, Serie A, Ligue 1, Europa League

    # ADDITIONAL SOCCER (priority 2-3) - NEW
    'soccer_mexico_ligamx': {'name': 'Liga MX', 'priority': 2},
    'soccer_brazil_campeonato': {'name': 'Brasileirão', 'priority': 3},

    # TENNIS (all Grand Slams) - NEW
    'tennis_atp_aus_open': {'name': 'Australian Open (ATP)', 'priority': 2},
    'tennis_atp_french_open': {'name': 'French Open (ATP)', 'priority': 2},
    'tennis_atp_wimbledon': {'name': 'Wimbledon (ATP)', 'priority': 2},
    'tennis_atp_us_open': {'name': 'US Open (ATP)', 'priority': 2},
    # + WTA equivalents

    # GOLF (all Majors) - NEW
    'golf_masters_tournament_winner': {'name': 'Masters', 'priority': 2},
    'golf_pga_championship_winner': {'name': 'PGA Championship', 'priority': 2},
    'golf_us_open_winner': {'name': 'US Open (Golf)', 'priority': 2},
    'golf_the_open_championship_winner': {'name': 'The Open', 'priority': 2},

    # POLITICS - NEW
    'politics_us_presidential_election_winner': {'name': 'US Presidential Election', 'priority': 1},

    # OTHER - NEW
    'rugbyleague_nrl': {'name': 'NRL (Rugby)', 'priority': 3},
    'cricket_ipl': {'name': 'IPL (Cricket)', 'priority': 3},
}
```

**New Features:**

```python
# Futures market support
MARKETS_FUTURES = ['outrights']

# Extended regions for arbitrage detection
REGIONS = ['us']  # Default
REGIONS_EXTENDED = ['us', 'us2', 'uk', 'eu', 'au']  # For comprehensive odds comparison

# Updated fetch_data signature
def fetch_data(
    sports=None,
    max_results=200,           # Was 100
    include_futures=True,      # NEW
    max_priority=2,            # NEW - Fetch priority 1+2 by default
    extended_regions=False     # NEW
)

# Dedicated futures normalization
def _normalize_futures_event(event, sport_key, sport_info):
    """Returns top 10 contenders with implied probabilities"""
```

**Results:**
| Before | After |
|--------|-------|
| 7 sports (priority 1 only) | 37 sports (priority 1+2) |
| No futures markets | 11 futures markets (Super Bowl, NBA Championship, etc.) |
| 100 max_results default | 200 max_results default |
| US region only | Extended regions available |
| No outrights market | outrights for championship winners |

**API Stats After Expansion:**
- Active sports from API: 64
- Sports in our SPORTS dict: 37
- Priority 1 sports: 17
- Priority 2 sports: 14
- Futures/Championship sports: 11

---

## Updated Commits

| Commit | Description |
|--------|-------------|
| `e31bece` | Kalshi prediction markets integration |
| `a7e82d4` | Web UI prediction markets panel |
| `139453a` | Handoff document |
| `1504338` | Auth middleware fix |
| `14aa43f` | The Odds API sports betting integration |
| `0e18a67` | Handoff update with sports odds |
| `24711d4` | MST timezone fix for sports odds |
| `5ae63be` | Market analyst agents |
| `3956413` | Handoff update with market analyst agents |
| `8556a41` | Fix SpiderData field names in Kalshi/Odds tasks |
| `ed5db6c` | Register market analysts in agent router |
| `62bb288` | Part 4: Bug fixes & testing documentation |
| `TBD` | Part 5: Spider data expansion (pagination + futures) |

---

## Updated Summary

Session 558 delivered complete market intelligence integration with **5x data expansion**:

**Kalshi Prediction Markets:**
- Spider now fetches **1000+ markets** (was 200) with pagination
- Covers politics, tech, economics, weather, entertainment, finance, science
- High-volume markets identified (Trump Fed nominations, Greenland purchase, etc.)

**The Odds API Sports Betting:**
- Spider now covers **37 sports** (was 7) including:
  - US major leagues (NFL, NBA, MLB, NHL)
  - Futures (Super Bowl, NBA Championship, World Series, Stanley Cup)
  - College sports (NCAAF, NCAAB + championship winners)
  - All 4 Grand Slams (tennis)
  - All 4 Golf majors
  - US Presidential Election
- Extended regions available for arbitrage detection
- Outrights market for championship/winner bets

**Total Data Increase:**
| Metric | Before | After | Increase |
|--------|--------|-------|----------|
| Kalshi markets | 200 | 1000+ | 5x |
| Sports covered | 7 | 37 | 5x |
| Futures markets | 0 | 11 | NEW |
| Default results | 100 | 200-500 | 2-5x |
