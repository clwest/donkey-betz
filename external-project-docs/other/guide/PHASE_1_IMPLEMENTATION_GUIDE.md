# Phase 1 Implementation Guide: Reddit API & Real-Time Prices

## Quick Start (Week 1-2)

### 1. Reddit API Integration

#### Step 1: Set Up Reddit App
```bash
# 1. Go to https://www.reddit.com/prefs/apps
# 2. Create app (script type)
# 3. Add to .env:
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=DonkeyBetz/1.0
```

#### Step 2: Install Dependencies
```bash
cd backend
pip install praw asyncpraw
```

#### Step 3: Create Reddit Service
```python
# backend/agent_orchestra/services/reddit_api_service.py
import praw
import asyncpraw
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RedditAPIService:
    """Real Reddit API integration for authentic data"""
    
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT
        )
    
    async def get_hot_ideas(self, subreddits: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """Get hot posts from business/startup subreddits"""
        ideas = []
        
        for subreddit_name in subreddits:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            for post in subreddit.hot(limit=limit):
                if self._is_business_idea(post):
                    ideas.append({
                        'id': post.id,
                        'title': post.title,
                        'text': post.selftext,
                        'score': post.score,
                        'upvote_ratio': post.upvote_ratio,
                        'num_comments': post.num_comments,
                        'created_utc': post.created_utc,
                        'author': str(post.author),
                        'subreddit': subreddit_name,
                        'url': post.url,
                        'awards': len(post.all_awardings)
                    })
        
        return ideas
    
    def _is_business_idea(self, post) -> bool:
        """Filter for actual business ideas"""
        keywords = ['idea', 'startup', 'business', 'app', 'saas', 'product']
        text = (post.title + ' ' + post.selftext).lower()
        return any(keyword in text for keyword in keywords)
```

#### Step 4: Update Reddit Scout Agent
```python
# Modify existing Reddit Scout to use real API
async def execute_reddit_scout(user, task):
    reddit_service = RedditAPIService()
    
    # Target subreddits
    subreddits = [
        'Entrepreneur',
        'startups', 
        'SaaS',
        'Business_Ideas',
        'Startup_Ideas',
        'smallbusiness'
    ]
    
    # Get real Reddit data
    ideas = await reddit_service.get_hot_ideas(subreddits, limit=100)
    
    # Process with ML scoring (Phase 1 basic version)
    scored_ideas = score_reddit_ideas(ideas)
    
    # Save to database
    for idea in scored_ideas[:20]:  # Top 20
        RedditIdea.objects.create(
            user=user,
            reddit_id=idea['id'],
            title=idea['title'],
            description=idea['text'],
            score=idea['ml_score'],
            source_data=idea
        )
```

### 2. Real-Time Price Monitoring

#### Step 1: Choose Provider (Alpha Vantage for start)
```bash
# Add to .env
ALPHA_VANTAGE_API_KEY=your_api_key
```

#### Step 2: Create Market Data Service
```python
# backend/agent_orchestra/services/market_data_service.py
import aiohttp
from decimal import Decimal
from django.core.cache import cache

class MarketDataService:
    """Real-time market data integration"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a symbol"""
        
        # Check cache first (5 min TTL)
        cache_key = f"quote_{symbol}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': settings.ALPHA_VANTAGE_API_KEY
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, params=params) as response:
                data = await response.json()
                
                if 'Global Quote' in data:
                    quote = self._parse_quote(data['Global Quote'])
                    cache.set(cache_key, quote, 300)  # 5 min cache
                    return quote
                    
        return None
    
    def _parse_quote(self, raw_quote) -> Dict[str, Any]:
        """Parse Alpha Vantage quote format"""
        return {
            'symbol': raw_quote['01. symbol'],
            'price': Decimal(raw_quote['05. price']),
            'change': Decimal(raw_quote['09. change']),
            'change_percent': raw_quote['10. change percent'].rstrip('%'),
            'volume': int(raw_quote['06. volume']),
            'latest_trading_day': raw_quote['07. latest trading day'],
            'previous_close': Decimal(raw_quote['08. previous close']),
            'open': Decimal(raw_quote['02. open']),
            'high': Decimal(raw_quote['03. high']),
            'low': Decimal(raw_quote['04. low'])
        }
```

#### Step 3: Add WebSocket for Live Updates
```python
# backend/agent_orchestra/consumers/stock_price_consumer.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class StockPriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
            
        await self.channel_layer.group_add("stock_prices", self.channel_name)
        await self.accept()
        
        # Send initial prices for user's watchlist
        await self.send_initial_prices()
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data['type'] == 'subscribe':
            symbols = data['symbols']
            # Start price monitoring for these symbols
            await self.subscribe_to_symbols(symbols)
        
    async def stock_price_update(self, event):
        """Send price update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'price_update',
            'symbol': event['symbol'],
            'price': event['price'],
            'change': event['change'],
            'change_percent': event['change_percent'],
            'volume': event['volume'],
            'timestamp': event['timestamp']
        }))
```

#### Step 4: Create Price Update Task
```python
# backend/agent_orchestra/tasks/market_data_tasks.py
from celery import shared_task
from channels.layers import get_channel_layer

@shared_task
def update_stock_prices():
    """Update prices every minute during market hours"""
    
    # Get all tracked symbols
    symbols = StockOpportunity.objects.values_list('ticker', flat=True).distinct()
    
    market_data_service = MarketDataService()
    channel_layer = get_channel_layer()
    
    for symbol in symbols:
        try:
            quote = market_data_service.get_quote(symbol)
            
            if quote:
                # Update database
                StockOpportunity.objects.filter(ticker=symbol).update(
                    current_price=quote['price']
                )
                
                # Send WebSocket update
                async_to_sync(channel_layer.group_send)(
                    "stock_prices",
                    {
                        "type": "stock_price_update",
                        "symbol": symbol,
                        "price": str(quote['price']),
                        "change": str(quote['change']),
                        "change_percent": quote['change_percent'],
                        "volume": quote['volume'],
                        "timestamp": timezone.now().isoformat()
                    }
                )
        except Exception as e:
            logger.error(f"Error updating {symbol}: {e}")
```

