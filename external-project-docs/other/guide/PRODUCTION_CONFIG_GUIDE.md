# Production Configuration Guide for Enhanced Agent System

## 🔑 Required API Keys

### 1. Financial Data APIs
- **Yahoo Finance API**: Set `YAHOO_FINANCE_API_KEY` in `.env`
  - Get from: https://rapidapi.com/yahoo-finance/api
  - Used for: Real-time stock quotes, financial metrics
  
- **Alpha Vantage API**: Set `ALPHA_VANTAGE_API_KEY` in `.env`
  - Get from: https://www.alphavantage.co/support/#api-key
  - Used for: Backup financial data, technical indicators

- **Polygon.io API**: Set `POLYGON_API_KEY` in `.env`
  - Get from: https://polygon.io/dashboard/api-keys
  - Used for: Market data, news aggregation

### 2. News & Sentiment APIs
- **News API**: Set `NEWS_API_KEY` in `.env`
  - Get from: https://newsapi.org/register
  - Used for: Latest news articles, sentiment analysis

### 3. Reddit API
- **Reddit App Credentials**: 
  ```env
  REDDIT_CLIENT_ID=your_client_id
  REDDIT_CLIENT_SECRET=your_client_secret
  REDDIT_USER_AGENT=DonkeyBetz/1.0
  ```
  - Get from: https://www.reddit.com/prefs/apps
  - Used for: Reddit sentiment analysis, trending discussions

## 📊 Monitoring Setup

### 1. Enable Production Monitoring
```python
# In server/settings.py
RESILIENCE_CONFIG = {
    'monitoring': {
        'enabled': True,
        'export_metrics': True,
        'metrics_endpoint': '/metrics',
        'alert_email': 'alerts@yourdomain.com'
    }
}
```

### 2. Set Up Prometheus Metrics
```bash
# Install prometheus client
pip install prometheus-client

# Add to requirements.txt
prometheus-client==0.19.0
```

### 3. Configure Alerts
```python
# In agent_orchestra/utils/monitoring.py
ALERT_THRESHOLDS = {
    'api_failure_rate': 0.5,  # Alert if >50% failures
    'response_time': 5.0,     # Alert if >5s response time
    'circuit_breaker_open': True  # Alert when circuit opens
}
```

## 🚀 Performance Optimization

### 1. Redis Configuration
```env
# In .env
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=900  # 15 minutes default
REDIS_MAX_CONNECTIONS=50
```

### 2. Database Optimization
```python
# In server/settings.py
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000'  # 30s timeout
}
```

### 3. Celery Configuration
```python
# In server/celery.py
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 270  # 4.5 minutes
CELERY_WORKER_MAX_TASKS_PER_CHILD = 50  # Prevent memory leaks
```

## 🛡️ Security Configuration

### 1. API Key Rotation
```python
# Add to cron job
python manage.py rotate_api_keys --days 90
```

### 2. Rate Limiting
```python
# In server/settings.py
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/hour',
    'user': '1000/hour',
    'stock_analysis': '100/day'  # Limit expensive operations
}
```

### 3. Input Validation
```python
# Already implemented in enhanced service
MAX_TICKER_LENGTH = 10
ALLOWED_ANALYSIS_TYPES = ['technical', 'fundamental', 'comprehensive']
```

## 📈 Scaling Recommendations

### 1. Horizontal Scaling
- Use multiple Celery workers: `celery -A server worker -l info -c 4`
- Load balance API requests with nginx
- Use Redis Sentinel for high availability

### 2. Caching Strategy
- Cache financial data for 15 minutes (already implemented)
- Cache news/Reddit data for 1 hour
- Use Redis clusters for cache distribution

### 3. Database Optimization
- Add indexes for frequently queried fields:
  ```sql
  CREATE INDEX idx_stock_analysis_ticker ON agent_orchestra_stockanalysis(ticker);
  CREATE INDEX idx_orchestration_status ON agent_orchestra_taskorchestration(overall_status);
  ```

## 🔧 Environment Variables Template

Create a `.env.production` file:

```env
# Django Settings
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/donkeybetz_prod

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=sk-...
YAHOO_FINANCE_API_KEY=...
ALPHA_VANTAGE_API_KEY=...
POLYGON_API_KEY=...
NEWS_API_KEY=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
DATADOG_API_KEY=...

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG...

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 🚨 Health Check Endpoints

### 1. System Health
```bash
curl https://yourdomain.com/api/agent-orchestra/health/
```

### 2. API Health
```bash
curl https://yourdomain.com/api/agent-orchestra/api-health/
```

### 3. Cache Health
```bash
curl https://yourdomain.com/api/agent-orchestra/cache-health/
```

## 📝 Deployment Checklist

- [ ] All API keys configured in production environment
- [ ] Redis server running and accessible
- [ ] Celery workers deployed and monitored
- [ ] Database migrations applied
- [ ] Static files collected and served
- [ ] SSL certificate configured
- [ ] Monitoring alerts configured
- [ ] Backup strategy implemented
- [ ] Rate limiting enabled
- [ ] Error tracking (Sentry) configured

## 🔍 Troubleshooting

### Common Issues

1. **"Hypothetical" data appearing**
   - Check API keys are valid
   - Verify circuit breakers are not tripped
   - Check cache is not stale

2. **Slow response times**
   - Monitor API response times in logs
   - Check Redis connection
   - Verify Celery workers are healthy

3. **High error rates**
   - Check `/api/agent-orchestra/api-health/`
   - Review circuit breaker status
   - Verify rate limits not exceeded

### Debug Commands

```bash
# Check API health
python manage.py check_api_health

# Test enhanced agents
python manage.py test_enhanced_agents --symbol AAPL

# Clear stale cache
python manage.py clear_resilience_cache

# Reset circuit breakers
python manage.py reset_circuit_breakers
```