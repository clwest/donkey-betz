# AI Content Studio with Donkey Betz Agent Orchestra - Production Deployment Guide

## 🚀 Overview

This guide provides comprehensive instructions for deploying the AI Content Studio with Donkey Betz Agent Orchestra to production. The system includes 13 specialized AI agents, comprehensive sports betting analytics, real-time data feeds, workflow automation, and enterprise-grade monitoring.

## 📋 Production Features

### Core Components
- **Load Testing Infrastructure** - Supports 100+ concurrent users with comprehensive performance monitoring
- **Workflow Templates** - 5 pre-configured betting analytics workflows with pause/resume capabilities  
- **Error Recovery & Resilience** - Circuit breakers, exponential backoff, graceful degradation
- **Real-time Sports Data** - Integration with multiple sportsbooks and data providers
- **Production Monitoring** - Prometheus/Grafana dashboards with intelligent alerting
- **Performance Optimization** - Multi-level Redis caching, async processing, database optimization

### Performance Targets
- Single agent execution: < 2 seconds (95th percentile)
- Multi-agent workflow: < 5 seconds
- Odds calculations: < 500ms  
- Memory retrieval: < 100ms
- Support 100+ concurrent users with < 2GB memory usage
- 99.9% uptime SLA

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Production Architecture                    │
├─────────────────────────────────────────────────────────────────────┤
│  Load Balancer (Nginx) → Django App Servers → Database (PostgreSQL) │
│                        ↗                    ↘                       │
│  Real-time Feeds ──────┴───→ Redis Cache ←───┴── Celery Workers    │
│                                   ↓                                  │
│  Monitoring Stack: Prometheus → Grafana → AlertManager             │
│                                                                     │
│  Sports Data: DraftKings, FanDuel, TheOddsAPI, Weather, Injuries   │
│  AI Providers: OpenAI GPT-4, Anthropic Claude                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 🛠️ Prerequisites

### System Requirements
- **CPU**: 8+ cores (16 recommended)
- **RAM**: 16GB minimum (32GB recommended)
- **Storage**: 500GB SSD (1TB recommended)
- **Network**: High-bandwidth connection for real-time data feeds

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.9+
- Node.js 16+ (for frontend builds)
- Git

### API Keys Required
```bash
# AI Providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Sports Data
ODDS_API_KEY=your_theoddsapi_key
WEATHER_API_KEY=your_openweathermap_key  
SPORTRADAR_API_KEY=your_sportradar_key

# System
SECRET_KEY=your_django_secret_key
DB_PASSWORD=secure_database_password
GRAFANA_PASSWORD=secure_grafana_password
FLOWER_PASSWORD=secure_flower_password
```

## 🚀 Quick Start Deployment

### 1. Clone and Setup
```bash
git clone <repository-url>
cd donkey-betz-agent-orchestra
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 2. Configure Environment Variables
```bash
# Create .env file with all required variables
cat > .env << EOF
# Django
SECRET_KEY=your-super-secure-django-secret-key-change-in-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_PASSWORD=super-secure-db-password

# AI Providers  
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Sports Data APIs
ODDS_API_KEY=your-theoddsapi-key
WEATHER_API_KEY=your-openweather-key
SPORTRADAR_API_KEY=your-sportradar-key

# Monitoring
GRAFANA_PASSWORD=secure-grafana-password
FLOWER_PASSWORD=secure-flower-password
EOF
```

### 3. Deploy with Docker Compose
```bash
# Build and start all services
docker-compose -f docker-compose.production.yml up -d

# Initialize database and load workflow templates  
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py deploy_production_system --component all

# Verify deployment
docker-compose exec web python manage.py deploy_production_system --verify
```

### 4. Access Services
- **Main Application**: http://localhost
- **Grafana Monitoring**: http://localhost:3000 (admin/your-grafana-password)
- **Prometheus Metrics**: http://localhost:9090
- **Flower (Celery)**: http://localhost:5555
- **Kibana Logs**: http://localhost:5601

## 📊 Comprehensive Deployment

### Step 1: Infrastructure Preparation
```bash
# Create necessary directories
mkdir -p logs/{django,celery,nginx}
mkdir -p docker/{ssl,nginx,prometheus,grafana}

# Set appropriate permissions
chmod 755 logs/
chown -R 1000:1000 logs/
```

### Step 2: SSL Certificate Setup
```bash
# Generate SSL certificates (use Let's Encrypt for production)
mkdir -p docker/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/ssl/private.key \
  -out docker/ssl/certificate.crt
```

### Step 3: Advanced Configuration
```bash
# Copy production configuration
cp production_config.json backend/
cp docker-compose.production.yml docker-compose.yml

# Configure monitoring
cp -r monitoring/grafana/json/ docker/grafana/dashboards/
cp monitoring/prometheus/ docker/prometheus/ -r
```

### Step 4: Database Initialization
```bash
# Start database services first
docker-compose up -d db redis

# Wait for services to be ready
sleep 30

# Run migrations and setup
docker-compose exec db psql -U donkey_betz -d donkey_betz_prod -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

