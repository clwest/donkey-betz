# Session 558: Kalshi Prediction Markets Integration

**Date:** December 26, 2025
**Status:** COMPLETE
**Focus:** Full integration of Kalshi prediction markets into the platform

---

## Overview

Added comprehensive Kalshi prediction markets integration including:
- Public API spider for market data
- Authenticated service for trading operations
- Celery tasks for automated data collection
- Market Intelligence Desk integration
- Discord `/predictions` command
- Web UI panel in Intelligence Command Center

---

## Components Created

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

**Authentication Flow:**
```
1. Create message: "{timestamp_ms}{method}{path}"
2. Sign with RSA-PSS padding + SHA-256
3. Headers: KALSHI-ACCESS-KEY, KALSHI-ACCESS-SIGNATURE, KALSHI-ACCESS-TIMESTAMP
```

### 3. Spider Registry
**File:** `ai_core/spiders/spider_registry.py`

Added Kalshi spider registration:
```python
self.register_spider('kalshi', KalshiSpider, {
    'category': 'prediction_markets',
    'priority': 1,
    'rate_limit': 1.0,
    'requires_auth': False,
    'api_key_env': 'KALSHI_API_KEY',
    'targets': ['api.elections.kalshi.com'],
    'description': 'Prediction market data: economics, politics, weather, tech events'
})
```

### 4. Celery Tasks
**File:** `core/tasks.py`

Two new tasks for automated collection:

```python
@shared_task
def collect_kalshi_prediction_markets():
    """
    Fetches 200 markets from Kalshi and stores in SpiderData.
    Runs every 30 minutes via Beat schedule.
    """

@shared_task
def collect_kalshi_market_intelligence():
    """
    Posts trending prediction markets to Discord #market-intelligence.
    Runs every 4 hours via Beat schedule.
    """
```

### 5. Celery Beat Schedules
**File:** `core/celery.py`

```python
'collect-kalshi-prediction-markets': {
    'task': 'core.tasks.collect_kalshi_prediction_markets',
    'schedule': crontab(minute='*/30'),  # Every 30 minutes
    'options': {'queue': 'default'},
},
'collect-kalshi-market-intelligence': {
    'task': 'core.tasks.collect_kalshi_market_intelligence',
    'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    'options': {'queue': 'default'},
},
```

### 6. Market Intelligence Desk Integration
**File:** `core/agents/stocks/market_intelligence_coordinator.py`

Added prediction market signals to the autonomous Market Intelligence Desk:

```python
def _get_prediction_market_signals(self, context: Dict) -> Dict[str, Any]:
    """
    Fetches Kalshi data and categorizes by:
    - economics_signals (jobs, inflation, GDP)
    - finance_signals (stocks, crypto)
    - politics_signals (elections, policy)
    - tech_signals (product launches, company events)
    - high_volume_markets (>10k volume)
    - high_probability_markets (>80%)
    - uncertain_markets (40-60%)
    """
```

Executive summary now includes prediction market insights.

### 7. Discord Command
**File:** `core/services/discord_bot.py`

Added `/predictions` command to SpiderCommands cog:

```
/predictions                      # Top 5 markets by volume
/predictions category:economics   # Filter by category
/predictions category:politics limit:10  # Combined filters
```

**Display Format:**
```
🎰 Prediction Markets
Live market data from Kalshi

📊 Will inflation exceed 3% in January 2025?
┌─────────────────────────────────────────┐
│ Probability: 72.5% ███████░░░           │
│ Yes: 71¢-74¢ | Vol: 45,230              │
│ Status: ⚪ Leaning                       │
└─────────────────────────────────────────┘
```

### 8. Web UI Panel
**Files:**
- `ai_core/templates/components/panels/intelligence_command_center.html`
- `ai_core/templates/partials/js/intelligence_command_center.html`
- `core/views_spider_intelligence.py`
- `core/urls.py`

Added Markets sub-tab to Intelligence Command Center:

**UI Components:**
- 🎲 Markets sub-tab button
- Stats row: Likely (>80%), Uncertain (40-60%), Unlikely (<20%), Total Volume
- Trending Markets section (top 5 by volume >10k)
- All Markets list (up to 20 markets)
- Category filter dropdown
- Refresh button

**Display Features:**
- Probability bar visualization (█░░░░░░░░░)
- Yes bid/ask prices in cents
- Volume numbers with formatting
- Category badges (economics, politics, tech, etc.)
- Status indicators (🟢 Likely, 🟡 Uncertain, 🔴 Unlikely, ⚪ Leaning)

**API Endpoint:**
```
GET /api/prediction-markets/
GET /api/prediction-markets/?category=economics
GET /api/prediction-markets/?category=politics&limit=20
```

**Access:** AI Studio → Intelligence Command Center → Markets tab

---

## Environment Variables

Required in `.env`:
```bash
KALSHI_API_KEY=your_api_key_here
KALSHI_PRIVATE_KEY=your_rsa_private_key_here
```

