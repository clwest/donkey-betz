# Agent Tool Execution Flow in Donkey Betz

## Overview

Agents in the Donkey Betz system execute tasks by leveraging a sophisticated tool system with 37 specialized APIs and services. Here's how the tool execution flow works:

## Tool Categories

### 1. **Financial Data Tools** (11 tools)
- `polygon_market_data`: Professional market data
- `polygon_quote`: Real-time stock quotes
- `polygon_technicals`: Technical indicators (RSI, MACD, etc.)
- `polygon_trades`: Detailed trade data
- `polygon_options`: Options chain analysis
- `polygon_historical`: Historical price data
- `yahoo_finance`: Backup market data
- `sec_edgar_api`: SEC filings
- `earnings_api`: Earnings calendars
- `get_real_time_quote`: Quick quotes
- `polygon_flat_files`: Bulk data downloads

### 2. **Research & Intelligence Tools** (9 tools)
- `web_search`: Internet search via Serper API
- `news_api`: News aggregation
- `reddit_api`: Reddit discussions
- `reddit_trending_stocks`: Trending stock mentions
- `sentiment_api`: Sentiment analysis
- `statista_api`: Market statistics
- `patent_api`: Patent searches
- `industry_reports`: Industry analysis
- `data_analyzer`: Comprehensive analysis

### 3. **Business Intelligence Tools** (4 tools)
- `crunchbase_api`: Startup and funding data
- `competitor_api`: Competitive analysis
- `github_api`: Code repository analysis
- `stackoverflow`: Technical Q&A data

### 4. **Government & Legal Tools** (3 tools)
- `congress_api`: Congressional data
- `federal_register`: Federal regulations
- `gov_contracts_api`: Government contracts

### 5. **Data Processing Tools** (10 tools)
- `spreadsheet_generator`: Financial models
- `chart_creator`: Data visualizations
- `pdf_generator`: Report generation
- `document_generator`: Document creation
- `trend_detector`: Pattern detection
- `risk_calculator`: Risk assessment
- `comparison_tool`: Comparative analysis
- `alert_system`: Notifications
- `calendar_checker`: Event tracking
- `data_analyzer`: Deep analysis

## Tool Execution Flow

### Step 1: Task Analysis & Tool Selection
```python
# Agent receives task
task = "Analyze Tesla's Q4 performance and market position"

# LLM analyzes and creates execution plan
execution_plan = {
    "steps": [
        {
            "description": "Get Tesla stock data",
            "tool": "polygon_market_data",
            "params": {"symbol": "TSLA", "timeframe": "Q4"}
        },
        {
            "description": "Fetch recent Tesla news",
            "tool": "news_api",
            "params": {"query": "Tesla Q4 earnings"}
        },
        {
            "description": "Analyze Reddit sentiment",
            "tool": "reddit_trending_stocks",
            "params": {"ticker": "TSLA"}
        }
    ]
}
```

### Step 2: Enhanced Tool Execution
The `EnhancedAgentService` executes each tool with resilience features:

```python
# For each step in the plan
for step in execution_plan["steps"]:
    # Execute with resilience features
    result = execute_step_with_resilience(
        step=step,
        features={
            "circuit_breaker": True,    # Prevent cascading failures
            "caching": True,            # Use intelligent caching
            "retry": True,              # Exponential backoff retry
            "validation": True          # Validate data quality
        }
    )
```

### Step 3: Circuit Breaker Protection
```python
# Tool execution wrapped in circuit breaker
@circuit_breaker(failure_threshold=3, recovery_timeout=60)
async def call_polygon_api(params):
    # If 3 failures occur, circuit opens for 60 seconds
    # Prevents overwhelming failing services
    return await polygon_api.get_data(params)
```

### Step 4: Intelligent Caching
```python
# Check cache before API call
cache_key = f"polygon_{symbol}_{timeframe}"
cached_data = APICache.get(cache_key)

if cached_data and not is_stale(cached_data):
    return cached_data
else:
    # Make API call and cache result
    fresh_data = await api_call()
    APICache.set(cache_key, fresh_data, ttl=300)  # 5 min cache
    return fresh_data
```

