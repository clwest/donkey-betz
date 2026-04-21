# AI Studio - Monitoring and Observability Setup Guide

## Overview

This comprehensive monitoring infrastructure provides real-time visibility into the AI Studio platform's performance, costs, and health. The system includes metrics collection, cost tracking, intelligent alerting, and interactive dashboards.

## Components

### 1. Metrics Collector (`/backend/monitoring/metrics_collector.py`)
- **Token usage tracking** by model (GPT-5, GPT-4, Claude, etc.) and feature
- **Cache performance monitoring** with hit rates, evictions, and response times  
- **Service health checks** for Redis, PostgreSQL, Celery, and API endpoints
- **Automatic system metrics** collection with minimal performance overhead

### 2. Cost Tracker (`/backend/monitoring/cost_tracker.py`)
- **Precise cost calculation** using real-time model pricing
- **Budget monitoring** with 50%, 80%, and 95% threshold alerts
- **Cache savings tracking** showing actual cost reductions
- **Optimization recommendations** based on usage patterns

### 3. Health Check System (`/backend/monitoring/health_checks.py`)
- **Service status monitoring** for all critical components
- **Performance benchmarking** with response time tracking
- **Detailed diagnostics** for troubleshooting issues
- **Circuit breaker patterns** to prevent cascading failures

### 4. Intelligent Alerting (`/backend/monitoring/alerting.py`)
- **Configurable thresholds** with smart deduplication
- **Multi-channel notifications** (email, Slack, webhooks)
- **Escalation policies** with cooldown periods
- **Alert acknowledgment** and suppression capabilities

### 5. Real-time Dashboard (`/monitoring/index.html`)
- **Live metrics visualization** with auto-refresh
- **Interactive charts** for token usage and cache performance
- **Service health matrix** with status indicators
- **Cost optimization recommendations** with actionable insights

## Installation and Configuration

### Step 1: Add Monitoring App to Django

1. **Update `INSTALLED_APPS`** in `/backend/core/settings.py`:
```python
INSTALLED_APPS = [
    # ... existing apps ...
    'monitoring',  # Add this line
]
```

2. **Add Monitoring Middleware** in `/backend/core/settings.py`:
```python
MIDDLEWARE = [
    # ... existing middleware ...
    'monitoring.middleware.MonitoringMiddleware',  # Add near the end
    'monitoring.middleware.TokenUsageResponseMiddleware',  # Add last
]
```

### Step 2: Configure Environment Variables

Add these to your `.env` file:

```bash
# Monitoring Configuration
REDIS_URL=redis://localhost:6379/0

# Alert Notifications (Optional)
ADMIN_EMAIL=admin@yourdomain.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
ALERT_WEBHOOK_URL=https://yourapp.com/webhooks/alerts

# Budget Limits (Optional - defaults provided)
MONTHLY_BUDGET_LIMIT=1000.0
DAILY_BUDGET_LIMIT=50.0
```

### Step 3: Update Django URLs

The monitoring URLs are already added to `/backend/api/urls.py`. Verify these endpoints are available:

- `GET /api/health/` - Overall system health
- `GET /api/metrics/current/` - Real-time metrics
- `GET /api/costs/summary/` - Cost and budget status
- `GET /api/dashboard/monitoring/` - Dashboard data

### Step 4: Start Services

1. **Ensure Redis is running**:
```bash
redis-server
```

2. **Start Celery workers** (if not already running):
```bash
cd backend
celery -A core worker -l info
```

3. **Start Django development server**:
```bash
cd backend
python manage.py runserver 8001
```

4. **Access the monitoring dashboard**:
Open `/monitoring/index.html` in your browser or serve it via a web server.

## API Integration

### Automatic Token Usage Tracking

The monitoring system automatically captures metrics from API responses. To integrate with existing views:

```python
from monitoring.middleware import record_api_token_usage

def your_api_view(request):
    # Your existing logic
    response_data = generate_content(...)
    
    # Record token usage
    record_api_token_usage(
        request=request,
        model='gpt-4',
        input_tokens=1000,
        output_tokens=500,
        cost=0.045,
        cache_hit=False
    )
    
    return JsonResponse(response_data)
```

### Using the Decorator

```python
from monitoring.middleware import track_token_usage

@track_token_usage(
    model_func=lambda req: req.data.get('model', 'gpt-4'),
    feature='content_generation'
)
def content_create_api(request):
    # Your view logic
    # Include 'usage' in response.data for automatic tracking
    return Response({
        'content': generated_content,
        'usage': {
            'model': 'gpt-4',
            'input_tokens': 1000,
            'output_tokens': 500,
            'cost': 0.045,
            'cache_hit': False
        }
    })
```

## Dashboard Features

### Real-time Metrics
- **System Status**: Overall health with service count
- **Monthly Cost**: Current spend vs budget with usage percentage
- **Cache Hit Rate**: Performance indicator with savings calculation
- **Response Time**: Average API response time with success rate

### Interactive Charts
- **Token Usage by Model**: Doughnut chart showing distribution
- **Cache Performance**: Bar chart with hit rate targets
- **Service Health Matrix**: Status indicators for all services

