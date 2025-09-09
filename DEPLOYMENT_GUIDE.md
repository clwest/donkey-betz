# Unified Donkey Betz Platform - Deployment Guide

## 🚀 Quick Start Commands

```bash
# Development Environment
make dev                    # Start complete development environment
make build                  # Build all Docker images
make monitor                # Check system health and status

# Production Deployment
make deploy                 # Deploy to production with monitoring
make scale                  # Scale services for high availability
make backup                 # Create comprehensive backup
```

## 📋 Prerequisites

### Development
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### Production
- Docker Swarm or Kubernetes cluster
- SSL certificates (Let's Encrypt supported)
- Domain name configured
- S3-compatible storage (optional)

## 🛠 Environment Setup

1. **Copy and configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Required environment variables for production:**
```bash
# Security
SECRET_KEY=your-super-secret-django-key-here
DOMAIN=your-domain.com
SSL_EMAIL=admin@your-domain.com

# Database
PROD_DB_PASSWORD=secure_prod_password
REDIS_PASSWORD=secure_redis_password

# Monitoring
GRAFANA_ADMIN_PASSWORD=secure_grafana_password
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## 🐳 Docker Deployment

### Development
```bash
# Start all services
make docker-up

# View logs
make docker-logs

# Scale specific service
make scale SERVICE=backend REPLICAS=3

# Stop all services
make docker-down
```

### Production
```bash
# Build production images
make docker-build-prod

# Deploy to production
make docker-up-prod

# Setup SSL certificates
make ssl-setup

# Configure load balancer
make nginx-setup
```

## 📊 Monitoring Stack

### Services Included
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **ELK Stack**: Centralized logging
- **Jaeger**: Distributed tracing
- **Uptime Kuma**: Service monitoring

### Access URLs (Development)
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601
- Jaeger: http://localhost:16686

### Start Monitoring Stack
```bash
make monitoring-up
```

## 🏥 Health Checks

### Manual Health Check
```bash
# Run comprehensive health check
./scripts/health-check.sh

# JSON output for automation
./scripts/health-check.sh --json

# Prometheus metrics format
./scripts/health-check.sh --prometheus
```

### Automated Health Monitoring
Health checks are built into Docker containers and run every 30 seconds.

## 💾 Backup and Recovery

### Automated Backups
```bash
# Manual backup
make backup-all

# Restore from backup
make restore-all BACKUP_DIR=backups/20231201_120000
```

### Backup Components
- PostgreSQL database (compressed)
- Redis data
- Django application data
- Media files
- Configuration files

### S3 Integration
Configure in `.env` for automated cloud backups:
```bash
AWS_S3_BUCKET=unified-donkey-betz-backups
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

## 📈 Scaling and Performance

### Horizontal Scaling
```bash
# Scale backend workers
make scale-backend

# Scale Celery workers
make scale-celery

# Custom scaling
make scale SERVICE=frontend REPLICAS=5
```

### Performance Optimization

1. **Database Optimization**
   - Connection pooling configured
   - Query optimization enabled
   - Proper indexing implemented

2. **Caching Strategy**
   - Redis caching for sessions
   - Static file caching
   - API response caching

3. **Load Balancing**
   - Nginx reverse proxy
   - Health check based routing
   - SSL termination

## 🔒 Security Configuration

### Production Security Checklist
- [x] SSL/TLS encryption
- [x] HSTS headers
- [x] Rate limiting
- [x] Content Security Policy
- [x] Database connection security
- [x] API key rotation
- [x] Container security scanning

### Security Commands
```bash
# Check security configuration
make verify-security

# Update SSL certificates
make ssl-renew

# Rotate API keys
make rotate-keys
```

## 🧪 Testing

### Test Suite
```bash
# Run all tests
make test-all

# Unit tests only
make test-unit

# Integration tests
make test-integration

# WebSocket tests
make ws-test
```

### Load Testing
```bash
# Install load testing tools
pip install locust

# Run load tests
locust -f tests/load_test.py --host http://localhost:8000
```

## 📝 Logging

### Log Aggregation
- All services log to ELK stack
- Structured JSON logging
- Centralized log analysis
- Real-time log monitoring

### Log Locations
```bash
# View live logs
make logs-live

# Service-specific logs
make docker-logs-backend
make docker-logs-frontend
make docker-logs-nginx
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**
```bash
# Check port usage
make check-ports

# Find and kill process using port
lsof -ti:8000 | xargs kill -9
```

2. **Database Connection Issues**
```bash
# Check PostgreSQL status
make check-postgres

# Restart database
docker-compose restart postgres
```

3. **Redis Connection Issues**
```bash
# Check Redis status
make check-redis

# Clear Redis cache
make cache-clear
```

4. **Memory Issues**
```bash
# Check system resources
make monitor

# Scale down services
make scale-down
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=True
export VERBOSE=true

# Run health checks with verbose output
./scripts/health-check.sh --verbose
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy Unified Platform
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and Deploy
        run: |
          make build
          make test-all
          make deploy
```

### Deployment Hooks
Pre and post-deployment hooks are available in `scripts/` directory:
- `pre-deploy.sh`: Pre-deployment checks
- `post-deploy.sh`: Post-deployment verification
- `rollback.sh`: Automated rollback procedures

## 🎯 Performance Metrics

### Key Performance Indicators
- Response time < 200ms (95th percentile)
- Uptime > 99.9%
- CPU usage < 70%
- Memory usage < 80%
- Database connections < 80% of max

### Monitoring Alerts
Configure alerts in `config/prometheus/alert-rules/`:
- High response time
- Service downtime
- Resource exhaustion
- Error rate spikes

## 📞 Support and Maintenance

### Regular Maintenance Tasks
```bash
# Weekly maintenance
make clean-all           # Clean temporary files
make backup-all         # Create backup
make check-security     # Security audit

# Monthly maintenance
make update-dependencies # Update packages
make ssl-renew          # Renew certificates
make optimize-db        # Database maintenance
```

### Emergency Procedures
```bash
# Emergency shutdown
make emergency-stop

# Quick recovery
make emergency-restore

# Status check
make emergency-status
```

## 🌐 Multi-Environment Support

### Environment Configuration
- Development: Full debugging, hot reload
- Staging: Production-like with debug tools
- Production: Optimized for performance and security

### Environment Switching
```bash
# Switch to staging
export ENV=staging
make deploy

# Switch to production
export ENV=production
make deploy
```

This deployment guide provides comprehensive instructions for managing the Unified Donkey Betz Platform across all environments. For additional support, refer to the individual service documentation in the `docs/` directory.