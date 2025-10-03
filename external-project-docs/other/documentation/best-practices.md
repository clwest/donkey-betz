# Best Practices

Recommended patterns and practices for optimal use of the Unified AI & Sports Analytics Platform.

## AI Provider Best Practices

### Model Selection

#### Choose the Right Model for the Task

| Task Type | Recommended Model | Reasoning |
|-----------|------------------|-----------|
| Simple queries | Claude 3 Haiku | Fast, cheap, adequate |
| General tasks | GPT-3.5 Turbo | Balanced performance/cost |
| Complex reasoning | GPT-4 | Superior capabilities |
| Long context | Claude 3 Sonnet | 100K+ token window |

```python
def select_model(task_complexity, context_length):
    """Smart model selection based on requirements."""
    if context_length > 50000:
        return 'claude-3-sonnet'
    elif task_complexity == 'simple':
        return 'claude-3-haiku'
    elif task_complexity == 'complex':
        return 'gpt-4'
    else:
        return 'gpt-3.5-turbo'
```

### Cost Optimization

#### 1. Implement Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_completion(prompt_hash, model):
    """Cache AI responses for repeated queries."""
    return ai.complete(prompt, model)

def get_completion(prompt, model='gpt-3.5-turbo'):
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    return cached_completion(prompt_hash, model)
```

#### 2. Batch Similar Requests

```python
def batch_completions(prompts, model='gpt-3.5-turbo'):
    """Process multiple prompts efficiently."""
    # Combine prompts with delimiters
    combined = "\n---\n".join(prompts)
    response = ai.complete(combined, model)
    
    # Split responses
    return response.split("\n---\n")
```

#### 3. Use Streaming for Long Responses

```python
async def stream_completion(prompt):
    """Stream responses to reduce perceived latency."""
    async for chunk in ai.stream_complete(prompt):
        yield chunk
        # Process chunk immediately
```

### Error Handling

#### Implement Robust Retry Logic

```python
import time
from typing import Optional

