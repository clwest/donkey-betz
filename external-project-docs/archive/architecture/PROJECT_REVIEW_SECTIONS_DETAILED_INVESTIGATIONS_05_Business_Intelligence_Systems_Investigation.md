# Detailed Investigation: Business Intelligence Systems

## Common Issues to Investigate

### Issue 1: Stock Data Shows "Hypothetical" Results
**Problem**: Stock analysis returns made-up data instead of real market data

**Investigation Steps:**

1. **Trace API Configuration**
   ```python
   # Check API keys in settings
   File: backend/server/settings/api_keys.py or .env
   
   POLYGON_API_KEY = ?
   ALPHA_VANTAGE_KEY = ? (deprecated?)
   
   # Verify in Django shell
   from django.conf import settings
   print(f"Polygon key exists: {bool(settings.POLYGON_API_KEY)}")
   ```

2. **API Service Investigation**
   ```
   File: backend/api_services/polygon_service.py
   
   Check:
   - Error handling when API fails
   - Fallback data generation
   - Mock data returns
   
   Look for:
   if not api_key or error:
       return generate_mock_data()  # This is the problem!
   ```

3. **Rate Limiting Check**
   ```python
   # Find rate limit implementation
   File: backend/api_services/rate_limiter.py
   
   # Check Redis for rate limit data
   from django.core.cache import cache
   print(cache.get('polygon_api_calls'))
   ```

### Issue 2: Reddit Scout Not Finding Real Opportunities
**Problem**: Reddit Scout returns generic/fake business ideas

**Investigation Steps:**

1. **Reddit API Authentication**
   ```python
   # Check Reddit credentials
   File: backend/api_services/reddit_api.py
   
   CLIENT_ID = ?
   CLIENT_SECRET = ?
   USER_AGENT = ?
   ```

2. **Subreddit Monitoring Logic**
   ```
   File: backend/api/business_hub/services/reddit_service.py
   Method: fetch_subreddit_posts()
   
   Add logging:
   logger.info(f"Fetching from: {subreddit}")
   logger.info(f"Posts retrieved: {len(posts)}")
   logger.info(f"First post title: {posts[0].title if posts else 'None'}")
   ```

3. **Opportunity Extraction**
   ```
   File: backend/api/business_hub/services/opportunity_extractor.py
   
   Questions:
   - How are opportunities identified?
   - Is AI used or keyword matching?
   - What scoring algorithm is used?
   ```

### Issue 3: Business Plans Too Generic
**Problem**: Generated business plans lack specific market data

**Investigation Steps:**

1. **Universal Builder Integration**
   ```
   File: backend/universal_builder/services/builder_service.py
   
   Trace:
   - How is market data injected?
   - What templates are used?
   - Is real data passed to agents?
   ```

2. **Agent Data Access**
   ```python
   # In business_strategy_agent.py
   def execute(self, prompt, context):
       # Check if market_data is in context
       market_data = context.get('market_data', {})
       logger.info(f"Market data available: {bool(market_data)}")
   ```

## Specific Code Queries

### Query 1: Find Mock Data Generation
```bash
# Find where mock/hypothetical data is created
grep -r "mock\|fake\|hypothetical\|example\.com" backend/api_services/ --include="*.py"
grep -r "generate.*sample\|create.*dummy" backend/api/business_hub/ --include="*.py"

# Find hardcoded stock prices
grep -r "price.*=.*[0-9]\+\.[0-9]\+\|100\|200\|150" backend/api/business_hub/ --include="*.py"
```

### Query 2: Trace Real Data Flow
```bash
# Find Polygon API calls
grep -r "polygon\.io\|/v2/aggs\|/v1/open-close" backend/ --include="*.py"

# Find data caching
grep -r "cache\.set.*stock\|cache\.get.*stock" backend/ --include="*.py"
```

### Query 3: Reddit Integration
```bash
# Find Reddit API usage
grep -r "reddit\|praw\|subreddit" backend/ --include="*.py"

# Find opportunity scoring
grep -r "score.*opportunity\|rank.*idea" backend/api/business_hub/ --include="*.py"
```

## Testing Real Data Flow

### Test 1: Stock API Connection
```python
# Direct API test
from api_services.polygon_service import PolygonService

service = PolygonService()
result = service.get_quote('AAPL')

print(f"Response: {result}")
print(f"Is real data: {'example.com' not in str(result)}")
print(f"Has price: {result.get('price') is not None}")
```

