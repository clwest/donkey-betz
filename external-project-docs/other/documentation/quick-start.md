# Quick Start Guide

Get up and running with the Unified AI & Sports Analytics Platform in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+ 
- Redis (for real-time features)
- API keys for AI providers (optional)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd unification-workspace
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/unified_db

# AI Providers (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
DEBUG=False
```

### 5. Initialize Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Basic Usage

### AI Provider Integration

```python
from backend.ai_providers.unified_provider import UnifiedAIProvider

# Initialize the unified provider
ai = UnifiedAIProvider()

# Get a completion
response = await ai.get_completion(
    prompt="Explain quantum computing",
    model="gpt-3.5-turbo",
    temperature=0.7
)

print(response.content)
```

### Sports Analytics

```python
from backend.sports.enhanced_calculator import EnhancedOddsCalculator
from backend.sports.strategies import BettingStrategies

# Initialize calculators
calc = EnhancedOddsCalculator()
strategies = BettingStrategies()

# Convert odds
decimal_odds = calc.american_to_decimal(-110)
print(f"Decimal odds: {decimal_odds}")

# Calculate expected value
ev = calc.calculate_ev(
    odds=-110,
    win_probability=0.55,
    stake=100
)
print(f"Expected value: ${ev:.2f}")

# Kelly Criterion bet sizing
kelly = strategies.kelly_criterion(
    bankroll=1000,
    win_probability=0.55,
    odds=-110
)
print(f"Recommended bet: ${kelly.recommended_stake:.2f}")
```

### Arbitrage Detection

```python
from backend.sports.arbitrage_detector import ArbitrageDetector

detector = ArbitrageDetector()

# Check for arbitrage
odds_set = [
    {'book': 'BookA', 'outcome': 'Team1', 'odds': 120},
    {'book': 'BookB', 'outcome': 'Team2', 'odds': 110}
]

opportunity = detector.find_arbitrage(odds_set)
if opportunity:
    print(f"Arbitrage found! ROI: {opportunity.roi_percentage:.2f}%")
```

## API Endpoints

### AI Completions
```http
POST /api/ai/completion/
Content-Type: application/json

{
  "prompt": "Your prompt here",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7
}
```

### Sports Analytics
```http
POST /api/sports/calculate_ev/
Content-Type: application/json

{
  "odds": -110,
  "win_probability": 0.55,
  "stake": 100
}
```

### Kelly Criterion
```http
POST /api/sports/kelly_criterion/
Content-Type: application/json

{
  "bankroll": 1000,
  "win_probability": 0.55,
  "odds": -110
}
```

## Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test suite
python backend/tests/test_sports_analytics.py

# Run with coverage
python -m pytest --cov=backend
```

## Common Operations

### 1. Find Value Bets

```python
# Check if a bet has positive expected value
odds = 150  # +150
your_probability = 0.45  # 45% chance

ev = calc.calculate_ev(odds, your_probability, 100)
if ev > 0:
    print(f"Value bet! EV: ${ev:.2f}")
```

### 2. Calculate Parlay

```python
from backend.sports.analytics_engine import SportsAnalyticsEngine

analytics = SportsAnalyticsEngine()

legs = [
    {'odds': -110, 'description': 'Game 1'},
    {'odds': 150, 'description': 'Game 2'}
]

parlay = analytics.calculate_parlay(legs, stake=100)
print(f"Parlay odds: {parlay.combined_odds}")
print(f"Potential payout: ${parlay.potential_payout:.2f}")
```

### 3. Use AI for Analysis

```python
# AI-enhanced sports analysis
from backend.sports.unified_integration import UnifiedSportsSystem

system = UnifiedSportsSystem()

game_data = {
    'home_team': 'Lakers',
    'away_team': 'Celtics',
    'home_odds': -110,
    'away_odds': -110
}

analysis = await system.analyze_with_ai(game_data)
print(f"AI confidence: {analysis['combined_confidence']:.1f}%")
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
python manage.py dbshell
```

### Redis Connection Issues
```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

### API Key Issues
- Ensure API keys are properly set in `.env`
- Check API key format (OpenAI: `sk-...`, Anthropic: `sk-ant-...`)
- Verify API credits/limits

## Next Steps

1. Read the [Architecture Guide](./architecture.md) to understand the system design
2. Explore the [API Reference](./api-reference.md) for detailed endpoint documentation
3. Check [Best Practices](./best-practices.md) for optimal usage patterns
4. Review [Training Materials](./training/README.md) for in-depth learning

## Getting Help

- 📖 [User Guide](./user-guide.md) - Detailed usage instructions
- 🛠️ [Developer Guide](./developer-guide.md) - For contributors
- 🎓 [Training Materials](./training/README.md) - Learn the system
- 🐛 [Issue Tracker](https://github.com/your-repo/issues) - Report bugs

---

*Ready to dive deeper? Continue to the [User Guide](./user-guide.md) →*