**Note:** Private key should be RSA format for RSA-PSS signing. The service loads it using `cryptography` library.

---

## API Endpoints Used

### Public (No Auth)
| Endpoint | Purpose |
|----------|---------|
| `GET /markets` | List all markets |
| `GET /markets/{ticker}` | Market details |
| `GET /markets/{ticker}/orderbook` | Order book |
| `GET /markets/{ticker}/candlesticks` | OHLC data |
| `GET /series` | Market categories |
| `GET /events` | Event collections |

### Authenticated
| Endpoint | Purpose |
|----------|---------|
| `GET /portfolio/balance` | Account balance |
| `GET /portfolio/positions` | Current positions |
| `GET /portfolio/orders` | Active orders |
| `POST /portfolio/orders` | Place order |
| `DELETE /portfolio/orders/{id}` | Cancel order |

---

## Testing

```bash
# Test spider
.venv/bin/python -c "
from ai_core.spiders.specialized.kalshi_spider import KalshiSpider
spider = KalshiSpider()
markets = spider.fetch_data(max_results=5)
for m in markets:
    if m.get('data_type') == 'prediction_market':
        print(f\"{m['title'][:50]} - {m['implied_probability_pct']:.1f}%\")
"

# Test authenticated service
.venv/bin/python -c "
from core.services.kalshi_service import KalshiService
service = KalshiService()
balance = service.get_balance()
print(f\"Balance: \${balance.get('balance', 0)/100:.2f}\")
"

# Test Celery task
.venv/bin/celery -A core call core.tasks.collect_kalshi_prediction_markets
```

---

## Data Model

Prediction markets are stored in `SpiderData` model:

```python
SpiderData.objects.filter(spider_name='kalshi')

# Fields populated:
# - spider_name: 'kalshi'
# - source_platform: 'kalshi'
# - source_url: 'https://kalshi.com/markets/{ticker}'
# - data_type: 'prediction_market'
# - raw_data: Full market JSON
# - title: Market title
# - category: Extracted category
```

---

## Bugs Fixed During Session

### 1. Orderbook Parsing
**Error:** `TypeError: list indices must be integers or slices, not str`
**Cause:** Orderbook format is `[[price, count], ...]` not `[{'price': x, 'count': y}]`
**Fix:** Changed `yes_bids[0]['price']` to `yes_bids[0][0]`

### 2. SpiderData Model Fields
**Error:** `Cannot resolve keyword 'source' into field`
**Cause:** Model uses `source_platform`, not `source`
**Fix:** Updated task to use correct field names:
```python
SpiderData.objects.update_or_create(
    spider_name='kalshi',
    source_url=f"https://kalshi.com/markets/{ticker}",
    defaults={'source_platform': 'kalshi', ...}
)
```

---

## Session 559 Recommendations

1. **Trading Automation**
   - Create trading agent that uses prediction market signals
   - Implement position tracking and P&L reporting
   - Paper trading mode for testing strategies

2. **Alert System**
   - Discord alerts when high-probability markets shift significantly
   - Alert when new markets match user interests
   - Threshold-based notifications (e.g., "probability changed >10%")

3. **Historical Analysis**
   - Track prediction accuracy over time
   - Build model for identifying mispriced markets
   - Backtest prediction strategies

4. **Enhanced UI**
   - Auto-refresh on Markets tab (every 60 seconds)
   - Market detail modal with orderbook and candlesticks
   - Watchlist functionality

---

## Files Modified

| File | Changes |
|------|---------|
| `ai_core/spiders/specialized/kalshi_spider.py` | **NEW** - 448 lines |
| `core/services/kalshi_service.py` | **NEW** - 350 lines |
| `ai_core/spiders/spider_registry.py` | Added kalshi registration |
| `core/tasks.py` | Added 2 Celery tasks |
| `core/celery.py` | Added 2 Beat schedules |
| `core/agents/stocks/market_intelligence_coordinator.py` | Added prediction signals |
| `core/services/discord_bot.py` | Added `/predictions` command |
| `ai_core/templates/components/panels/intelligence_command_center.html` | Added Markets sub-tab (+99 lines) |
| `ai_core/templates/partials/js/intelligence_command_center.html` | Added `loadPredictionMarkets()` (+140 lines) |
| `core/views_spider_intelligence.py` | Added `get_prediction_markets()` API view |
| `core/urls.py` | Added `/api/prediction-markets/` route |

---

## Summary

Session 558 delivered complete Kalshi prediction markets integration:
- **Spider:** Fetches 200 markets with probabilities, volumes, categories
- **Service:** RSA-PSS authenticated trading capability
- **Automation:** 30-minute data collection + 4-hour intelligence posts
- **Integration:** Market Intelligence Desk includes prediction signals
- **Discord:** `/predictions` command with category filtering
- **Web UI:** Markets sub-tab in Intelligence Command Center with stats, trending, and all markets

The platform now has real-time access to prediction market data for economics, politics, tech, finance, weather, and entertainment categories via Discord, Web UI, and programmatic API.