### Test 2: Reddit Data Retrieval
```python
# Test Reddit connection
from api.business_hub.services.reddit_service import RedditService

service = RedditService()
posts = service.fetch_subreddit_posts('entrepreneur', limit=5)

for post in posts:
    print(f"Title: {post.title}")
    print(f"Score: {post.score}")
    print(f"URL: {post.url}")
    print("---")
```

### Test 3: End-to-End Business Generation
```python
# Test complete flow
from agent_orchestra.services.orchestration_service import OrchestrationService

orchestrator = OrchestrationService()
result = orchestrator.create_orchestration(
    template_id='business_plan',
    parameters={'industry': 'technology', 'budget': 50000}
)

# Check for real data markers
print("Contains real market data:", "NYSE" in str(result) or "NASDAQ" in str(result))
print("Contains hypothetical:", "hypothetical" in str(result).lower())
```

## Critical Files to Debug

1. **Data Services**
   - `backend/api_services/polygon_service.py` - Stock data
   - `backend/api_services/reddit_api.py` - Reddit data
   - `backend/api_services/market_data_service.py` - Data aggregation

2. **Business Logic**
   - `backend/api/business_hub/services/stock_service.py` - Stock analysis
   - `backend/api/business_hub/services/reddit_service.py` - Reddit mining
   - `backend/api/business_hub/services/opportunity_extractor.py` - Opportunity logic

3. **Agent Integration**
   - `backend/agent_orchestra/agents/market_research_agent.py` - Market data usage
   - `backend/agent_orchestra/agents/business_strategy_agent.py` - Business planning

## Common Problems and Solutions

### Problem: API Returns Mock Data on Failure
```python
# Bad pattern in polygon_service.py
def get_quote(self, symbol):
    try:
        response = self.api_call(f"/v2/aggs/ticker/{symbol}")
        return response
    except Exception as e:
        # Don't do this!
        return {
            'symbol': symbol,
            'price': 150.00,  # Hardcoded!
            'source': 'hypothetical'
        }

# Better approach
def get_quote(self, symbol):
    try:
        response = self.api_call(f"/v2/aggs/ticker/{symbol}")
        return response
    except Exception as e:
        logger.error(f"Polygon API failed: {e}")
        # Try cache
        cached = cache.get(f"stock:{symbol}")
        if cached:
            cached['source'] = 'cache'
            return cached
        # Return error, don't fake it
        return {'error': 'Unable to fetch real-time data', 'symbol': symbol}
```

### Problem: Reddit Posts Not Being Analyzed
```python
# Check opportunity extraction
def extract_opportunities(self, posts):
    opportunities = []
    
    for post in posts:
        # Log what's happening
        logger.info(f"Analyzing post: {post.title[:50]}")
        
        # Check if AI service is called
        if self.use_ai_analysis:
            analysis = self.ai_service.analyze_post(post)
            logger.info(f"AI analysis result: {analysis}")
        
        # Verify scoring
        score = self.calculate_opportunity_score(post)
        logger.info(f"Opportunity score: {score}")
        
        if score > self.threshold:
            opportunities.append(self.create_opportunity(post))
    
    return opportunities
```

### Problem: Business Plans Missing Market Context
```python
# Ensure context is passed to agents
def generate_business_plan(self, idea, market_data=None):
    # Fetch real market data if not provided
    if not market_data:
        market_data = self.fetch_market_data(idea.industry)
    
    # Pass to agent with full context
    context = {
        'idea': idea,
        'market_data': market_data,
        'competitors': self.fetch_competitors(idea.industry),
        'trends': self.fetch_industry_trends(idea.industry)
    }
    
    # Agent should receive all data
    result = self.business_agent.execute(
        prompt=f"Create business plan for: {idea.description}",
        context=context
    )
    
    return result
```

## Performance Investigation

### Check API Rate Limits
```python
# Monitor API usage
from django.core.cache import cache
from datetime import datetime, timedelta

# Check Polygon usage
polygon_calls = cache.get('polygon_api_calls_today', 0)
print(f"Polygon API calls today: {polygon_calls}")

# Check Reddit usage  
reddit_calls = cache.get('reddit_api_calls_hour', 0)
print(f"Reddit API calls this hour: {reddit_calls}")
```

### Optimize Data Fetching
```python
# Batch API calls
def get_multiple_quotes(self, symbols):
    # Instead of individual calls
    # for symbol in symbols:
    #     self.get_quote(symbol)
    
    # Use batch endpoint
    symbols_str = ','.join(symbols)
    response = self.api_call(f"/v2/aggs/grouped/locale/us/market/stocks/{date}")
    
    # Process and cache results
    for ticker_data in response['results']:
        cache.set(f"stock:{ticker_data['T']}", ticker_data, timeout=300)
    
    return response['results']
```