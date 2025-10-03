# System Architecture

## Overview

The Unified AI & Sports Analytics Platform is built on a modular, layered architecture designed for scalability, maintainability, and extensibility. The system integrates advanced AI capabilities with sophisticated sports analytics in a cohesive framework.

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                      Client Layer                          │
│  (Web UI, Mobile Apps, API Clients, WebSocket Clients)    │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                      API Gateway                           │
│          (REST APIs, WebSocket Endpoints, Auth)           │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                   Orchestration Layer                      │
│        (Universal Executor, Agent System, Events)         │
└────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    ▼                     ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│   AI Provider Module    │  │   Sports Analytics Module    │
├─────────────────────────┤  ├──────────────────────────────┤
│ • Provider Router       │  │ • Odds Calculator            │
│ • Cost Optimizer        │  │ • Arbitrage Detector         │
│ • Unified Interface     │  │ • Betting Strategies         │
│ • Fallback Manager      │  │ • Analytics Engine           │
└─────────────────────────┘  └──────────────────────────────┘
                    │                     │
                    └─────────┬──────────┘
                              ▼
┌────────────────────────────────────────────────────────────┐
│                      Data Layer                            │
│              (Django ORM, Models, Migrations)             │
└────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    ▼                     ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│      PostgreSQL         │  │         Redis                │
│   (Primary Database)    │  │   (Cache & Real-time)        │
└─────────────────────────┘  └──────────────────────────────┘
```

## Core Components

### 1. AI Provider Module (Phase 7)

The AI Provider Module provides a unified interface for multiple AI services with intelligent routing and cost optimization.

#### Components:

**BaseAIProvider** (`backend/ai_providers/base.py`)
- Abstract base class defining the provider interface
- Standardized request/response models
- Common functionality for all providers

**Provider Implementations**
- `OpenAIProvider`: Integration with OpenAI GPT models
- `AnthropicProvider`: Integration with Claude models
- `MockProvider`: For testing and development

**AIProviderRouter** (`backend/ai_providers/router.py`)
- Intelligent routing with 6 strategies:
  - Cost-optimized
  - Performance-optimized
  - Balanced
  - Round-robin
  - Failover
  - Load-balanced
- Automatic fallback on provider failure

**CostOptimizer** (`backend/ai_providers/cost_optimizer.py`)
- Budget tracking and enforcement
- Cost prediction
- Optimal model selection
- Usage analytics

**UnifiedAIProvider** (`backend/ai_providers/unified_provider.py`)
- Single entry point for all AI operations
- Combines routing, optimization, and monitoring
- Async/await support

### 2. Sports Analytics Module (Phase 8)

Advanced sports betting analytics with mathematical models and AI integration.

#### Components:

**EnhancedOddsCalculator** (`backend/sports/enhanced_calculator.py`)
- Odds format conversion (American/Decimal/Fractional)
- Expected value calculations
- Implied probability
- Juice removal and no-vig odds

**ArbitrageDetector** (`backend/sports/arbitrage_detector.py`)
- Real-time arbitrage opportunity detection
- Optimal stake calculation
- ROI computation
- Multi-bookmaker analysis

**BettingStrategies** (`backend/sports/strategies.py`)
- Kelly Criterion (full and fractional)
- Fixed percentage/unit betting
- Proportional betting
- Martingale and Fibonacci sequences
- Risk management

**SportsAnalyticsEngine** (`backend/sports/analytics_engine.py`)
- Parlay calculations
- Round-robin generation
- Line movement tracking
- Teaser calculations
- Performance analysis

**UnifiedSportsSystem** (`backend/sports/unified_integration.py`)
- AI-enhanced sports analysis
- Value bet detection
- Real-time monitoring
- Agent orchestration

### 3. Orchestration Layer

Coordinates between modules and manages system-wide operations.

**UniversalExecutor** (`backend/orchestration/universal_executor.py`)
- Task execution framework
- Agent management
- Resource allocation

**EventBus** (`backend/realtime/event_bus.py`)
- System-wide event propagation
- WebSocket broadcasting
- Real-time updates

### 4. Data Layer

Handles data persistence and caching.

**Models**
- User management
- API credentials
- Betting history
- Analytics data

**PostgreSQL**
- Primary data store
- ACID compliance
- Complex queries
- pgvector for embeddings

**Redis**
- Response caching
- Session management
- Real-time data
- Pub/sub messaging

## Design Patterns

### 1. Strategy Pattern
Used in AI provider routing to allow dynamic selection of routing algorithms.

```python
class RoutingStrategy(Enum):
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    BALANCED = "balanced"
```

### 2. Factory Pattern
Provider creation based on configuration.

```python
def create_provider(provider_type: str) -> BaseAIProvider:
    if provider_type == "openai":
        return OpenAIProvider()
    elif provider_type == "anthropic":
        return AnthropicProvider()