### Step 5: Data Validation
```python
# Validate API response data
validator = DataValidator()
validated_data = validator.validate(
    data=api_response,
    schema={
        "required": ["symbol", "price", "volume"],
        "types": {
            "symbol": str,
            "price": float,
            "volume": int
        }
    }
)
```

### Step 6: Agent Communication
Agents share tool results with other agents:
```python
# Agent broadcasts successful data retrieval
message = AgentMessage(
    agent_id=agent.id,
    task="Fetched TSLA market data",
    data={
        "symbol": "TSLA",
        "price": 238.45,
        "volume": 142384900,
        "change_pct": 3.2
    },
    quality=DataQuality.REAL_TIME
)
communicator.send_message(message)
```

## Real-World Example: Stock Scout Agent

Here's how the Stock Scout Agent uses multiple tools:

```python
# 1. Reddit Scout discovers trending stock
reddit_data = await reddit_api.get_trending_stocks()
# Result: "NVDA mentioned 245 times, 89% positive"

# 2. Get comprehensive market data
market_data = await polygon_market_data.get_quote("NVDA")
technical_data = await polygon_technicals.get_indicators("NVDA")
# Result: Price $722, RSI 68, MACD bullish

# 3. Fetch recent news
news = await news_api.search("NVIDIA AI chips")
# Result: "New H200 chip announcement, major contracts"

# 4. SEC filings check
filings = await sec_edgar_api.get_latest_filings("NVDA")
# Result: "Q3 revenue $18.12B, beat estimates"

# 5. Sentiment analysis
sentiment = await sentiment_api.analyze({
    "reddit": reddit_data,
    "news": news
})
# Result: "Overall sentiment: 8.5/10 bullish"

# 6. Generate comprehensive report
report = await document_generator.create_report({
    "title": "NVDA Investment Opportunity",
    "sections": {
        "market_data": market_data,
        "technicals": technical_data,
        "sentiment": sentiment,
        "fundamentals": filings
    }
})
```

## Error Handling & Fallbacks

### Graceful Degradation
When a tool fails, agents use fallback strategies:

```python
try:
    # Primary: Polygon.io for real-time data
    data = await polygon_quote.get("AAPL")
except PolygonAPIError:
    try:
        # Fallback 1: Yahoo Finance
        data = await yahoo_finance.get("AAPL")
    except YahooAPIError:
        # Fallback 2: Use cached data with warning
        data = get_cached_data("AAPL")
        data["warning"] = "Using cached data from 1 hour ago"
```

### Error Classification
The system classifies errors for appropriate handling:
- **Transient**: Network timeouts → Retry with backoff
- **Rate Limit**: Too many requests → Queue and throttle
- **Data Quality**: Invalid response → Use validation fallback
- **Service Down**: API unavailable → Circuit breaker + cache

## Performance Optimizations

### 1. **Batch Processing**
Instead of individual API calls:
```python
# Inefficient: 10 separate API calls
for symbol in symbols:
    data = await get_quote(symbol)

# Optimized: 1 batch API call
data = await get_quotes_batch(symbols)
# Reduces API costs by 50-80%
```

### 2. **Pre-warming Cache**
For financial agents:
```python
# Pre-warm cache with common symbols
CacheWarmer.warm_market_data(['AAPL', 'GOOGL', 'MSFT', 'TSLA'])
# Subsequent requests hit cache, no API calls needed
```

### 3. **Parallel Tool Execution**
When tools don't depend on each other:
```python
# Execute independent tools in parallel
results = await asyncio.gather(
    news_api.search("Tesla"),
    reddit_api.get_sentiment("TSLA"),
    polygon_api.get_technicals("TSLA")
)
# 3x faster than sequential execution
```

## Tool Access Control

Each agent type has specific tool access:

### Financial Agents
- Full access to all Polygon APIs
- SEC filings and earnings data
- Risk calculators and technical indicators

### Research Agents
- Web search and news APIs
- Patent and academic databases
- Industry reports and statistics

### Business Agents
- Crunchbase for startup data
- Competitor analysis tools
- Market sizing and projections

This sophisticated tool system enables agents to gather real-world data, process it intelligently, and deliver actionable insights while maintaining high reliability and performance.