### 3. Basic ML Scoring System

#### Step 1: Create Feature Extractor
```python
# backend/agent_orchestra/ml/reddit_feature_extractor.py
import numpy as np
from typing import Dict, List

class RedditFeatureExtractor:
    """Extract ML features from Reddit posts"""
    
    def extract_features(self, post: Dict) -> np.ndarray:
        """Convert Reddit post to feature vector"""
        
        features = []
        
        # Engagement metrics
        features.append(post['score'])  # Upvotes
        features.append(post['upvote_ratio'])  # Quality indicator
        features.append(post['num_comments'])  # Discussion level
        features.append(post['awards'])  # Premium engagement
        
        # Time features
        hours_old = (time.time() - post['created_utc']) / 3600
        features.append(hours_old)
        features.append(post['score'] / max(hours_old, 1))  # Velocity
        
        # Text features
        text = post['title'] + ' ' + post['text']
        features.append(len(text.split()))  # Word count
        features.append(text.count('?'))  # Questions
        features.append(text.count('!'))  # Excitement
        
        # Keywords (simplified - use embeddings later)
        keywords = ['revolutionary', 'disrupt', 'ai', 'saas', 'app']
        for keyword in keywords:
            features.append(1 if keyword in text.lower() else 0)
        
        return np.array(features)
```

#### Step 2: Simple Scoring Model
```python
# backend/agent_orchestra/ml/reddit_scorer.py
from sklearn.ensemble import RandomForestRegressor
import joblib

class RedditIdeaScorer:
    """Score Reddit ideas using ML"""
    
    def __init__(self):
        # Load pre-trained model or use rules-based for v1
        try:
            self.model = joblib.load('models/reddit_scorer.pkl')
        except:
            self.model = None  # Fallback to rules
    
    def score_ideas(self, ideas: List[Dict]) -> List[Dict]:
        """Score a batch of Reddit ideas"""
        
        if self.model:
            # ML scoring
            features = [self.extract_features(idea) for idea in ideas]
            scores = self.model.predict(features)
        else:
            # Rules-based scoring for v1
            scores = [self._rules_based_score(idea) for idea in ideas]
        
        # Add scores to ideas
        for idea, score in zip(ideas, scores):
            idea['ml_score'] = float(score)
            idea['confidence'] = self._calculate_confidence(idea)
        
        return sorted(ideas, key=lambda x: x['ml_score'], reverse=True)
    
    def _rules_based_score(self, idea: Dict) -> float:
        """Simple rules-based scoring"""
        score = 50.0  # Base score
        
        # Engagement scoring
        score += min(idea['score'] / 10, 30)  # Max 30 points
        score += min(idea['num_comments'] / 5, 20)  # Max 20 points
        
        # Quality indicators
        if idea['upvote_ratio'] > 0.8:
            score += 10
        if idea['awards'] > 0:
            score += 5 * min(idea['awards'], 3)
        
        # Recency boost
        hours_old = (time.time() - idea['created_utc']) / 3600
        if hours_old < 24:
            score += 10
        elif hours_old < 72:
            score += 5
        
        return min(score, 100)  # Cap at 100
```

### 4. Frontend Integration Updates

#### React Component for Real-Time Prices
```typescript
// frontend/src/components/RealTimePriceTicker.tsx
import { useWebSocket } from '../hooks/useWebSocket';

export const RealTimePriceTicker = ({ symbol, initialPrice }) => {
  const [price, setPrice] = useState(initialPrice);
  const [change, setChange] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  
  const { sendMessage } = useWebSocket({
    url: '/ws/stock-prices/',
    onMessage: (data) => {
      if (data.type === 'price_update' && data.symbol === symbol) {
        setPrice(data.price);
        setChange(data.change);
      }
    },
    onOpen: () => {
      setIsConnected(true);
      sendMessage({ type: 'subscribe', symbols: [symbol] });
    }
  });
  
  return (
    <div className={`price-ticker ${change > 0 ? 'positive' : 'negative'}`}>
      <span className="symbol">{symbol}</span>
      <span className="price">${price}</span>
      <span className="change">
        {change > 0 ? '+' : ''}{change} ({changePercent}%)
      </span>
      {isConnected && <div className="live-indicator" />}
    </div>
  );
};
```

### 5. Database Migrations

```python
# New models needed
class RedditPost(models.Model):
    reddit_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=300)
    text = models.TextField()
    author = models.CharField(max_length=100)
    subreddit = models.CharField(max_length=50)
    score = models.IntegerField()
    upvote_ratio = models.FloatField()
    num_comments = models.IntegerField()
    created_utc = models.DateTimeField()
    ml_score = models.FloatField(null=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class MarketDataCache(models.Model):
    symbol = models.CharField(max_length=10)
    data_type = models.CharField(max_length=50)  # quote, intraday, etc
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['symbol', 'data_type']
```

### Testing & Deployment Checklist

- [ ] Reddit API credentials working
- [ ] Alpha Vantage API key valid
- [ ] WebSocket connection established
- [ ] Price updates flowing
- [ ] Reddit posts being fetched
- [ ] ML scoring functioning
- [ ] Frontend displaying real-time data
- [ ] Error handling for API limits
- [ ] Caching layer working
- [ ] Background tasks scheduled

This implementation guide provides concrete steps to get Phase 1 features working within 2 weeks!