### Step 5: Load Testing Validation
```bash
# Deploy and run load tests
docker-compose exec web python manage.py deploy_production_system \
  --component load_testing \
  --load-test-users 100 \
  --load-test-duration 300

# Monitor results in Grafana
# Navigate to http://localhost:3000/d/load-testing
```

## 🏃 Workflow Templates Deployment

### Available Templates
1. **Daily Betting Analysis** - Comprehensive daily analysis across all major sports
2. **Arbitrage Hunter** - Real-time arbitrage opportunity detection  
3. **Value Bet Scanner** - Statistical value betting using market inefficiencies
4. **Bankroll Optimizer** - Kelly Criterion optimization and risk management
5. **Live Betting Monitor** - In-game betting opportunities with fast alerts

### Template Configuration
```bash
# Initialize all workflow templates
docker-compose exec web python manage.py deploy_production_system --component workflows

# Configure specific template
docker-compose exec web python manage.py shell -c "
from workflows.models import WorkflowTemplate
template = WorkflowTemplate.objects.get(name='daily_betting_analysis')
template.max_execution_time = 1800  # 30 minutes
template.save()
"

# Schedule daily execution
docker-compose exec web python manage.py shell -c "
from workflows.models import WorkflowSchedule
from django.contrib.auth.models import User
user = User.objects.first()
WorkflowSchedule.objects.create(
    template_id='daily_betting_analysis',
    user=user,
    name='Daily Analysis - 8AM',
    schedule_type='daily',
    start_date='2025-01-10T08:00:00Z',
    input_variables={'sports': ['nfl', 'nba'], 'bankroll': 10000}
)
"
```

## 🛡️ Resilience System Configuration

### Circuit Breakers
```bash
# Configure circuit breakers for external APIs
docker-compose exec web python manage.py shell -c "
from core.resilience import circuit_breakers, CircuitBreakerConfig

# DraftKings API protection
config = CircuitBreakerConfig(
    name='draftkings_api',
    failure_threshold=3,
    timeout=30.0,
    expected_exception=(ConnectionError, TimeoutError)
)
"
```

### Retry Policies
The system automatically configures exponential backoff with jitter for:
- Sports data API calls
- Database operations  
- AI provider requests
- Workflow step execution

### Rate Limiting
- TheOddsAPI: 500 requests/hour
- Weather API: 1000 requests/hour
- AI Providers: Dynamic based on usage

## 📊 Monitoring Setup

### Grafana Dashboards
6 comprehensive dashboards are automatically deployed:

1. **System Overview** - CPU, memory, disk, network, database connections
2. **Agent Performance** - Execution times, success rates, queue depths
3. **Sports Analytics** - Odds calculations, line movements, arbitrage opportunities
4. **Workflow Performance** - Template execution, step-level metrics
5. **Cost Monitoring** - AI provider costs, token usage, optimization opportunities  
6. **Business Metrics** - ROI, win rates, betting performance

### Alert Rules
```bash
# Configure alerts for critical thresholds
docker-compose exec web python manage.py shell -c "
from monitoring.metrics import alert_manager, setup_default_alerts
setup_default_alerts()
alert_manager.start_monitoring()
"
```

### Custom Metrics
```python
from monitoring.metrics import metrics_collector

# Record custom business metrics
metrics_collector.record_betting_performance('arbitrage_strategy', 15.5, 'daily')
metrics_collector.record_arbitrage_opportunity('nfl', 2.3)
metrics_collector.record_line_movement('nba', 'steam')
```

## 🏎️ Performance Optimization

### Cache Configuration
```bash
# Multi-level caching is automatically configured:
# L1: In-memory LRU cache (1000 entries per cache)
# L2: Redis distributed cache (5 minute default TTL)
# L3: Database query result cache

# Monitor cache performance
docker-compose exec web python manage.py shell -c "
from performance.optimization import smart_caches
for name, cache in smart_caches.items():
    print(f'{name}: {cache.get_stats()}')
"
```

### Async Processing
```bash
# Celery workers process tasks across priority queues:
# - high_priority: Real-time alerts, arbitrage opportunities
# - normal_priority: Regular agent executions
# - low_priority: Background analysis
# - background: Cleanup, reporting

# Monitor task processing
curl http://localhost:5555/api/workers
```

### Database Optimization
- Connection pooling (20 base + 30 overflow connections)
- Query result caching with intelligent invalidation
- Read/write replica support (configure multiple databases)
- Slow query logging and optimization suggestions

## 🔒 Security Configuration

### Production Security Checklist
- [ ] Change all default passwords
- [ ] Configure SSL certificates
- [ ] Set up firewall rules
- [ ] Enable database encryption at rest
- [ ] Configure backup encryption
- [ ] Set up intrusion detection
- [ ] Enable audit logging
- [ ] Configure rate limiting
- [ ] Set up VPN access for admin functions

### API Security
```bash
# Configure API rate limits
docker-compose exec web python manage.py shell -c "
from django.conf import settings
settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'user': '1000/hour',
    'anon': '100/hour'
}
"
```