def resilient_ai_call(
    prompt: str,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> Optional[str]:
    """AI call with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return ai.complete(prompt)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = backoff_factor ** attempt
            time.sleep(wait_time)
    
    return None
```

## Sports Analytics Best Practices

### Bankroll Management

#### 1. Never Risk More Than 5% Per Bet

```python
def calculate_safe_stake(bankroll: float, kelly_stake: float) -> float:
    """Ensure stake doesn't exceed safe limits."""
    max_stake = bankroll * 0.05  # 5% maximum
    return min(kelly_stake, max_stake)
```

#### 2. Use Fractional Kelly for Stability

```python
def stable_kelly(bankroll, probability, odds):
    """Use quarter Kelly for reduced variance."""
    full_kelly = kelly_criterion(bankroll, probability, odds)
    
    # Quarter Kelly (25% of full)
    safe_stake = full_kelly.recommended_stake * 0.25
    
    return {
        'stake': safe_stake,
        'percentage': safe_stake / bankroll * 100,
        'risk_level': 'conservative'
    }
```

#### 3. Track Everything

```python
class BettingTracker:
    """Track all bets for analysis."""
    
    def __init__(self):
        self.history = []
    
    def record_bet(self, bet_data):
        bet_data['timestamp'] = datetime.now()
        self.history.append(bet_data)
        self.save_to_database()
    
    def analyze_performance(self):
        return {
            'total_bets': len(self.history),
            'win_rate': self.calculate_win_rate(),
            'roi': self.calculate_roi(),
            'profit': self.calculate_profit()
        }
```

### Expected Value Calculations

#### Always Calculate EV Before Betting

```python
def should_place_bet(odds, estimated_probability, stake=100):
    """Determine if bet has positive expected value."""
    ev = calculate_ev(odds, estimated_probability, stake)
    
    if ev <= 0:
        return {
            'bet': False,
            'reason': 'Negative expected value',
            'ev': ev
        }
    
    # Additional checks
    edge = estimated_probability - implied_probability(odds)
    
    if edge < 0.02:  # Less than 2% edge
        return {
            'bet': False,
            'reason': 'Insufficient edge',
            'edge': edge
        }
    
    return {
        'bet': True,
        'ev': ev,
        'edge': edge,
        'confidence': 'high' if edge > 0.05 else 'medium'
    }
```

### Arbitrage Detection

#### Quick Arbitrage Validation

```python
def validate_arbitrage(opportunity):
    """Verify arbitrage before execution."""
    # Check if still available
    if not opportunity.is_active():
        return False
    
    # Verify ROI threshold
    if opportunity.roi_percentage < 1.0:
        return False  # Less than 1% not worth the risk
    
    # Check stake limits
    if opportunity.total_stake > MAX_ARBITRAGE_STAKE:
        return False
    
    # Verify odds haven't moved
    current_odds = fetch_current_odds(opportunity.bookmakers)
    if odds_have_moved(opportunity.original_odds, current_odds):
        return False
    
    return True
```

### Parlay Strategy

#### Limit Parlay Size

```python
def smart_parlay(legs, max_legs=3):
    """Limit parlay size for better probability."""
    if len(legs) > max_legs:
        # Select best legs based on EV
        sorted_legs = sorted(legs, 
                           key=lambda x: calculate_ev(x['odds'], 
                                                     x['probability'], 
                                                     100),
                           reverse=True)
        legs = sorted_legs[:max_legs]
    
    return calculate_parlay(legs)
```

## System Integration Best Practices

### API Usage

#### 1. Implement Rate Limiting

```python
from functools import wraps
import time

class RateLimiter:
    def __init__(self, calls_per_second=10):
        self.calls_per_second = calls_per_second
        self.last_call = 0
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current = time.time()
            time_since_last = current - self.last_call
            
            if time_since_last < 1.0 / self.calls_per_second:
                time.sleep(1.0 / self.calls_per_second - time_since_last)
            
            self.last_call = time.time()
            return func(*args, **kwargs)
        
        return wrapper

@RateLimiter(calls_per_second=10)
def api_call():
    """Rate-limited API call."""
    pass
```

#### 2. Use Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    """Create session with connection pooling."""
    session = requests.Session()
    
    retry = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504]
    )
    
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=10,
        pool_maxsize=10
    )
    
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session
```

### Data Management

#### 1. Efficient Database Queries

```python
# Good: Single query with joins
results = (
    BetHistory.objects
    .select_related('user', 'sport')
    .prefetch_related('outcomes')
    .filter(created_at__gte=start_date)
)

# Bad: N+1 queries
for bet in BetHistory.objects.all():
    print(bet.user.name)  # Extra query each time
```

#### 2. Use Bulk Operations

```python
# Good: Bulk create
BetHistory.objects.bulk_create([
    BetHistory(data=d) for d in bet_data
])

# Bad: Individual creates
for data in bet_data:
    BetHistory.objects.create(data=data)
```

### Security Best Practices

#### 1. Input Validation

```python
def validate_input(data):
    """Comprehensive input validation."""
    # Type checking
    if not isinstance(data.get('odds'), (int, float)):
        raise ValueError("Odds must be numeric")
    
    # Range checking
    if not 0 <= data.get('probability', 0) <= 1:
        raise ValueError("Probability must be between 0 and 1")
    
    # Sanitization
    data['description'] = bleach.clean(data.get('description', ''))
    
    return data
```

#### 2. Secure API Keys

```python
import os
from cryptography.fernet import Fernet

class SecureConfig:
    """Encrypt sensitive configuration."""
    
    def __init__(self):
        self.cipher = Fernet(os.environ['ENCRYPTION_KEY'])
    
    def get_api_key(self, provider):
        encrypted = os.environ[f'{provider.upper()}_API_KEY']
        return self.cipher.decrypt(encrypted.encode()).decode()
```

### Performance Optimization

#### 1. Use Async Operations

```python
import asyncio

async def process_multiple_bets(bet_list):
    """Process bets concurrently."""
    tasks = [
        calculate_ev_async(bet['odds'], bet['probability'])
        for bet in bet_list
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

#### 2. Implement Caching

```python
from django.core.cache import cache

def get_odds_with_cache(game_id):
    """Cache odds for 60 seconds."""
    cache_key = f'odds_{game_id}'
    
    odds = cache.get(cache_key)
    if odds is None:
        odds = fetch_odds_from_api(game_id)
        cache.set(cache_key, odds, timeout=60)
    
    return odds
```

## Monitoring and Observability

### Logging Best Practices

```python
import logging
import json

# Structured logging
logger = logging.getLogger(__name__)

def log_bet_placed(bet_data):
    """Log bet with structured data."""
    logger.info(
        "Bet placed",
        extra={
            'bet_id': bet_data['id'],
            'amount': bet_data['stake'],
            'odds': bet_data['odds'],
            'expected_value': bet_data['ev'],
            'user_id': bet_data['user_id'],
            'timestamp': bet_data['timestamp']
        }
    )
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
bets_placed = Counter('bets_placed_total', 'Total bets placed')
bet_amount = Histogram('bet_amount_dollars', 'Bet amounts in dollars')
active_arbitrage = Gauge('active_arbitrage_opportunities', 'Current arbitrage opportunities')

def track_bet(bet):
    """Track bet metrics."""
    bets_placed.inc()
    bet_amount.observe(bet['stake'])
```

## Testing Best Practices

### Unit Testing

```python
import unittest
from unittest.mock import Mock, patch

class TestOddsCalculator(unittest.TestCase):
    """Comprehensive unit tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = OddsCalculator()
    
    def test_american_to_decimal(self):
        """Test with multiple cases."""
        test_cases = [
            (-110, 1.909),
            (150, 2.5),
            (-200, 1.5),
            (100, 2.0)
        ]
        
        for american, expected_decimal in test_cases:
            with self.subTest(american=american):
                result = self.calculator.american_to_decimal(american)
                self.assertAlmostEqual(result, expected_decimal, places=3)
```

### Integration Testing

```python
@pytest.mark.integration
def test_end_to_end_bet_flow():
    """Test complete betting workflow."""
    # 1. Calculate EV
    ev = calculate_ev(-110, 0.55, 100)
    assert ev > 0
    
    # 2. Determine stake
    stake = kelly_criterion(1000, 0.55, -110)
    assert 0 < stake.recommended_stake < 50
    
    # 3. Place bet
    bet = place_bet(stake.recommended_stake, -110)
    assert bet.status == 'placed'
    
    # 4. Track result
    track_bet_result(bet)
    assert bet.id in get_bet_history()
```

## Documentation Standards

### Code Documentation

```python
def calculate_kelly_criterion(
    bankroll: float,
    win_probability: float,
    odds: int,
    fraction: float = 1.0
) -> Dict[str, float]:
    """
    Calculate optimal bet size using Kelly Criterion.
    
    The Kelly Criterion determines the optimal fraction of bankroll
    to wager to maximize long-term growth rate.
    
    Args:
        bankroll: Total available bankroll in dollars.
        win_probability: Estimated probability of winning (0-1).
        odds: American format odds (-110, +150, etc).
        fraction: Kelly fraction to use (default 1.0 for full Kelly).
    
    Returns:
        Dictionary containing:
            - recommended_stake: Dollar amount to bet
            - recommended_percentage: Percentage of bankroll
            - expected_growth: Expected growth rate
            - risk_of_ruin: Estimated risk of bankruptcy
    
    Raises:
        ValueError: If probability not in [0, 1] or bankroll negative.
    
    Examples:
        >>> calculate_kelly_criterion(1000, 0.55, -110)
        {'recommended_stake': 50.0, 'recommended_percentage': 0.05, ...}
    """
    # Implementation
    pass
```

## Continuous Improvement

### Regular Reviews

1. **Weekly Performance Review**
   - Analyze betting performance
   - Review AI costs
   - Check error rates

2. **Monthly Optimization**
   - Update model selections
   - Refine betting strategies
   - Optimize costs

3. **Quarterly Assessment**
   - System architecture review
   - Security audit
   - Performance benchmarking

---

*Remember: These are guidelines, not rules. Adapt them to your specific needs and always prioritize safety and sustainability over short-term gains.*