```

### 3. Singleton Pattern
Unified provider instance shared across the application.

### 4. Observer Pattern
Event bus for system-wide notifications.

### 5. Chain of Responsibility
Fallback mechanism for provider failures.

## Data Flow

### AI Completion Request Flow

1. Client sends request to API endpoint
2. API Gateway validates and authenticates
3. UnifiedAIProvider receives request
4. Router selects optimal provider
5. Provider executes completion
6. Response returned through layers
7. Cost tracked and logged

### Sports Analysis Flow

1. Odds data ingested
2. Calculator processes conversions
3. Arbitrage detector scans opportunities
4. Kelly Criterion calculates stakes
5. AI enhancement (optional)
6. Results returned to client

## Security Architecture

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control (RBAC)
- API key management

### Data Protection
- Encryption at rest (PostgreSQL)
- Encryption in transit (HTTPS)
- Sensitive data masking
- PII protection

### Input Validation
- Request sanitization
- SQL injection prevention
- XSS protection
- Rate limiting

## Performance Optimization

### Caching Strategy
- Redis for hot data
- Response caching
- Computed value caching
- TTL-based expiration

### Async Operations
- Async/await for I/O operations
- Concurrent request handling
- Background task processing

### Database Optimization
- Indexed queries
- Connection pooling
- Query optimization
- Lazy loading

## Scalability

### Horizontal Scaling
- Stateless application servers
- Load balancer ready
- Distributed caching
- Database replication

### Vertical Scaling
- Resource monitoring
- Performance profiling
- Memory optimization
- CPU utilization

## Monitoring & Observability

### Metrics Collection
- Request latency
- Error rates
- Cost tracking
- Usage patterns

### Logging
- Structured logging
- Log aggregation
- Error tracking
- Audit trails

### Health Checks
- Service availability
- Database connectivity
- Redis status
- Provider health

## Deployment Architecture

### Development
```
Local PostgreSQL + Redis
Mock AI providers
Debug mode enabled
```

### Staging
```
Cloud PostgreSQL
Managed Redis
Real AI providers (limited)
Performance monitoring
```

### Production
```
PostgreSQL cluster
Redis cluster
Load balancer
Auto-scaling
Full monitoring
```

## Technology Stack

### Backend
- **Language**: Python 3.9+
- **Framework**: Django 4.2+
- **Async**: asyncio, Django Channels
- **Testing**: unittest, pytest

### Database
- **Primary**: PostgreSQL 12+
- **Cache**: Redis 6+
- **Migrations**: Django migrations

### AI Integration
- **OpenAI**: GPT-3.5, GPT-4
- **Anthropic**: Claude 3 family
- **Custom**: Extensible provider interface

### Real-time
- **WebSocket**: Django Channels
- **Protocol**: WSS
- **Events**: Redis pub/sub

## API Standards

### RESTful Design
- Resource-based URLs
- HTTP verbs (GET, POST, PUT, DELETE)
- Status codes
- JSON responses

### API Versioning
```
/api/v1/sports/...
/api/v1/ai/...
```

### Response Format
```json
{
  "success": true,
  "data": {...},
  "meta": {
    "timestamp": "2025-01-09T12:00:00Z",
    "version": "1.0.0"
  }
}
```

## Future Considerations

### Phase 11 - Migration & Deployment
- Cloud deployment
- CI/CD pipeline
- Infrastructure as code

### Phase 12 - Optimization
- Performance tuning
- Cost reduction
- Feature enhancement

---

*Next: [API Reference](./api-reference.md) →*