## 🔧 Maintenance Operations

### Health Checks
```bash
# System health verification
docker-compose exec web python manage.py deploy_production_system --verify

# Service-specific health checks
curl http://localhost:8000/health/
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health # Grafana
```

### Backup Operations
```bash
# Database backup
docker-compose exec db pg_dump -U donkey_betz donkey_betz_prod > backup_$(date +%Y%m%d).sql

# Redis backup  
docker-compose exec redis redis-cli BGSAVE

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz docker/ *.yml *.json .env
```

### Log Management
```bash
# View real-time logs
docker-compose logs -f web
docker-compose logs -f celery_worker  
docker-compose logs -f nginx

# Access structured logs via Kibana
# Navigate to http://localhost:5601
```

### Scaling Operations
```bash
# Scale web servers
docker-compose up -d --scale web=3

# Scale Celery workers
docker-compose up -d --scale celery_worker=5

# Update load balancer configuration
# Edit docker/nginx/nginx.conf and reload
docker-compose exec nginx nginx -s reload
```

## 🚨 Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Check memory usage by service
docker stats

# Optimize cache sizes
docker-compose exec web python manage.py shell -c "
from performance.optimization import performance_manager
performance_manager.optimize_for_load(50)  # Reduce for lower memory
"
```

#### Database Connection Issues
```bash
# Check database connections
docker-compose exec web python manage.py dbshell -c "
SELECT state, count(*) FROM pg_stat_activity 
WHERE datname = 'donkey_betz_prod' 
GROUP BY state;
"

# Reset connection pool
docker-compose restart web celery_worker
```

#### API Rate Limits
```bash
# Check rate limit status
docker-compose exec redis redis-cli keys "rate_limit:*"

# Clear rate limits (emergency only)
docker-compose exec redis redis-cli flushdb 1
```

### Performance Issues
```bash
# Generate performance report
docker-compose exec web python manage.py shell -c "
from performance.optimization import performance_manager
print(performance_manager.generate_optimization_report())
"

# Profile slow functions
docker-compose exec web python manage.py shell -c "
from performance.optimization import performance_profiler
print(performance_profiler.get_performance_report())
"
```

## 📈 Monitoring and Alerts

### Key Metrics to Monitor
- Agent execution success rate (> 95%)
- API response time P95 (< 2 seconds)
- Memory usage (< 2GB total)
- Database connection pool utilization (< 80%)
- Redis memory usage (< 1.5GB)
- Celery task queue depth (< 100 pending)

### Alert Channels
Configure in `/docker/alertmanager/alertmanager.yml`:
```yaml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://your-webhook-url'
    send_resolved: true
```

## 🔄 Updates and Upgrades

### Rolling Updates
```bash
# Update application code
git pull origin main
docker-compose build web celery_worker
docker-compose up -d --no-deps web celery_worker

# Update dependencies
docker-compose exec web pip install -r requirements.txt
docker-compose restart web celery_worker
```

### Database Migrations
```bash
# Apply new migrations
docker-compose exec web python manage.py migrate

# Create migration for model changes
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## 📞 Support and Monitoring

### Dashboard URLs
- **System Health**: http://localhost:3000/d/system-overview
- **Agent Performance**: http://localhost:3000/d/agent-performance  
- **Sports Analytics**: http://localhost:3000/d/sports-analytics
- **Business Metrics**: http://localhost:3000/d/business-metrics

### Log Analysis
- **Application Logs**: Kibana at http://localhost:5601
- **System Metrics**: Prometheus at http://localhost:9090
- **Task Queue**: Flower at http://localhost:5555

### Performance Baselines
After successful deployment, establish baselines:
- Run load test: `docker-compose exec web python manage.py deploy_production_system --component load_testing`
- Monitor for 24 hours
- Document normal operating ranges
- Set up alerting thresholds at 20% above normal

## 🎯 Success Criteria

Deployment is successful when:
- [ ] All health checks pass
- [ ] Load test supports 100+ concurrent users
- [ ] All 5 workflow templates are functional
- [ ] Monitoring dashboards show green status
- [ ] API response times meet targets (< 2s P95)
- [ ] Memory usage is within limits (< 2GB)
- [ ] Sports data feeds are operational
- [ ] AI agents execute successfully
- [ ] Error rates are below 1%
- [ ] Backup systems are operational

---

## 🚀 Ready for Production!

Your AI Content Studio with Donkey Betz Agent Orchestra is now ready for enterprise production deployment. The system provides:

- **Scalability**: Handles 100+ concurrent users with sub-2 second response times
- **Reliability**: 99.9% uptime with comprehensive error recovery
- **Monitoring**: Full observability with Prometheus, Grafana, and intelligent alerting
- **Performance**: Multi-level caching and async processing for optimal speed
- **Sports Analytics**: Real-time integration with major sportsbooks and data providers
- **Automation**: 5 production-ready workflow templates for betting analytics

For support, monitoring, and optimization assistance, refer to the comprehensive dashboards and monitoring systems deployed with your system.

**Happy Betting Analytics!** 🎰📊🚀