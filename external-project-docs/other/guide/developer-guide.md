# Developer Guide

Complete guide for developers working with the Unified AI & Sports Analytics Platform.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Code Structure](#code-structure)
3. [Contributing](#contributing)
4. [Testing](#testing)
5. [Deployment](#deployment)
6. [API Development](#api-development)
7. [Extending the Platform](#extending-the-platform)

## Development Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Git
- Virtual environment tool (venv, conda)

### Local Environment Setup

1. **Clone the Repository**
```bash
git clone https://github.com/your-org/unification-workspace.git
cd unification-workspace
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database Setup**
```bash
# Create database
createdb unified_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

6. **Start Development Server**
```bash
# Start Redis
redis-server

# Start Django
python manage.py runserver

# Start Channels (WebSocket)
python manage.py runworker
```

## Code Structure

### Directory Layout

```
unification-workspace/
├── backend/
│   ├── ai_providers/       # AI provider integration
│   │   ├── base.py        # Abstract base classes
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── router.py      # Provider routing
│   │   ├── cost_optimizer.py
│   │   └── unified_provider.py
│   │
│   ├── sports/            # Sports analytics
│   │   ├── enhanced_calculator.py
│   │   ├── arbitrage_detector.py
│   │   ├── strategies.py
│   │   ├── analytics_engine.py
│   │   └── unified_integration.py
│   │
│   ├── orchestration/     # System orchestration
│   │   └── universal_executor.py
│   │
│   ├── realtime/          # Real-time features
│   │   └── event_bus.py
│   │
│   └── tests/             # Test suite
│       ├── test_ai_providers.py
│       ├── test_sports_analytics.py
│       └── test_integration.py
│
├── docs/                  # Documentation
├── migrations/            # Database migrations
└── requirements.txt       # Dependencies
```

### Key Modules

#### AI Providers Module
```python
# backend/ai_providers/base.py
class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def get_completion(self, request: CompletionRequest) -> CompletionResponse:
        """Get text completion from AI."""
        pass
    
    @abstractmethod
    def get_embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Get text embedding."""
        pass
```

#### Sports Analytics Module
```python
# backend/sports/enhanced_calculator.py
class EnhancedOddsCalculator:
    """Comprehensive odds calculation engine."""
    
    def american_to_decimal(self, odds: int) -> float:
        """Convert American odds to decimal."""
        if odds > 0:
            return (odds / 100) + 1
        else:
            return (100 / abs(odds)) + 1
```

## Contributing

### Development Workflow

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Changes**
- Write code following style guide
- Add tests for new features
- Update documentation

3. **Run Tests**
```bash
python -m pytest
python -m pytest --cov=backend  # With coverage
```

4. **Commit Changes**
```bash
git add .
git commit -m "feat: add new feature description"
```

5. **Push and Create PR**
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

### Commit Message Convention

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style
- `refactor:` Refactoring
- `test:` Tests
- `chore:` Maintenance

### Code Style

#### Python Style Guide

Follow PEP 8 with these additions:

```python
# Good: Descriptive names
def calculate_expected_value(odds: int, probability: float) -> float:
    """Calculate expected value of a bet."""
    pass

# Bad: Unclear names
def calc_ev(o, p):
    pass
```

#### Type Hints

Always use type hints:

```python
from typing import List, Dict, Optional

def process_odds(
    odds_list: List[int],
    config: Optional[Dict] = None
) -> Dict[str, float]:
    """Process list of odds."""
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def kelly_criterion(
    bankroll: float,
    win_probability: float,
    odds: int
) -> KellyResult:
    """
    Calculate optimal bet size using Kelly Criterion.
    
    Args:
        bankroll: Total available bankroll.
        win_probability: Estimated probability of winning (0-1).
        odds: American format odds.
    
    Returns:
        KellyResult containing recommended stake and metrics.
    
    Raises:
        ValueError: If probability not in [0, 1] range.
    """
    pass
```

## Testing

### Running Tests

```bash
# All tests
python -m pytest

# Specific module
python -m pytest backend/tests/test_sports_analytics.py

# With coverage
python -m pytest --cov=backend --cov-report=html

# Performance tests
python backend/tests/test_performance.py

# Security tests
python backend/tests/test_security.py
```

### Writing Tests

#### Unit Tests
```python
import unittest
from backend.sports.enhanced_calculator import EnhancedOddsCalculator

class TestOddsCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = EnhancedOddsCalculator()
    
    def test_american_to_decimal(self):
        """Test American to decimal conversion."""
        result = self.calculator.american_to_decimal(-110)
        self.assertAlmostEqual(result, 1.909, places=3)
```

#### Integration Tests
```python
class TestAISportsIntegration(unittest.TestCase):
    def test_ai_enhanced_analysis(self):
        """Test AI integration with sports analysis."""
        system = UnifiedSportsSystem()
        result = system.analyze_with_ai(game_data)
        self.assertIn('ai_insights', result)
```

#### Performance Tests
```python
def test_calculation_speed(self):
    """Benchmark calculation performance."""
    start = time.perf_counter()
    for _ in range(1000):
        self.calculator.american_to_decimal(-110)
    elapsed = time.perf_counter() - start
    
    self.assertLess(elapsed, 0.1)  # Should complete in < 100ms
```

### Test Coverage Goals

- Unit tests: > 80% coverage
- Integration tests: All critical paths
- Performance tests: Key operations
- Security tests: All inputs/outputs

## API Development

### Creating New Endpoints

1. **Define View**
```python
# backend/sports/api.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class SportsAnalyticsViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def calculate_ev(self, request):
        """Calculate expected value endpoint."""
        odds = request.data.get('odds')
        probability = request.data.get('win_probability')
        
        ev = self.calculator.calculate_ev(odds, probability, 100)
        
        return Response({
            'success': True,
            'data': {'expected_value': ev}
        })
```

2. **Add URL Route**
```python
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('sports', SportsAnalyticsViewSet, basename='sports')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
```

3. **Add Validation**
```python
from rest_framework import serializers

class EVSerializer(serializers.Serializer):
    odds = serializers.IntegerField(required=True)
    win_probability = serializers.FloatField(min_value=0, max_value=1)
    stake = serializers.FloatField(default=100)
```

### WebSocket Implementation

```python
# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OddsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("odds", self.channel_name)
        await self.accept()
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        # Process message
    
    async def odds_update(self, event):
        await self.send(text_data=json.dumps(event['data']))
```

## Extending the Platform

### Adding New AI Provider

1. **Create Provider Class**
```python
# backend/ai_providers/custom_provider.py
from backend.ai_providers.base import BaseAIProvider

class CustomProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.name = "custom"
    
    def get_completion(self, request: CompletionRequest) -> CompletionResponse:
        # Implement API call
        pass
```

2. **Register Provider**
```python
# backend/ai_providers/router.py
def _initialize_providers(self):
    self.providers['custom'] = CustomProvider(api_key)
```

### Adding New Sports Feature

1. **Create Feature Module**
```python
# backend/sports/new_feature.py
class NewSportsFeature:
    def calculate_something(self, data):
        # Implementation
        pass
```

2. **Add Tests**
```python
# backend/tests/test_new_feature.py
class TestNewFeature(unittest.TestCase):
    def test_calculation(self):
        # Test implementation
        pass
```

3. **Create API Endpoint**
```python
@action(detail=False, methods=['post'])
def new_feature(self, request):
    # Endpoint implementation
    pass
```

## Deployment

### Production Setup

1. **Environment Variables**
```bash
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://host:6379
SECRET_KEY=production-secret-key
DEBUG=False
ALLOWED_HOSTS=api.your-domain.com
```

2. **Database Migrations**
```bash
python manage.py migrate --no-input
```

3. **Static Files**
```bash
python manage.py collectstatic --no-input
```

4. **Gunicorn Configuration**
```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
```

5. **Docker Deployment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "config.wsgi:application"]
```

### Monitoring

1. **Health Check Endpoint**
```python
@action(detail=False, methods=['get'])
def health(self, request):
    return Response({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
```

2. **Logging Configuration**
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

## Performance Optimization

### Database Optimization

```python
# Use select_related for foreign keys
queryset = Model.objects.select_related('related_model')

# Use prefetch_related for many-to-many
queryset = Model.objects.prefetch_related('many_to_many_field')

# Add database indexes
class Meta:
    indexes = [
        models.Index(fields=['frequently_queried_field']),
    ]
```

### Caching Strategy

```python
from django.core.cache import cache

def get_expensive_data():
    key = 'expensive_data'
    data = cache.get(key)
    
    if data is None:
        data = calculate_expensive_operation()
        cache.set(key, data, timeout=3600)  # 1 hour
    
    return data
```

### Async Operations

```python
import asyncio
from asgiref.sync import sync_to_async

@sync_to_async
def database_operation():
    return Model.objects.all()

async def async_view():
    data = await database_operation()
    return data
```

## Security Best Practices

### Input Validation
```python
def validate_odds(odds):
    if not isinstance(odds, (int, float)):
        raise ValueError("Odds must be numeric")
    if odds == 0 or odds == -100:
        raise ValueError("Invalid odds value")
    return odds
```

### API Authentication
```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class SecureViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
```

### Rate Limiting
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/m')
def api_view(request):
    pass
```

---

*Next: [Best Practices](./best-practices.md) →*