### Cost Optimization
- **Smart Recommendations**: AI-powered suggestions for cost reduction
- **Potential Savings**: Quantified optimization opportunities
- **Implementation Effort**: Difficulty assessment for each recommendation

## Alert Configuration

### Default Alert Rules

1. **Cache Hit Rate < 50%**: Warning level, 1-hour cooldown
2. **Budget > 80%**: Warning with email + Slack notifications
3. **Budget > 95%**: Critical with all notification channels
4. **Service Unhealthy**: Critical alert for service failures
5. **High Queue Depth**: Warning when Celery queue > 100 tasks
6. **High Response Time**: Warning when API response > 5 seconds
7. **High Error Rate**: Critical when error rate > 10%

### Custom Alert Rules

```python
from monitoring.alerting import get_alert_manager, AlertRule, AlertSeverity

# Add custom rule
alert_manager = get_alert_manager()
custom_rule = AlertRule(
    id="custom_metric_alert",
    name="Custom Metric Alert",
    description="Alert when custom metric exceeds threshold",
    condition="custom_metric > 100",
    severity=AlertSeverity.WARNING,
    notification_channels=['email']
)
alert_manager.add_alert_rule(custom_rule)
```

## Health Check Endpoints

### Individual Service Checks
- `GET /api/health/redis/` - Redis connectivity and performance
- `GET /api/health/database/` - PostgreSQL status and query performance
- `GET /api/health/celery/` - Worker status and queue depth
- `GET /api/health/cache/` - Django cache performance

### Health Check Response Format
```json
{
    "service": "redis",
    "status": "healthy",
    "response_time_ms": 45.2,
    "message": "Redis is healthy",
    "details": {
        "memory_usage_percent": 35.2,
        "total_keys": 1524,
        "ping_time_ms": 1.2
    },
    "timestamp": "2025-01-15T10:30:00Z"
}
```

## Cost Tracking

### Model Pricing
The system includes current pricing for:
- **OpenAI**: GPT-5, GPT-4, GPT-3.5-turbo variants
- **Anthropic**: Claude-3 (Opus, Sonnet, Haiku)
- **Google**: Gemini Pro models
- **Stability AI**: Image and video generation
- **ElevenLabs**: Text-to-speech
- **Runway ML**: Video generation

### Cost Analysis Features
- **Real-time cost calculation** with precise token counting
- **Cache savings tracking** showing avoided API costs
- **Budget projections** using moving averages
- **User-level cost breakdown** for multi-tenant usage
- **Export functionality** in JSON and CSV formats

## Performance Considerations

### Minimal Overhead
- **Asynchronous collection**: Non-blocking metrics gathering
- **Efficient storage**: Time-series data with automatic cleanup
- **Sampling strategies**: High-frequency event sampling
- **Circular buffers**: Memory-efficient metric storage

### Redis Usage
- **7-day retention** for raw metrics
- **Compressed aggregations** for historical data
- **Automatic expiration** prevents storage bloat
- **Fallback handling** when Redis is unavailable

### Database Impact
- **Read-only health checks**: No write operations during monitoring
- **Connection pooling**: Efficient database connection usage
- **Query optimization**: Fast health check queries
- **Timeout handling**: Prevents hanging connections

## Troubleshooting

### Common Issues

1. **"Connection Failed" in Dashboard**
   - Check Django server is running on port 8001
   - Verify API token in localStorage: `<redacted-993f8273-2026-04-20>`
   - Check CORS settings in Django

2. **No Metrics Appearing**
   - Ensure Redis is running and accessible
   - Check Django logs for monitoring middleware errors
   - Verify metrics collection is started

3. **Alerts Not Sending**
   - Check email configuration in Django settings
   - Verify Slack webhook URL in environment variables
   - Check alert rule conditions and cooldown periods

4. **High Memory Usage**
   - Check metrics buffer sizes in collector
   - Verify Redis memory limits
   - Review alert rule efficiency

### Monitoring Logs

Enable debug logging for detailed monitoring information:

```python
LOGGING = {
    # ... existing config ...
    'loggers': {
        'monitoring': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
```

## Production Deployment

### Security Considerations
- **API authentication**: All endpoints require valid tokens
- **Rate limiting**: Built-in protection against abuse
- **Data isolation**: User-scoped metrics and costs
- **Secure notifications**: Encrypted alert channels

### Scaling Recommendations
- **Redis Cluster**: For high-availability deployments
- **Separate monitoring DB**: Isolate monitoring data
- **Load balancer health checks**: Use monitoring endpoints
- **Distributed collection**: Multiple collector instances

### Maintenance
- **Regular backups**: Export cost and alert data
- **Metric pruning**: Automated cleanup of old data
- **Performance reviews**: Monthly optimization assessments
- **Alert rule updates**: Adjust thresholds based on usage patterns

## Support and Customization

The monitoring system is designed to be highly customizable and extensible. Key extension points include:

- **Custom metrics**: Add domain-specific measurements
- **Alert rules**: Create specialized conditions and actions
- **Notification channels**: Integrate with additional services
- **Dashboard widgets**: Add custom visualizations
- **Cost models**: Support for new AI service pricing

For additional customization or support, refer to the individual component files for detailed implementation examples and extension patterns.